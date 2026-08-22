import os
from .models import DeploymentReport
from .tools import (
    ApplicationInspectorTool,
    DeploymentConfigGeneratorTool,
    DockerBuildTool,
    ContainerRunnerTool,
    VerificationTool,
    CleanupTool
)

class DeploymentEngineerAgent:
    def __init__(self, scenario: str = "normal"):
        self.scenario = scenario
        self.tools = {
            "inspector": ApplicationInspectorTool(),
            "generator": DeploymentConfigGeneratorTool(),
            "builder": DockerBuildTool(),
            "runner": ContainerRunnerTool(),
            "verifier": VerificationTool(),
            "cleaner": CleanupTool()
        }
        
    def execute_deployment(self) -> DeploymentReport:
        app_path = os.path.join(os.path.dirname(__file__), "demo_apps", self.scenario)
        output_dir = os.path.join(os.getcwd(), "output")
        image_name = "fde-lab/customer-app"
        
        report = DeploymentReport(
            application="Customer Demo API",
            runtime="Unknown",
            deployment_tech="Docker",
            image=image_name,
            port=0,
            health_endpoint=""
        )
        
        # 1. Inspect
        inspection = self.tools["inspector"].execute(app_path)
        report.runtime = f"{inspection.runtime} {inspection.runtime_version}"
        report.port = inspection.port
        report.health_endpoint = inspection.health_endpoint
        
        # 2. Generate
        dockerfile_path, json_path = self.tools["generator"].execute(app_path, inspection, output_dir)
        report.generated_artifacts = [dockerfile_path, json_path]
        
        # 3. Build
        success, err = self.tools["builder"].execute(output_dir, app_path, image_name)
        if not success:
            report.build_status = "FAILED"
            report.failure_stage = "Docker build"
            report.failure_cause = "Required dependency could not be installed.\n" + err.strip()
            report.recommended_action = f"Update the dependency versions in {inspection.dependency_file}."
            report.cleanup_status = "No running container remains."
            return report
            
        report.build_status = "SUCCESS"
        
        # 4. Deploy
        try:
            container_id, mapped_port = self.tools["runner"].execute(image_name, inspection.port)
            report.deployment_status = "SUCCESS"
        except Exception as e:
            report.deployment_status = "FAILED"
            report.failure_stage = "Docker run"
            report.failure_cause = str(e)
            report.recommended_action = "Check Docker daemon and port availability."
            return report
            
        # 5. Verify
        health_ok, api_ok = self.tools["verifier"].execute(mapped_port, inspection.health_endpoint)
        report.health_status = "HEALTHY" if health_ok else "FAILED"
        report.functional_status = "PASSED" if api_ok else "FAILED"
        
        # 6. Clean up
        self.tools["cleaner"].execute(container_id)
        report.cleanup_status = "COMPLETE"
        
        if not health_ok or not api_ok:
            report.failure_stage = "Verification"
            report.failure_cause = "Application started but endpoints are not responding correctly."
            report.recommended_action = "Check application logs and health endpoint logic."
            
        return report
