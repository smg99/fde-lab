import logging

from fde_lab.pocs.configuration_engineer.models import ConfigurationReport
from fde_lab.pocs.configuration_engineer.tools import (
    ConfigurationReaderTool, ConfigurationSchemaTool, ConfigurationValidatorTool,
    ChangePlannerTool, RiskAssessmentTool, ConfigurationReportTool
)

logger = logging.getLogger("fde_lab.pocs.configuration_engineer.agent")

class ConfigurationEngineerAgent:
    def __init__(self):
        self.reader_tool = ConfigurationReaderTool()
        self.schema_tool = ConfigurationSchemaTool()
        self.validator_tool = ConfigurationValidatorTool()
        self.planner_tool = ChangePlannerTool()
        self.risk_tool = RiskAssessmentTool()
        self.report_tool = ConfigurationReportTool()
        
    def run(self, scenario: str) -> ConfigurationReport:
        logger.info(f"Starting Configuration Engineer for scenario: {scenario}")
        
        config = self.reader_tool.execute(scenario=scenario)
        schema = self.schema_tool.execute()
        
        issues = self.validator_tool.execute(config=config, schema=schema)
        
        if not issues:
            report = ConfigurationReport(
                status="valid",
                scenario=scenario,
                customer="Acme SaaS",
                environment=config.get("environment", "unknown"),
                observations=["Configuration matches schema exactly."],
                issues=[],
                recommended_changes=[],
                risk=self.risk_tool.execute(changes=[], scenario=scenario),
                action_required=False,
                changes_applied=False
            )
        else:
            changes = self.planner_tool.execute(issues=issues, schema=schema)
            risk = self.risk_tool.execute(changes=changes, scenario=scenario)
            
            report = ConfigurationReport(
                status="needs_changes",
                scenario=scenario,
                customer="Acme SaaS",
                environment=config.get("environment", "unknown"),
                observations=[f"Found {len(issues)} issues in configuration."],
                issues=issues,
                recommended_changes=changes,
                risk=risk,
                action_required=risk.requires_approval,
                changes_applied=False
            )
            
        paths = self.report_tool.execute(report=report.to_dict())
        report.report_path = paths["report_path"]
        report.human_output = paths["human_output"]
        
        return report
