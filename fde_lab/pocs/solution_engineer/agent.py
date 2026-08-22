import logging

from fde_lab.pocs.solution_engineer.models import SolutionReport, Risk, Assumption, CustomerQuestion
from fde_lab.pocs.solution_engineer.tools import (
    ReaderTool, ConflictDetectorTool, GapAnalysisTool, 
    ArchitecturePlannerTool, ImplementationPlannerTool, SolutionReportTool
)

logger = logging.getLogger("fde_lab.pocs.solution_engineer.agent")

class SolutionEngineerAgent:
    def __init__(self):
        self.req_tool = ReaderTool("read_reqs", "Reads requirements", "requirements.json")
        self.env_tool = ReaderTool("read_env", "Reads environment", "environment.json")
        self.const_tool = ReaderTool("read_const", "Reads constraints", "constraints.json")
        self.int_tool = ReaderTool("read_int", "Reads integrations", "integrations.json")
        
        self.conflict_tool = ConflictDetectorTool()
        self.gap_tool = GapAnalysisTool()
        self.arch_tool = ArchitecturePlannerTool()
        self.impl_tool = ImplementationPlannerTool()
        self.report_tool = SolutionReportTool()
        
    def run(self, scenario: str) -> SolutionReport:
        logger.info(f"Starting Solution Engineer for scenario: {scenario}")
        
        reqs = self.req_tool.execute(scenario=scenario)
        env = self.env_tool.execute(scenario=scenario)
        const = self.const_tool.execute(scenario=scenario)
        ints = self.int_tool.execute(scenario=scenario)
        
        # Insufficient info check
        if not ints.get("systems"):
            report = SolutionReport(
                status="needs_customer_input",
                scenario=scenario,
                requirements=reqs.get("requirements", []),
                observations=["Existing systems inventory is completely empty."],
                constraints=[],
                gaps=[],
                conflicts=[],
                architecture=None,
                implementation_plan=[],
                risks=[],
                assumptions=[],
                customer_questions=[CustomerQuestion("What billing/CRM systems currently exist?")],
                confidence="LOW",
                requires_customer_input=True
            )
            paths = self.report_tool.execute(report=report.to_dict())
            report.report_path = paths["report_path"]
            report.human_output = paths["human_output"]
            return report
            
        conflicts = self.conflict_tool.execute(requirements=reqs)
        if conflicts:
            report = SolutionReport(
                status="conflict_detected",
                scenario=scenario,
                requirements=reqs.get("requirements", []),
                observations=[],
                constraints=[],
                gaps=[],
                conflicts=conflicts,
                architecture=None,
                implementation_plan=[],
                risks=[],
                assumptions=[],
                customer_questions=[CustomerQuestion(c.recommendation) for c in conflicts],
                confidence="MEDIUM",
                requires_customer_input=True
            )
            paths = self.report_tool.execute(report=report.to_dict())
            report.report_path = paths["report_path"]
            report.human_output = paths["human_output"]
            return report
            
        gaps = self.gap_tool.execute(integrations=ints)
        arch = self.arch_tool.execute(environment=env)
        plan = self.impl_tool.execute()
        
        risks = []
        if scenario == "constrained-environment":
            risks.append(Risk("Restricted deployment window", "HIGH", "Schedule deployments carefully."))
        else:
            risks.append(Risk("Integration failure", "MEDIUM", "Add circuit breakers."))
            
        assumptions = [Assumption("Commerce API is fully REST compliant.")]
        
        report = SolutionReport(
            status="ready",
            scenario=scenario,
            requirements=reqs.get("requirements", []),
            observations=["Existing infrastructure supports core routing."],
            constraints=const.get("technical", []) + const.get("business", []),
            gaps=gaps,
            conflicts=[],
            architecture=arch,
            implementation_plan=plan,
            risks=risks,
            assumptions=assumptions,
            customer_questions=[],
            confidence="HIGH",
            requires_customer_input=False
        )
        
        paths = self.report_tool.execute(report=report.to_dict())
        report.report_path = paths["report_path"]
        report.human_output = paths["human_output"]
        
        return report
