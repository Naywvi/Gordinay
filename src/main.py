from __conf__.main import ENVIRONNEMENT
from __utils__.coloredFormatter import ColoredFormatter
from datetime import datetime
import logging, os


class Main:
    """Main application class"""
    
    '''
    -> how to use log message:
        self.new_log("Application started", "info") 
        self.new_log("This is a debug message", "debug")
        self.new_log("This is a warning message", "warning")
        self.new_log("This is an error message", "error")
        self.new_log("This is a critical message", "critical")
    '''

    __ENVIRONNEMENT = ENVIRONNEMENT.configuration()
    logger = None

    LOG_DIR = "logs/global"
    APP_NAME = "Gordinay"
    VERSION = "1.0.0"
    
    def __init__(self) -> None:
        """Init main class"""

        try:
            self.__ascii_art__()
            self.__debug_mode__()
            self.__setup_log__()
            # self.__run__()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] {e}")
            else:
                print(f"[ERROR] {e}")

    @staticmethod
    def __ascii_art__() -> None:
        """Display ASCII art"""

        # ASCII art from /assets/gordinay.txt
        try:
            with open("src/assets/gordinay.txt", "r", encoding="utf-8") as f:
                #clear console
                os.system('cls' if os.name == 'nt' else 'clear')
                ascii_art = f.read()
                print(ascii_art)
        except Exception as e:
            raise e
    
    def new_log(self, message: str, level: str = "info") -> None:
        """Create a new log entry"""
        
        try:
            if not self.logger:
                raise Exception("Logger not initialized")
            
            # Config logger
            logger = logging.getLogger(self.__class__.__name__)
            logger.setLevel(logging.DEBUG)

            # Define log format
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%H:%M:%S"
            )

            # Create a log record
            record = logger.makeRecord(
                name=logger.name,
                level=getattr(logging, level.upper(), logging.DEBUG),
                fn="",
                lno=0,
                msg=message,
                args=(),
                exc_info=None
            )
            formatted_message = formatter.format(record)

            if hasattr(self, 'log_file'): # Check if log_file attribute exists
                with open(self.log_file, "a", encoding="utf-8") as f:
                    match level.lower():
                        case "debug":
                            f.write(f"{formatted_message}\n")
                        case "info":
                            f.write(f"{formatted_message}\n")
                        case "warning":
                            f.write(f"{formatted_message}\n")
                        case "error":
                            f.write(f"{formatted_message}\n")
                        case "critical":
                            f.write(f"{formatted_message}\n")
                        case _:
                            f.write(f"[UNKNOWN LEVEL] {message}\n")
                    
        except Exception as e:
            raise e
        
    def __setup_log__(self):
        """Log main application events"""

        try:
            # Check if logging is enabled in the configuration
            if not self.__ENVIRONNEMENT.get("global_log"):
                self.logger.error("[CONFIG ERROR]")
                return

            # Create logs directory if it doesn't exist
            if not os.path.exists("logs"):
                os.makedirs(self.LOG_DIR, exist_ok=True)

            # Create log file with timestamp
            timestamp = self.__get_timestamp__()
            log_filename = f"{self.LOG_DIR}/{timestamp}.log"

            # Create log file if it doesn't exist
            if not os.path.exists(log_filename):
                with open(log_filename, "w", encoding="utf-8") as f:
                    f.write(f"[✔] Log file created at {timestamp}\n")

            self.logger.info(f"Log file ready: {log_filename}")

            # Store log file path in an instance variable
            self.log_file = log_filename
        except Exception as e:
            raise e
        
    def __debug_mode__(self) -> None:
        """Enable debug mode"""

        try:
            if self.__ENVIRONNEMENT["debug_mode"]:
                level_value = getattr(
                    logging, self.__ENVIRONNEMENT["LOG_LEVEL"].upper(), logging.INFO
                )
                self.logger = logging.getLogger(self.__class__.__name__)

                console_handler = logging.StreamHandler()
                formatter = ColoredFormatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%H:%M:%S"
                )
                logging.basicConfig(
                    level=level_value,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%H:%M:%S",
                )

                # Prevent log messages from being propagated to the root logger
                # This avoids duplicate log entries
                self.logger.propagate = False
                self.logger.handlers.clear()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
                
            else:
                self.logger = False

        except Exception as e:
            raise e

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

    @staticmethod
    def __get_timestamp__() -> str:
        """Get current timestamp"""

        try:
            return datetime.now().strftime("%Y-%m-%d")
        except Exception as e:
            raise e

if __name__ == "__main__":
    Main()
