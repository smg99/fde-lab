import sys
import json
import argparse

from fde_lab.pocs.support_escalation_engineer.agent import SupportEscalationEngineerAgent
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example, ArtifactEnvelope
from fde_lab.runtime.exit_codes import ExitCode

def print_ui(report):
    print("\nFDE Lab")
    print("────────────────────────────────")
    print("\nSUPPORT ESCALATION\n")
    
    print(f"Customer:\n{report.customer}\n")
    print(f"Issue:\n{report.summary}\n")
    print(f"Classification:\n{report.issue.classification.value}\n")
    print(f"Severity:\n{report.issue.severity.value}\n")
    print(f"Reproduction:\n{report.issue.reproducibility.value}\n")
    
    if len(report.recommended_next_steps) > 0:
        print("Next step:")
        print(f"{report.recommended_next_steps[0]}\n")
        
    print("Generated Artifacts:")
    print(f"- {getattr(report, 'escalation_json_path', '')}")
    print(f"- {getattr(report, 'evidence_json_path', '')}")
    print(f"- {getattr(report, 'reproduction_md_path', '')}")
    print(f"- {getattr(report, 'escalation_md_path', '')}")

def generate_manifest() -> WorkerManifest:
    return WorkerManifest(
        name="support-escalation-engineer",
        version="0.1.0",
        description="Investigates ambiguous customer issues and generates engineering escalations.",
        capabilities=[
            "inspect_customer_issue",
            "inspect_environment",
            "investigate_evidence",
            "attempt_reproduction",
            "classify_issue",
            "assess_severity",
            "generate_escalation"
        ],
        inputs={
            "scenario": "The escalation scenario to execute (normal, not-reproducible, product-bug, customer-configuration)."
        },
        outputs={
            "escalation-json": "Structured escalation data",
            "evidence-json": "Extracted evidence",
            "reproduction-md": "Reproduction steps and results",
            "escalation-report": "Engineering-ready escalation summary"
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
                command="npx @fde-lab/support-escalation-engineer --scenario normal",
                purpose="Runs the escalation workflow for a reproducible bug."
            )
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - Support Escalation Engineer")
    parser.add_argument("command", nargs="?", choices=["escalate"], help="Command to run")
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
        agent = SupportEscalationEngineerAgent()
        report = agent.run(args.scenario)
        
        if args.json:
            artifacts = []
            if hasattr(report, "escalation_json_path"):
                artifacts.append(ArtifactEnvelope(path=report.escalation_json_path, type="escalation-json", description="Structured escalation data"))
            if hasattr(report, "evidence_json_path"):
                artifacts.append(ArtifactEnvelope(path=report.evidence_json_path, type="evidence-json", description="Extracted evidence"))
            if hasattr(report, "reproduction_md_path"):
                artifacts.append(ArtifactEnvelope(path=report.reproduction_md_path, type="reproduction-md", description="Reproduction details"))
            if hasattr(report, "escalation_md_path"):
                artifacts.append(ArtifactEnvelope(path=report.escalation_md_path, type="escalation-report", description="Engineering report"))
                
            status_map = {
                "REPRODUCIBLE": "success",
                "NOT_REPRODUCIBLE": "success", # Both are successful resolutions by the worker
            }
            
            result = WorkerResult(
                worker={"name": "support-escalation-engineer", "version": "0.1.0"},
                status=status_map.get(report.issue.reproducibility.value, "success"),
                summary=f"Escalation status: {report.issue.reproducibility.value}",
                facts=[f"Classification: {report.issue.classification.value}"],
                artifacts=artifacts,
                errors=[],
                next_steps=report.recommended_next_steps
            )
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print_ui(report)
            
        sys.exit(ExitCode.SUCCESS)
        
    except Exception as e:
        if args.json:
            from fde_lab.runtime.result import WorkerError
            result = WorkerResult(
                worker={"name": "support-escalation-engineer", "version": "0.1.0"},
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
