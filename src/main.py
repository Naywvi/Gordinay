from __utils__.log import Logger as log
from __utils__.asciiArt import AsciiArt

class Main:
    """Main application class"""
    
    '''
    -> how to use log message:
        self.writeLog("Application started", "info") 
        self.writeLog("This is a debug message", "debug")
        self.writeLog("This is a warning message", "warning")
        self.writeLog("This is an error message", "error")
        self.writeLog("This is a critical message", "critical")
    '''

    LOG_DIR = "logs/global"
    APP_NAME = "Gordinay"
    VERSION = "1.0.0"
    
    def __init__(self) -> None:
        """Init main class"""

        try:
            AsciiArt.__display__()

            if not (logger := log(self.APP_NAME, self.VERSION, self.LOG_DIR)):
                self.logger = None
                raise Exception("Logger initialization failed")
            else: 
                self.logger = logger
                self.writeLog = logger.new_log
            
            self.writeLog("Application started", "info")
            
        except Exception as e:
            # if self.logger:
            #     self.logger.error(f"[ERROR] {e}")
            # else:
            #     print(f"[ERROR] {e}") # Fallback if logger is not initialized
            print(f"[ERROR] {e}") # Fallback if logger is not initialized
    
    def __run__(self):
        """Run main application logic"""

        try:
            pass
        except Exception as e:
            raise e
        
    def __server_start__(self):
        """Start server"""

        try:
            pass
        except Exception as e:
            raise e

    def __client_start__(self):
        """Start client"""

        try:
            pass
        except Exception as e:
            raise e

    def __stop__(self, message: str = None):
        """Stop main application"""

        try:
            pass
        except Exception as e:
            raise e

    @classmethod
    def __restart__(cls):
        """Restart main application"""

        try:
            pass
        except Exception as e:
            raise e

    def __status__(self):
        """Get current status of main application"""

        try:
            pass
        except Exception as e:
            raise e

if __name__ == "__main__":
    Main()
