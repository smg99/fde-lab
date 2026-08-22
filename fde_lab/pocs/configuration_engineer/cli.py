import sys
import json
import argparse

from fde_lab.pocs.configuration_engineer.agent import ConfigurationEngineerAgent
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example, ArtifactEnvelope
from fde_lab.runtime.exit_codes import ExitCode

def generate_manifest() -> WorkerManifest:
    return WorkerManifest(
        name="configuration-engineer",
        version="0.1.0",
        description="Inspects customer configuration, identifies issues, and proposes a safe change plan.",
        capabilities=[
            "read_customer_configuration",
            "read_configuration_schema",
            "validate_configuration",
            "plan_configuration_changes",
            "assess_change_risk",
            "write_configuration_report"
        ],
        inputs={
            "scenario": "The configuration scenario to execute (normal, missing-required, invalid-values, conflicting-config, unsafe-change)."
        },
        outputs={
            "configuration-change-plan": "Full JSON configuration plan patch"
        },
        side_effects=SideEffectMetadata(
            filesystem=True,
            network=False,
            credentials=False,
            production=False,
            destructive=False,
            external_systems=False
        ),
        requirements=EnvironmentRequirements(
            node=True,
            python=True,
            docker=False
        ),
        examples=[
            Example(
                command="npx @fde-lab/configuration-engineer --scenario missing-required",
                purpose="Inspects customer configuration and proposes a fix for missing fields."
            )
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - Configuration Engineer")
    parser.add_argument("command", nargs="?", choices=["inspect-configuration"], help="Command to run")
    parser.add_argument("-s", "--scenario", default="normal", help="Scenario to run")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--manifest", action="store_true", help="Output capability manifest JSON")
    
    args = parser.parse_args()
    
    machine_mode = args.json or args.manifest
    configure_logging(machine_mode=machine_mode)
    
    if args.manifest:
        manifest = generate_manifest()
        print(json.dumps(manifest.to_dict(), indent=2))
        sys.exit(ExitCode.SUCCESS)
        
    try:
        agent = ConfigurationEngineerAgent()
        report = agent.run(args.scenario)
        
        if args.json:
            artifacts = []
            if hasattr(report, "report_path") and report.report_path:
                artifacts.append(ArtifactEnvelope(path=report.report_path, type="configuration-change-plan", description="Configuration change plan"))
                
            result = WorkerResult(
                worker={"name": "configuration-engineer", "version": "0.1.0"},
                status=report.status,
                summary=f"Configuration inspection complete. Status: {report.status.upper()}",
                facts=[
                    f"Issues Found: {len(report.issues)}",
                    f"Risk Level: {report.risk.level}",
                    f"Action Required: {report.action_required}"
                ],
                artifacts=artifacts,
                errors=[],
                next_steps=[c.reason for c in report.recommended_changes]
            )
            
            # Inject structured outputs for AI consumption
            res_dict = result.to_dict()
            res_dict["scenario"] = report.scenario
            res_dict["observations"] = report.observations
            res_dict["issues"] = [
                {"path": i.path, "type": i.issue_type, "description": i.description, "current": i.current_value, "expected": i.expected_value} for i in report.issues
            ]
            res_dict["recommended_changes"] = [
                {"path": c.path, "current": c.current_value, "proposed": c.proposed_value, "reason": c.reason} for c in report.recommended_changes
            ]
            res_dict["risk"] = {
                "level": report.risk.level,
                "reason": report.risk.reason,
                "requires_approval": report.risk.requires_approval
            }
            res_dict["action_required"] = report.action_required
            res_dict["changes_applied"] = report.changes_applied
            
            print(json.dumps(res_dict, indent=2))
        else:
            print(report.human_output)
            
        sys.exit(ExitCode.SUCCESS)
        
    except Exception as e:
        if args.json:
            from fde_lab.runtime.result import WorkerError
            result = WorkerResult(
                worker={"name": "configuration-engineer", "version": "0.1.0"},
                status="failure",
                summary="Execution failed",
                errors=[WorkerError(code="INTERNAL_ERROR", message=str(e), stage="execution", recoverable=False, suggested_action="Check logs")]
            )
            print(json.dumps(result.to_dict(), indent=2))
        else:
            import traceback
            traceback.print_exc()
        sys.exit(ExitCode.FAILURE)

if __name__ == "__main__":
    main()
