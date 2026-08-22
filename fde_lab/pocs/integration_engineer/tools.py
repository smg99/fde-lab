import os
import json
from typing import List, Dict, Any
from .models import FieldSchema, Mapping, MappingRule, ValidationResult
from fde_lab.tools.base import Tool

class SourceSchemaTool(Tool):
    @property
    def name(self) -> str: return "SourceSchemaTool"
    @property
    def description(self) -> str: return "Returns the source CRM schema"
    def execute(self) -> List[Dict[str, Any]]:
        return [
            {"name": "customer_id", "type": "string", "required": True},
            {"name": "first_name", "type": "string", "required": True},
            {"name": "last_name", "type": "string", "required": True},
            {"name": "email", "type": "string", "required": True},
            {"name": "company", "type": "string", "required": False},
            {"name": "country", "type": "string", "required": True},
            {"name": "plan", "type": "string", "required": True},
            {"name": "marketing_opt_in", "type": "boolean", "required": False}
        ]

class TargetSchemaTool(Tool):
    @property
    def name(self) -> str: return "TargetSchemaTool"
    @property
    def description(self) -> str: return "Returns the target billing schema"
    def execute(self) -> List[Dict[str, Any]]:
        return [
            {"name": "external_customer_id", "type": "string", "required": True},
            {"name": "name", "type": "string", "required": True},
            {"name": "email_address", "type": "string", "required": True},
            {"name": "organization", "type": "string", "required": False},
            {"name": "country_code", "type": "string", "required": True},
            {"name": "subscription_tier", "type": "string", "required": True}
        ]

class RecordReaderTool(Tool):
    @property
    def name(self) -> str: return "RecordReaderTool"
    @property
    def description(self) -> str: return "Reads the source records"
    def __init__(self, scenario: str = "normal"):
        self.scenario = scenario

    def execute(self) -> List[Dict[str, str]]:
        if self.scenario == "invalid-data":
            return [
                {"customer_id": "C001", "first_name": "John", "last_name": "Smith", "email": "john@example.com", "company": "Acme Inc", "country": "US", "plan": "PRO", "marketing_opt_in": "true"},
                {"customer_id": "C003", "first_name": "", "last_name": "", "email": "", "company": "Acme Ltd", "country": "US", "plan": "PRO", "marketing_opt_in": "false"},
                {"customer_id": "C004", "first_name": "Alice", "last_name": "Walker", "email": "alice@example.com", "company": "Acme Ltd", "country": "XX", "plan": "PRO", "marketing_opt_in": "true"},
                {"customer_id": "C005", "first_name": "Bob", "last_name": "Stone", "email": "bob@example.com", "company": "Acme Ltd", "country": "US", "plan": "UNKNOWN", "marketing_opt_in": "false"}
            ]
        # normal scenario
        return [
            {"customer_id": "C001", "first_name": "John", "last_name": "Smith", "email": "john@example.com", "company": "Acme Inc", "country": "US", "plan": "PRO", "marketing_opt_in": "true"},
            {"customer_id": "C002", "first_name": "Sarah", "last_name": "Lee", "email": "sarah@example.com", "company": "Acme Inc", "country": "US", "plan": "BASIC", "marketing_opt_in": "false"}
        ]

class ValidationTool(Tool):
    @property
    def name(self) -> str: return "ValidationTool"
    @property
    def description(self) -> str: return "Validates a record against requirements"
    def execute(self, record: Dict[str, str]) -> ValidationResult:
        errors = []
        if not record.get("email"):
            errors.append("Missing email address")
        if record.get("country") not in ["US", "UK", "CA"]:
            errors.append(f"Unsupported country code: {record.get('country')}")
        if record.get("plan") not in ["BASIC", "PRO", "ENTERPRISE"]:
            errors.append(f"Unsupported subscription tier: {record.get('plan')}")
            
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

class TransformationTool(Tool):
    @property
    def name(self) -> str: return "TransformationTool"
    @property
    def description(self) -> str: return "Transforms a record using a mapping"
    def execute(self, record: Dict[str, str], mapping: Mapping) -> Dict[str, Any]:
        result = {}
        for rule in mapping.rules:
            if rule.transformation_type == "direct":
                result[rule.target_field] = record.get(rule.source_fields[0], "")
            elif rule.transformation_type == "concat":
                values = [record.get(f, "") for f in rule.source_fields]
                result[rule.target_field] = " ".join([v for v in values if v]).strip()
        return result

class OutputWriterTool(Tool):
    @property
    def name(self) -> str: return "OutputWriterTool"
    @property
    def description(self) -> str: return "Writes the output array to a JSON file"
    def execute(self, records: List[Dict[str, Any]], filename: str = "billing-customers.json") -> str:
        # Create output relative to CWD so the user sees it where they ran it
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w") as f:
            json.dump(records, f, indent=2)
        return file_path
