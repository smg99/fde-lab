import logging
from typing import Dict, Any, List

from fde_lab.pocs.data_migration_engineer.models import (
    MigrationRecord, RecordStatus, MigrationReport
)
from fde_lab.pocs.data_migration_engineer.tools import (
    SchemaInspectorTool, SourceRecordReaderTool, RecordTransformerTool,
    FieldValidatorTool, DuplicateDetectorTool, MigrationWriterTool
)

logger = logging.getLogger("fde_lab.pocs.data_migration_engineer.agent")

class DataMigrationEngineerAgent:
    def __init__(self):
        self.schema_tool = SchemaInspectorTool()
        self.source_tool = SourceRecordReaderTool()
        self.transformer = RecordTransformerTool()
        self.validator = FieldValidatorTool()
        self.deduper = DuplicateDetectorTool()
        self.writer = MigrationWriterTool()
        
    def run(self, scenario: str) -> MigrationReport:
        logger.info(f"Starting Data Migration for scenario: {scenario}")
        is_dry_run = (scenario == "dry-run")
        
        # We might need to load normal data for dry-run if dry-run doesn't have its own source.
        # But we created dry-run data, so we'll use that.
        
        schema = self.schema_tool.execute(scenario=scenario)
        source_records = self.source_tool.execute(scenario=scenario)
        
        duplicates = self.deduper.execute(records=source_records)
        
        migrated = []
        quarantined = []
        rejected = 0
        
        all_warnings = []
        all_transformations = []
        all_conflicts = []
        
        for src in source_records:
            lid = src.get("legacy_id")
            
            # Check duplicates first
            if lid in duplicates:
                quarantined.append({
                    "legacy_id": lid,
                    "reason": "Duplicate record",
                    "details": duplicates[lid],
                    "original_record": src
                })
                all_warnings.append(f"Duplicate detected: {lid}")
                continue
                
            # Transform
            t_res = self.transformer.execute(record=src, schema=schema)
            target = t_res["target"]
            transformations = t_res["transformations"]
            
            # Validate
            v_res = self.validator.execute(target_record=target, schema=schema)
            
            if not v_res["is_valid"]:
                # Failed validation -> quarantine/reject
                quarantined.append({
                    "legacy_id": lid,
                    "reason": "Schema validation failed",
                    "details": v_res["errors"],
                    "original_record": src,
                    "attempted_mapping": target
                })
                for err in v_res["errors"]:
                    if "Missing required field" in err or "Invalid" in err:
                        all_conflicts.append(err)
                continue
                
            # Success
            migrated.append(target)
            all_transformations.extend(transformations)
            
        status = "completed"
        if len(quarantined) > 0:
            status = "completed_with_warnings"
            
        report = MigrationReport(
            source="Legacy CRM",
            target="New Customer Platform",
            records_inspected=len(source_records),
            migrated_records=len(migrated),
            rejected_records=rejected, # Hard failures, we used quarantine for everything
            quarantined_records=len(quarantined),
            warnings=all_warnings,
            transformations=all_transformations,
            schema_conflicts=all_conflicts,
            status=status
        )
        
        w_res = self.writer.execute(
            migrated=migrated,
            quarantined=quarantined,
            report=report.to_dict(),
            is_dry_run=is_dry_run
        )
        
        # Attach dynamic outputs
        report.migrated_path = w_res["migrated_path"]
        report.quarantine_path = w_res["quarantine_path"]
        report.report_path = w_res["report_path"]
        report.human_output = w_res["human_output"]
        
        return report
