#!/usr/bin/env node

import { checkEnvironment, setupAndRunPython } from '@fde-lab/cli-core';
import chalk from 'chalk';
import path from 'path';

async function main() {
  console.log(chalk.bold.blue('\nFDE Lab'));
  console.log(chalk.blue('────────────────────────────────'));
  console.log(chalk.bold('Environment Inspector\n'));

  // 1. Check dependencies
  const isEnvReady = await checkEnvironment();
  if (!isEnvReady) {
    process.exit(1);
  }

  // 2. Resolve package root
  // The structure is dist/cli.js, so the root is __dirname/..
  const packageRoot = path.join(__dirname, '..');

  // 3. Setup and Run Python
  // The module we want to run is fde_lab.cli.main
  await setupAndRunPython(packageRoot, 'fde_lab.cli.main', ['demo']);
  
  console.log(chalk.blue('────────────────────────────────'));
  console.log('FDE Lab is ready.');
  console.log('\nExample:');
  console.log('"What services are running?"');
  console.log('\nPress Ctrl+C to stop.');
}

main().catch(err => {
  console.error(chalk.red('\nFatal error: ' + err.message));
  process.exit(1);
});
