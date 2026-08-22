# @fde-lab/deployment-engineer

> POC #3 of the FDE Lab project: An AI-powered deployment configuration solution.

## Mission

**FDE Lab** is a collection of production-style, customer-facing AI engineering solutions designed to demonstrate the skills of a Forward Deployed Engineer (FDE). 

The core philosophy is:
> **One command → install → run → demo.**

This specific package, **Deployment Engineer**, demonstrates understanding customer code, packaging it for production, and safely deploying and verifying it using Docker.

## Try it

You can run the Deployment Engineer directly via NPX without needing to clone the repository or manually install dependencies.

### Standard Scenario (Normal App)
```bash
npx @fde-lab/deployment-engineer
```

### Broken App Scenario
To demonstrate how the system handles deployment failures safely and performs cleanup, you can run the broken app scenario:
```bash
npx @fde-lab/deployment-engineer --scenario broken-app
```

## Learn More

Check out the <a href="https://github.com/smg99/fde-lab" target="_blank">FDE Lab GitHub Repository</a> for more information and to view the other FDE Lab solutions.
