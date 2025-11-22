"""
Shell Executor - Execute shell commands
For educational purposes only - For Educational Use Only
"""

from datetime import datetime
import subprocess

class ShellExecutor:
    """Execute shell commands on the system"""
    
    def __init__(self, timeout=30) -> None:
        """
        Initialize shell executor
        Args:
            timeout: Command execution timeout in seconds
        """

        try:
            self.timeout = timeout
        except Exception as e:
            raise Exception(f"ShellExecutor initialization error in __init__ function: {e}")    
    
    def execute(self, command) -> dict:
        """
        Execute a shell command
        Args:
            command: Command string to execute
        Returns:
            dict: Result containing stdout, stderr, return_code
        """

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return {
                'success': True,
                'command': command,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode,
                'timestamp': datetime.now().isoformat()
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'command': command,
                'error': f'Command timeout ({self.timeout}s)',
                'return_code': -1,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'command': command,
                'error': str(e),
                'return_code': -1,
                'timestamp': datetime.now().isoformat()
            }
    
    def execute_async(self, command) -> subprocess.Popen:
        """
        Execute command without waiting (async)
        Args:
            command: Command string to execute
        Returns:
            subprocess.Popen: Process handle
        """

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return process
        
        except Exception as e:
            raise Exception(f"ShellExecutor error in execute_async function: {e}")
            return None