# @fde-lab/incident-engineer

> POC #1 of the FDE Lab project: An AI-powered incident investigation solution.

## Mission

**FDE Lab** is a collection of production-style, customer-facing AI engineering solutions designed to demonstrate the skills of a Forward Deployed Engineer (FDE). 

The core philosophy is:
> **One command → install → run → demo.**

This specific package, **Incident Engineer**, represents a realistic AI incident investigation workflow. 

The customer has an application experiencing an incident. The Incident Engineer investigates the supplied information, correlates logs, metrics, and deployment history, and produces an evidence-backed incident report.

## Try it

You can run the Incident Engineer directly via NPX without needing to clone the repository or manually install dependencies.

### Standard Scenario (Known Cause)
```bash
npx @fde-lab/incident-engineer
```
The agent will ingest the simulated customer data, evaluate it against candidate root causes, and provide an evidence-backed incident report detailing the exhausting connection pool caused by deployment #184.

### Inconclusive Scenario (Safety Verification)
To demonstrate that the agent is bound by strict safety policies and will not "hallucinate" an answer when data is missing, you can run the inconclusive scenario:
```bash
npx @fde-lab/incident-engineer --scenario inconclusive
```
The agent will report that the root cause is **Inconclusive** with **Low** confidence, adhering to the FDE principle that uncertainty is mandatory when evidence is lacking.

## Architecture

This POC is strictly finite. It is not a monitoring platform or background worker. It evaluates the environment exactly once and cleanly exits when the report is rendered. 

It is built utilizing the core FDE Lab architecture:
- Thin Node.js CLI bootstrap for zero-friction environment setup.
- Isolated Python Agent runtime.
- Deterministic, read-only tools ensuring no unauthorized mutations.

## Learn More

Check out the <a href="https://github.com/smg99/fde-lab" target="_blank">FDE Lab GitHub Repository</a> for more information and to view the other FDE Lab solutions.
