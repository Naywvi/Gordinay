"""
Tests for SocketClient feature
"""

from unittest.mock import patch, MagicMock, PropertyMock
from queue import Queue
import pytest, sys, os, json, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSocketClient:
    """Tests for SocketClient class"""
    
    def test_socket_client_init(self):
        """Test SocketClient initialization"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(
            host="127.0.0.1",
            port=4444,
            use_ssl=False
        )
        
        assert client.host == "127.0.0.1"
        assert client.port == 4444
        assert client.use_ssl is False
        assert client.connected is False
        assert client.running is False
    
    def test_socket_client_init_with_ssl(self):
        """Test SocketClient initialization with SSL"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(
            host="localhost",
            port=443,
            use_ssl=True
        )
        
        assert client.use_ssl is True
    
    def test_socket_client_init_custom_reconnect_delay(self):
        """Test SocketClient with custom reconnect delay"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(
            host="127.0.0.1",
            port=4444,
            reconnect_delay=10
        )
        
        assert client.reconnect_delay == 10
    
    def test_socket_client_init_queues(self):
        """Test SocketClient initializes queues"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        assert isinstance(client.send_queue, Queue)
        assert isinstance(client.receive_queue, Queue)
    
    def test_socket_client_init_statistics(self):
        """Test SocketClient initializes statistics to zero"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        assert client.bytes_sent == 0
        assert client.bytes_received == 0
        assert client.messages_sent == 0
        assert client.messages_received == 0
    
    def test_set_callbacks(self):
        """Test setting callbacks"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        on_connect = MagicMock()
        on_disconnect = MagicMock()
        on_message = MagicMock()
        
        client.set_callbacks(
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            on_message=on_message
        )
        
        assert client.on_connect_callback == on_connect
        assert client.on_disconnect_callback == on_disconnect
        assert client.on_message_callback == on_message
    
    def test_set_callbacks_partial(self):
        """Test setting only some callbacks"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        on_connect = MagicMock()
        client.set_callbacks(on_connect=on_connect)
        
        assert client.on_connect_callback == on_connect
        assert client.on_disconnect_callback is None
        assert client.on_message_callback is None
    
    def test_send_adds_to_queue(self):
        """Test send adds message to queue"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        message = {"type": "test", "data": "hello"}
        client.send(message)
        
        assert not client.send_queue.empty()
        queued_message = client.send_queue.get()
        assert queued_message == message
    
    def test_send_string_message(self):
        """Test send with string message"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        client.send("plain string")
        
        queued = client.send_queue.get()
        assert queued == "plain string"
    
    def test_is_connected_false_initially(self):
        """Test is_connected returns False initially"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        assert client.is_connected() is False
    
    def test_is_connected_returns_connected_state(self):
        """Test is_connected returns connected state"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        client.connected = True
        
        assert client.is_connected() is True
    
    def test_get_statistics_none_when_not_started(self):
        """Test get_statistics returns None when not started"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        assert client.get_statistics() is None
    
    def test_get_statistics_returns_dict_when_started(self):
        """Test get_statistics returns dict when connection started"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        client.connection_start_time = time.time()
        
        stats = client.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'connected' in stats
        assert 'uptime_seconds' in stats
        assert 'bytes_sent' in stats
        assert 'bytes_received' in stats
        assert 'messages_sent' in stats
        assert 'messages_received' in stats
    
    def test_create_socket_no_ssl(self):
        """Test _create_socket without SSL"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            
            client = SocketClient(host="127.0.0.1", port=4444, use_ssl=False)
            sock = client._create_socket()
            
            assert sock == mock_sock
            mock_sock.setsockopt.assert_called()
            mock_sock.settimeout.assert_called_with(10)
    
    def test_create_socket_with_ssl(self):
        """Test _create_socket with SSL"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        with patch('socket.socket') as mock_socket, \
             patch('ssl.create_default_context') as mock_ssl:
            
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            
            mock_context = MagicMock()
            mock_ssl.return_value = mock_context
            mock_context.wrap_socket.return_value = MagicMock()
            
            client = SocketClient(host="127.0.0.1", port=4444, use_ssl=True)
            sock = client._create_socket()
            
            mock_context.wrap_socket.assert_called()
    
    def test_connect_success(self):
        """Test successful connection"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            
            client = SocketClient(host="127.0.0.1", port=4444, use_ssl=False)
            result = client._connect()
            
            assert result is True
            assert client.connected is True
            mock_sock.connect.assert_called_with(("127.0.0.1", 4444))
    
    def test_connect_failure(self):
        """Test connection failure"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect.side_effect = ConnectionRefusedError()
            mock_socket.return_value = mock_sock
            
            client = SocketClient(host="127.0.0.1", port=4444, use_ssl=False)
            result = client._connect()
            
            assert result is False
            assert client.connected is False
    
    def test_connect_calls_callback(self):
        """Test connection calls on_connect callback"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            
            callback = MagicMock()
            
            client = SocketClient(host="127.0.0.1", port=4444, use_ssl=False)
            client.on_connect_callback = callback
            client._connect()
            
            callback.assert_called_once()
    
    def test_disconnect(self):
        """Test disconnect closes socket"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        client.connected = True
        mock_socket = MagicMock()
        client.socket = mock_socket
        
        client._disconnect()
        
        assert client.connected is False
        mock_socket.close.assert_called_once()
        assert client.socket is None
    
    def test_disconnect_calls_callback(self):
        """Test disconnect calls on_disconnect callback"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        callback = MagicMock()
        
        client = SocketClient(host="127.0.0.1", port=4444)
        client.on_disconnect_callback = callback
        client.connected = True
        client.socket = MagicMock()
        
        client._disconnect()
        
        callback.assert_called_once()
    
    def test_start_sets_running(self):
        """Test start sets running flag"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        client.start()
        
        assert client.running is True
        
        # Cleanup
        client.running = False
    
    def test_start_creates_threads(self):
        """Test start creates threads"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        client.start()
        
        assert client.send_thread is not None
        assert client.receive_thread is not None
        assert client.heartbeat_thread is not None
        
        # Cleanup
        client.stop()
    
    def test_start_idempotent(self):
        """Test start does nothing if already running"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        client.running = True
        
        original_thread = client.send_thread
        client.start()
        
        # Thread shouldn't change
        assert client.send_thread == original_thread
    
    def test_stop_sets_not_running(self):
        """Test stop sets running to False"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        client.running = True
        client.connected = True
        client.socket = MagicMock()
        
        client.stop()
        
        assert client.running is False
    
    def test_receive_returns_from_queue(self):
        """Test receive returns message from queue"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        test_message = {"type": "test"}
        client.receive_queue.put(test_message)
        
        result = client.receive(timeout=1)
        
        assert result == test_message
    
    def test_receive_returns_none_on_timeout(self):
        """Test receive returns None on timeout"""
        from __app__.client_app.features.socketClient.main import SocketClient
        
        client = SocketClient(host="127.0.0.1", port=4444)
        
        result = client.receive(timeout=0.1)
        
        assert result is None
