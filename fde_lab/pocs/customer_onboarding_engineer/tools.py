import json
import csv
import os
from fde_lab.tools.base import Tool
from fde_lab.pocs.customer_onboarding_engineer.models import (
    CustomerRequirements, ProductCapabilities, UserRecord, ValidationResult, MappingResult, NormalizedConfig, OnboardingReport
)

class CustomerConfigInspectorTool(Tool):
    @property
    def name(self) -> str: return "inspect_customer_config"
    @property
    def description(self) -> str: return "Reads the customer onboarding JSON and users CSV."
    
    def get_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario": {"type": "string"}
                },
                "required": ["scenario"]
            }
        }
        
    def execute(self, **kwargs) -> dict:
        scenario = kwargs.get("scenario")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(current_dir, "demo_data", "acme_health", scenario)
        
        with open(os.path.join(base_path, "onboarding.json"), "r") as f:
            config = json.load(f)
            
        users = []
        with open(os.path.join(base_path, "users.csv"), "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(row)
                
        config["users"] = users
        return config

class ProductCapabilityTool(Tool):
    @property
    def name(self) -> str: return "get_product_capabilities"
    @property
    def description(self) -> str: return "Returns the supported roles, features, and integrations."
    
    def get_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": {}}
        }
        
    def execute(self, **kwargs) -> dict:
        return {
            "roles": ["admin", "manager", "viewer"],
            "features": ["analytics", "exports", "notifications"],
            "integrations": ["slack", "webhook"]
        }

class ConfigurationValidatorTool(Tool):
    @property
    def name(self) -> str: return "validate_configuration"
    @property
    def description(self) -> str: return "Validates users and basic structural constraints."
    
    def get_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_config": {"type": "object"},
                    "capabilities": {"type": "object"}
                },
                "required": ["customer_config", "capabilities"]
            }
        }
        
    def execute(self, **kwargs) -> dict:
        config = kwargs.get("customer_config")
        capabilities = kwargs.get("capabilities")
        
        errors = []
        
        # Validate users
        seen_emails = set()
        for user in config.get("users", []):
            if "email" not in user or not user["email"]:
                errors.append("User missing email.")
                continue
            if user["email"] in seen_emails:
                errors.append(f"Duplicate user email: {user['email']}")
            seen_emails.add(user["email"])
            
            if user.get("role") not in capabilities["roles"]:
                errors.append(f"Invalid role '{user.get('role')}' for user {user['email']}")
                
        # Structural validation
        if "customer" not in config or "name" not in config["customer"]:
            errors.append("Missing customer name.")
            
        return {"valid": len(errors) == 0, "errors": errors}

class RequirementMapperTool(Tool):
    @property
    def name(self) -> str: return "map_requirements"
    @property
    def description(self) -> str: return "Checks customer config against capabilities."
    
    def get_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_config": {"type": "object"},
                    "capabilities": {"type": "object"}
                },
                "required": ["customer_config", "capabilities"]
            }
        }
        
    def execute(self, **kwargs) -> dict:
        config = kwargs.get("customer_config")
        caps = kwargs.get("capabilities")
        
        missing = []
        unsupported = []
        satisfied = 0
        total = 0
        
        # Check features
        for req_feat, enabled in config.get("features", {}).items():
            if enabled:
                total += 1
                if req_feat in caps["features"]:
                    satisfied += 1
                else:
                    unsupported.append(f"Feature: {req_feat}")
                    
        # Check missing core features (e.g., analytics is required)
        if "analytics" not in config.get("features", {}) or not config["features"]["analytics"]:
            missing.append("Analytics feature configuration")
            
        # Check integrations
        for req_int, details in config.get("integrations", {}).items():
            if details.get("enabled"):
                total += 1
                if req_int in caps["integrations"]:
                    # Check if config is complete
                    if req_int == "slack" and "webhook_url" not in details:
                        missing.append("Slack integration credentials/configuration")
                    else:
                        satisfied += 1
                else:
                    unsupported.append(f"Integration: {req_int}")
                    
        status = "READY"
        if len(unsupported) > 0:
            status = "BLOCKED"
        elif len(missing) > 0:
            status = "INCOMPLETE"
            
        return {
            "missing": missing,
            "unsupported": unsupported,
            "satisfied_count": satisfied,
            "total_count": total,
            "status": status
        }

class OnboardingConfigGeneratorTool(Tool):
    @property
    def name(self) -> str: return "generate_onboarding_package"
    @property
    def description(self) -> str: return "Generates normalized configuration, checklist, and report."
    
    def get_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_config": {"type": "object"},
                    "mapping": {"type": "object"}
                },
                "required": ["customer_config", "mapping"]
            }
        }
        
    def execute(self, **kwargs) -> dict:
        config = kwargs.get("customer_config")
        mapping = kwargs.get("mapping")
        
        os.makedirs("output", exist_ok=True)
        
        # 1. Config
        norm = {
            "customer": config.get("customer", {}),
            "users": config.get("users", []),
            "features": config.get("features", {}),
            "integrations": config.get("integrations", {})
        }
        
        with open("output/onboarding-config.json", "w") as f:
            json.dump(norm, f, indent=2)
            
        # 2. Checklist
        status = mapping["status"]
        lines = [f"# {config.get('customer', {}).get('name', 'Customer')} — Onboarding Checklist\n\n## Completed"]
        lines.append("- [x] Organization configuration")
        lines.append("- [x] User configuration")
        for f in config.get("features", {}):
            lines.append(f"- [x] {f.title()}")
            
        if len(mapping["missing"]) > 0:
            lines.append("\n## Remaining")
            for m in mapping["missing"]:
                lines.append(f"- [ ] Configure {m}")
                
        lines.append(f"\n## Status\n\n{status}")
        
        with open("output/onboarding-checklist.md", "w") as f:
            f.write("\n".join(lines))
            
        return {
            "config_path": "output/onboarding-config.json",
            "checklist_path": "output/onboarding-checklist.md",
            "normalized_config": norm
        }

class OnboardingReportTool(Tool):
    @property
    def name(self) -> str: return "generate_report"
    @property
    def description(self) -> str: return "Generates the onboarding report."
    
    def get_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_config": {"type": "object"},
                    "mapping": {"type": "object"},
                    "validation": {"type": "object"}
                },
                "required": ["customer_config", "mapping", "validation"]
            }
        }
        
    def execute(self, **kwargs) -> dict:
        c = kwargs.get("customer_config")
        m = kwargs.get("mapping")
        v = kwargs.get("validation")
        
        lines = [
            f"Customer:\n{c.get('customer', {}).get('name')}\n",
            f"Overall status:\n{m['status']}\n",
            f"Requirements:\n{m['satisfied_count']}/{m['total_count']} satisfied\n"
        ]
        
        if not v['valid']:
            lines.append(f"Validation Errors:\n- " + "\n- ".join(v['errors']) + "\n")
            
        if len(m['missing']) > 0:
            lines.append(f"Missing:\n- " + "\n- ".join(m['missing']) + "\n")
            
        if len(m['unsupported']) > 0:
            lines.append(f"Unsupported:\n- " + "\n- ".join(m['unsupported']) + "\n")
            
        if m['status'] == "READY":
            lines.append("Recommended next steps:\nImport the configuration package.")
        elif m['status'] == "INCOMPLETE":
            lines.append("Recommended next steps:\nResolve missing configurations.")
        elif m['status'] == "BLOCKED":
            lines.append("Recommended next steps:\nConfirm alternative integrations or escalate to product review.")
            
        with open("output/onboarding-report.md", "w") as f:
            f.write("\n".join(lines))
            
        return {"report_path": "output/onboarding-report.md"}
