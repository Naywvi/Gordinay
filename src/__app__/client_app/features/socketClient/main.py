"""
TCP Socket Client with SSL/TLS Encryption - For Educational Use Only
This module implements a TCP socket client that supports SSL/TLS encryption. It provides features such as automatic reconnection,
message queuing, and callback functions for connection events and message handling.
"""

from queue import Queue, Empty
from datetime import datetime
import threading, time, json, ssl, socket

class SocketClient:
    '''TCP Socket client with SSL/TLS encryption - For educational use only'''
    
    def __init__(self, host, port, use_ssl=True, reconnect_delay=5, 
                 certfile=None, keyfile=None, ca_cert=None) -> None:
        """
        Initialize the socket client
        Args:
            host: Server hostname or IP
            port: Server port
            use_ssl: Enable SSL/TLS encryption
            reconnect_delay: Seconds to wait before reconnection attempt
            certfile: Path to client certificate (optional)
            keyfile: Path to client private key (optional)
            ca_cert: Path to CA certificate for server verification (optional)
        """

        try:
            self.host = host
            self.port = port
            self.use_ssl = use_ssl
            self.reconnect_delay = reconnect_delay
            self.certfile = certfile
            self.keyfile = keyfile
            self.ca_cert = ca_cert
            
            # Socket and connection state
            self.socket = None
            self.connected = False
            self.running = False
            
            # Threading
            self.send_thread = None
            self.receive_thread = None
            self.heartbeat_thread = None
            
            # Queues for thread-safe communication
            self.send_queue = Queue()
            self.receive_queue = Queue()
            
            # Callbacks
            self.on_connect_callback = None
            self.on_disconnect_callback = None
            self.on_message_callback = None
            
            # Statistics
            self.bytes_sent = 0
            self.bytes_received = 0
            self.messages_sent = 0
            self.messages_received = 0
            self.connection_start_time = None
        except Exception as e:
            raise Exception("SocketClient Initialization Error in __init__ function - " + str(e))
    
    def _create_socket(self) -> socket.socket:
        """Create and configure the socket"""
        # Uncomment for debugging

        try:
            try:
                # Create TCP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                sock.settimeout(10)
                
                # Wrap with SSL if enabled
                if self.use_ssl:
                    context = ssl.create_default_context()
                    
                    # FOR SELF-SIGNED CERTIFICATE (development)
                    # Disable certificate verification
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    # Load client certificate if provided
                    if self.certfile and self.keyfile:
                        context.load_cert_chain(self.certfile, self.keyfile)
                    
                    # Wrap socket with SSL
                    sock = context.wrap_socket(sock, server_hostname=self.host)
                
                return sock
                
            except Exception as e:
                # print(f"Error creating socket: {e}") # For debugging
                return None
        except Exception as e:
            raise Exception("SocketClient Socket Creation Error in _create_socket function - " + str(e))
        
    def _connect(self) -> bool:
        """Establish connection to server"""
        # Uncomment for debugging

        try:
            try:
                # print(f"Connecting to {self.host}:{self.port}...")
                
                # Create socket
                self.socket = self._create_socket()
                if not self.socket:
                    return False
                
                # Connect to server
                self.socket.connect((self.host, self.port))
                
                self.connected = True
                self.connection_start_time = time.time()
                
                # print(f"Connected to {self.host}:{self.port}")
                
                # Call connect callback
                if self.on_connect_callback:
                    self.on_connect_callback()
                
                return True
                
            except Exception as e:
                # print(f"Connection error: {e}")
                self.connected = False
                return False
        except Exception as e:
            raise Exception("SocketClient Connection Error in _connect function - " + str(e))
    
    def _disconnect(self) -> None:
        """Close connection"""

        try:
            self.connected = False
            
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            
            # Call disconnect callback
            if self.on_disconnect_callback:
                self.on_disconnect_callback()
            
            # print("Disconnected from server")
        except Exception as e:
            raise Exception("SocketClient Disconnection Error in _disconnect function - " + str(e))
    
    def _send_loop(self) -> None:
        """Thread loop for sending messages"""

        try:
            while self.running:
                try:
                    # Check if connected
                    if not self.connected:
                        time.sleep(0.5)
                        continue
                    
                    # Get message from queue (with timeout)
                    try:
                        message = self.send_queue.get(timeout=1)
                    except Empty:
                        continue
                    
                    # Convert to JSON and encode
                    if isinstance(message, dict):
                        message_json = json.dumps(message)
                    else:
                        message_json = str(message)
                    
                    # Add message delimiter (for framing)
                    message_bytes = (message_json + '\n').encode('utf-8')
                    
                    # Send message
                    self.socket.sendall(message_bytes)
                    
                    # Update statistics
                    self.bytes_sent += len(message_bytes)
                    self.messages_sent += 1
                    
                    self.send_queue.task_done()
                    
                except Exception as e:
                    # print(f"Send error: {e}")
                    self._disconnect()
                    time.sleep(self.reconnect_delay)
        except Exception as e:
            raise Exception("SocketClient Send Loop Error in _send_loop function - " + str(e))
    
    def _receive_loop(self) -> None:
        """Thread loop for receiving messages"""

        try:
            buffer = ""
            
            while self.running:
                try:
                    # Check if connected
                    if not self.connected:
                        time.sleep(0.5)
                        continue
                    
                    # Receive data
                    data = self.socket.recv(4096)
                    
                    if not data:
                        # Connection closed by server
                        # print("Connection closed by server")
                        self._disconnect()
                        time.sleep(self.reconnect_delay)
                        continue
                    
                    # Update statistics
                    self.bytes_received += len(data)
                    
                    # Decode and add to buffer
                    buffer += data.decode('utf-8')
                    
                    # Process complete messages (delimited by newline)
                    while '\n' in buffer:
                        message_str, buffer = buffer.split('\n', 1)
                        
                        # Parse JSON
                        try:
                            message = json.loads(message_str)
                        except json.JSONDecodeError:
                            message = message_str
                        
                        # Update statistics
                        self.messages_received += 1
                        
                        # Add to receive queue
                        self.receive_queue.put(message)
                        
                        # Call message callback
                        if self.on_message_callback:
                            self.on_message_callback(message)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    # print(f"Receive error: {e}")
                    self._disconnect()
                    time.sleep(self.reconnect_delay)
        except Exception as e:
            raise Exception("SocketClient Receive Loop Error in _receive_loop function - " + str(e))
    
    def _heartbeat_loop(self) -> None:
        """Thread loop for sending heartbeat and reconnecting"""

        try:
            while self.running:
                try:
                    # Try to reconnect if disconnected
                    if not self.connected:
                        if self._connect():
                            time.sleep(1)
                        else:
                            time.sleep(self.reconnect_delay)
                        continue
                    
                    # Send heartbeat every 30 seconds
                    time.sleep(30)
                    
                    if self.connected:
                        self.send({
                            'type': 'heartbeat',
                            'timestamp': datetime.now().isoformat()
                        })
                    
                except Exception as e:
                    # print(f"Heartbeat error: {e}")
                    time.sleep(self.reconnect_delay)
        except Exception as e:
            raise Exception("SocketClient Heartbeat Loop Error in _heartbeat_loop function - " + str(e))
    
    def start(self) -> None:
        """Start the socket client"""

        try:
            if self.running:
                return
            
            self.running = True
            
            # Start threads
            self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            
            self.send_thread.start()
            self.receive_thread.start()
            self.heartbeat_thread.start()
            
            # print("Socket client started")
        except Exception as e:
            raise Exception("SocketClient Start Error in start function - " + str(e))
    
    def stop(self) -> None:
        """Stop the socket client"""

        try:
            self.running = False
            self._disconnect()
            
            # Wait for threads to finish
            if self.send_thread:
                self.send_thread.join(timeout=5)
            if self.receive_thread:
                self.receive_thread.join(timeout=5)
            if self.heartbeat_thread:
                self.heartbeat_thread.join(timeout=5)
            
            # print("Socket client stopped")
        except Exception as e:
            raise Exception("SocketClient Stop Error in stop function - " + str(e))
    
    def send(self, message) -> None:
        """
        Send a message to server
        Args:
            message: Dictionary or string to send
        """

        try:
            self.send_queue.put(message)
        except Exception as e:
            raise Exception("SocketClient Send Error in send function - " + str(e))
    
    def receive(self, timeout=None) -> any:
        """
        Receive a message from server (blocking)
        Args:
            timeout: Seconds to wait for message
        Returns:
            Message or None if timeout
        """

        try:
            return self.receive_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def is_connected(self) -> bool:
        """Check if connected to server"""

        return self.connected
    
    def get_statistics(self) -> dict | None:
        """Get connection statistics"""

        try:
            if self.connection_start_time:
                uptime = time.time() - self.connection_start_time
                return {
                    'connected': self.connected,
                    'uptime_seconds': round(uptime, 2),
                    'bytes_sent': self.bytes_sent,
                    'bytes_received': self.bytes_received,
                    'messages_sent': self.messages_sent,
                    'messages_received': self.messages_received,
                    'send_queue_size': self.send_queue.qsize(),
                    'receive_queue_size': self.receive_queue.qsize()
                }
            return None
        except Exception as e:
            raise Exception("SocketClient Get Statistics Error in get_statistics function - " + str(e))
    
    def set_callbacks(self, on_connect=None, on_disconnect=None, on_message=None) -> None:
        """
        Set callback functions
        Args:
            on_connect: Function called when connected
            on_disconnect: Function called when disconnected
            on_message: Function called when message received
        """

        try:
            if on_connect:
                self.on_connect_callback = on_connect
            if on_disconnect:
                self.on_disconnect_callback = on_disconnect
            if on_message:
                self.on_message_callback = on_message
        except Exception as e:
            raise Exception("SocketClient Set Callbacks Error in set_callbacks function - " + str(e))