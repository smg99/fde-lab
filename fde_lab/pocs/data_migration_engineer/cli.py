import sys
import json
import argparse

from fde_lab.pocs.data_migration_engineer.agent import DataMigrationEngineerAgent
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example, ArtifactEnvelope
from fde_lab.runtime.exit_codes import ExitCode

def generate_manifest() -> WorkerManifest:
    return WorkerManifest(
        name="data-migration-engineer",
        version="0.1.0",
        description="Inspects legacy data, maps to target schema, and safely executes migration.",
        capabilities=[
            "inspect_schema",
            "read_source_records",
            "transform_record",
            "validate_record",
            "detect_duplicates",
            "write_migration_output"
        ],
        inputs={
            "scenario": "The migration scenario to execute (normal, messy-data, schema-conflict, dry-run)."
        },
        outputs={
            "migrated-json": "Successfully migrated records",
            "quarantine-json": "Records failing validation",
            "report-json": "Migration analysis report"
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
                command="npx @fde-lab/data-migration-engineer --scenario messy-data",
                purpose="Runs the migration analysis with dirty data."
            )
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - Data Migration Engineer")
    parser.add_argument("command", nargs="?", choices=["migrate"], help="Command to run")
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
        agent = DataMigrationEngineerAgent()
        report = agent.run(args.scenario)
        
        if args.json:
            artifacts = []
            if hasattr(report, "migrated_path") and report.migrated_path:
                artifacts.append(ArtifactEnvelope(path=report.migrated_path, type="migrated-json", description="Migrated records"))
            if hasattr(report, "quarantine_path") and report.quarantine_path:
                artifacts.append(ArtifactEnvelope(path=report.quarantine_path, type="quarantine-json", description="Quarantined records"))
            if hasattr(report, "report_path") and report.report_path:
                artifacts.append(ArtifactEnvelope(path=report.report_path, type="report-json", description="Migration report"))
                
            result = WorkerResult(
                worker={"name": "data-migration-engineer", "version": "0.1.0"},
                status="success",
                summary=f"Migration {report.status}. Inspected {report.records_inspected} records.",
                facts=[
                    f"Migrated: {report.migrated_records}",
                    f"Quarantined: {report.quarantined_records}"
                ],
                artifacts=artifacts,
                errors=[],
                next_steps=["Review quarantine" if report.quarantined_records > 0 else "Ready for import"]
            )
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(report.human_output)
            
        sys.exit(ExitCode.SUCCESS)
        
    except Exception as e:
        if args.json:
            from fde_lab.runtime.result import WorkerError
            result = WorkerResult(
                worker={"name": "data-migration-engineer", "version": "0.1.0"},
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
