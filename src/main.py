"""
Main application entry point
"""

from __utils__.log import Logger as log
from __utils__.asciiArt import AsciiArt
from __app__.client_app.main import ClientApp
from __utils__.terminal import TerminalUtils as term_utils
from __app__.client_app.utils.clientError.main import ClientError
import asyncio

class Main:
    """Main application class"""
    
    '''
    -> how to use log message:
        self.print("Application started", "info") 
        self.print("This is a debug message", "debug")
        self.print("This is a warning message", "warning")
        self.print("This is an error message", "error")
        self.print("This is a critical message", "critical")
    '''

    LOG_DIR = "logs/client"
    APP_NAME = "Gordinay"
    VERSION = "1.0.0"
    
    def __init__(self) -> None:
        """Initialize main class (synchronous)"""
        
        self.logger = None
        self.print = print
    
    async def initialize(self) -> None:
        """Asynchronous initialization method"""
        
        try:
            AsciiArt.__display__()
            self._log_init()
            await self.__start__server__()
            await self.__start__client__()
            
        except Exception as e:
            if self.logger:
                data = e.args[0]
                self.print(data["message"], data["level"])
            else:
                print(f"[ERROR] {e}") # The only way to display the error is here, as the logger may not be initialized.

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
            raise ClientError("Main error in _log_init function - " + str(e), "critical")
        
    async def __start__client__(self) -> None:
        """Start client"""

        try:
            ClientApp()
        except Exception as e:
            raise ClientError("Main error in __start__client__ function - " + str(e), "critical")

    async def __start__server__(self) -> None:
        """Start server"""

        try:
            cmd = term_utils.get_python_command()
            term_utils.open_new_terminal(f"{cmd} src/__app__/server_app/server.py")
        except Exception as e:
            raise ClientError("Main error in __start__server__ function - " + str(e), "critical")
    
async def main() -> None:
    """Asynchronous entry point"""

    try:
        app = Main()
        await app.initialize()

    except Exception as e:
        print(f"[ERROR] {e}") # The only way to display the error is here, as the logger may not be initialized.

if __name__ == "__main__":
    asyncio.run(main())