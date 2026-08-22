import logging

from fde_lab.pocs.performance_engineer.models import PerformanceReport
from fde_lab.pocs.performance_engineer.tools import (
    MetricsReaderTool, TraceReaderTool, BottleneckCorrelationTool, PerformanceReportTool
)

logger = logging.getLogger("fde_lab.pocs.performance_engineer.agent")

class PerformanceEngineerAgent:
    def __init__(self):
        self.metrics_tool = MetricsReaderTool()
        self.trace_tool = TraceReaderTool()
        self.correlation_tool = BottleneckCorrelationTool()
        self.report_tool = PerformanceReportTool()
        
    def run(self, scenario: str) -> PerformanceReport:
        logger.info(f"Starting Performance Engineer for scenario: {scenario}")
        
        metrics = self.metrics_tool.execute(scenario=scenario)
        trace = self.trace_tool.execute(scenario=scenario)
        
        analysis = self.correlation_tool.execute(metrics=metrics, trace=trace)
        
        status = "completed"
        
        # Combine metrics into a single dict for the report
        combined_metrics = {
            "endpoint_p50_ms": trace.endpoint_p50_ms,
            "endpoint_p95_ms": trace.endpoint_p95_ms,
            "database_p95_ms": trace.database_p95_ms,
            "external_api_p95_ms": trace.external_api_p95_ms,
            "slowest_query_ms": trace.slowest_query_ms,
            "slowest_query_id": trace.slowest_query_id,
            "request_rate_tps": metrics.request_rate_tps,
            "error_rate_percent": metrics.error_rate_percent,
            "cpu_utilization_percent": metrics.cpu_utilization_percent,
            "memory_utilization_percent": metrics.memory_utilization_percent,
            "connection_pool_utilization_percent": metrics.connection_pool_utilization_percent
        }
        
        report = PerformanceReport(
            status=status,
            scenario=scenario,
            service=metrics.service,
            diagnosis=analysis["diagnosis"],
            metrics=combined_metrics,
            evidence=analysis["evidence"],
            contradictory_evidence=analysis["contradictory"],
            impact=analysis["impact"],
            recommendations=analysis["recommendations"]
        )
        
        paths = self.report_tool.execute(report=report.to_dict())
        report.report_path = paths["report_path"]
        report.findings_path = paths["findings_path"]
        report.human_output = paths["human_output"]
        
        return report
