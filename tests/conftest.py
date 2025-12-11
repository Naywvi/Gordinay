"""
Pytest configuration and shared fixtures for Gordinay tests
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
import pytest, sys, os, tempfile, shutil, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock modules BEFORE any import
mock_cv2 = MagicMock()
mock_cv2.VideoCapture = MagicMock()
mock_cv2.imwrite = MagicMock(return_value=True)
mock_cv2.imencode = MagicMock(return_value=(True, b'fake_image_data'))
mock_cv2.cvtColor = MagicMock(return_value=MagicMock())
mock_cv2.GaussianBlur = MagicMock(return_value=MagicMock())
mock_cv2.absdiff = MagicMock(return_value=MagicMock())
mock_cv2.threshold = MagicMock(return_value=(None, MagicMock()))
mock_cv2.dilate = MagicMock(return_value=MagicMock())
mock_cv2.countNonZero = MagicMock(return_value=100)
mock_cv2.resize = MagicMock(return_value=MagicMock())
mock_cv2.IMWRITE_JPEG_QUALITY = 1
mock_cv2.COLOR_BGR2GRAY = 6
mock_cv2.THRESH_BINARY = 0
mock_cv2.CAP_PROP_FRAME_WIDTH = 3
mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
mock_cv2.CAP_PROP_FPS = 5
sys.modules['cv2'] = mock_cv2

mock_pil = MagicMock()
mock_pil_image = MagicMock()
mock_pil_image.width = 1920
mock_pil_image.height = 1080
mock_pil_image.resize.return_value = mock_pil_image
mock_pil.Image = MagicMock()
mock_pil.ImageGrab = MagicMock()
mock_pil.ImageGrab.grab.return_value = mock_pil_image
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = mock_pil.Image
sys.modules['PIL.ImageGrab'] = mock_pil.ImageGrab

mock_tabulate = MagicMock()
mock_tabulate.tabulate = MagicMock(return_value="mocked table")
sys.modules['tabulate'] = mock_tabulate

@pytest.fixture(autouse=True)
def mock_os_exit():
    """Prevent os._exit from killing pytest"""
    with patch('os._exit'):
        yield
        
@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("server_log", "true")
    monkeypatch.setenv("client_log", "true")
    monkeypatch.setenv("global_log", "true")
    monkeypatch.setenv("debug_mode", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    import time
    time.sleep(0.1)
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def temp_log_dir(temp_dir):
    """Create a temporary log directory"""
    log_dir = os.path.join(temp_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


@pytest.fixture
def mock_socket():
    """Mock socket for network tests"""
    with patch('socket.socket') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        mock_instance.connect.return_value = None
        mock_instance.send.return_value = 100
        mock_instance.recv.return_value = b'{"type": "test"}\n'
        mock_instance.getsockname.return_value = ('127.0.0.1', 12345)
        yield mock_instance


@pytest.fixture
def mock_ssl_context():
    """Mock SSL context"""
    with patch('ssl.create_default_context') as mock:
        mock_context = MagicMock()
        mock.return_value = mock_context
        mock_context.wrap_socket.return_value = MagicMock()
        yield mock_context


@pytest.fixture
def mock_sounddevice():
    """Mock sounddevice for audio tests"""
    with patch.dict('sys.modules', {'sounddevice': MagicMock()}):
        import sounddevice as sd
        sd.rec = MagicMock(return_value=MagicMock())
        sd.wait = MagicMock()
        sd.InputStream = MagicMock()
        sd.query_devices = MagicMock(return_value=[
            {'name': 'Test Mic', 'max_input_channels': 2, 'default_samplerate': 44100}
        ])
        yield sd


@pytest.fixture
def mock_pynput():
    """Mock pynput for keylogger tests"""
    with patch.dict('sys.modules', {'pynput': MagicMock(), 'pynput.keyboard': MagicMock()}):
        from pynput import keyboard
        keyboard.Listener = MagicMock()
        keyboard.Key = MagicMock()
        keyboard.Key.space = MagicMock()
        keyboard.Key.enter = MagicMock()
        keyboard.Key.backspace = MagicMock()
        keyboard.Key.tab = MagicMock()
        keyboard.Key.esc = MagicMock()
        yield keyboard


@pytest.fixture
def mock_ctypes():
    """Mock ctypes for Windows API calls"""
    with patch('ctypes.windll') as mock:
        mock.user32.GetForegroundWindow.return_value = 12345
        mock.user32.GetWindowTextLengthW.return_value = 10
        mock.user32.GetWindowTextW.return_value = 0
        mock.shell32.IsUserAnAdmin.return_value = 0
        yield mock


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for shell commands"""
    with patch('subprocess.run') as mock_run, \
         patch('subprocess.Popen') as mock_popen:
        
        mock_result = MagicMock()
        mock_result.stdout = "test output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        mock_process = MagicMock()
        mock_process.stdout.read.return_value = b"test output"
        mock_process.stderr.read.return_value = b""
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        yield {'run': mock_run, 'popen': mock_popen}


@pytest.fixture
def mock_requests():
    """Mock requests for network info"""
    with patch('requests.get') as mock:
        mock_response = MagicMock()
        mock_response.json.return_value = {'ip': '8.8.8.8'}
        mock_response.text = '8.8.8.8'
        mock.return_value = mock_response
        yield mock

@pytest.fixture
def mock_client_config():
    """Create a mock ClientAppConfig"""
    config = MagicMock()
    config.server_host = "127.0.0.1"
    config.server_port = 4444
    config.use_ssl = False
    config.reconnect_delay = 1
    config.keylogger_enabled = False
    config.keylogger_interval = 5
    config.webcam_snapshot_enabled = False
    config.webcam_movement_enabled = False
    config.webcam_interval = 30
    config.webcam_stream_enabled = False
    config.webcam_stream_motion_only = False
    config.webcam_stream_fps = 10
    config.webcam_stream_resolution = (640, 480)
    config.webcam_stream_quality = 60
    config.screenshot_enabled = False
    config.screenshot_interval = 60
    config.screenshot_quality = 85
    config.screenshot_change_detection = False
    config.network_info_enabled = False
    config.network_info_track_changes = True
    config.network_info_interval = 300
    config.audio_enabled = False
    config.audio_duration = 10
    config.audio_interval = 60
    
    config.get_config.return_value = {
        'keylogger_interval': 5,
        'webcam_interval': 30,
        'screenshot_interval': 60,
        'features': {
            'keylogger': False,
            'webcam_snapshot': False,
            'screenshot': False,
        }
    }
    config.set_config.return_value = True
    config.load_profile.return_value = True
    
    return config


@pytest.fixture
def sample_keylog_data():
    """Sample keylog data for testing"""
    return [
        {
            "timestamp": "2024-01-01T12:00:00",
            "text": "test input",
            "window": "Test Window",
            "length": 10
        }
    ]


@pytest.fixture
def sample_network_info():
    """Sample network info for testing"""
    return {
        "timestamp": "2024-01-01T12:00:00",
        "hostname": "test-pc",
        "local_ip": "192.168.1.100",
        "public_ip": "8.8.8.8",
        "mac_address": "00:11:22:33:44:55",
        "default_gateway": "192.168.1.1",
        "dns_servers": ["8.8.8.8", "8.8.4.4"]
    }

@pytest.fixture
def mock_server_socket():
    """Mock server socket"""
    with patch('socket.socket') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        mock_instance.bind.return_value = None
        mock_instance.listen.return_value = None
        mock_instance.accept.return_value = (MagicMock(), ('127.0.0.1', 12345))
        yield mock_instance

@pytest.fixture
def sample_file(temp_dir):
    """Create a sample file for file manager tests"""
    file_path = os.path.join(temp_dir, "test_file.txt")
    with open(file_path, 'w') as f:
        f.write("Test content for file manager")
    return file_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file"""
    file_path = os.path.join(temp_dir, "test.json")
    data = {"key": "value", "number": 42}
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path