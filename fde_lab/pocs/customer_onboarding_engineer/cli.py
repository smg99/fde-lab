import sys
import json
import argparse
from typing import Dict, Any

from fde_lab.pocs.customer_onboarding_engineer.agent import CustomerOnboardingEngineerAgent
from fde_lab.pocs.customer_onboarding_engineer.models import OnboardingReport
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example, ArtifactEnvelope
from fde_lab.runtime.exit_codes import ExitCode

def print_ui(report: OnboardingReport):
    print("\nFDE Lab")
    print("────────────────────────────────")
    print("\nCustomer Onboarding Engineer\n")
    
    if report.mapping.status == "READY" and report.validation.valid:
        print("ONBOARDING READY\n")
    elif report.mapping.status == "INCOMPLETE":
        print("ONBOARDING INCOMPLETE\n")
    else:
        print("UNSUPPORTED\n")
        
    print(f"Customer:\n{report.customer_name}\n")
    
    if report.validation.valid:
        print("Configuration:\nVALID\n")
    else:
        print("Configuration:\nINVALID\n")
        for err in report.validation.errors:
            print(f"- {err}")
        print()
        
    print(f"Requirements:\n{report.mapping.satisfied_count}/{report.mapping.total_count} satisfied\n")
    
    if len(report.mapping.missing) > 0:
        print("Missing:")
        for m in report.mapping.missing:
            print(f"- {m}")
        print()
        
    if len(report.mapping.unsupported) > 0:
        print("Unsupported:")
        for u in report.mapping.unsupported:
            print(f"- {u}")
        print()
        
    print(f"Status:\n{report.mapping.status}\n")
    
    if report.mapping.status == "READY":
        print("Generated package:")
        print(f"{report.config_path}")
        print("\nChecklist:")
        print(f"{report.checklist_path}")
    elif report.mapping.status == "INCOMPLETE":
        print("Recommended next steps:")
        print("Resolve missing configurations.")
    elif report.mapping.status == "BLOCKED":
        print("Recommended action:")
        print("Confirm alternative integrations or escalate the requirement for product review.")

def generate_manifest() -> WorkerManifest:
    return WorkerManifest(
        name="customer-onboarding-engineer",
        version="0.1.0",
        description="Validates customer configuration and generates onboarding packages.",
        capabilities=[
            "inspect_customer",
            "validate_onboarding",
            "map_requirements",
            "generate_configuration",
            "verify_onboarding"
        ],
        inputs={
            "scenario": "The onboarding scenario to execute (normal, incomplete, unsupported)."
        },
        outputs={
            "onboarding-config": "Normalized JSON configuration",
            "onboarding-checklist": "Markdown checklist",
            "onboarding-report": "Markdown execution report"
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
                command="npx @fde-lab/customer-onboarding-engineer --scenario normal",
                purpose="Runs the onboarding validation for a normal customer scenario."
            )
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - Customer Onboarding Engineer")
    parser.add_argument("command", nargs="?", choices=["onboard"], help="Command to run")
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
        agent = CustomerOnboardingEngineerAgent()
        report = agent.run(args.scenario)
        
        if args.json:
            artifacts = []
            if report.config_path:
                artifacts.append(ArtifactEnvelope(path=report.config_path, type="onboarding-config", description="Normalized onboarding config"))
            if report.checklist_path:
                artifacts.append(ArtifactEnvelope(path=report.checklist_path, type="onboarding-checklist", description="Markdown checklist"))
            if report.report_path:
                artifacts.append(ArtifactEnvelope(path=report.report_path, type="onboarding-report", description="Markdown report"))
                
            status_map = {
                "READY": "success",
                "INCOMPLETE": "failure",
                "BLOCKED": "failure"
            }
            
            # Convert raw strings to WorkerError if any
            worker_errors = []
            if not report.validation.valid:
                for err in report.validation.errors:
                    from fde_lab.runtime.result import WorkerError
                    worker_errors.append(WorkerError(code="VALIDATION_ERROR", message=err, stage="validate", recoverable=False, suggested_action="Fix config"))
                    
            result = WorkerResult(
                worker={"name": "customer-onboarding-engineer", "version": "0.1.0"},
                status=status_map.get(report.mapping.status, "failure"),
                summary=f"Onboarding status: {report.mapping.status}",
                facts=[f"Requirements satisfied: {report.mapping.satisfied_count}/{report.mapping.total_count}"],
                artifacts=artifacts,
                errors=worker_errors
            )
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print_ui(report)
            
        sys.exit(ExitCode.SUCCESS)
        
    except Exception as e:
        if args.json:
            from fde_lab.runtime.result import WorkerError
            result = WorkerResult(
                worker={"name": "customer-onboarding-engineer", "version": "0.1.0"},
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
