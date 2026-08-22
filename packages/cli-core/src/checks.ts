import execa from 'execa';
import chalk from 'chalk';

export interface CheckResult {
  passed: boolean;
  message?: string;
}

export async function checkCommand(command: string, args: string[], name: string, installInstructions: string): Promise<CheckResult> {
  try {
    await execa(command, args);
    console.log(chalk.green(`✓ ${name}`));
    return { passed: true };
  } catch (error) {
    console.log(chalk.red(`✗ ${name}`));
    return {
      passed: false,
      message: `\n${name} is required for this demo.\n\n${installInstructions}\n`
    };
  }
}

export async function checkEnvironment(): Promise<boolean> {
  console.log(chalk.blue('\nChecking environment...'));
  
  const nodeCheck = await checkCommand('node', ['-v'], 'Node.js', 'Please install Node.js from https://nodejs.org/');
  const pythonCheck = await checkCommand('python3', ['--version'], 'Python 3', 'Please install Python 3 from https://www.python.org/downloads/');
  const dockerCheck = await checkCommand('docker', ['--version'], 'Docker', 'Please install Docker Desktop from https://www.docker.com/products/docker-desktop/');
  
  const results = [nodeCheck, pythonCheck, dockerCheck];
  const failed = results.filter(r => !r.passed);
  
  if (failed.length > 0) {
    failed.forEach(f => console.log(chalk.yellow(f.message)));
    return false;
  }
  
  return true;
}
