import pytest
from fde_lab.pocs.api_integration_engineer.agent import ApiIntegrationEngineerAgent

def test_api_integration_normal_scenario():
    agent = ApiIntegrationEngineerAgent()
    report = agent.run("normal")
    
    assert report.discovery_status == "success"
    assert report.auth_status == "success"
    assert report.endpoint_status == "success"
    assert report.request_validation_status == "success"
    assert report.response_validation_status == "success"
    assert len(report.integration_risks) > 0 # At least bearer and 429
    assert report.report_path is not None

def test_api_integration_auth_failure_scenario():
    agent = ApiIntegrationEngineerAgent()
    report = agent.run("auth-failure")
    
    assert report.auth_status == "failure"
    assert any("401" in r for r in report.integration_risks) or any("missing" in r.lower() for r in report.integration_risks)

def test_api_integration_schema_mismatch_scenario():
    agent = ApiIntegrationEngineerAgent()
    report = agent.run("schema-mismatch")
    
    # Payload has customer_email but spec needs email
    assert report.request_validation_status == "failure"
    assert any("customer_email" in r for r in report.integration_risks) or any("email" in r for r in report.integration_risks)

def test_api_integration_api_error_scenario():
    agent = ApiIntegrationEngineerAgent()
    report = agent.run("api-error")
    
    # Payload triggers 429 rate limit
    assert report.response_validation_status == "failure"
    assert any("429" in r for r in report.integration_risks)
