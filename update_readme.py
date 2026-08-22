import json

with open("registry/packages.json", "r") as f:
    packages = json.load(f)

# POC names and descriptions mapped from their package.json or hardcoded based on 1-10

poc_list = ""
for i, pkg in enumerate(packages):
    poc_list += f"| {i+1} | `{pkg['worker_id']}` | AI-native {pkg['worker_id'].replace('_', ' ')} | [`{pkg['npm_package']}`]({pkg['npm_url']}) | ✅ Published |\n"

readme_content = f"""# FDE Lab

FDE Lab is a collection of 10 AI-native Forward Deployed Engineer (FDE) workers. These workers handle various complex infrastructure and software tasks deterministically and output machine-readable JSON.

## Try it

```bash
npx @fde-lab/incident-engineer
```

## AI-Native Interface

Every worker supports standard AI-native execution modes for orchestrators.

**Manifest Mode** (`--manifest`)
```bash
npx @fde-lab/incident-engineer --manifest
```
Outputs standard capabilities for AI discovery.

**JSON Mode** (`--json`)
```bash
npx @fde-lab/incident-engineer --json
```
Outputs standardized execution results:
```json
{{
  "success": true,
  "worker": "incident-engineer",
  "version": "0.1.5",
  "status": "success",
  "result": {{ ... }},
  "errors": [],
  "warnings": []
}}
```

## Workers

| # | Worker | Purpose | npm | Status |
|---|---|---|---|---|
{poc_list}

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

## Development

Use Make to manage the workspace:
```bash
make install
make build
make test
```

## npm / GitHub

The npm packages wrap the Python workers for easy distribution. The packages contain pre-bundled Python environments that install transparently into a local cache directory on first run.

Source: [https://github.com/smg99/fde-lab](https://github.com/smg99/fde-lab)
"""

with open("README.md", "w") as f:
    f.write(readme_content)

print("Updated README.md")
