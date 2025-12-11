"""
Tests for FileManager feature
"""

from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest, sys, os, base64, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestFileManager:
    """Tests for FileManager class"""
    
    def test_file_manager_init(self):
        """Test FileManager initialization"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager()
        
        assert manager.max_search_results == 100
    
    def test_file_manager_init_custom_max_results(self):
        """Test FileManager with custom max results"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager(max_search_results=50)
        
        assert manager.max_search_results == 50
    
    def test_download_success(self, temp_dir):
        """Test successful file download"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        test_file = os.path.join(temp_dir, "test.txt")
        test_content = b"Hello, World!"
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        manager = FileManager()
        result = manager.download(test_file)
        
        assert result['success'] is True
        assert result['filename'] == "test.txt"
        assert result['size'] == len(test_content)
        assert 'data' in result
        
        # base64
        decoded = base64.b64decode(result['data'])
        assert decoded == test_content
    
    def test_download_file_not_found(self):
        """Test download with non-existent file"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager()
        result = manager.download("/nonexistent/path/file.txt")
        
        assert result['success'] is False
        assert 'error' in result
        assert 'not found' in result['error'].lower()
    
    def test_download_directory(self, temp_dir):
        """Test download fails for directory"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager()
        result = manager.download(temp_dir)
        
        assert result['success'] is False
        assert 'not a file' in result['error'].lower()
    
    def test_download_large_file_rejected(self, temp_dir):
        """Test download rejects files over 50MB"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        test_file = os.path.join(temp_dir, "large.bin")
        with open(test_file, 'wb') as f:
            f.write(b"x")
        
        manager = FileManager()
        
        os.stat
        
        class FakeStat:
            st_size = 60 * 1024 * 1024  # 60MB
            st_mode = 0o100644
            st_mtime = 0
        
        with patch('pathlib.Path.stat', return_value=FakeStat()):
            result = manager.download(test_file)
        
        assert result['success'] is False
        assert 'too large' in result['error'].lower() or 'large' in result['error'].lower()
    
    def test_download_has_timestamp(self, temp_dir):
        """Test download result includes timestamp"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        manager = FileManager()
        result = manager.download(test_file)
        
        assert 'timestamp' in result
    
    def test_upload_success(self, temp_dir):
        """Test successful file upload"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        target_file = os.path.join(temp_dir, "uploaded.txt")
        content = b"Uploaded content"
        encoded = base64.b64encode(content).decode('utf-8')
        
        manager = FileManager()
        result = manager.upload(target_file, encoded)
        
        assert result['success'] is True
        assert result['size'] == len(content)
        
        assert os.path.exists(target_file)
        with open(target_file, 'rb') as f:
            assert f.read() == content
    
    def test_upload_creates_directory(self, temp_dir):
        """Test upload creates parent directories"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        target_file = os.path.join(temp_dir, "new_dir", "subdir", "file.txt")
        content = b"test"
        encoded = base64.b64encode(content).decode('utf-8')
        
        manager = FileManager()
        result = manager.upload(target_file, encoded)
        
        assert result['success'] is True
        assert os.path.exists(target_file)
    
    def test_upload_invalid_base64(self, temp_dir):
        """Test upload with invalid base64 data"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        target_file = os.path.join(temp_dir, "file.txt")
        
        manager = FileManager()
        result = manager.upload(target_file, "not-valid-base64!!!")
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_upload_has_timestamp(self, temp_dir):
        """Test upload result includes timestamp"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        target_file = os.path.join(temp_dir, "file.txt")
        encoded = base64.b64encode(b"test").decode('utf-8')
        
        manager = FileManager()
        result = manager.upload(target_file, encoded)
        
        assert 'timestamp' in result
    
    def test_search_finds_files(self, temp_dir):
        """Test search finds matching files"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        for name in ["doc1.txt", "doc2.txt", "image.png"]:
            with open(os.path.join(temp_dir, name), 'w') as f:
                f.write("test")
        
        manager = FileManager()
        result = manager.search("*.txt", search_dirs=[Path(temp_dir)])
        
        assert result['success'] is True
        assert result['count'] == 2
        assert len(result['results']) == 2
    
    def test_search_returns_file_info(self, temp_dir):
        """Test search returns file information"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("content")
        
        manager = FileManager()
        result = manager.search("test.txt", search_dirs=[Path(temp_dir)])
        
        assert result['success'] is True
        assert len(result['results']) == 1
        
        file_info = result['results'][0]
        assert 'path' in file_info
        assert 'name' in file_info
        assert 'size' in file_info
        assert 'modified' in file_info
    
    def test_search_limits_results(self, temp_dir):
        """Test search respects max_search_results"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        for i in range(20):
            with open(os.path.join(temp_dir, f"file{i}.txt"), 'w') as f:
                f.write("test")
        
        manager = FileManager(max_search_results=5)
        result = manager.search("*.txt", search_dirs=[Path(temp_dir)])
        
        assert result['count'] == 5
        assert result['limited'] is True
    
    def test_search_no_results(self, temp_dir):
        """Test search with no matching files"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager()
        result = manager.search("*.xyz", search_dirs=[Path(temp_dir)])
        
        assert result['success'] is True
        assert result['count'] == 0
        assert len(result['results']) == 0
    
    def test_search_includes_pattern(self, temp_dir):
        """Test search result includes search pattern"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager()
        result = manager.search("*.pdf", search_dirs=[Path(temp_dir)])
        
        assert result['pattern'] == "*.pdf"
    
    def test_list_directory_success(self, temp_dir):
        """Test successful directory listing"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        with open(os.path.join(temp_dir, "file.txt"), 'w') as f:
            f.write("test")
        os.makedirs(os.path.join(temp_dir, "subdir"))
        
        manager = FileManager()
        result = manager.list_directory(temp_dir)
        
        assert result['success'] is True
        assert result['count'] == 2
        assert 'contents' in result
    
    def test_list_directory_includes_types(self, temp_dir):
        """Test list_directory includes file types"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        with open(os.path.join(temp_dir, "file.txt"), 'w') as f:
            f.write("test")
        os.makedirs(os.path.join(temp_dir, "subdir"))
        
        manager = FileManager()
        result = manager.list_directory(temp_dir)
        
        types = [item['type'] for item in result['contents']]
        assert 'file' in types
        assert 'dir' in types
    
    def test_list_directory_not_found(self):
        """Test list_directory with non-existent directory"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        manager = FileManager()
        result = manager.list_directory("/nonexistent/path")
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()
    
    def test_list_directory_on_file(self, temp_dir):
        """Test list_directory fails on file path"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        test_file = os.path.join(temp_dir, "file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        manager = FileManager()
        result = manager.list_directory(test_file)
        
        assert result['success'] is False
        assert 'not a directory' in result['error'].lower()
    
    def test_list_directory_includes_metadata(self, temp_dir):
        """Test list_directory includes file metadata"""
        from __app__.client_app.features.fileManager.main import FileManager
        
        test_file = os.path.join(temp_dir, "file.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        manager = FileManager()
        result = manager.list_directory(temp_dir)
        
        file_item = result['contents'][0]
        assert 'name' in file_item
        assert 'path' in file_item
        assert 'type' in file_item
        assert 'size' in file_item
        assert 'modified' in file_item
