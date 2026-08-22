# FDE Lab — Foundation

**Status:** *Early Stage / Architectural Prototype*

One sentence explaining the customer problem: Customers need to see realistic, working AI engineering proofs-of-concept without friction.

## Try it

```bash
npx @fde-lab/incident-engineer
```

You can also test the system's safety and uncertainty constraints by running a scenario where the incident cannot be proven:
```bash
npx @fde-lab/incident-engineer --scenario inconclusive
```

## What happens

The CLI will:
1. Detect required dependencies (Node, Python, Docker).
2. Create a clean, isolated local Python virtual environment automatically.
3. Install the FDE Lab Python runtime into the environment.
4. Launch the **Incident Engineer** agent to investigate the simulated customer environment.

## Available POCs

- **Incident Engineer** (`@fde-lab/incident-engineer`): Investigates a simulated customer incident (Checkout API HTTP 500s) by correlating logs, metrics, git history, and deployments into a comprehensive incident report.
- **Environment Inspector** (`@fde-lab/environment-inspector`): The foundational demo demonstrating simple environment inspection.

## Demo

Once started, the agent allows you to inspect the simulated local environment. Try asking:
- "What services are currently running?"

## Architecture
FDE Lab uses a thin Node.js/TypeScript CLI bootstrap layer to handle dependency validation and environment setup. The core agent runtime is built in lightweight, modular Python.

```text
npx @fde-lab/<poc>
          │
          ▼
     FDE CLI
          │
          ├── dependency checks
          ├── environment preparation
          └── runtime startup
                    │
                    ▼
              Python runtime
```

## Development

If you want to contribute to the repository or work directly with the Python core:

```bash
# Setup the environment and install dependencies
make install

# Run the Python tests
make test

# Launch the demo agent interactively
make demo

# Build and pack the JS packages for local npx testing
make pack-demo
```

## 7. How the Agent/Skill/Tool Model Works
- **Agent**: The core execution loop (currently rule-based for the vertical slice, ready for LLM injection).
- **Tools**: Classes implementing a standard interface (e.g., `GetServicesTool`) to interact with the environment.
- **Memory**: Tracks conversation and tool history.
- **Skills**: (Upcoming) Reusable orchestrations of tools.

## 8. How Future POCs Will Plug Into the Foundation
Future Proof of Concepts (POCs) will reside in the `fde_lab/pocs/` directory and will import the base `Agent`, `Tool`, and observability modules, defining only their specific tools and instructions, preventing boilerplate duplication.

## 9. Open-Source Philosophy
Everything required for the default local demo must be open source and runnable locally. Prefer local infrastructure (e.g., PostgreSQL, Ollama) over mandatory paid APIs.

## 10. Roadmap
- [x] Foundation vertical slice (CLI, Runtime, Tool, Demo)
- [ ] Connect local LLM (Ollama) to the Agent loop
- [ ] Implement robust Tool schema validation (Pydantic)
- [ ] Build POC 1: Incident Engineer
- [ ] Build POC 2: Support Engineer
