"""
Server Application - Main coordination class
Coordinates ServerSocket and ServerCLI
"""

from __app__.server_app.server_socket import ServerSocket
from __app__.server_app.server_cli import ServerCLI
from __utils__.clientError import ClientError
import signal, atexit, sys, traceback

class ServerApp():
    """Main server application class"""

    '''
    -> how to use log message:
        self.print("Application started", "info") 
        self.print("This is a debug message", "debug")
        self.print("This is a warning message", "warning")
        self.print("This is an error message", "error")
        self.print("This is a critical message", "critical")
    '''
    def __init__(self, host='0.0.0.0', port=4444, use_ssl=True, printer=None) -> None:
        """
        Initialize server application
        Args:
            host: Interface to bind to (0.0.0.0 = all interfaces)
            port: Port to listen on
            use_ssl: Enable SSL/TLS encryption
        """
        
        try:
            self.print = printer
            self.host = host
            self.port = port
            self.use_ssl = use_ssl
            
            # Create server socket
            self.server = ServerSocket(
                host=self.host,
                port=self.port,
                use_ssl=self.use_ssl,
                printer=self.print
            )
            
            # Create CLI interface
            self.cli = ServerCLI(self.server, printer=self.print)
            
            # Register cleanup handler
            atexit.register(self._cleanup)
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except Exception as e:
            raise ClientError("ServerApp initialization error in __init__ function - " + str(e), "critical")
    
    def _signal_handler(self, sig, frame) -> None:
        """Handle signals (Ctrl+C, etc)"""

        try:
            self.print("\nReceived interrupt signal", "critical")
            self.stop()
            sys.exit(0)
        except Exception as e:
            raise ClientError("Signal handling error in _signal_handler function - " + str(e), "critical")
    
    def _cleanup(self) -> None:
        """Cleanup on exit"""

        try:
            if hasattr(self, 'server') and self.server:
                self.server.stop()
        except:
            pass
    
    def start(self) -> None:
        """Start the server and CLI"""

        try:
            # Start server socket
            self.server.start(printer= self.print)
            
            # Check if server started successfully
            if not self.server.running:
                self.print("Failed to start server", "warning")
                sys.exit(1)
            
            # Start CLI loop (blocking)
            self.cli.cmdloop()
        
        except KeyboardInterrupt:
            self.print("\nInterrupted by user", "critical")
            self.stop()
        
        except Exception as e:
            self.print(f"Fatal error: {e}", "error")
            traceback.print_exc()
            self.stop()
    
    def stop(self) -> None:
        """Stop the server"""

        self.print("Stopping server...", "critical")
        
        if hasattr(self, 'server') and self.server:
            self.server.stop()
        
        self.print("Server stopped", "critical")


if __name__ == "__main__":
    app = ServerApp()
    app.start()