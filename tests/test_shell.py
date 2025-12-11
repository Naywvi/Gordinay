"""
Tests for ShellExecutor feature
"""

from unittest.mock import patch, MagicMock
import pytest, sys, os, subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestShellExecutor:
    """Tests for ShellExecutor class"""
    
    def test_shell_executor_init_default(self):
        """Test ShellExecutor initialization with default timeout"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        executor = ShellExecutor()
        
        assert executor.timeout == 30
    
    def test_shell_executor_init_custom_timeout(self):
        """Test ShellExecutor initialization with custom timeout"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        executor = ShellExecutor(timeout=60)
        
        assert executor.timeout == 60
    
    def test_execute_success(self):
        """Test successful command execution"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = "Hello World"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            executor = ShellExecutor()
            result = executor.execute("echo Hello World")
            
            assert result['success'] is True
            assert result['command'] == "echo Hello World"
            assert result['output'] == "Hello World"
            assert result['return_code'] == 0
    
    def test_execute_with_error(self):
        """Test command execution with error output"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_result.stderr = "Command not found"
            mock_result.returncode = 1
            mock_run.return_value = mock_result
            
            executor = ShellExecutor()
            result = executor.execute("nonexistent_command")
            
            assert result['success'] is True
            assert result['error'] == "Command not found"
            assert result['return_code'] == 1
    
    def test_execute_timeout(self):
        """Test command execution timeout"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=30)
            
            executor = ShellExecutor(timeout=30)
            result = executor.execute("sleep 60")
            
            assert result['success'] is False
            assert 'timeout' in result['error'].lower()
            assert result['return_code'] == -1
    
    def test_execute_exception(self):
        """Test command execution with exception"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Unexpected error")
            
            executor = ShellExecutor()
            result = executor.execute("test_command")
            
            assert result['success'] is False
            assert 'Unexpected error' in result['error']
            assert result['return_code'] == -1
    
    def test_execute_includes_timestamp(self):
        """Test execute result includes timestamp"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = "output"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            executor = ShellExecutor()
            result = executor.execute("test")
            
            assert 'timestamp' in result
    
    def test_execute_uses_shell(self):
        """Test execute uses shell=True"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            executor = ShellExecutor()
            executor.execute("test")
            
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs['shell'] is True
    
    def test_execute_uses_timeout(self):
        """Test execute passes timeout to subprocess"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            executor = ShellExecutor(timeout=45)
            executor.execute("test")
            
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs['timeout'] == 45
    
    def test_execute_async_returns_popen(self):
        """Test execute_async returns Popen object"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process
            
            executor = ShellExecutor()
            result = executor.execute_async("test_command")
            
            assert result == mock_process
    
    def test_execute_async_uses_pipes(self):
        """Test execute_async sets up pipes"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process
            
            executor = ShellExecutor()
            executor.execute_async("test")
            
            call_kwargs = mock_popen.call_args[1]
            assert call_kwargs['stdout'] == subprocess.PIPE
            assert call_kwargs['stderr'] == subprocess.PIPE
    
    def test_execute_async_exception(self):
        """Test execute_async handles exceptions"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        with patch('subprocess.Popen') as mock_popen:
            mock_popen.side_effect = Exception("Popen failed")
            
            executor = ShellExecutor()
            
            with pytest.raises(Exception) as exc_info:
                executor.execute_async("test")
            
            assert "Popen failed" in str(exc_info.value)
    
    @pytest.mark.skipif(os.name != 'nt', reason="Windows only test")
    def test_execute_real_windows_command(self):
        """Test real Windows command execution"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        executor = ShellExecutor()
        result = executor.execute("echo test")
        
        assert result['success'] is True
        assert 'test' in result['output']
    
    @pytest.mark.skipif(os.name == 'nt', reason="Unix only test")
    def test_execute_real_unix_command(self):
        """Test real Unix command execution"""
        from __app__.client_app.features.shell.main import ShellExecutor
        
        executor = ShellExecutor()
        result = executor.execute("echo test")
        
        assert result['success'] is True
        assert 'test' in result['output']
