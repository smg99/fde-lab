import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List

from fde_lab.tools.base import Tool
from fde_lab.pocs.data_migration_engineer.models import MigrationRecord, RecordStatus, ValidationResult

def get_demo_data_path(scenario: str, filename: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "demo_data", "acme_saas", scenario, filename)

class SchemaInspectorTool(Tool):
    @property
    def name(self) -> str: return "inspect_schema"
    @property
    def description(self) -> str: return "Reads the target database schema constraints."
    
    def execute(self, **kwargs) -> dict:
        with open(get_demo_data_path(kwargs["scenario"], "target_schema.json"), "r") as f:
            return json.load(f)

class SourceRecordReaderTool(Tool):
    @property
    def name(self) -> str: return "read_source_records"
    @property
    def description(self) -> str: return "Reads records from the legacy CRM system."
    
    def execute(self, **kwargs) -> list:
        with open(get_demo_data_path(kwargs["scenario"], "source_data.json"), "r") as f:
            return json.load(f)

class RecordTransformerTool(Tool):
    @property
    def name(self) -> str: return "transform_record"
    @property
    def description(self) -> str: return "Maps source legacy fields to the new target schema fields."
    
    def execute(self, **kwargs) -> dict:
        record = kwargs["record"]
        schema = kwargs["schema"]
        
        target = {}
        transformations = []
        
        # Mapping logic
        if "legacy_id" in record:
            target["customer_id"] = record["legacy_id"]
            
        if "first_name" in record or "last_name" in record:
            first = record.get("first_name", "").strip()
            last = record.get("last_name", "").strip()
            target["full_name"] = f"{first} {last}".strip()
            
        if "email" in record:
            target["email_address"] = record["email"].strip().lower()
            if target["email_address"] != record["email"]:
                transformations.append(f"Normalized email to lowercase: {target['email_address']}")
                
        if "phone" in record:
            target["phone_number"] = record["phone"]
            
        if "company" in record:
            target["organization_name"] = record["company"]
            
        if "country" in record:
            country = record["country"].strip().upper()
            target["country_code"] = country
            if country != record["country"]:
                transformations.append(f"Normalized country code to uppercase: {country}")
                
        if "status" in record:
            status = record["status"].upper()
            if status == "ACTIVE":
                target["account_status"] = "ACTIVE"
            elif status == "CANCELLED" or status == "INACTIVE":
                target["account_status"] = "CANCELLED"
            else:
                target["account_status"] = "SUSPENDED"
                
        if "plan" in record:
            plan = record["plan"].upper()
            if plan in ["BASIC", "PRO", "ENTERPRISE"]:
                target["subscription_tier"] = plan
            else:
                target["subscription_tier"] = plan # Let validator catch it
                
        if "marketing_opt_in" in record:
            opt = str(record["marketing_opt_in"]).lower()
            target["marketing_consent"] = (opt == "yes" or opt == "true")
            
        if "created_at" in record:
            # Try to parse mm/dd/yyyy and convert to ISO
            date_str = record["created_at"]
            try:
                dt = datetime.strptime(date_str, "%m/%d/%Y")
                target["registered_at"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                transformations.append(f"Converted date {date_str} to ISO8601")
            except ValueError:
                target["registered_at"] = date_str # Let validator catch it
                
        # Address concatenation
        parts = []
        if "address_line_1" in record: parts.append(record["address_line_1"])
        if "address_line_2" in record: parts.append(record["address_line_2"])
        if "city" in record: parts.append(record["city"])
        if "state" in record: parts.append(record["state"])
        if "postal_code" in record: parts.append(record["postal_code"])
        
        address = ", ".join([p for p in parts if p.strip()])
        if address:
            target["address"] = address
            
        return {
            "target": target,
            "transformations": transformations
        }

class FieldValidatorTool(Tool):
    @property
    def name(self) -> str: return "validate_record"
    @property
    def description(self) -> str: return "Validates a mapped record against target schema constraints."
    
    def execute(self, **kwargs) -> dict:
        target = kwargs["target_record"]
        schema = kwargs["schema"]
        
        errors = []
        warnings = []
        
        for field in schema.get("fields", []):
            name = field["name"]
            is_req = field.get("required", False)
            val = target.get(name)
            
            if is_req and (val is None or val == ""):
                errors.append(f"Missing required field: {name}")
                continue
                
            if val is not None and val != "":
                # Type validation (simplified)
                if field.get("type") == "enum":
                    allowed = field.get("values", [])
                    if val not in allowed:
                        errors.append(f"Invalid enum value '{val}' for field {name}. Allowed: {allowed}")
                        
                if field.get("format") == "email":
                    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", val):
                        errors.append(f"Invalid email format: {val}")
                        
                if field.get("format") == "date-iso8601":
                    try:
                        datetime.strptime(val, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        errors.append(f"Invalid date format for {name}, expected ISO8601: {val}")
                        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

class DuplicateDetectorTool(Tool):
    @property
    def name(self) -> str: return "detect_duplicates"
    @property
    def description(self) -> str: return "Checks for legacy ID and email uniqueness across the batch."
    
    def execute(self, **kwargs) -> dict:
        records = kwargs["records"]
        
        seen_ids = set()
        seen_emails = set()
        
        duplicates = {} # legacy_id -> list of reasons
        
        for rec in records:
            lid = rec.get("legacy_id")
            email = rec.get("email", "").lower()
            
            issues = []
            if lid in seen_ids:
                issues.append(f"Duplicate legacy_id: {lid}")
            else:
                seen_ids.add(lid)
                
            if email and email in seen_emails:
                issues.append(f"Duplicate email: {email}")
            elif email:
                seen_emails.add(email)
                
            if issues:
                duplicates[lid] = issues
                
        return duplicates

class MigrationWriterTool(Tool):
    @property
    def name(self) -> str: return "write_migration_output"
    @property
    def description(self) -> str: return "Writes the migrated and quarantined output to disk."
    
    def execute(self, **kwargs) -> dict:
        migrated = kwargs["migrated"]
        quarantined = kwargs["quarantined"]
        report = kwargs["report"]
        is_dry_run = kwargs.get("is_dry_run", False)
        
        os.makedirs("output", exist_ok=True)
        
        if not is_dry_run:
            with open("output/migrated-customers.json", "w") as f:
                json.dump(migrated, f, indent=2)
                
            with open("output/quarantine.json", "w") as f:
                json.dump(quarantined, f, indent=2)
                
            with open("output/migration-report.json", "w") as f:
                json.dump(report, f, indent=2)
        
        # Build human readable text
        output_txt = f"Migration Analysis\n------------------\n\n"
        output_txt += f"Source:\nLegacy CRM\n\nTarget:\nNew Customer Platform\n\n"
        output_txt += f"Records inspected: {report.get('records_inspected')}\n"
        output_txt += f"Successfully migrated: {report.get('migrated_records')}\n"
        output_txt += f"Rejected: {report.get('rejected_records')}\n"
        output_txt += f"Quarantined: {report.get('quarantined_records')}\n\n"
        
        output_txt += f"Key findings:\n"
        
        # Deduplicate transformations/warnings for summary
        unique_t = list(set(report.get("transformations", [])))
        unique_w = list(set(report.get("warnings", [])))
        unique_c = list(set(report.get("schema_conflicts", [])))
        
        for t in unique_t[:3]:
            output_txt += f"✓ {t}\n"
            
        for w in unique_w[:3]:
            output_txt += f"⚠ {w}\n"
            
        for c in unique_c[:5]:
            output_txt += f"✗ {c}\n"
            
        output_txt += "\n"
        if is_dry_run:
            output_txt += "Output:\n(Dry run - no files written)\n"
        else:
            output_txt += "Output:\n./output/migrated-customers.json\n\nQuarantine:\n./output/quarantine.json\n"
            
        return {
            "migrated_path": "output/migrated-customers.json" if not is_dry_run else None,
            "quarantine_path": "output/quarantine.json" if not is_dry_run else None,
            "report_path": "output/migration-report.json" if not is_dry_run else None,
            "human_output": output_txt
        }
