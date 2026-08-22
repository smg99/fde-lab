import json
import subprocess
import os

def run_worker_command(worker_name: str, args: list) -> tuple[int, str, str]:
    env = os.environ.copy()
    
    cmd = ["node", f"packages/{worker_name}/dist/cli.js"] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env
    )
    return result.returncode, result.stdout, result.stderr

def test_manifest_schema():
    workers = ["incident-engineer", "integration-engineer", "configuration-engineer"]
    for worker in workers:
        code, stdout, stderr = run_worker_command(worker, ["--manifest"])
        assert code == 0, f"{worker} --manifest failed with code {code}\n{stderr}"
        
        manifest = json.loads(stdout)
        assert manifest["name"] == worker
        assert "exit_codes" in manifest
        assert manifest["exit_codes"]["INCONCLUSIVE"] == 5
        
        # Check result schema
        worker_result_schema = manifest["outputs"]["WorkerResult"]
        assert worker_result_schema["type"] == "object"
        assert "status" in worker_result_schema["properties"]

def test_exit_code_propagation():
    # Incident engineer with inconclusive scenario should exit with 5
    code, stdout, stderr = run_worker_command("incident-engineer", ["--json", "--scenario", "inconclusive"])
    
    # We expect code 5, not 1!
    assert code == 5, f"Expected code 5, got {code}\nSTDOUT: {stdout}\nSTDERR: {stderr}"
    
    # stdout should still be valid json
    result = json.loads(stdout)
    assert result["status"] == "inconclusive"
if __name__ == "__main__":
    test_manifest_schema()
    test_exit_code_propagation()
    print("All tests passed!")
