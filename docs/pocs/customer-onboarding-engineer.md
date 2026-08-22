# POC #4 — Customer Onboarding Engineer

The **Customer Onboarding Engineer** demonstrates how a Forward Deployed Engineer (FDE) takes an unfamiliar customer onboarding specification, understands the requirements, maps them to product capabilities, validates the input, and generates a normalized, ready-to-use configuration package without mutating external systems.

## Customer Problem

Customers often provide their onboarding configuration in disparate formats (JSON, CSV, emails). They expect the implementation team to catch errors early, let them know if anything is missing, and flag requirements that the product does not currently support. Manual validation is error-prone and time-consuming.

## FDE Workflow
This worker performs the following deterministic steps:
1. **Inspect**: Read the customer's `onboarding.json` and `users.csv`.
2. **Discover Capabilities**: Load the hardcoded supported capabilities of the system.
3. **Validate**: Check structural integrity and constraints (e.g., duplicate users, invalid roles).
4. **Map Requirements**: Compare customer requests against supported features and integrations.
5. **Generate**: Produce a normalized configuration package.
6. **Report**: Create an onboarding checklist and a status report (`READY`, `INCOMPLETE`, or `BLOCKED`).

## Scenarios

### 1. Normal Scenario
**Command:** `npx @fde-lab/customer-onboarding-engineer`
A valid, complete configuration. The system maps all 8 requirements, outputs a normalized config, and sets the status to `READY`.

### 2. Incomplete Scenario
**Command:** `npx @fde-lab/customer-onboarding-engineer --scenario incomplete`
The configuration is missing mandatory features (analytics) and contains duplicate users. The agent detects the gaps and sets the status to `INCOMPLETE`.

### 3. Unsupported Scenario
**Command:** `npx @fde-lab/customer-onboarding-engineer --scenario unsupported`
The customer requests an integration ("Salesforce") that the product does not support. The agent distinguishes between "missing" and "unsupported", setting the status to `BLOCKED`.

## AI-Native Contract
This tool strictly implements the `AI-NATIVE-CONTRACT.md`:
- `--manifest`: Emits the capability manifest detailing inputs, outputs, and side-effects.
- `--json`: Runs silently and emits a structured `WorkerResult` object with `artifacts` and `errors`.
