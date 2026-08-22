#!/usr/bin/env node

import { checkEnvironment, setupAndRunPython } from '@fde-lab/cli-core';
import chalk from 'chalk';
import path from 'path';
import { Command } from 'commander';

const program = new Command();

program
  .name('fde-performance-engineer')
  .description('FDE Lab - Performance Engineer')
  .option('-s, --scenario <scenario>', 'Scenario to run', 'normal')
  .option('--json', 'Output machine-readable JSON')
  .option('--manifest', 'Output capability manifest JSON')
  .parse(process.argv);

const options = program.opts();

async function main() {
  const machineMode = options.json || options.manifest;
  
  // 1. Check dependencies
  const isEnvReady = await checkEnvironment(machineMode);
  if (!isEnvReady) {
    process.exit(1);
  }

  // 2. Resolve package root
  const packageRoot = path.join(__dirname, '..');

  // 3. Setup and Run Python
  const pyArgs = ['investigate-performance', '--scenario', options.scenario];
  if (options.json) pyArgs.push('--json');
  if (options.manifest) pyArgs.push('--manifest');
  
  await setupAndRunPython(packageRoot, 'fde_lab.pocs.performance_engineer.cli', pyArgs, machineMode);
}

main().catch(err => {
  if (!program.opts().json && !program.opts().manifest) {
    console.error(chalk.red('\nFatal error: ' + err.message));
  }
  process.exit(1);
});
