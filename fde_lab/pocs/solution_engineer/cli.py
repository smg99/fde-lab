import sys
import json
import argparse

from fde_lab.pocs.solution_engineer.agent import SolutionEngineerAgent
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example, ArtifactEnvelope
from fde_lab.runtime.exit_codes import ExitCode

def generate_manifest() -> WorkerManifest:
    return WorkerManifest(
        name="solution-engineer",
        version="0.1.0",
        description="Turns ambiguous customer requirements into concrete technical implementation plans, identifying gaps and conflicts.",
        capabilities=[
            "read_requirements",
            "read_environment",
            "detect_conflicts",
            "analyze_gaps",
            "plan_architecture",
            "plan_implementation",
            "assess_risks"
        ],
        inputs={
            "scenario": "The scenario to execute (normal, constrained-environment, integration-gap, conflicting-requirements, insufficient-information)."
        },
        outputs={
            "solution-report": "Full JSON solution blueprint"
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
                command="npx @fde-lab/solution-engineer --scenario normal",
                purpose="Designs a solution architecture for a standard customer requirement."
            )
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - Solution Engineer")
    parser.add_argument("command", nargs="?", choices=["design-solution"], help="Command to run")
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
        agent = SolutionEngineerAgent()
        report = agent.run(args.scenario)
        
        if args.json:
            artifacts = []
            if hasattr(report, "report_path") and report.report_path:
                artifacts.append(ArtifactEnvelope(path=report.report_path, type="solution-report", description="Structured solution report JSON"))
                
            result = WorkerResult(
                worker={"name": "solution-engineer", "version": "0.1.0"},
                status=report.status,
                summary=f"Solution design complete. Status: {report.status.upper()}",
                facts=[
                    f"Conflicts: {len(report.conflicts)}",
                    f"Gaps: {len(report.gaps)}",
                    f"Requires Input: {report.requires_customer_input}"
                ],
                artifacts=artifacts,
                errors=[],
                next_steps=["Review solution report"] if not report.requires_customer_input else ["Provide requested customer input"]
            )
            
            # Inject structured data for AI Consumption
            res_dict = result.to_dict()
            report_dict = report.to_dict()
            for key in ["scenario", "requirements", "observations", "constraints", "gaps", "conflicts", "architecture", "implementation_plan", "risks", "assumptions", "customer_questions", "confidence", "requires_customer_input"]:
                res_dict[key] = report_dict.get(key)
                
            print(json.dumps(res_dict, indent=2))
        else:
            print(report.human_output)
            
        sys.exit(ExitCode.SUCCESS)
        
    except Exception as e:
        if args.json:
            from fde_lab.runtime.result import WorkerError
            result = WorkerResult(
                worker={"name": "solution-engineer", "version": "0.1.0"},
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
