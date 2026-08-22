import subprocess
import json
import pytest
import sys

POC_MODULES = {
    "fde_lab.pocs.incident_engineer.cli": "investigate",
    "fde_lab.pocs.integration_engineer.cli": "integrate",
    "fde_lab.pocs.deployment_engineer.cli": "deploy"
}

@pytest.mark.parametrize("module, command", POC_MODULES.items())
def test_worker_manifest_valid_json(module, command):
    # Test --manifest
    res = subprocess.run([sys.executable, "-m", module, command, "--manifest"], capture_output=True, text=True)
    assert res.returncode == 0, f"{module} --manifest failed with exit code {res.returncode}"
    
    # Must be valid json on stdout
    try:
        manifest = json.loads(res.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Stdout is not valid JSON:\n{res.stdout}")
        
    # Check manifest required fields
    assert "name" in manifest
    assert "version" in manifest
    assert "description" in manifest
    assert "capabilities" in manifest
    assert "inputs" in manifest
    assert "outputs" in manifest
    assert "side_effects" in manifest
    assert "requirements" in manifest

@pytest.mark.parametrize("module, command", POC_MODULES.items())
def test_worker_json_valid_envelope(module, command):
    # Test --json
    # Pass --json to the CLI
    res = subprocess.run([sys.executable, "-m", module, command, "--json"], capture_output=True, text=True)
    # The agent might fail (like deployment engineer without docker), but it MUST return a predictable code (like 0, 1, 5)
    assert res.returncode in [0, 1, 2, 3, 4, 5], f"{module} --json returned unknown exit code {res.returncode}"
    
    # Must be valid json on stdout
    try:
        result = json.loads(res.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Stdout is not valid JSON:\n{res.stdout}")
        
    # Check result required fields
    assert "schema_version" in result
    assert "worker" in result
    assert "status" in result
    assert "summary" in result
    assert "facts" in result
    assert "artifacts" in result
    assert "errors" in result

def test_human_ux_preserved():
    # Just a quick check to ensure human mode doesn't output JSON
    res = subprocess.run([sys.executable, "-m", "fde_lab.pocs.incident_engineer.cli", "investigate"], capture_output=True, text=True)
    assert "FDE Lab" in res.stdout
    assert "{" not in res.stdout[0:5] # Shouldn't start with JSON brace
