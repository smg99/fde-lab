# AI-Native Contract

All FDE Lab workers are designed to be "AI-Native." This means they are equally usable by humans in the terminal (with rich formatting, spinners, and readable outputs) and by AI agents (with deterministic, machine-readable JSON interfaces).

AI agents discover how to interact with these tools by reading the repository documentation (like the `README.md`) which explicitly documents the existence of the machine-readable contract.

## The Contract

Every FDE Lab worker must adhere to the following contract to guarantee zero friction for AI orchestration:

### 1. The Manifest Flag (`--manifest`)

When invoked with `--manifest`, the worker MUST:
- Exit with code `0`.
- Output exactly one strictly formatted JSON object to `stdout`.
- Emit NO logs, spinners, or human-readable text to `stdout`.
- Comply with the `WorkerManifest` schema, detailing its capabilities, required inputs, deterministic outputs, and side effects.

This allows a central orchestrator or AI agent to dynamically discover what a worker can do without running it.

**Example usage:**
```bash
npx @fde-lab/incident-engineer --manifest
```

### 2. The JSON Execution Flag (`--json`)

When invoked with `--json`, the worker MUST:
- Run its full execution flow silently.
- Emit NO interactive UI, progress spinners, or human-readable text to `stdout`.
- Route all diagnostic logging and errors exclusively to `stderr`.
- Output exactly one strictly formatted JSON object to `stdout` at the end of the execution.
- Comply with the `WorkerResult` schema, containing standard `status`, `summary`, `facts`, `artifacts`, and `errors` fields.
- Exit with a predictable and documented exit code.

**Example usage:**
```bash
npx @fde-lab/incident-engineer --json
```

### 3. Predictable Exit Codes

All workers must use standardized exit codes (defined in `fde_lab.runtime.exit_codes`) to convey execution state:
- `0` - SUCCESS
- `1` - FAILURE (Generic unhandled error)
- `2` - INVALID_INPUT
- `3` - ENVIRONMENT_ERROR (Missing dependencies)
- `4` - TIMEOUT
- `5` - INCONCLUSIVE (The worker operated correctly but could not determine a definitive outcome)

### 4. Zero Cross-Contamination

When the worker operates in human mode (no flags), it presents a rich UI via stdout. However, the presence of `--manifest` or `--json` triggers a strict boundary where stdout becomes an immutable API response. Agents can safely parse stdout using standard JSON parsers.
