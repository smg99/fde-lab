import sys
import json
import argparse
from fde_lab.pocs.deployment_engineer.agent import DeploymentEngineerAgent
from fde_lab.pocs.deployment_engineer.models import DeploymentReport
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example, ArtifactEnvelope, WorkerError
from fde_lab.runtime.exit_codes import ExitCode

def print_ui(report: DeploymentReport):
    print("\nFDE Lab")
    print("────────────────────────────────")
    print("\nDeployment Engineer\n")
    
    print("Analyzing customer application...")
    print(f"✓ Application detected ({report.application})")
    print(f"✓ Runtime requirements detected ({report.runtime})")
    print(f"✓ HTTP service detected")
    print(f"✓ Health endpoint detected ({report.health_endpoint})\n")
    
    print("Generating deployment configuration...")
    if report.generated_artifacts:
        for artifact in report.generated_artifacts:
            print(f"✓ Generated {artifact}")
    else:
        print("✗ No artifacts generated")
    print("")
    
    print("Building container...")
    if report.build_status == "SUCCESS":
        print("✓ Image built\n")
        print("Deploying locally...")
        if report.deployment_status == "SUCCESS":
            print("✓ Container started\n")
            print("Verifying application...")
            
            if report.health_status == "HEALTHY":
                print(f"✓ GET {report.health_endpoint}")
            else:
                print(f"✗ GET {report.health_endpoint} failed")
                
            if report.functional_status == "PASSED":
                print("✓ Functional API check\n")
            else:
                print("✗ Functional API check failed\n")
        else:
            print("✗ Container deployment failed\n")
    else:
        print("✗ Image build failed\n")

    # Result Summary
    print("DEPLOYMENT REPORT")
    print("────────────────────────────")
    print(f"Application:\n{report.application}\n")
    
    if report.build_status != "SUCCESS":
        print("Build:\nFAILED\n")
        print(f"Cause:\n{report.failure_cause}\n")
        print("Deployment:\nNOT ATTEMPTED\n")
        print(f"Recommended action:\n{report.recommended_action}\n")
        print(f"Cleanup:\n{report.cleanup_status}\n")
    elif report.health_status != "HEALTHY" or report.functional_status != "PASSED":
        print("Build:\nSUCCESS\n")
        print("Deployment:\nSUCCESS\n")
        print(f"Health:\n{report.health_status}\n")
        print(f"Functional verification:\n{report.functional_status}\n")
        print(f"Cause:\n{report.failure_cause}\n")
        print(f"Recommended action:\n{report.recommended_action}\n")
        print(f"Cleanup:\n{report.cleanup_status}\n")
    else:
        print(f"Runtime:\n{report.runtime}\n")
        print(f"Deployment:\n{report.deployment_tech}\n")
        print(f"Container:\n{report.image}\n")
        print(f"Port:\n{report.port}\n")
        print(f"Health endpoint:\n{report.health_endpoint}\n")
        print(f"Build:\n{report.build_status}\n")
        print(f"Deployment:\n{report.deployment_status}\n")
        print(f"Health:\n{report.health_status}\n")
        print(f"Functional verification:\n{report.functional_status}\n")
        print("Generated artifacts:")
        for artifact in report.generated_artifacts:
            print(artifact)
        print("")

    print("No production systems were modified.")
    print("────────────────────────────────\n")

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - Deployment Engineer")
    parser.add_argument("command", nargs="?", choices=["deploy"], help="Command to execute")
    parser.add_argument("--scenario", default="normal", help="Scenario to run")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--manifest", action="store_true", help="Output capability manifest JSON")
    args = parser.parse_args()

    machine_mode = args.json or args.manifest
    configure_logging(level="WARNING", machine_mode=machine_mode)

    if args.manifest:
        manifest = WorkerManifest(
            name="deployment-engineer",
            version="0.1.0",
            description="Inspects an unfamiliar application, generates deployment configuration, deploys it locally, and verifies it.",
            capabilities=["inspect_application", "generate_deployment", "deploy", "verify"],
            inputs={"scenario": {"type": "string", "allowed": ["normal", "broken-app"], "default": "normal"}},
            outputs={"WorkerResult": "Standard FDE Lab result envelope"},
            side_effects=SideEffectMetadata(filesystem=True, network=True, credentials=False, production=False, destructive=False, external_systems=False),
            requirements=EnvironmentRequirements(node=True, python=True, docker=True),
            examples=[Example(command="npx @fde-lab/deployment-engineer --json", purpose="Deploy the seeded customer application and return a structured result.")]
        )
        print(json.dumps(manifest.to_dict(), indent=2))
        sys.exit(ExitCode.SUCCESS)

    agent = DeploymentEngineerAgent(scenario=args.scenario)
    report = agent.execute_deployment()
    
    if args.json:
        is_success = report.build_status == "SUCCESS" and report.deployment_status == "SUCCESS" and report.health_status == "HEALTHY" and report.functional_status == "PASSED"
        status = "success" if is_success else "failed"
        
        errors = []
        if not is_success:
            errors.append(WorkerError(
                code="DEPLOYMENT_FAILED",
                message=report.failure_cause or "Unknown failure",
                stage=report.failure_stage or "Unknown",
                recoverable=True,
                suggested_action=report.recommended_action or "Check logs"
            ))
            
        artifacts = []
        for artifact in report.generated_artifacts:
            artifacts.append(ArtifactEnvelope(path=artifact, type="deployment-config", description="Generated deployment configuration"))
            
        result = WorkerResult(
            worker={"name": "deployment-engineer", "version": "0.1.0"},
            status=status,
            summary=f"Application deployed and verified successfully." if is_success else "Deployment failed.",
            artifacts=artifacts,
            errors=errors,
            facts=[f"Runtime: {report.runtime}", f"Port: {report.port}"]
        )
        print(json.dumps(result.to_dict(), indent=2))
        sys.exit(ExitCode.SUCCESS if status == "success" else ExitCode.FAILURE)
    else:
        print_ui(report)
        is_success = report.build_status == "SUCCESS" and report.deployment_status == "SUCCESS" and report.health_status == "HEALTHY" and report.functional_status == "PASSED"
        sys.exit(ExitCode.SUCCESS if is_success else ExitCode.FAILURE)

if __name__ == "__main__":
    main()
