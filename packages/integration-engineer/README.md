# @fde-lab/integration-engineer

> POC #2 of the FDE Lab project: An AI-powered integration configuration solution.

## Mission

**FDE Lab** is a collection of production-style, customer-facing AI engineering solutions designed to demonstrate the skills of a Forward Deployed Engineer (FDE). 

The core philosophy is:
> **One command → install → run → demo.**

This specific package, **Integration Engineer**, demonstrates understanding data schemas and safely mapping/transforming records between systems.

## Try it

You can run the Integration Engineer directly via NPX without needing to clone the repository or manually install dependencies.

### Standard Scenario (Normal Data)
```bash
npx @fde-lab/integration-engineer
```

### Invalid Data Scenario
To demonstrate how the system rejects invalid or unsupported data, you can run the invalid-data scenario:
```bash
npx @fde-lab/integration-engineer --scenario invalid-data
```

### AI-Native Mode

This tool is AI-Native. Agents can interface with it programmatically using:
- `--manifest`: Returns a JSON capability manifest.
- `--json`: Runs the workflow and returns a standard JSON result envelope.

## Learn More

Check out the <a href="https://github.com/smg99/fde-lab" target="_blank">FDE Lab GitHub Repository</a> for more information and to view the other FDE Lab solutions.
