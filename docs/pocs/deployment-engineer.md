# POC #3: Deployment Engineer

## Customer Problem
A customer has provided an unfamiliar application (a Python service) and needs an FDE to configure it for deployment, run it reproducibly, verify that it works, and explain the architecture, all without breaking production.

## Why this is an FDE problem
FDEs constantly adapt to unfamiliar customer codebases. They must inspect the application structure, determine the required runtime, install dependencies, and package it safely without hallucinating or making assumptions.

## Customer Application
The seeded application is a small FastAPI service with `/health` and `/api/customers` endpoints.

## Agent Capabilities
The Deployment Engineer orchestrates a deterministic pipeline using discrete tools:

1. **Application Inspection:** Derives the `requirements.txt`, entrypoint, and exposed port by parsing the source files.
2. **Configuration Generation:** Dynamically writes a `Dockerfile` and `deployment.json` using the inspected parameters.
3. **Docker Build:** Deterministically builds `fde-lab/customer-app`.
4. **Local Deployment:** Runs the container on a dynamic host port (mapping `0:8000`) to prevent port collisions.
5. **Verification:** Polls `/health` and the functional API endpoint to prove the deployment succeeded.
6. **Cleanup:** Stops and removes the container to prevent orphaned resources.

## Demo

```bash
npx @fde-lab/deployment-engineer
```

### Failure Handling
To demonstrate how the agent handles broken applications or environments:

```bash
npx @fde-lab/deployment-engineer --scenario broken-app
```
The agent detects the failure (e.g., missing dependency or Docker daemon unavailability), halts the deployment gracefully, skips verification, and advises the user on how to fix it.

## Architecture
- `ApplicationInspectorTool`
- `DeploymentConfigGeneratorTool`
- `DockerBuildTool`
- `ContainerRunnerTool`
- `VerificationTool`
- `CleanupTool`

All tools are tightly scoped and prevent arbitrary shell execution.

## Safety
- No external network calls are made.
- Docker operations are explicitly limited to `fde-lab/customer-app`.
- Cleanup is guaranteed.
