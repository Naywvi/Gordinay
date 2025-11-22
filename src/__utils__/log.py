"""
Logger utility for application logging
"""

from .coloredFormatter import ColoredFormatter
from __conf__.main import ENVIRONNEMENT
from datetime import datetime
import logging, os

class Logger:
    '''Logger class for handling application logging'''

    __ENVIRONNEMENT = ENVIRONNEMENT.configuration()
    logger = None
    
    def __init__(self, app_name: str, version: str, log_dir: str = "logs/global") -> None:
        '''Initialize Logger class'''
        
        try:
            #if nor parameters are provided raise error
            if not app_name or not version:
                raise ValueError("App name and version must be provided")
            
            self.APP_NAME = app_name
            self.VERSION = version
            self.LOG_DIR = log_dir
            self.__debug_mode__()
            self.__setup_log__()
        except Exception as e:
            raise e

    def new_log(self, message: str, level: str = "info") -> None:
        '''Create a new log entry'''
        
        try:
            if not self.logger:
                raise Exception("Logger not initialized")
            
            # Config logger
            logger = logging.getLogger(f"{self.APP_NAME}, {self.VERSION}")
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
            print(e)
            raise e
        
    def __setup_log__(self) -> None:
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
        '''Enable debug mode'''

        try:
            if self.__ENVIRONNEMENT["debug_mode"]:
                level_value = getattr(
                    logging, self.__ENVIRONNEMENT["LOG_LEVEL"].upper(), logging.INFO
                )
                self.logger = logging.getLogger(f"{self.APP_NAME}, {self.VERSION}")

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
    
    @staticmethod
    def __get_timestamp__() -> str:
        '''Get current timestamp'''

        try:
            return datetime.now().strftime("%Y-%m-%d")
        except Exception as e:
            raise e
    
    def __print_log__(self, message: str, level: str = "info") -> None:
        """Print a log message to console and write it to file."""

        try:
            level = level.lower()

            log_methods = {
                "debug": self.logger.debug,
                "info": self.logger.info,
                "warning": self.logger.warning,
                "error": self.logger.error,
                "critical": self.logger.critical,
            }
            log_fn = log_methods.get(level, self.logger.info)
            log_fn(f"[{level.upper()}] {message}")
            self.new_log(message, level)

        except Exception as e:
            raise Exception(f"Logging failed: {e}")