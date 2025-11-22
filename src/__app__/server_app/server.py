"""
RAT Server - Main Entry Point
Remote Administration Tool Server
For educational purposes only
"""

from pathlib import Path
import signal, os, sys, argparse

src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from __app__.server_app.server_app import ServerApp
from __utils__.log import Logger as log
from __utils__.clientError import ClientError

class ServerInitializer:
    """RAT Server Application"""

    '''
    -> how to use log message:
        self.print("Application started", "info") 
        self.print("This is a debug message", "debug")
        self.print("This is a warning message", "warning")
        self.print("This is an error message", "error")
        self.print("This is a critical message", "critical")
    '''

    LOG_DIR = "logs/server"
    APP_NAME = "Gordinay-server"
    VERSION = "1.0.0"

    def __init__(self) -> None:
        """Initialize server application"""

        try:
            self.logger = None
            self.print = print
            self._log_init()
            self.__arguments__()
            self.__start__server__()
        except Exception as e:
            if self.logger:
                data = e.args[0]
                self.print(data["message"], data["level"])
            else:
                print(f"[ERROR] {e}") # The only way to display the error is here, as the logger may not be initialized.

    def __arguments__(self) -> None:
        """Parse command-line arguments and start server"""

        try:
            # Parse arguments
            self.parser = argparse.ArgumentParser(
                description='RAT Server - Remote Administration Tool',
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog='''
                Examples:
                python server.py                          # Start on default 127.0.0.1:4444
                python server.py --host 0.0.0.0           # Start on all interfaces
                python server.py --port 5555              # Start on custom port
                python server.py --no-ssl                 # Start without SSL/TLS
                '''
            )
            
            self.parser.add_argument(
                '--host',
                default='127.0.0.1',
                help='Host to bind to (default: 127.0.0.1)'
            )
            
            self.parser.add_argument(
                '--port',
                type=int,
                default=4444,
                help='Port to listen on (default: 4444)'
            )
            
            self.parser.add_argument(
                '--no-ssl',
                action='store_true',
                help='Disable SSL/TLS encryption (not recommended)'
            )
            
            self.args = self.parser.parse_args()
            
            # Register signal handler
            signal.signal(signal.SIGINT, self.signal_handler)
            
            # print => better idea .... burk
            self.print(f"\n\n- Starting RAT Server on {self.args.host}:{self.args.port} \n- SSL/TLS: {'Disabled' if self.args.no_ssl else 'Enabled'}\n {self.print_banner()}", "info")
        except Exception as e:
            raise ClientError("Argument parsing error in __arguments__ function - " + str(e), "critical")
        
    def __start__server__(self) -> None:
        """Start the RAT server with specified configurations"""

        try:
            app = ServerApp(
                host=self.args.host,
                port=self.args.port,
                use_ssl=not self.args.no_ssl,
                printer=self.print
            )
            app.start()
        
        except Exception as e:
            print(f"[!] Fatal error: {e}")
            import traceback
            traceback.print_exc()
            
            # Cleanup terminal before exit
            if os.name != 'nt':
                os.system('stty sane')
            raise ClientError("Server start error in __start__server__ function - " + str(e), "critical")
        finally:
            sys.exit(1)

    def _log_init(self) -> None:
            """Initialize logger"""

            try:
                if not (logger := log(self.APP_NAME, self.VERSION, self.LOG_DIR)):
                    self.logger = None
                    raise Exception("Logger initialization failed")
                else:
                    self.logger = True
                    self.print = logger.__print_log__
            except Exception as e:
                raise ClientError("Logger initialization error in _log_init function - " + str(e), "critical")
            
    def signal_handler(self,sig, frame) -> None:
        """Handle Ctrl+C gracefully"""

        try:
            self.print('\n[*] Received interrupt signal','critical')
            
            # FORCE terminal reset
            if os.name != 'nt':
                os.system('stty sane')
            
            self.print('[*] Shutting down server...','critical')
            os._exit(0)
        except Exception as e:
            raise ClientError("Signal handling error in signal_handler function - " + str(e), "critical")

    def print_banner(self) -> str:
        """Server banner"""

        return """
        ╔═══════════════════════════════════════════════════════════╗
        ║                 Gordinay SERVER CONSOLE                   ║
        ║              Remote Administration Tool v1.0              ║
        ║                  For Educational Use Only                 ║
        ╚═══════════════════════════════════════════════════════════╝
        """


if __name__ == "__main__":
    ServerInitializer()