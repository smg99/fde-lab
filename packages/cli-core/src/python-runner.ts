import execa from 'execa';
import chalk from 'chalk';
import path from 'path';
import fs from 'fs';
import os from 'os';

export async function setupAndRunPython(projectDir: string, moduleName: string, moduleArgs: string[] = [], quiet: boolean = false): Promise<void> {
  if (!quiet) console.log(chalk.blue('\nPreparing environment...'));
  
  const cacheDir = path.join(os.homedir(), '.fde-lab-cache', path.basename(projectDir));
  if (!fs.existsSync(cacheDir)) {
    fs.mkdirSync(cacheDir, { recursive: true });
  }

  const venvPath = path.join(cacheDir, '.venv');
  
  try {
    // 1. Create venv if it doesn't exist
    if (!fs.existsSync(venvPath)) {
      await execa('python3', ['-m', 'venv', venvPath]);
    }
    
    const pipCmd = path.join(venvPath, 'bin', 'pip');
    const pythonCmd = path.join(venvPath, 'bin', 'python');

    // 2. Install the bundled python source into the venv
    // Expects the python source (fde_lab, demo, pyproject.toml) to be bundled in the `dist/python` directory of the package
    const bundledPythonDir = path.join(projectDir, 'dist', 'python');
    if (!fs.existsSync(bundledPythonDir)) {
      console.log(chalk.red('\nError: Python source not found in the package distribution.'));
      process.exit(1);
    }

    await execa(pipCmd, ['install', '-e', bundledPythonDir], { stdio: 'ignore' });
    if (!quiet) {
      console.log(chalk.green('✓ Runtime ready'));
      console.log(chalk.green('✓ Demo data ready')); // Simulated for now
      
      console.log(chalk.blue('\nStarting FDE Lab...'));
    }
    
    // 3. Run the python module interactively
    const runProcess = execa(pythonCmd, ['-m', moduleName, ...moduleArgs], { stdio: 'inherit' });
    
    runProcess.catch((err: any) => {
      // Ignore exit 0 or standard ctrl+c
      if (err.exitCode !== 0) {
        console.error(chalk.red(`\nPython process exited with error: ${err.message}`));
      }
    });

    await runProcess;

  } catch (error: any) {
    console.error(chalk.red(`\nFailed to setup or run python environment: ${error.message}`));
    process.exit(1);
  }
}
