import os
import json
from typing import Dict, Any, List

from fde_lab.tools.base import Tool
from fde_lab.pocs.solution_engineer.models import (
    Gap, Conflict, Component, Connection, Architecture, Phase, Risk, Assumption, CustomerQuestion
)

def get_demo_data_path(scenario: str, filename: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "demo_data", "acme_commerce", scenario, filename)

class ReaderTool(Tool):
    def __init__(self, name: str, desc: str, filename: str):
        self._name = name
        self._desc = desc
        self._filename = filename
        
    @property
    def name(self) -> str: return self._name
    @property
    def description(self) -> str: return self._desc
    
    def execute(self, **kwargs) -> dict:
        with open(get_demo_data_path(kwargs["scenario"], self._filename), "r") as f:
            return json.load(f)

class ConflictDetectorTool(Tool):
    @property
    def name(self) -> str: return "detect_conflicts"
    @property
    def description(self) -> str: return "Detects conflicting requirements."
    
    def execute(self, **kwargs) -> List[Conflict]:
        reqs = kwargs.get("requirements", {}).get("requirements", [])
        conflicts = []
        sync = any("synchronous" in r.lower() for r in reqs)
        async_billing = any("never wait for the billing" in r.lower() for r in reqs)
        
        if sync and async_billing:
            conflicts.append(Conflict(
                description="Contradictory requirements: Checkout must be synchronous vs Checkout must never wait for billing.",
                recommendation="Clarify if the customer wants a synchronous UI experience with asynchronous backend processing, or if billing must be inline."
            ))
        return conflicts

class GapAnalysisTool(Tool):
    @property
    def name(self) -> str: return "analyze_gaps"
    @property
    def description(self) -> str: return "Identifies integration gaps."
    
    def execute(self, **kwargs) -> List[Gap]:
        integrations = kwargs.get("integrations", {}).get("systems", [])
        gaps = []
        
        has_sub = False
        for sys in integrations:
            if "subscription" in sys.get("capabilities", []):
                has_sub = True
                
        if not has_sub:
            gaps.append(Gap(
                description="Existing Payment Provider lacks 'subscription' capability.",
                impact="Cannot natively schedule recurring billing without custom orchestration or a new provider."
            ))
        return gaps

class ArchitecturePlannerTool(Tool):
    @property
    def name(self) -> str: return "plan_architecture"
    @property
    def description(self) -> str: return "Designs the architecture."
    
    def execute(self, **kwargs) -> Architecture:
        env = kwargs.get("environment", {}).get("infrastructure", [])
        
        components = [Component("Web Application"), Component("Commerce API")]
        if any("Database" in e for e in env):
            components.append(Component("Customer Database"))
        components.append(Component("Payment Provider"))
        
        connections = [
            Connection("Web Application", "Commerce API", "Checkout requests"),
            Connection("Commerce API", "Payment Provider", "Process billing")
        ]
        if Component("Customer Database") in components:
            connections.append(Connection("Commerce API", "Customer Database", "Sync subscribers"))
            
        return Architecture(components=components, connections=connections)

class ImplementationPlannerTool(Tool):
    @property
    def name(self) -> str: return "plan_implementation"
    @property
    def description(self) -> str: return "Produces implementation phases."
    
    def execute(self, **kwargs) -> List[Phase]:
        return [
            Phase("Phase 1 — Foundation", "Define models and API contracts.", ["define subscription domain model", "extend commerce API"]),
            Phase("Phase 2 — Integration", "Implement billing sync.", ["implement billing synchronization", "add webhook handling"]),
            Phase("Phase 3 — UI", "Expose checkout.", ["implement subscription checkout", "expose billing status"]),
            Phase("Phase 4 — Validation", "Testing and rollout.", ["integration tests", "customer acceptance testing"])
        ]

class SolutionReportTool(Tool):
    @property
    def name(self) -> str: return "write_solution_report"
    @property
    def description(self) -> str: return "Writes the solution report."
    
    def execute(self, **kwargs) -> dict:
        report = kwargs["report"]
        
        os.makedirs("output", exist_ok=True)
        
        report_path = "output/solution-report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        txt = "SOLUTION ENGINEER REPORT\n────────────────────────────────────────\n\n"
        txt += f"Status: {report['status'].upper()}\n\n"
        
        if report["requires_customer_input"]:
            txt += "STATUS: NEEDS CUSTOMER INPUT\n\n"
            for q in report["customer_questions"]:
                txt += f"- {q}\n"
            return {"report_path": report_path, "human_output": txt}
            
        if report["conflicts"]:
            txt += "CONFLICT DETECTED\n\n"
            for c in report["conflicts"]:
                txt += f"- {c['description']}\n  Recommendation: {c['recommendation']}\n\n"
            return {"report_path": report_path, "human_output": txt}
            
        txt += "ARCHITECTURE\n\n"
        for conn in report["architecture"]["connections"]:
            txt += f"{conn['source']} --({conn['description']})--> {conn['target']}\n"
            
        txt += "\nGAPS\n\n"
        if not report["gaps"]:
            txt += "None\n"
        else:
            for g in report["gaps"]:
                txt += f"- {g['description']} (Impact: {g['impact']})\n"
                
        txt += "\nIMPLEMENTATION PLAN\n\n"
        for p in report["implementation_plan"]:
            txt += f"{p['name']} - {p['objective']}\n"
            for t in p['tasks']:
                txt += f"  - {t}\n"
                
        txt += "\nRISKS\n\n"
        for r in report["risks"]:
            txt += f"- [{r['severity']}] {r['description']}\n"
            
        txt += "\nASSUMPTIONS\n\n"
        for a in report["assumptions"]:
            txt += f"- {a}\n"
            
        txt += "\nNO CUSTOMER CHANGES WERE MADE.\n"
        
        return {"report_path": report_path, "human_output": txt}
