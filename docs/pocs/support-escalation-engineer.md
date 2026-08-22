# FDE Lab — Support Escalation Engineer (POC #5)

The **Support Escalation Engineer** worker investigates ambiguous customer bug reports, analyzes application logs, attempts deterministic reproduction, classifies the issue (e.g., Product Bug vs. Customer Configuration), assesses severity, and generates an engineering-ready escalation report.

## The Objective

Take an ambiguous issue report, gather evidence, perform reproducible tests safely, and output a structured escalation with no hallucination.

## Running

To run the worker in human mode:

```bash
npx @fde-lab/support-escalation-engineer --scenario normal
```

Scenarios:
- `normal`: A reproducible product bug (discount percentage logic error).
- `not-reproducible`: Random checkout failures with no evidence or logs.
- `product-bug`: A reproducible database error due to a missing column.
- `customer-configuration`: A reproducible payment error due to invalid API keys.

## AI-Native Contract (Machine Mode)

To run the worker and get machine-readable JSON output:

```bash
npx @fde-lab/support-escalation-engineer --scenario product-bug --json
```

To view the capability manifest:

```bash
npx @fde-lab/support-escalation-engineer --manifest
```
