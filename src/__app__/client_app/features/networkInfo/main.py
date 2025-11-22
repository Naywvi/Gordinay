"""
Network information collection feature with change detection and logging functionality. - For Educational Use Only
"""

from datetime import datetime
from pathlib import Path
import threading, subprocess, re, time, requests, socket, json

class NetworkInfo:
    '''Network information collection class - For educational use only'''
    
    def __init__(self, output_file="network_info.json", interval=300, track_changes=True) -> None:
        """
        Initialize the network info collector
        Args:
            output_file: Path to JSON output file
            interval: Seconds between network checks
            track_changes: Only log when network configuration changes
        """
        try:
            self.output_file = Path(output_file)
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.interval = interval
            self.track_changes = track_changes
            self.running = False
            self.monitor_thread = None
            self.previous_config = None
            
            # Create file if it doesn't exist
            if not self.output_file.exists():
                self.output_file.write_text("[]", encoding="utf-8")
        except Exception as e:
            raise Exception(f"NetworkInfo Initialization Error in __init__ function - {e}")
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""

        try:
            try:
                # Create a socket connection to determine local IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                return local_ip
            except:
                return "Unknown"
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _get_local_ip function - {e}")
    
    def _get_public_ip(self) -> str:
        """Get public IP address"""

        try:
            try:
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                return response.json()['ip']
            except:
                try:
                    # Fallback API
                    response = requests.get('https://ifconfig.me/ip', timeout=5)
                    return response.text.strip()
                except:
                    return "Unknown"
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _get_public_ip function - {e}")
    
    def _get_hostname(self) -> str:
        """Get computer hostname"""

        try:
            try:
                return socket.gethostname()
            except:
                return "Unknown"
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _get_hostname function - {e}")
    
    def _get_mac_address(self) -> str:
        """Get MAC address of primary network adapter"""

        try:
            try:
                import uuid
                mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
                return mac
            except:
                return "Unknown"
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _get_mac_address function - {e}")
    
    def _get_ipconfig_details(self) -> str:
        """Get detailed ipconfig information (Windows)"""

        try:
            try:
                result = subprocess.run(['ipconfig', '/all'], 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=10)
                return result.stdout
            except:
                return "Unable to retrieve ipconfig details"
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _get_ipconfig_details function - {e}")
    
    def _get_network_interfaces(self) -> list:
        """Get all network interfaces with details"""

        try:
            interfaces = []
            try:
                import psutil
                
                # Get network interface addresses
                net_if_addrs = psutil.net_if_addrs()
                net_if_stats = psutil.net_if_stats()
                
                for interface_name, addresses in net_if_addrs.items():
                    interface_info = {
                        "name": interface_name,
                        "is_up": net_if_stats[interface_name].isup if interface_name in net_if_stats else False,
                        "addresses": []
                    }
                    
                    for addr in addresses:
                        addr_info = {
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast
                        }
                        interface_info["addresses"].append(addr_info)
                    
                    interfaces.append(interface_info)
                
                return interfaces
            except ImportError:
                # If psutil not available, return basic info
                return [{"info": "Install psutil for detailed interface information"}]
            except Exception as e:
                return [{"error": str(e)}]
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _get_network_interfaces function - {e}")
    
    def _get_dns_servers(self) -> list:
        """Get DNS server addresses"""

        try:
            try:
                result = subprocess.run(['ipconfig', '/all'], 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=10)
                
                dns_servers = []
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'DNS Servers' in line or 'Serveurs DNS' in line:
                        # Extract IP from this line
                        match = re.search(r'\d+\.\d+\.\d+\.\d+', line)
                        if match:
                            dns_servers.append(match.group())
                        
                        # Check next lines for additional DNS servers
                        j = i + 1
                        while j < len(lines):
                            match = re.search(r'^\s+(\d+\.\d+\.\d+\.\d+)', lines[j])
                            if match:
                                dns_servers.append(match.group(1))
                                j += 1
                            else:
                                break
                
                return dns_servers if dns_servers else ["Unknown"]
            except:
                return ["Unknown"]
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _get_dns_servers function - {e}")
    
    def _get_gateway(self) -> str:
        """Get default gateway"""

        try:
            try:
                result = subprocess.run(['ipconfig'], 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=10)
                
                # Search for default gateway
                match = re.search(r'Default Gateway.*?:\s*(\d+\.\d+\.\d+\.\d+)', result.stdout)
                if match:
                    return match.group(1)
                
                # French version 🤡 because we love fromages and baguette
                match = re.search(r'Passerelle par défaut.*?:\s*(\d+\.\d+\.\d+\.\d+)', result.stdout)
                if match:
                    return match.group(1)
                
                return "Unknown"
            except:
                return "Unknown"
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _get_gateway function - {e}")
    
    def _collect_network_info(self) -> dict:
        """Collect all network information"""

        try:
            try:
                network_config = {
                    "timestamp": datetime.now().isoformat(),
                    "hostname": self._get_hostname(),
                    "local_ip": self._get_local_ip(),
                    "public_ip": self._get_public_ip(),
                    "mac_address": self._get_mac_address(),
                    "default_gateway": self._get_gateway(),
                    "dns_servers": self._get_dns_servers(),
                    "interfaces": self._get_network_interfaces()
                }
                
                return network_config
                
            except Exception as e:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _collect_network_info function - {e}")
    
    def _has_changed(self, current_config: dict) -> bool:
        """Check if network configuration has changed"""

        try:
            if self.previous_config is None:
                return True
            
            # Compare key fields
            key_fields = ['local_ip', 'public_ip', 'default_gateway', 'dns_servers']
            
            for field in key_fields:
                if current_config.get(field) != self.previous_config.get(field):
                    return True
            
            return False
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _has_changed function - {e}")
    
    def _save_network_info(self, network_config: dict) -> None:
        """Save network configuration to JSON file"""

        try:
            try:
                existing_data = json.loads(self.output_file.read_text(encoding="utf-8"))
                existing_data.append(network_config)
                
                self.output_file.write_text(
                    json.dumps(existing_data, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                
            except Exception as e:
                # Backup in case of error
                backup_file = self.output_file.parent / f"network_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_file.write_text(
                    json.dumps([network_config], indent=2),
                    encoding="utf-8"
                )
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _save_network_info function - {e}")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop running in thread"""

        try:
            while self.running:
                current_config = self._collect_network_info()
                
                # Save only if changed (or if tracking is disabled)
                if not self.track_changes or self._has_changed(current_config):
                    self._save_network_info(current_config)
                    self.previous_config = current_config
                
                time.sleep(self.interval)
        except Exception as e:
            raise Exception(f"NetworkInfo Error in _monitor_loop function - {e}")
    
    def start(self) -> None:
        """Start monitoring network configuration"""

        try:
            if self.running:
                return
            
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
        except Exception as e:
            raise Exception(f"NetworkInfo Error in start function - {e}")
    
    def stop(self) -> None:
        """Stop monitoring network configuration"""

        try:
            self.running = False
            
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
        except Exception as e:
            raise Exception(f"NetworkInfo Error in stop function - {e}")
    
    def get_current_info(self) -> dict:
        """Get current network information immediately"""

        try:
            return self._collect_network_info()
        except Exception as e:
            raise Exception(f"NetworkInfo Error in get_current_info function - {e}")
    
    def save_current_info(self) -> dict:
        """Collect and save current network info immediately"""
        
        try:
            current_config = self._collect_network_info()
            self._save_network_info(current_config)
            return current_config
        except Exception as e:
            raise Exception(f"NetworkInfo Error in save_current_info function - {e}")