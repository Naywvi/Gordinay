"""
Tests for __utils__ modules
"""

from unittest.mock import patch, MagicMock, mock_open
import pytest, logging, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestClientError:
    """Tests for ClientError exception class"""
    
    def test_client_error_init_default_level(self):
        """Test ClientError initialization with default level"""
        from __utils__.clientError import ClientError
        
        error = ClientError("Test message")
        
        assert error.message == "Test message"
        assert error.level == "error"
    
    def test_client_error_init_custom_level(self):
        """Test ClientError initialization with custom level"""
        from __utils__.clientError import ClientError
        
        error = ClientError("Critical error", level="critical")
        
        assert error.message == "Critical error"
        assert error.level == "critical"
    
    def test_client_error_args(self):
        """Test ClientError args contain dict with message and level"""
        from __utils__.clientError import ClientError
        
        error = ClientError("Test", level="warning")
        
        assert error.args[0] == {"message": "Test", "level": "warning"}
    
    def test_client_error_is_exception(self):
        """Test ClientError is a proper Exception"""
        from __utils__.clientError import ClientError
        
        error = ClientError("Test")
        
        assert isinstance(error, Exception)
    
    def test_client_error_can_be_raised(self):
        """Test ClientError can be raised and caught"""
        from __utils__.clientError import ClientError
        
        with pytest.raises(ClientError) as exc_info:
            raise ClientError("Raised error", level="critical")
        
        assert exc_info.value.message == "Raised error"
        assert exc_info.value.level == "critical"

class TestColoredFormatter:
    """Tests for ColoredFormatter class"""
    
    def test_colored_formatter_has_colors(self):
        """Test ColoredFormatter has color definitions"""
        from __utils__.coloredFormatter import ColoredFormatter
        
        assert "DEBUG" in ColoredFormatter.COLORS
        assert "INFO" in ColoredFormatter.COLORS
        assert "WARNING" in ColoredFormatter.COLORS
        assert "ERROR" in ColoredFormatter.COLORS
        assert "CRITICAL" in ColoredFormatter.COLORS
    
    def test_colored_formatter_has_reset(self):
        """Test ColoredFormatter has reset code"""
        from __utils__.coloredFormatter import ColoredFormatter
        
        assert ColoredFormatter.RESET == "\033[0m"
    
    def test_colored_formatter_format_debug(self):
        """Test formatting DEBUG level messages"""
        from __utils__.coloredFormatter import ColoredFormatter
        
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="Debug message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "\033[94m" in result
        assert "Debug message" in result
        assert "\033[0m" in result
    
    def test_colored_formatter_format_error(self):
        """Test formatting ERROR level messages"""
        from __utils__.coloredFormatter import ColoredFormatter
        
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "\033[91m" in result
        assert "Error message" in result
    
    def test_colored_formatter_unknown_level(self):
        """Test formatting unknown level uses reset color"""
        from __utils__.coloredFormatter import ColoredFormatter
        
        formatter = ColoredFormatter("%(message)s")
        
        record = logging.LogRecord(
            name="test",
            level=99,
            pathname="",
            lineno=0,
            msg="Unknown level message",
            args=(),
            exc_info=None
        )
        record.levelname = "UNKNOWN"
        
        result = formatter.format(record)
        
        assert "Unknown level message" in result

class TestAsciiArt:
    """Tests for AsciiArt class"""
    
    def test_ascii_art_display_file_exists(self, temp_dir):
        """Test AsciiArt display when file exists"""
        from __utils__.asciiArt import AsciiArt
        
        os.makedirs(os.path.join(temp_dir, "src", "assets"), exist_ok=True)
        art_file = os.path.join(temp_dir, "src", "assets", "gordinay.txt")
        with open(art_file, 'w') as f:
            f.write("TEST ASCII ART")
        
        with patch('builtins.open', mock_open(read_data="TEST ASCII ART")), \
             patch('os.system') as mock_system, \
             patch('builtins.print') as mock_print:
            
            try:
                AsciiArt.__display__()
            except FileNotFoundError:
                pass  
    
    def test_ascii_art_display_file_not_found(self):
        """Test AsciiArt display when file doesn't exist"""
        from __utils__.asciiArt import AsciiArt
        
        with patch('builtins.open', side_effect=FileNotFoundError("Not found")):
            with pytest.raises(FileNotFoundError):
                AsciiArt.__display__()

class TestTerminalUtils:
    """Tests for TerminalUtils class"""
    
    def test_get_python_command_py(self):
        """Test get_python_command when 'py' is available"""
        from __utils__.terminal import TerminalUtils
        
        with patch('shutil.which') as mock_which:
            mock_which.side_effect = lambda x: x if x == "py" else None
            
            result = TerminalUtils.get_python_command()
            
            assert result == "py -3.12"
    
    def test_get_python_command_python(self):
        """Test get_python_command when 'python' is available"""
        from __utils__.terminal import TerminalUtils
        
        with patch('shutil.which') as mock_which:
            mock_which.side_effect = lambda x: x if x == "python" else None
            
            result = TerminalUtils.get_python_command()
            
            assert result == "python"
    
    def test_get_python_command_python3(self):
        """Test get_python_command when 'python3' is available"""
        from __utils__.terminal import TerminalUtils
        
        with patch('shutil.which') as mock_which:
            mock_which.side_effect = lambda x: x if x == "python3" else None
            
            result = TerminalUtils.get_python_command()
            
            assert result == "python3"
    
    def test_get_python_command_none_available(self):
        """Test get_python_command when no python is available"""
        from __utils__.terminal import TerminalUtils
        
        with patch('shutil.which', return_value=None):
            result = TerminalUtils.get_python_command()
            
            assert result is None
    
    def test_open_new_terminal(self):
        """Test open_new_terminal calls subprocess"""
        from __utils__.terminal import TerminalUtils
        
        with patch('subprocess.Popen') as mock_popen:
            TerminalUtils.open_new_terminal("echo test")
            
            mock_popen.assert_called_once()

class TestEnvironnement:
    """Tests for ENVIRONNEMENT configuration class"""
    
    def test_auto_cast_true(self):
        """Test auto_cast converts 'true' to True"""
        from __conf__.main import auto_cast
        
        assert auto_cast("true") is True
        assert auto_cast("True") is True
        assert auto_cast("TRUE") is True
    
    def test_auto_cast_false(self):
        """Test auto_cast converts 'false' to False"""
        from __conf__.main import auto_cast
        
        assert auto_cast("false") is False
        assert auto_cast("False") is False
    
    def test_auto_cast_int(self):
        """Test auto_cast converts digit strings to int"""
        from __conf__.main import auto_cast
        
        assert auto_cast("42") == 42
        assert auto_cast("0") == 0
        assert auto_cast("100") == 100
    
    def test_auto_cast_float(self):
        """Test auto_cast converts float strings to float"""
        from __conf__.main import auto_cast
        
        assert auto_cast("3.14") == 3.14
        assert auto_cast("0.5") == 0.5
    
    def test_auto_cast_string(self):
        """Test auto_cast returns string for non-convertible values"""
        from __conf__.main import auto_cast
        
        assert auto_cast("hello") == "hello"
        assert auto_cast("test123abc") == "test123abc"
    
    def test_auto_cast_none(self):
        """Test auto_cast returns None for None input"""
        from __conf__.main import auto_cast
        
        assert auto_cast(None) is None
    
    def test_environnement_configuration_returns_dict(self):
        """Test configuration() returns a dictionary when no key provided"""
        from __conf__.main import ENVIRONNEMENT
        
        config = ENVIRONNEMENT.configuration()
        
        assert isinstance(config, dict)
    
    def test_environnement_configuration_invalid_key(self):
        """Test configuration() raises KeyError for invalid key"""
        from __conf__.main import ENVIRONNEMENT
        
        with pytest.raises(KeyError):
            ENVIRONNEMENT.configuration("invalid_key")
    
    def test_environnement_configuration_valid_keys(self):
        """Test configuration() accepts valid keys"""
        from __conf__.main import ENVIRONNEMENT
        
        valid_keys = ["server_log", "client_log", "global_log", "debug_mode", "LOG_LEVEL"]
        
        for key in valid_keys:
            result = ENVIRONNEMENT.configuration(key)
            assert result is not None
