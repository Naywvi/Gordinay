"""
Utility functions for terminal operations
"""

import subprocess, os, sys, shutil

class TerminalUtils:
    """Utility class for terminal operations"""
    
    @staticmethod
    def open_new_terminal(command: str):
        """Open a new terminal window and run the specified command"""

        try:
            subprocess.Popen([
                "start", "cmd", "/k", command
            ], shell=True)
        except Exception as e:
            raise e
    
    @staticmethod
    def get_python_command():
        """Get the appropriate Python command based on the system configuration"""
        
        try:
            if shutil.which("py"): return "py -3.12"
            
            if shutil.which("python"): return "python"
        
            if shutil.which("python3"): return "python3"
        except Exception as e:
            raise e