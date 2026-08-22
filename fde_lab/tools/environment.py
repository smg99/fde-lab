from fde_lab.tools.base import Tool

class GetServicesTool(Tool):
    """Tool to inspect the local environment services."""
    
    @property
    def name(self) -> str:
        return "get_services"
        
    @property
    def description(self) -> str:
        return "Returns a list of currently running services in the environment."
        
    def execute(self, **kwargs):
        # In a real scenario, this would query Docker, systemctl, etc.
        # For the demo vertical slice, we return mock data.
        return {
            "status": "success",
            "services": [
                {"name": "postgres", "status": "running", "port": 5432},
                {"name": "api-gateway", "status": "running", "port": 8000},
                {"name": "redis", "status": "stopped", "port": 6379}
            ]
        }
