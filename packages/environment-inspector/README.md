# @fde-lab/environment-inspector

> Foundational Proof-of-Concept (POC #0) for the FDE Lab project.

## Mission

**FDE Lab** is a collection of production-style, customer-facing AI engineering solutions designed to demonstrate the skills of a Forward Deployed Engineer (FDE). 

The core philosophy is:
> **One command → install → run → demo.**

This specific package, **Environment Inspector**, is the foundational test-bed for the FDE Lab architecture. It verifies that the AI agent, memory layer, tools, and CLI bootstrap process are functioning correctly.

## Try it

You can run the Environment Inspector directly via NPX without needing to clone the repository or manually install dependencies.

```bash
npx @fde-lab/environment-inspector
```

*(Note: Requires Node.js and Python 3 to be installed on your system).*

## What it does

When executed, the FDE Lab CLI will:
1. Verify your local environment dependencies.
2. Automatically create a clean, isolated Python virtual environment (`~/.fde-lab-cache/environment-inspector/.venv`).
3. Launch the core Agent loop.
4. Allow you to interact with the environment through standard tools (e.g. asking "What services are running?").

## Learn More

Check out the [FDE Lab GitHub Repository](https://github.com/sumitg/fde-lab) for more information and to view the other FDE Lab solutions.
