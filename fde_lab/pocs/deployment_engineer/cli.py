import argparse
from fde_lab.pocs.deployment_engineer.agent import DeploymentEngineerAgent
from fde_lab.pocs.deployment_engineer.models import DeploymentReport

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
    parser.add_argument("command", choices=["deploy"], help="Command to execute")
    parser.add_argument("--scenario", default="normal", help="Scenario to run")
    args = parser.parse_args()

    if args.command == "deploy":
        agent = DeploymentEngineerAgent(scenario=args.scenario)
        report = agent.execute_deployment()
        print_ui(report)

if __name__ == "__main__":
    main()
