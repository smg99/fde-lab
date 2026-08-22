import json
from fde_lab.pocs.integration_engineer.models import IntegrationReport, Mapping, MappingRule
from fde_lab.pocs.integration_engineer.tools import (
    SourceSchemaTool, TargetSchemaTool, RecordReaderTool, ValidationTool, TransformationTool, OutputWriterTool
)
from fde_lab.observability.logger import get_logger

logger = get_logger("fde_lab.integration_engineer")

class IntegrationEngineerAgent:
    def __init__(self, scenario: str = "normal"):
        self.scenario = scenario
        self.tools = {
            "source_schema": SourceSchemaTool(),
            "target_schema": TargetSchemaTool(),
            "reader": RecordReaderTool(scenario),
            "validator": ValidationTool(),
            "transformer": TransformationTool(),
            "writer": OutputWriterTool()
        }

    def execute_integration(self) -> IntegrationReport:
        logger.info(f"Starting integration run for scenario: {self.scenario}")
        
        # 1. Inspect Source Schema
        source_schema = self.tools["source_schema"].execute()
        source_fields = [f["name"] for f in source_schema]
        
        # 2. Inspect Target Schema
        target_schema = self.tools["target_schema"].execute()
        target_fields = [f["name"] for f in target_schema]
        
        # 3. Build Mapping (simulated agent intelligence determining rules)
        mapping = Mapping(
            rules=[
                MappingRule(["customer_id"], "external_customer_id", "direct"),
                MappingRule(["first_name", "last_name"], "name", "concat"),
                MappingRule(["email"], "email_address", "direct"),
                MappingRule(["company"], "organization", "direct"),
                MappingRule(["country"], "country_code", "direct"),
                MappingRule(["plan"], "subscription_tier", "direct"),
            ],
            unmapped_source_fields=["marketing_opt_in"]
        )

        # 4. Read Records
        records = self.tools["reader"].execute()
        
        valid_records = []
        rejected_records = {}
        
        # 5. Validate & 6. Transform
        for rec in records:
            cid = rec.get("customer_id", "UNKNOWN")
            validation = self.tools["validator"].execute(rec)
            if validation.is_valid:
                transformed = self.tools["transformer"].execute(rec, mapping)
                valid_records.append(transformed)
            else:
                rejected_records[cid] = ", ".join(validation.errors)
        
        # 7. Produce Result
        output_path = self.tools["writer"].execute(valid_records)
        
        # 8. Explain
        explanation = (
            "The CRM and billing systems use different field names.\n\n"
            "I mapped the customer identifier, combined first and last\n"
            "names into the billing name field, and mapped the remaining\n"
            "compatible fields.\n\n"
        )
        if rejected_records:
            explanation += f"{len(rejected_records)} record(s) were rejected due to data quality issues (e.g., missing email, unsupported countries).\n\n"
        
        explanation += "No data was sent externally. Integration prepared successfully."

        return IntegrationReport(
            records_received=len(records),
            records_transformed=len(valid_records),
            records_rejected=len(rejected_records),
            mapping=mapping,
            rejected_records=rejected_records,
            output_path=output_path,
            explanation=explanation
        )
