import pytest
import os
import json
from unittest.mock import patch, MagicMock
from fde_lab.pocs.deployment_engineer.agent import DeploymentEngineerAgent
from fde_lab.pocs.deployment_engineer.models import DeploymentReport

@patch('fde_lab.pocs.deployment_engineer.tools.ContainerRunnerTool.execute')
@patch('fde_lab.pocs.deployment_engineer.tools.DockerBuildTool.execute')
@patch('fde_lab.pocs.deployment_engineer.tools.CleanupTool.execute')
@patch('fde_lab.pocs.deployment_engineer.tools.VerificationTool.execute')
def test_deployment_engineer_normal_scenario(mock_verify, mock_clean, mock_build, mock_run):
    # Setup mocks for success
    mock_build.return_value = (True, "")
    mock_run.return_value = ("mock_container_id", 32768)
    mock_verify.return_value = (True, True)
    
    agent = DeploymentEngineerAgent(scenario="normal")
    report = agent.execute_deployment()
    
    assert isinstance(report, DeploymentReport)
    assert report.build_status == "SUCCESS"
    assert report.deployment_status == "SUCCESS"
    assert report.health_status == "HEALTHY"
    assert report.functional_status == "PASSED"
    assert report.cleanup_status == "COMPLETE"
    assert report.port == 8000
    
    # Check that output files were generated
    output_dir = os.path.join(os.getcwd(), "output")
    assert os.path.exists(os.path.join(output_dir, "Dockerfile"))
    assert os.path.exists(os.path.join(output_dir, "deployment.json"))
    
    # Clean up mock output files to not pollute workspace
    try:
        os.remove(os.path.join(output_dir, "Dockerfile"))
        os.remove(os.path.join(output_dir, "deployment.json"))
    except:
        pass

@patch('fde_lab.pocs.deployment_engineer.tools.DockerBuildTool.execute')
def test_deployment_engineer_broken_app_scenario(mock_build):
    # Setup mocks for build failure
    mock_build.return_value = (False, "ERROR: Could not find a version that satisfies the requirement fastapi==999.999.0")
    
    agent = DeploymentEngineerAgent(scenario="broken")
    report = agent.execute_deployment()
    
    assert isinstance(report, DeploymentReport)
    assert report.build_status == "FAILED"
    assert report.deployment_status == "PENDING"
    assert "999.999.0" in report.failure_cause
    assert report.recommended_action is not None
    assert "requirements.txt" in report.recommended_action
    assert report.cleanup_status == "No running container remains."
