import pytest
import os
import json
from fde_lab.pocs.integration_engineer.agent import IntegrationEngineerAgent
from fde_lab.pocs.integration_engineer.models import IntegrationReport

def test_integration_engineer_normal_scenario():
    agent = IntegrationEngineerAgent(scenario="normal")
    report = agent.execute_integration()
    
    assert isinstance(report, IntegrationReport)
    assert report.records_received == 2
    assert report.records_transformed == 2
    assert report.records_rejected == 0
    assert len(report.rejected_records) == 0
    assert "marketing_opt_in" in report.mapping.unmapped_source_fields
    
    # Check that output file was created and contains valid JSON
    assert os.path.exists(report.output_path)
    with open(report.output_path, "r") as f:
        data = json.load(f)
        assert len(data) == 2
        assert data[0]["external_customer_id"] == "C001"
        assert data[0]["name"] == "John Smith"
        assert data[0]["email_address"] == "john@example.com"
        assert data[0]["organization"] == "Acme Inc"
        assert data[0]["country_code"] == "US"
        assert data[0]["subscription_tier"] == "PRO"

def test_integration_engineer_invalid_data_scenario():
    agent = IntegrationEngineerAgent(scenario="invalid-data")
    report = agent.execute_integration()
    
    assert isinstance(report, IntegrationReport)
    assert report.records_received == 4
    # 2 are invalid (C003 missing email, C004 invalid country XX, C005 invalid plan UNKNOWN)
    # Wait, in the RecordReaderTool:
    # C003 missing email -> Invalid
    # C004 country XX -> Invalid
    # C005 plan UNKNOWN -> Invalid
    # Let's check how many were invalid
    assert report.records_transformed == 1 # Only C001 is valid
    assert report.records_rejected == 3
    assert "C003" in report.rejected_records
    assert "C004" in report.rejected_records
    assert "C005" in report.rejected_records

def test_transformation_concat():
    agent = IntegrationEngineerAgent(scenario="normal")
    record = {"first_name": "Jane", "last_name": "Doe"}
    # Agent builds mapping with concat for name
    agent.tools["source_schema"].execute()
    agent.tools["target_schema"].execute()
    report = agent.execute_integration()
    
    # Check the actual mapping rules directly
    concat_rule = next(r for r in report.mapping.rules if r.transformation_type == "concat")
    assert concat_rule.source_fields == ["first_name", "last_name"]
    assert concat_rule.target_field == "name"

