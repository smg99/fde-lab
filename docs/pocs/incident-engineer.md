# POC #1: Incident Engineer

**Customer problem:** When a major incident occurs, engineers spend excessive time manually gathering logs, checking Git histories, querying metrics, and building timelines before they can even begin to diagnose the root cause.

## Why this is an FDE problem
Forward Deployed Engineers often drop into new environments where they must quickly connect disparate, messy data sources to understand a complex system failure. This POC demonstrates an automated approach to triaging those incidents.

## Try it
```bash
npx @fde-lab/incident-engineer
```

### Try the inconclusive scenario
```bash
npx @fde-lab/incident-engineer --scenario inconclusive
```

## Demo Scenario
A customer's checkout API starts returning HTTP 500 errors shortly after a deployment. You are asked to investigate. The Incident Engineer connects to the simulated environment, builds a timeline, and issues a report.

## Architecture
- **Read-Only Tools**: Connects to the simulated environment to retrieve deployment history, logs, git commits, and metrics.
- **Evidence Extraction**: Formats raw telemetry into structured `Evidence` (Source, Time, Observation, Relevance).
- **Correlation**: Builds a timeline from the evidence.
- **Reporting**: Distinguishes between observable facts and derived inferences, producing a final professional incident report.

## Safety & Limitations
This agent is strictly **READ-ONLY**. It does not possess any tools for restarting services, modifying configurations, or triggering deployments. 

If the agent does not have sufficient information (simulated via the `--scenario inconclusive` flag), it is programmed to declare the root cause as "Inconclusive" with "Low" confidence, rather than hallucinating an explanation. This demonstrates safe and trustworthy AI behavior in enterprise environments.
