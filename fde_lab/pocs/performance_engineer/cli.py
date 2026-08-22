import sys
import json
import argparse

from fde_lab.pocs.performance_engineer.agent import PerformanceEngineerAgent
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example, ArtifactEnvelope
from fde_lab.runtime.exit_codes import ExitCode

def generate_manifest() -> WorkerManifest:
    return WorkerManifest(
        name="performance-engineer",
        version="0.1.0",
        description="Investigates performance metrics and determines likely bottlenecks.",
        capabilities=[
            "read_metrics",
            "read_traces",
            "correlate_bottleneck",
            "write_performance_artifacts"
        ],
        inputs={
            "scenario": "The performance scenario to execute (normal, database-bottleneck, external-api-bottleneck, application-bottleneck, inconclusive)."
        },
        outputs={
            "performance-report": "Full investigation report",
            "performance-findings": "Structured bottleneck diagnosis"
        },
        side_effects=SideEffectMetadata(
            filesystem=True,
            network=False,
            credentials=False,
            production=False,
            destructive=False,
            external_systems=False
        ),
        requirements=EnvironmentRequirements(
            node=True,
            python=True,
            docker=False
        ),
        examples=[
            Example(
                command="npx @fde-lab/performance-engineer --scenario database-bottleneck",
                purpose="Investigates performance evidence indicating a database latency issue."
            )
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - Performance Engineer")
    parser.add_argument("command", nargs="?", choices=["investigate-performance"], help="Command to run")
    parser.add_argument("-s", "--scenario", default="normal", help="Scenario to run")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--manifest", action="store_true", help="Output capability manifest JSON")
    
    args = parser.parse_args()
    
    machine_mode = args.json or args.manifest
    configure_logging(machine_mode=machine_mode)
    
    if args.manifest:
        manifest = generate_manifest()
        print(json.dumps(manifest.to_dict(), indent=2))
        sys.exit(ExitCode.SUCCESS)
        
    try:
        agent = PerformanceEngineerAgent()
        report = agent.run(args.scenario)
        
        if args.json:
            artifacts = []
            if hasattr(report, "report_path") and report.report_path:
                artifacts.append(ArtifactEnvelope(path=report.report_path, type="performance-report", description="Performance report"))
            if hasattr(report, "findings_path") and report.findings_path:
                artifacts.append(ArtifactEnvelope(path=report.findings_path, type="performance-findings", description="Performance findings"))
                
            result = WorkerResult(
                worker={"name": "performance-engineer", "version": "0.1.0"},
                status=report.status,
                summary=f"Performance investigation complete. Bottleneck: {report.diagnosis.category.upper()}",
                facts=[
                    f"Confidence: {report.diagnosis.confidence}",
                    f"p95 Latency: {report.metrics['endpoint_p95_ms']}ms",
                    f"CPU: {report.metrics['cpu_utilization_percent']}%"
                ],
                artifacts=artifacts,
                errors=[],
                next_steps=report.recommendations
            )
            
            # Inject the detailed metrics, diagnosis, and evidence into the JSON result envelope root (since the spec said to output these directly)
            res_dict = result.to_dict()
            res_dict["service"] = report.service
            res_dict["diagnosis"] = report.diagnosis.category
            res_dict["confidence"] = report.diagnosis.confidence
            res_dict["metrics"] = report.metrics
            res_dict["evidence"] = report.evidence
            res_dict["contradictory_evidence"] = report.contradictory_evidence
            res_dict["impact"] = report.impact
            
            print(json.dumps(res_dict, indent=2))
        else:
            print(report.human_output)
            
        sys.exit(ExitCode.SUCCESS)
        
    except Exception as e:
        if args.json:
            from fde_lab.runtime.result import WorkerError
            result = WorkerResult(
                worker={"name": "performance-engineer", "version": "0.1.0"},
                status="failure",
                summary="Execution failed",
                errors=[WorkerError(code="INTERNAL_ERROR", message=str(e), stage="execution", recoverable=False, suggested_action="Check logs")]
            )
            print(json.dumps(result.to_dict(), indent=2))
        else:
            import traceback
            traceback.print_exc()
        sys.exit(ExitCode.FAILURE)

if __name__ == "__main__":
    main()
