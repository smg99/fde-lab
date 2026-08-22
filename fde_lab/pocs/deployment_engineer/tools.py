import os
import json
import time
import subprocess
import requests
from typing import Optional, Tuple
from fde_lab.tools.base import Tool
from .models import InspectionResult, DeploymentConfig

class ApplicationInspectorTool(Tool):
    @property
    def name(self) -> str: return "ApplicationInspectorTool"
    @property
    def description(self) -> str: return "Inspects the customer application"
    
    def execute(self, app_path: str) -> InspectionResult:
        has_reqs = os.path.exists(os.path.join(app_path, "requirements.txt"))
        has_app_py = os.path.exists(os.path.join(app_path, "app", "application.py"))
        has_config = os.path.exists(os.path.join(app_path, "config.example.json"))
        
        port = 8000
        health_endpoint = "/health"
        
        if has_app_py:
            with open(os.path.join(app_path, "app", "application.py"), "r") as f:
                content = f.read()
                if "port=" in content:
                    try:
                        port_str = content.split("port=")[1].split(")")[0].strip()
                        port = int(port_str)
                    except:
                        pass
        
        return InspectionResult(
            runtime="Python",
            runtime_version="3.11",
            dependency_file="requirements.txt" if has_reqs else "",
            entrypoint="app/application.py" if has_app_py else "",
            port=port,
            health_endpoint=health_endpoint,
            configuration_file="config.example.json" if has_config else ""
        )

class DeploymentConfigGeneratorTool(Tool):
    @property
    def name(self) -> str: return "DeploymentConfigGeneratorTool"
    @property
    def description(self) -> str: return "Generates Dockerfile and deployment.json"
    
    def execute(self, app_path: str, inspection: InspectionResult, output_dir: str) -> Tuple[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        
        dockerfile_path = os.path.join(output_dir, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(f"""FROM python:{inspection.runtime_version}-slim
WORKDIR /app
COPY {inspection.dependency_file} .
RUN pip install --no-cache-dir -r {inspection.dependency_file}
COPY app ./app
EXPOSE {inspection.port}
CMD ["python", "{inspection.entrypoint}"]
""")

        deployment_json_path = os.path.join(output_dir, "deployment.json")
        config = {
            "application": "customer-demo-api",
            "runtime": inspection.runtime.lower(),
            "runtime_version": inspection.runtime_version,
            "container": {
                "technology": "docker",
                "image": "fde-lab/customer-app"
            },
            "port": inspection.port,
            "health_endpoint": inspection.health_endpoint,
            "entrypoint": inspection.entrypoint
        }
        
        with open(deployment_json_path, "w") as f:
            json.dump(config, f, indent=2)
            
        return dockerfile_path, deployment_json_path

class DockerBuildTool(Tool):
    @property
    def name(self) -> str: return "DockerBuildTool"
    @property
    def description(self) -> str: return "Builds the docker image"
    
    def execute(self, dockerfile_dir: str, app_path: str, image_name: str) -> Tuple[bool, str]:
        cmd = ["docker", "build", "-t", image_name, "-f", os.path.join(dockerfile_dir, "Dockerfile"), app_path]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, ""
        except subprocess.CalledProcessError as e:
            return False, e.stderr

class ContainerRunnerTool(Tool):
    @property
    def name(self) -> str: return "ContainerRunnerTool"
    @property
    def description(self) -> str: return "Runs the docker container on a dynamic port"
    
    def execute(self, image_name: str, internal_port: int) -> Tuple[str, int]:
        cmd = ["docker", "run", "-d", "-p", f"0:{internal_port}", image_name]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            container_id = res.stdout.strip()
            
            port_cmd = ["docker", "port", container_id, str(internal_port)]
            port_res = subprocess.run(port_cmd, capture_output=True, text=True, check=True)
            mapped_port_str = port_res.stdout.strip().split(":")[-1]
            return container_id, int(mapped_port_str)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to start container: {e.stderr}")

class VerificationTool(Tool):
    @property
    def name(self) -> str: return "VerificationTool"
    @property
    def description(self) -> str: return "Verifies endpoints are responsive"
    
    def execute(self, mapped_port: int, health_endpoint: str) -> Tuple[bool, bool]:
        time.sleep(2)  # Allow container to start
        base_url = f"http://localhost:{mapped_port}"
        
        health_ok = False
        api_ok = False
        
        try:
            res = requests.get(f"{base_url}{health_endpoint}", timeout=5)
            health_ok = res.status_code == 200
        except:
            pass
            
        try:
            res = requests.get(f"{base_url}/api/customers", timeout=5)
            api_ok = res.status_code == 200
        except:
            pass
            
        return health_ok, api_ok

class CleanupTool(Tool):
    @property
    def name(self) -> str: return "CleanupTool"
    @property
    def description(self) -> str: return "Stops and removes the container"
    
    def execute(self, container_id: str):
        try:
            subprocess.run(["docker", "stop", container_id], capture_output=True, check=True)
            subprocess.run(["docker", "rm", container_id], capture_output=True, check=True)
        except:
            pass
