# FDE Lab — Performance Engineer (POC #8)

The **Performance Engineer** worker simulates an FDE investigating a customer application experiencing slow response times. It reads seeded performance evidence (metrics, endpoint latency traces) and deterministically correlates this data to identify the likely bottleneck. 

It handles multiple potential root causes, calculates confidence levels, and gracefully reports an inconclusive status if the evidence is insufficient or contradictory.

## Running

```bash
npx @fde-lab/performance-engineer --scenario normal
```

Scenarios:
- `normal`: System is healthy, p95 latencies are well within bounds.
- `database-bottleneck`: Overall latency is elevated due to significant time spent executing a slow query (high Database p95).
- `external-api-bottleneck`: Overall latency is elevated due to a third-party dependency timing out (high External API p95).
- `application-bottleneck`: Database and External APIs are fast, but CPU is maxed out, implicating the application's processing layer.
- `inconclusive`: General performance degradation where no single dependency is uniquely responsible, prompting a recommendation for deeper tracing.

## AI-Native Contract (Machine Mode)

Like all workers in FDE Lab, the Performance Engineer exposes its capabilities and structured output automatically for orchestration layers to consume:

```bash
# Get the execution result structured safely as JSON, omitting human UI
npx @fde-lab/performance-engineer --scenario external-api-bottleneck --json
```

```bash
# Discover what the agent can do and its scenarios
npx @fde-lab/performance-engineer --manifest
```
