# FDE Lab — API Integration Engineer (POC #7)

The **API Integration Engineer** worker demonstrates an FDE workflow for integrating an unfamiliar third-party API. It statically analyzes the API specification (a simulated AcmePay API), dynamically tests authentication, validates the request payloads against the spec before sending, executes the simulated API call, and handles API errors appropriately. Finally, it produces an integration code example and report.

## Running

```bash
npx @fde-lab/api-integration-engineer --scenario normal
```

Scenarios:
- `normal`: Analyzes the API with valid configurations, successfully generating a report and mock integration code mapping.
- `auth-failure`: Simulates an integration attempt where the bearer token is missing or invalid, yielding a 401 error.
- `schema-mismatch`: Simulates an integration payload where the customer sends `customer_email`, but the API expects `email`.
- `api-error`: Simulates a customer request hitting a 429 Rate Limited endpoint.

## AI-Native Contract (Machine Mode)

Like all workers in FDE Lab, the API Integration Engineer exposes its capabilities and structured output automatically for orchestration layers to consume:

```bash
# Get the execution result structured safely as JSON, omitting human UI
npx @fde-lab/api-integration-engineer --scenario schema-mismatch --json
```

```bash
# Discover what the agent can do and its scenarios
npx @fde-lab/api-integration-engineer --manifest
```
