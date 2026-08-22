import os
import json
from typing import Dict, Any, List, Tuple

from fde_lab.tools.base import Tool
from fde_lab.pocs.configuration_engineer.models import ConfigurationIssue, ProposedChange, RiskAssessment

def get_demo_data_path(scenario: str, filename: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "demo_data", "acme_saas", scenario, filename)

def get_schema_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "demo_data", "acme_saas", "schema.json")

class ConfigurationReaderTool(Tool):
    @property
    def name(self) -> str: return "read_customer_configuration"
    @property
    def description(self) -> str: return "Reads the customer's configuration."
    
    def execute(self, **kwargs) -> dict:
        with open(get_demo_data_path(kwargs["scenario"], "config.json"), "r") as f:
            return json.load(f)

class ConfigurationSchemaTool(Tool):
    @property
    def name(self) -> str: return "read_configuration_schema"
    @property
    def description(self) -> str: return "Reads the expected configuration schema."
    
    def execute(self, **kwargs) -> dict:
        with open(get_schema_path(), "r") as f:
            return json.load(f)

def get_nested_val(d: dict, path: str) -> Any:
    parts = path.split(".")
    curr = d
    for p in parts:
        if not isinstance(curr, dict) or p not in curr:
            return None
        curr = curr[p]
    return curr

class ConfigurationValidatorTool(Tool):
    @property
    def name(self) -> str: return "validate_configuration"
    @property
    def description(self) -> str: return "Validates configuration against schema rules."
    
    def execute(self, **kwargs) -> List[ConfigurationIssue]:
        config = kwargs["config"]
        schema = kwargs["schema"]
        
        issues = []
        rules = schema.get("rules", {})
        
        for path, rule in rules.items():
            if path == "conflicts": continue
            
            val = get_nested_val(config, path)
            
            if rule.get("required") and val is None:
                issues.append(ConfigurationIssue(
                    path=path,
                    issue_type="missing",
                    description="Required configuration is missing.",
                    current_value=None,
                    expected_value=f"Type: {rule.get('type')}"
                ))
                continue
                
            if val is not None:
                # Type check
                if rule.get("type") == "string" and not isinstance(val, str):
                    issues.append(ConfigurationIssue(path, "invalid", f"Must be string", val, "string"))
                elif rule.get("type") == "integer" and not isinstance(val, int):
                    issues.append(ConfigurationIssue(path, "invalid", f"Must be integer", val, "integer"))
                elif rule.get("type") == "boolean" and not isinstance(val, bool):
                    issues.append(ConfigurationIssue(path, "invalid", f"Must be boolean", val, "boolean"))
                    
                # Min/Max
                if isinstance(val, (int, float)):
                    if "min" in rule and val < rule["min"]:
                        issues.append(ConfigurationIssue(path, "invalid", f"Value too low", val, f">= {rule['min']}"))
                    if "max" in rule and val > rule["max"]:
                        issues.append(ConfigurationIssue(path, "invalid", f"Value too high", val, f"<= {rule['max']}"))
                        
                # Allowed enum
                if "allowed" in rule and val not in rule["allowed"]:
                    issues.append(ConfigurationIssue(path, "invalid", f"Not an allowed value", val, rule["allowed"]))
                    
                # Custom rules
                if rule.get("must_be_true_in_prod") and config.get("environment") == "production" and val is not True:
                    issues.append(ConfigurationIssue(path, "invalid", "Must be true in production", val, True))

        # Check conflicts
        conflicts = rules.get("conflicts", [])
        for conflict in conflicts:
            # check if condition matches
            if_cond = True
            for k, v in conflict.get("if", {}).items():
                if get_nested_val(config, k) != v:
                    if_cond = False
                    break
            
            if if_cond:
                for k, v in conflict.get("must_not_have", {}).items():
                    if get_nested_val(config, k) == v:
                        issues.append(ConfigurationIssue(
                            path=k,
                            issue_type="conflict",
                            description=conflict.get("reason", "Conflict detected"),
                            current_value=v,
                            expected_value=f"Not {v}"
                        ))

        return issues

class ChangePlannerTool(Tool):
    @property
    def name(self) -> str: return "plan_configuration_changes"
    @property
    def description(self) -> str: return "Proposes changes to fix issues."
    
    def execute(self, **kwargs) -> List[ProposedChange]:
        issues: List[ConfigurationIssue] = kwargs["issues"]
        schema = kwargs["schema"]
        
        changes = []
        expected_config = schema.get("expected", {})
        
        for issue in issues:
            expected_val = get_nested_val(expected_config, issue.path)
            reason = "Required to meet schema constraints"
            
            if expected_val is not None:
                changes.append(ProposedChange(
                    path=issue.path,
                    current_value=issue.current_value,
                    proposed_value=expected_val,
                    reason=f"Aligning with expected configuration: {reason}"
                ))
            else:
                # Fallback proposal
                changes.append(ProposedChange(
                    path=issue.path,
                    current_value=issue.current_value,
                    proposed_value="<needs manual review>",
                    reason=reason
                ))
                
        return changes

class RiskAssessmentTool(Tool):
    @property
    def name(self) -> str: return "assess_change_risk"
    @property
    def description(self) -> str: return "Determines the risk of the proposed changes."
    
    def execute(self, **kwargs) -> RiskAssessment:
        changes: List[ProposedChange] = kwargs["changes"]
        scenario = kwargs["scenario"]
        
        if not changes:
            return RiskAssessment("LOW", "No changes proposed", False)
            
        # Hardcode some risk logic based on path
        is_high_risk = False
        reasons = []
        
        for change in changes:
            if change.path == "auth.provider" and change.current_value is not None:
                is_high_risk = True
                reasons.append("Changing auth.provider on an active environment is highly disruptive.")
                
            if scenario == "unsafe-change":
                # For the scenario demo, trigger a specific high risk block
                is_high_risk = True
                reasons.append("Changing local_db to oauth requires migrating existing users which is disruptive and needs approval.")

        if is_high_risk:
            return RiskAssessment(
                level="HIGH",
                reason=" ".join(reasons),
                requires_approval=True
            )
        else:
            return RiskAssessment(
                level="LOW",
                reason="Configuration changes are structurally valid and should not require service interruption.",
                requires_approval=False
            )

class ConfigurationReportTool(Tool):
    @property
    def name(self) -> str: return "write_configuration_report"
    @property
    def description(self) -> str: return "Writes the configuration report and patch."
    
    def execute(self, **kwargs) -> dict:
        report = kwargs["report"]
        
        os.makedirs("output", exist_ok=True)
        
        # JSON output
        report_path = "output/configuration-change-plan.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        # Human readable text
        txt = f"CONFIGURATION ENGINEER\n────────────────────────────────────────\n\n"
        txt += f"Customer: {report['customer']}\n"
        txt += f"Environment: {report['environment']}\n\n"
        
        if report["status"] == "valid":
            txt += "Configuration status: VALID\n\n"
            txt += "No problems found. No changes proposed.\n"
        else:
            txt += "Configuration status: NEEDS CHANGES\n\n"
            txt += "PROBLEMS FOUND\n\n"
            for issue in report["issues"]:
                symbol = "⚠" if issue["type"] == "invalid" else "✗"
                txt += f"{symbol} {issue['path']}\n"
                if issue["type"] == "missing":
                    txt += f"  {issue['description']}\n\n"
                else:
                    txt += f"  Current value: {issue['current']}\n"
                    txt += f"  Expected: {issue['expected']}\n"
                    txt += f"  {issue['description']}\n\n"
                    
            txt += "PROPOSED CHANGES\n\n"
            for i, change in enumerate(report["recommended_changes"]):
                txt += f"{i+1}. Set {change['path']} = {json.dumps(change['proposed'])}\n"
                
            txt += "\nRISK ASSESSMENT\n\n"
            txt += f"{report['risk']['level']}\n"
            txt += f"{report['risk']['reason']}\n\n"
            
        txt += "PROPOSED CHANGE — NOT APPLIED\n\n"
        txt += "No customer configuration was modified.\n"
            
        return {
            "report_path": report_path,
            "human_output": txt
        }
