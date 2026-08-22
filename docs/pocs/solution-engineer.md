# FDE Lab — Solution Engineer (POC #10)

The **Solution Engineer** worker simulates a Forward Deployed Engineer (or Solution Architect) turning an ambiguous customer requirement into a concrete technical implementation plan. It reads customer requirements, their existing infrastructure, business/technical constraints, and integration capabilities to output a tailored architecture and implementation phasing.

**Crucially, this worker demonstrates scenario safety.** If it lacks sufficient information to propose a valid architecture, it halts and requests input rather than hallucinating fake systems. If it detects contradictory requirements, it flags the conflict for human resolution.

## Running

```bash
npx @fde-lab/solution-engineer --scenario normal
```

Scenarios:
- `normal`: Customer environment is sufficient to support the subscription checkout goal. Output includes architecture mapping, gap analysis, phases, and risks.
- `constrained-environment`: Customer constraints (e.g. tight deployment windows) inject higher risk.
- `integration-gap`: Existing integrations lack necessary capabilities (e.g. payment provider missing subscription billing). A gap is flagged with its downstream impact.
- `conflicting-requirements`: Customer requires synchronous UI flow but prohibits waiting on billing. Worker halts and requests clarification.
- `insufficient-information`: Customer inventory data is empty/missing. Worker halts, requesting what billing/CRM systems exist.

## AI-Native Contract (Machine Mode)

The Solution Engineer fully implements the FDE Lab AI-Native Contract. Because solution architecture is extremely text-heavy, the JSON envelope standardizes the domain model so an orchestrator doesn't need to string-parse complex architecture diagrams:

```bash
# Get the execution result structured safely as JSON
npx @fde-lab/solution-engineer --scenario normal --json
```

```bash
# Discover capabilities
npx @fde-lab/solution-engineer --manifest
```
