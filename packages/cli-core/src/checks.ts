import execa from 'execa';
import chalk from 'chalk';

export interface CheckResult {
  passed: boolean;
  message?: string;
}

export async function checkCommand(command: string, args: string[], name: string, installInstructions: string, quiet: boolean = false): Promise<CheckResult> {
  try {
    await execa(command, args);
    if (!quiet) console.log(chalk.green(`✓ ${name}`));
    return { passed: true };
  } catch (error) {
    if (!quiet) console.log(chalk.red(`✗ ${name}`));
    return {
      passed: false,
      message: `\n${name} is required for this demo.\n\n${installInstructions}\n`
    };
  }
}

export async function checkEnvironment(quiet: boolean = false): Promise<boolean> {
  if (!quiet) console.log(chalk.blue('\nChecking environment...'));
  
  const nodeCheck = await checkCommand('node', ['-v'], 'Node.js', 'Please install Node.js from https://nodejs.org/', quiet);
  const pythonCheck = await checkCommand('python3', ['--version'], 'Python 3', 'Please install Python 3 from https://www.python.org/downloads/', quiet);
  const dockerCheck = await checkCommand('docker', ['--version'], 'Docker', 'Please install Docker Desktop from https://www.docker.com/products/docker-desktop/', quiet);
  
  const results = [nodeCheck, pythonCheck, dockerCheck];
  const failed = results.filter(r => !r.passed);
  
  if (failed.length > 0) {
    const errorMsg = failed.map(f => f.message).join('');
    if (quiet) {
      console.log(JSON.stringify({
        schema_version: "0.1",
        status: "failed",
        errors: [{
          code: "ENV_PROBLEM",
          message: errorMsg,
          stage: "environment_check",
          recoverable: true,
          suggested_action: "Install missing dependencies."
        }]
      }));
      process.exit(3); // Environment problem
    } else {
      failed.forEach(f => console.log(chalk.yellow(f.message)));
    }
    return false;
  }
  
  return true;
}
