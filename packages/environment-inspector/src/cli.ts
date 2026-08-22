#!/usr/bin/env node

import { checkEnvironment, setupAndRunPython } from '@fde-lab/cli-core';
import chalk from 'chalk';
import path from 'path';
import { Command } from 'commander';

const program = new Command();

program
  .name('fde-environment-inspector')
  .description('FDE Lab - Environment Inspector')
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
  const pyArgs = ['demo'];
  if (options.manifest) {
    pyArgs.push('--manifest');
  } else if (options.json) {
    pyArgs.push('--json');
  }

  await setupAndRunPython(packageRoot, "fde_lab.cli.main", pyArgs, machineMode);
  
  if (!machineMode) {
    console.log(chalk.blue('────────────────────────────────'));
    console.log('FDE Lab is ready.');
    console.log('\nExample:');
    console.log('"What services are running?"');
    console.log('\nPress Ctrl+C to stop.');
  }
}

main().catch(err => {
  if (!program.opts().json && !program.opts().manifest) {
    console.error(chalk.red('\nFatal error: ' + err.message));
  } else {
    console.error(`Fatal error: ${err.message}`);
  }
  process.exit(1);
});
