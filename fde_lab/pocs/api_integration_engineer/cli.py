import sys
import json
import argparse

from fde_lab.pocs.api_integration_engineer.agent import ApiIntegrationEngineerAgent
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example, ArtifactEnvelope
from fde_lab.runtime.exit_codes import ExitCode

def generate_manifest() -> WorkerManifest:
    return WorkerManifest(
        name="api-integration-engineer",
        version="0.1.0",
        description="Discovers and analyzes a 3rd party API contract and tests integration.",
        capabilities=[
            "read_api_spec",
            "read_customer_config",
            "validate_request",
            "simulate_api_call",
            "write_integration_artifacts"
        ],
        inputs={
            "scenario": "The integration scenario to execute (normal, auth-failure, schema-mismatch, api-error)."
        },
        outputs={
            "api-integration-report": "Integration analysis and risks",
            "integration-example": "Generated integration code/schema"
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
                command="npx @fde-lab/api-integration-engineer --scenario auth-failure",
                purpose="Runs the API integration analysis simulating an auth failure."
            )
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - API Integration Engineer")
    parser.add_argument("command", nargs="?", choices=["integrate-api"], help="Command to run")
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
        agent = ApiIntegrationEngineerAgent()
        report = agent.run(args.scenario)
        
        if args.json:
            artifacts = []
            if hasattr(report, "report_path") and report.report_path:
                artifacts.append(ArtifactEnvelope(path=report.report_path, type="api-integration-report", description="Integration report"))
            if hasattr(report, "example_path") and report.example_path:
                artifacts.append(ArtifactEnvelope(path=report.example_path, type="integration-example", description="Integration example structure"))
                
            overall_status = "success"
            if "failure" in [report.auth_status, report.endpoint_status, report.request_validation_status, report.response_validation_status]:
                overall_status = "failure"
                
            result = WorkerResult(
                worker={"name": "api-integration-engineer", "version": "0.1.0"},
                status=overall_status,
                summary=f"API Analysis complete. Found {len(report.integration_risks)} risks.",
                facts=[
                    f"Auth: {report.auth_status}",
                    f"Request: {report.request_validation_status}",
                    f"Response: {report.response_validation_status}"
                ],
                artifacts=artifacts,
                errors=[],
                next_steps=report.recommended_approach
            )
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(report.human_output)
            
        sys.exit(ExitCode.SUCCESS)
        
    except Exception as e:
        if args.json:
            from fde_lab.runtime.result import WorkerError
            result = WorkerResult(
                worker={"name": "api-integration-engineer", "version": "0.1.0"},
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
