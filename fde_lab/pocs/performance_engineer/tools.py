import os
import json
from typing import Dict, Any, List

from fde_lab.tools.base import Tool
from fde_lab.pocs.performance_engineer.models import PerformanceMetrics, PerformanceTrace, Diagnosis

def get_demo_data_path(scenario: str, filename: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "demo_data", "acme_commerce", scenario, filename)

class MetricsReaderTool(Tool):
    @property
    def name(self) -> str: return "read_metrics"
    @property
    def description(self) -> str: return "Reads the performance metrics."
    
    def execute(self, **kwargs) -> PerformanceMetrics:
        with open(get_demo_data_path(kwargs["scenario"], "metrics.json"), "r") as f:
            data = json.load(f)
            return PerformanceMetrics(**data)

class TraceReaderTool(Tool):
    @property
    def name(self) -> str: return "read_traces"
    @property
    def description(self) -> str: return "Reads the request traces."
    
    def execute(self, **kwargs) -> PerformanceTrace:
        with open(get_demo_data_path(kwargs["scenario"], "traces.json"), "r") as f:
            data = json.load(f)
            return PerformanceTrace(**data)

class BottleneckCorrelationTool(Tool):
    @property
    def name(self) -> str: return "correlate_bottleneck"
    @property
    def description(self) -> str: return "Correlates evidence to determine the bottleneck."
    
    def execute(self, **kwargs) -> dict:
        metrics: PerformanceMetrics = kwargs["metrics"]
        trace: PerformanceTrace = kwargs["trace"]
        
        evidence = []
        contradictory = []
        impact = {}
        recs = []
        
        # 1. Healthy check
        if trace.endpoint_p95_ms < 500:
            evidence.append(f"{metrics.endpoint} p95 is healthy at {trace.endpoint_p95_ms}ms")
            impact["latency"] = "Normal"
            recs.append("No action required. Performance is within acceptable bounds.")
            return {
                "diagnosis": Diagnosis("healthy", "HIGH"),
                "evidence": evidence,
                "contradictory": contradictory,
                "impact": impact,
                "recommendations": recs
            }
            
        evidence.append(f"{metrics.endpoint} p95 increased to {trace.endpoint_p95_ms:,} ms")
        impact["latency"] = f"Requests are experiencing approximately {trace.endpoint_p95_ms / 1000:.1f} seconds of additional latency."
        
        # We know p95 >= 500 (probably >= 1000 in our scenarios).
        db_ratio = trace.database_p95_ms / trace.endpoint_p95_ms
        api_ratio = trace.external_api_p95_ms / trace.endpoint_p95_ms
        
        # 2. Database bottleneck
        if db_ratio > 0.6 and trace.database_p95_ms > 1000:
            evidence.append(f"database p95 increased to {trace.database_p95_ms:,} ms")
            if trace.slowest_query_ms > 1000:
                evidence.append(f"query {trace.slowest_query_id} accounts for {trace.slowest_query_ms:,} ms")
            if metrics.connection_pool_utilization_percent > 80:
                evidence.append(f"connection pool utilization reached {metrics.connection_pool_utilization_percent}%")
            
            recs.append(f"Investigate query {trace.slowest_query_id} and database connection-pool configuration.")
            
            conf = "HIGH" if db_ratio > 0.75 else "MEDIUM"
            return {
                "diagnosis": Diagnosis("database", conf),
                "evidence": evidence,
                "contradictory": contradictory,
                "impact": impact,
                "recommendations": recs
            }
            
        # 3. External API bottleneck
        if api_ratio > 0.6 and trace.external_api_p95_ms > 1000:
            evidence.append(f"external API p95 increased to {trace.external_api_p95_ms:,} ms")
            recs.append("Investigate external API health and consider adding circuit breakers or timeouts.")
            
            conf = "HIGH" if api_ratio > 0.75 else "MEDIUM"
            return {
                "diagnosis": Diagnosis("external_api", conf),
                "evidence": evidence,
                "contradictory": contradictory,
                "impact": impact,
                "recommendations": recs
            }
            
        # 4. Application bottleneck
        if metrics.cpu_utilization_percent > 80 and trace.database_p95_ms < 500 and trace.external_api_p95_ms < 500:
            evidence.append(f"CPU utilization is high at {metrics.cpu_utilization_percent}%")
            evidence.append("Database and External API latencies are normal, ruling out dependencies.")
            
            recs.append("Profile application code for CPU-bound tasks or optimize resource allocation.")
            
            conf = "HIGH" if metrics.cpu_utilization_percent > 90 else "MEDIUM"
            return {
                "diagnosis": Diagnosis("application", conf),
                "evidence": evidence,
                "contradictory": contradictory,
                "impact": impact,
                "recommendations": recs
            }
            
        # 5. Inconclusive
        evidence.append("Latencies are elevated but neither DB, External API, nor CPU are definitive bottlenecks.")
        contradictory.append("Metrics show broad degradation without a clear singular culprit.")
        recs.append("Enable deeper distributed tracing and collect thread dumps.")
        
        return {
            "diagnosis": Diagnosis("inconclusive", "LOW"),
            "evidence": evidence,
            "contradictory": contradictory,
            "impact": impact,
            "recommendations": recs
        }

class PerformanceReportTool(Tool):
    @property
    def name(self) -> str: return "write_performance_artifacts"
    @property
    def description(self) -> str: return "Writes the performance report."
    
    def execute(self, **kwargs) -> dict:
        report = kwargs["report"]
        
        os.makedirs("output", exist_ok=True)
        
        with open("output/performance-report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        with open("output/performance-findings.json", "w") as f:
            json.dump(report["diagnosis"], f, indent=2)
            
        # Build human readable text
        txt = f"Performance Investigation\n-------------------------\n\n"
        txt += f"Customer: Acme Commerce\n"
        txt += f"Service: {report['service']}\n\n"
        
        if report['diagnosis']['category'] == 'healthy':
            txt += "Overall status: HEALTHY\n\n"
        else:
            txt += "Overall status: PERFORMANCE REGRESSION\n\n"
            
        metrics = report['metrics']
        txt += f"p95 latency: {metrics['endpoint_p95_ms']:,} ms\n"
        txt += f"Error rate: {metrics['error_rate_percent']}%\n"
        txt += f"CPU: {metrics['cpu_utilization_percent']}%\n"
        txt += f"Memory: {metrics['memory_utilization_percent']}%\n"
        txt += f"Database p95: {metrics['database_p95_ms']:,} ms\n"
        txt += f"External API p95: {metrics['external_api_p95_ms']:,} ms\n\n"
        
        cat_map = {
            "database": "Database",
            "external_api": "External API",
            "application": "Application Processing",
            "healthy": "None",
            "inconclusive": "Inconclusive"
        }
        
        txt += "LIKELY BOTTLENECK\n-----------------\n\n"
        txt += f"{cat_map.get(report['diagnosis']['category'], 'Unknown')}\n\n"
        txt += f"Confidence: {report['diagnosis']['confidence']}\n\n"
        
        txt += "Key evidence:\n"
        for ev in report.get("evidence", []):
            txt += f"✓ {ev}\n"
            
        if report.get("contradictory_evidence"):
            txt += "\nContradictory evidence:\n"
            for cev in report["contradictory_evidence"]:
                txt += f"✗ {cev}\n"
                
        if report.get("impact", {}).get("latency"):
            txt += f"\nImpact:\n{report['impact']['latency']}\n"
            
        txt += "\nRECOMMENDED ACTION\n------------------\n\n"
        for rec in report.get("recommendations", []):
            txt += f"- {rec}\n"
            
        txt += "\nNo automatic changes were made.\n"
            
        return {
            "report_path": "output/performance-report.json",
            "findings_path": "output/performance-findings.json",
            "human_output": txt
        }
