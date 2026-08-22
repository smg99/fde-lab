# FDE Lab

FDE Lab is a collection of 11 AI-native Forward Deployed Engineer (FDE) workers. These workers handle various complex infrastructure and software tasks deterministically and output machine-readable JSON.

## Try it

```bash
npx @fde-lab/incident-engineer
```

## AI Consumption Contract

Every worker supports standard AI-native execution modes and a predictable contract designed specifically for external orchestrators.

1. **Discover worker:** Use `--manifest` to discover worker capabilities, input scenarios, and expected side-effects.
   ```bash
   npx @fde-lab/incident-engineer --manifest
   ```

2. **Understand invocation:** The manifest (`manifest.inputs` and `manifest.examples`) documents how to execute the worker.

3. **Understand result:** The manifest (`manifest.outputs.WorkerResult`) provides a strict JSON Schema detailing exactly what data the worker will return.

4. **Execute:** Invoke the worker via `npx`, passing required inputs.

5. **Parse:** Use `--json` to retrieve the strictly-structured output. The stdout is guaranteed to contain only the clean JSON result envelope.
   ```bash
   npx @fde-lab/incident-engineer --json > result.json
   ```

6. **Interpret:** The JSON payload provides actionable context including `status`, `confidence`, `next_steps`, and `artifacts`.

7. **Use process exit code:** The Node.js process propagates the granular Python semantic exit codes (e.g., `5` for Inconclusive, `0` for Success) as documented in `manifest.exit_codes`. This allows orchestrators to make immediate fallback or circuit-breaker decisions without parsing stdout.

## Workers

| # | Worker | Purpose | npm | Status |
|---|---|---|---|---|
| 1 | `integration_engineer` | AI-native integration engineer | [`@fde-lab/integration-engineer`](https://www.npmjs.com/package/@fde-lab/integration-engineer) | ✅ Published |
| 2 | `deployment_engineer` | AI-native deployment engineer | [`@fde-lab/deployment-engineer`](https://www.npmjs.com/package/@fde-lab/deployment-engineer) | ✅ Published |
| 3 | `customer_onboarding_engineer` | AI-native customer onboarding engineer | [`@fde-lab/customer-onboarding-engineer`](https://www.npmjs.com/package/@fde-lab/customer-onboarding-engineer) | ✅ Published |
| 4 | `data_migration_engineer` | AI-native data migration engineer | [`@fde-lab/data-migration-engineer`](https://www.npmjs.com/package/@fde-lab/data-migration-engineer) | ✅ Published |
| 5 | `performance_engineer` | AI-native performance engineer | [`@fde-lab/performance-engineer`](https://www.npmjs.com/package/@fde-lab/performance-engineer) | ✅ Published |
| 6 | `environment_inspector` | AI-native environment inspector | [`@fde-lab/environment-inspector`](https://www.npmjs.com/package/@fde-lab/environment-inspector) | ✅ Published |
| 7 | `incident_engineer` | AI-native incident engineer | [`@fde-lab/incident-engineer`](https://www.npmjs.com/package/@fde-lab/incident-engineer) | ✅ Published |
| 8 | `api_integration_engineer` | AI-native api integration engineer | [`@fde-lab/api-integration-engineer`](https://www.npmjs.com/package/@fde-lab/api-integration-engineer) | ✅ Published |
| 9 | `solution_engineer` | AI-native solution engineer | [`@fde-lab/solution-engineer`](https://www.npmjs.com/package/@fde-lab/solution-engineer) | ✅ Published |
| 10 | `support_escalation_engineer` | AI-native support escalation engineer | [`@fde-lab/support-escalation-engineer`](https://www.npmjs.com/package/@fde-lab/support-escalation-engineer) | ✅ Published |
| 11 | `configuration_engineer` | AI-native configuration engineer | [`@fde-lab/configuration-engineer`](https://www.npmjs.com/package/@fde-lab/configuration-engineer) | ✅ Published |

## Architecture

```text
AI / Orchestrator
        ↓
   --manifest
        ↓
    FDE Worker
        ↓
   --json result
        ↓
AI / Orchestrator
```

## Repository structure

- `packages/`: Individual worker npm packages
- `fde_lab/`: Shared Python runtime and POC implementations
- `registry/`: Capability and package registries
- `docs/`: POC documentation

## npm / GitHub

The npm packages wrap the Python workers for easy distribution. The packages contain pre-bundled Python environments that install transparently into a local cache directory on first run.

Source: [https://github.com/smg99/fde-lab](https://github.com/smg99/fde-lab)
