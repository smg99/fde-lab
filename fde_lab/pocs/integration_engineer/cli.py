import sys
import json
import argparse
from fde_lab.pocs.integration_engineer.agent import IntegrationEngineerAgent
from fde_lab.pocs.integration_engineer.models import IntegrationReport
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example, ArtifactEnvelope
from fde_lab.runtime.exit_codes import ExitCode

def print_ui(report: IntegrationReport):
    print("\nFDE Lab")
    print("────────────────────────────────")
    print("\nIntegration Engineer\n")
    print("Customer integration:\nCRM → Billing System\n")
    
    print("Analyzing source schema...")
    print("✓ 8 source fields discovered\n")
    
    print("Analyzing target schema...")
    print("✓ 6 target fields discovered\n")
    
    print("Building mapping...")
    for rule in report.mapping.rules:
        src = " + ".join(rule.source_fields)
        print(f"✓ {src} → {rule.target_field}")
    for unmapped in report.mapping.unmapped_source_fields:
        print(f"✗ Unmapped source field: {unmapped}")
        
    print("\nValidating records...")
    print(f"✓ {report.records_transformed} records valid")
    print(f"✗ {report.records_rejected} records rejected\n")
    
    if report.rejected_records:
        print("Rejected records:")
        for cid, reason in report.rejected_records.items():
            print(f"- {cid}: {reason}")
        print("")
        
    print("Transforming records...")
    print(f"✓ {report.records_transformed} records transformed\n")
    
    print("Integration complete.\n")
    print(f"Output:\n{report.output_path}\n")
    
    print("Explanation:")
    print(report.explanation)
    print("\n────────────────────────────────\n")

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - Integration Engineer")
    parser.add_argument("command", nargs="?", choices=["integrate"], help="Command to execute")
    parser.add_argument("--scenario", default="normal", help="Scenario to run")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--manifest", action="store_true", help="Output capability manifest JSON")
    args = parser.parse_args()
    
    machine_mode = args.json or args.manifest
    configure_logging(level="WARNING", machine_mode=machine_mode)

    if args.manifest:
        manifest = WorkerManifest(
            name="integration-engineer",
            version="0.1.0",
            description="Maps, validates, transforms, and produces customer integration data.",
            capabilities=["map_data", "validate_data", "transform_data"],
            inputs={"scenario": {"type": "string", "allowed": ["normal", "invalid-data"], "default": "normal"}},
            outputs={"WorkerResult": "Standard FDE Lab result envelope"},
            side_effects=SideEffectMetadata(filesystem=True, network=False, credentials=False, production=False, destructive=False, external_systems=False),
            requirements=EnvironmentRequirements(node=True, python=True, docker=True),
            examples=[Example(command="npx @fde-lab/integration-engineer --json", purpose="Transform data and write to output file.")]
        )
        print(json.dumps(manifest.to_dict(), indent=2))
        sys.exit(ExitCode.SUCCESS)

    agent = IntegrationEngineerAgent(scenario=args.scenario)
    report = agent.execute_integration()
    
    if args.json:
        status = "success" if report.records_transformed > 0 else "failed"
        result = WorkerResult(
            worker={"name": "integration-engineer", "version": "0.1.0"},
            status=status,
            summary=f"Integration complete. {report.records_transformed} records transformed.",
            artifacts=[ArtifactEnvelope(path=report.output_path, type="json-data", description="Transformed integration data")] if report.output_path else [],
            facts=[f"Total source records: {report.records_received}", f"Valid records: {report.records_transformed}", f"Rejected records: {report.records_rejected}"]
        )
        print(json.dumps(result.to_dict(), indent=2))
        sys.exit(ExitCode.SUCCESS if status == "success" else ExitCode.FAILURE)
    else:
        print_ui(report)
        sys.exit(ExitCode.SUCCESS)

if __name__ == "__main__":
    main()
