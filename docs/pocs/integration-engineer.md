# POC #2: Integration Engineer

## Customer Problem
A customer has exported their existing users from their CRM (`customers.csv`). They want to import this data into their new Billing System. However, the CRM and the Billing System use completely different schemas. The customer needs an engineer to understand how the fields relate, map them, validate the data against the billing constraints, and produce the final JSON payload.

## Why this is an FDE problem
Forward Deployed Engineers (FDEs) frequently bridge the gap between abstract systems and messy customer data. They must:
- Intelligently understand schema mismatches.
- Perform safe, verifiable transformations.
- Handle edge cases (missing data, unsupported enums) cleanly.
- Explain the integration simply to the customer.

## Source System (CRM)
- `customer_id` (string)
- `first_name` (string)
- `last_name` (string)
- `email` (string)
- `company` (string, optional)
- `country` (string)
- `plan` (string)
- `marketing_opt_in` (boolean)

## Target System (Billing System)
- `external_customer_id` (string)
- `name` (string)
- `email_address` (string)
- `organization` (string, optional)
- `country_code` (string)
- `subscription_tier` (string)

## Demo

You can run this POC using NPX (no cloning required).

### Standard Scenario
```bash
npx @fde-lab/integration-engineer
```
The agent maps the fields (e.g. `first_name` + `last_name` -> `name`), ignores `marketing_opt_in` (since it has no target equivalent), and transforms the valid records, saving them to `./output/billing-customers.json`.

### Invalid Data Scenario
```bash
npx @fde-lab/integration-engineer --scenario invalid-data
```
The agent encounters simulated messy data and successfully validates it. It will explicitly reject records with:
- Missing email addresses.
- Unsupported country codes.
- Unknown subscription tiers.

## Safety & Boundaries
- The output is strictly written to a local `./output/` file.
- **No data is sent over the network.**
- **No external systems are mutated.**
- The POC is intentionally finite and does not run continuously in the background.

## Architecture
This POC reuses the FDE Lab foundation:
- `@fde-lab/cli-core` handles the Node.js bootstrap and isolated Python environment.
- The `IntegrationEngineerAgent` utilizes specialized tools (`TargetSchemaTool`, `ValidationTool`, `OutputWriterTool`) to perform a deterministic pipeline execution.
