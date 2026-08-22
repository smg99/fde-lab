import logging
from typing import Dict, Any

from fde_lab.pocs.support_escalation_engineer.models import (
    EscalationReport, Issue, IssueClassification, Severity, 
    Reproducibility, ReproductionResult, Evidence
)
from fde_lab.pocs.support_escalation_engineer.tools import (
    CustomerReportTool, EnvironmentInspectorTool, LogSearchTool,
    RequestSampleTool, RecentChangesTool, ReproductionTool,
    EscalationGeneratorTool
)

logger = logging.getLogger("fde_lab.pocs.support_escalation_engineer.agent")

class SupportEscalationEngineerAgent:
    def __init__(self):
        self.report_tool = CustomerReportTool()
        self.env_tool = EnvironmentInspectorTool()
        self.log_tool = LogSearchTool()
        self.req_tool = RequestSampleTool()
        self.changes_tool = RecentChangesTool()
        self.repro_tool = ReproductionTool()
        self.esc_tool = EscalationGeneratorTool()
        
    def run(self, scenario: str) -> EscalationReport:
        logger.info(f"Starting Support Escalation Engineer for scenario: {scenario}")
        
        report_data = self.report_tool.execute(scenario=scenario)
        env_data = self.env_tool.execute(scenario=scenario)
        logs = self.log_tool.execute(scenario=scenario)
        reqs = self.req_tool.execute(scenario=scenario)
        changes = self.changes_tool.execute(scenario=scenario)
        
        evidence = []
        facts = []
        observations = []
        hypotheses = []
        
        # Analyze report
        facts.append(f"Customer reported issue: {report_data.get('issue')}")
        evidence.append(Evidence("Customer Report", "Issue reported by customer", "Direct context", "HIGH"))
        
        # Analyze logs
        has_error = False
        error_msg = ""
        for log in logs:
            if log.get("level") == "ERROR":
                has_error = True
                error_msg = log.get("message", "")
                facts.append(f"Application error found: {error_msg}")
                evidence.append(Evidence("Application Logs", error_msg, "Identifies failure point", "HIGH"))
                break
                
        # Analyze requests
        has_requests = len(reqs) > 0
        if has_requests:
            observations.append(f"Found {len(reqs)} sample requests correlating with the issue.")
            evidence.append(Evidence("Request Samples", f"Found request {reqs[0].get('request_id')}", "Identifies inputs", "HIGH"))
            
        # Analyze changes
        if len(changes) > 0:
            change = changes[0]
            hypotheses.append(f"Recent change '{change.get('title')}' might be related to the issue.")
            evidence.append(Evidence("Recent Changes", change.get("description"), "Potential root cause", "MEDIUM"))
            
        # Attempt reproduction
        repro_data = self.repro_tool.execute(requests=reqs, logs=logs)
        
        repro_status = Reproducibility.NOT_REPRODUCIBLE
        if repro_data.get("status") == "REPRODUCIBLE":
            repro_status = Reproducibility.REPRODUCIBLE
            
        repro_result = ReproductionResult(
            status=repro_status,
            steps=repro_data.get("steps", []),
            expected=repro_data.get("expected", ""),
            observed=repro_data.get("observed", "")
        )
        
        # Classify and assess severity
        classification = IssueClassification.UNKNOWN
        severity = Severity.UNKNOWN
        next_steps = []
        
        if repro_status == Reproducibility.NOT_REPRODUCIBLE:
            severity = Severity.LOW
            next_steps = [
                "Request additional request IDs from customer.",
                "Request exact timestamps.",
                "Collect affected customer/account information.",
                "Increase logging around the relevant operation."
            ]
        else:
            # Reproducible. Let's see what kind
            if "Stripe API key invalid" in error_msg:
                classification = IssueClassification.CUSTOMER_CONFIGURATION
                severity = Severity.MEDIUM
                next_steps = ["Customer must update their Stripe API key in the admin panel."]
            elif "column" in error_msg and "does not exist" in error_msg:
                classification = IssueClassification.PRODUCT_BUG
                severity = Severity.HIGH
                next_steps = ["Engineering needs to run the database migration to add the missing column."]
            elif "percentage" in error_msg:
                classification = IssueClassification.PRODUCT_BUG
                severity = Severity.HIGH
                next_steps = ["Engineering needs to fix the discount calculation logic for percentage discounts."]
            else:
                classification = IssueClassification.PRODUCT_BUG
                severity = Severity.MEDIUM
                next_steps = ["Engineering investigation required."]
                
        issue = Issue(
            title=f"Escalation: {report_data.get('issue')[:50]}...",
            classification=classification,
            severity=severity,
            reproducibility=repro_status
        )
        
        report = EscalationReport(
            customer=report_data.get("customer", "Unknown"),
            issue=issue,
            summary=report_data.get("issue", ""),
            facts=facts,
            observations=observations,
            hypotheses=hypotheses,
            reproduction=repro_result,
            evidence=evidence,
            recommended_next_steps=next_steps
        )
        
        # Generate artifacts
        paths = self.esc_tool.execute(report=report.to_dict())
        
        # Attach paths dynamically for CLI use
        report.escalation_json_path = paths["escalation_json_path"]
        report.evidence_json_path = paths["evidence_json_path"]
        report.reproduction_md_path = paths["reproduction_md_path"]
        report.escalation_md_path = paths["escalation_md_path"]
        
        return report
