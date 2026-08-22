# FDE Lab — Data Migration Engineer (POC #6)

The **Data Migration Engineer** worker demonstrates an FDE workflow for performing a complex ETL/data migration operation. It inspects source data from a legacy CRM system, reads a new target schema constraints (JSON), performs deterministic data mapping and transformations (like email and date normalization), detects duplicates, and validates against the schema. 

Instead of silently discarding bad records, any data failing constraints is safely placed into a `quarantine.json` file for manual review.

## Running

```bash
npx @fde-lab/data-migration-engineer --scenario normal
```

Scenarios:
- `normal`: Migrates a small batch of clean records safely.
- `messy-data`: Contains invalid emails, malformed dates, missing required fields, and duplicate legacy IDs. Shows how the worker quarantines bad records while migrating the good ones.
- `schema-conflict`: Simulates a schema mismatch where the target requires a field the legacy CRM simply does not have.
- `dry-run`: Runs the migration analysis but skips writing output files to disk.

## AI-Native Contract (Machine Mode)

Like all workers in FDE Lab, the Data Migration Engineer exposes its capabilities and structured output automatically for orchestration layers to consume:

```bash
# Get the execution result structured safely as JSON, omitting human UI
npx @fde-lab/data-migration-engineer --scenario messy-data --json
```

```bash
# Discover what the agent can do and its scenarios
npx @fde-lab/data-migration-engineer --manifest
```
