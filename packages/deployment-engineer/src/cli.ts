#!/usr/bin/env node

import { checkEnvironment, setupAndRunPython } from '@fde-lab/cli-core';
import chalk from 'chalk';
import path from 'path';
import { Command } from 'commander';

const program = new Command();

program
  .name('fde-deployment-engineer')
  .description('FDE Lab - Deployment Engineer')
  .option('-s, --scenario <scenario>', 'Scenario to run: normal or broken-app', 'normal')
  .parse(process.argv);

const options = program.opts();

async function main() {
  // 1. Check dependencies
  const isEnvReady = await checkEnvironment();
  if (!isEnvReady) {
    process.exit(1);
  }

  // 2. Resolve package root
  const packageRoot = path.join(__dirname, '..');

  // 3. Setup and Run Python
  // We want to run fde_lab.pocs.deployment_engineer.cli with the given scenario
  await setupAndRunPython(packageRoot, 'fde_lab.pocs.deployment_engineer.cli', ['deploy', '--scenario', options.scenario]);
}

main().catch(err => {
  console.error(chalk.red('\nFatal error: ' + err.message));
  process.exit(1);
});
