import { checkCommand } from '../src/checks';

// Mock execa to avoid actually running system commands in the unit test
jest.mock('execa', () => jest.fn((cmd, args) => {
  if (cmd === 'node' && args[0] === '-v') {
    return Promise.resolve({ stdout: 'v20.0.0' });
  }
  if (cmd === 'missing-tool') {
    return Promise.reject(new Error('command not found'));
  }
  return Promise.resolve({ stdout: '' });
}));

describe('checks', () => {
  it('should pass for a successful command', async () => {
    const result = await checkCommand('node', ['-v'], 'Node.js', 'Please install Node.js');
    expect(result.passed).toBe(true);
  });

  it('should fail and return a message for a missing command', async () => {
    const result = await checkCommand('missing-tool', ['-v'], 'Missing', 'Please install Missing');
    expect(result.passed).toBe(false);
    expect(result.message).toContain('Please install Missing');
  });
});
