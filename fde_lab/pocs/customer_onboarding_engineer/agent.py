import logging
from fde_lab.pocs.customer_onboarding_engineer.models import (
    CustomerRequirements, ProductCapabilities, ValidationResult, MappingResult, NormalizedConfig, OnboardingReport
)
from fde_lab.pocs.customer_onboarding_engineer.tools import (
    CustomerConfigInspectorTool, ProductCapabilityTool, ConfigurationValidatorTool, RequirementMapperTool,
    OnboardingConfigGeneratorTool, OnboardingReportTool
)

logger = logging.getLogger(__name__)

class CustomerOnboardingEngineerAgent:
    def __init__(self):
        self.inspector = CustomerConfigInspectorTool()
        self.capability_tool = ProductCapabilityTool()
        self.validator = ConfigurationValidatorTool()
        self.mapper = RequirementMapperTool()
        self.generator = OnboardingConfigGeneratorTool()
        self.reporter = OnboardingReportTool()
        
    def run(self, scenario: str) -> OnboardingReport:
        logger.info(f"Starting Customer Onboarding Engineer for scenario: {scenario}")
        
        # 1. Inspect
        logger.info("Discovering customer requirements...")
        raw_config = self.inspector.execute(scenario=scenario)
        reqs = CustomerRequirements(**raw_config)
        
        # 2. Capabilities
        logger.info("Discovering product capabilities...")
        raw_caps = self.capability_tool.execute()
        caps = ProductCapabilities(**raw_caps)
        
        # 3. Validate
        logger.info("Validating configuration...")
        raw_val = self.validator.execute(customer_config=raw_config, capabilities=raw_caps)
        val = ValidationResult(**raw_val)
        
        # 4. Map
        logger.info("Mapping requirements...")
        raw_map = self.mapper.execute(customer_config=raw_config, capabilities=raw_caps)
        map_res = MappingResult(**raw_map)
        
        # 5. Generate
        logger.info("Generating onboarding package...")
        gen_res = self.generator.execute(customer_config=raw_config, mapping=raw_map)
        
        # 6. Report
        logger.info("Verifying and generating report...")
        rep_res = self.reporter.execute(customer_config=raw_config, mapping=raw_map, validation=raw_val)
        
        return OnboardingReport(
            customer_name=reqs.customer.get("name", "Unknown"),
            requirements=reqs,
            validation=val,
            mapping=map_res,
            config=NormalizedConfig(**gen_res["normalized_config"]),
            config_path=gen_res["config_path"],
            checklist_path=gen_res["checklist_path"],
            report_path=rep_res["report_path"]
        )
