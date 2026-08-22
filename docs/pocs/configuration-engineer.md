# FDE Lab — Configuration Engineer (POC #9)

The **Configuration Engineer** worker simulates a Forward Deployed Engineer inspecting a customer's environment configuration. It reads the existing setup, validates it against expected schema rules, identifies missing, invalid, or conflicting values, and generates a proposed configuration change plan along with a risk assessment.

**Crucially, this worker is READ-ONLY.** It will never automatically modify the customer's configuration, nor will it restart services or deploy code. It only outputs a proposed patch plan for human or orchestration review.

## Running

```bash
npx @fde-lab/configuration-engineer --scenario missing-required
```

Scenarios:
- `normal`: Configuration is valid and matches the expected schema.
- `missing-required`: Essential configuration keys are missing.
- `invalid-values`: Values fall outside of bounds (e.g. negative timeouts or unsupported enums).
- `conflicting-config`: Mutually exclusive features are enabled, or dangerous configurations are present (e.g. `DEBUG` logging in `production`).
- `unsafe-change`: The configuration is invalid, but the fix involves a highly disruptive change (e.g. switching auth providers), triggering a `HIGH` risk assessment requiring human approval.

## AI-Native Contract (Machine Mode)

The Configuration Engineer fully implements the FDE Lab AI-Native Contract, making it extremely easy for an orchestrator to consume:

```bash
# Get the execution result structured safely as JSON, omitting human UI
npx @fde-lab/configuration-engineer --scenario invalid-values --json
```

```bash
# Discover what the agent can do and its scenarios
npx @fde-lab/configuration-engineer --manifest
```
