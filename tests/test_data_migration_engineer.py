import pytest
from fde_lab.pocs.data_migration_engineer.agent import DataMigrationEngineerAgent

def test_migration_normal_scenario():
    agent = DataMigrationEngineerAgent()
    report = agent.run("normal")
    
    assert report.records_inspected == 2
    assert report.migrated_records == 2
    assert report.quarantined_records == 0
    assert report.status == "completed"
    assert len(report.transformations) > 0 # At least email normalization and date ISO
    assert report.migrated_path is not None
    assert report.quarantine_path is not None

def test_migration_messy_data_scenario():
    agent = DataMigrationEngineerAgent()
    report = agent.run("messy-data")
    
    # 6 records total
    # L-201: OK
    # L-202: invalid email -> Quarantine
    # L-203: missing full_name parts -> Quarantine
    # L-201 duplicate: duplicate legacy ID -> Quarantine
    # L-205: not a date, unknown tier -> Quarantine
    # L-206: duplicate email (with Charlie) -> Quarantine
    
    assert report.records_inspected == 6
    assert report.quarantined_records >= 5 
    assert report.status == "completed_with_warnings"

def test_migration_schema_conflict_scenario():
    agent = DataMigrationEngineerAgent()
    report = agent.run("schema-conflict")
    
    # Needs tax_id which source_data doesn't have
    assert report.records_inspected == 1
    assert report.quarantined_records == 1
    assert report.migrated_records == 0
    assert any("tax_id" in c for c in report.schema_conflicts)

def test_migration_dry_run_scenario():
    agent = DataMigrationEngineerAgent()
    report = agent.run("dry-run")
    
    # Should work but paths should be None
    assert report.records_inspected == 1
    assert report.migrated_records == 1
    assert report.migrated_path is None
    assert report.quarantine_path is None
    assert report.report_path is None
