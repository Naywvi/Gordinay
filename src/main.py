from __conf__.main import ENVIRONNEMENT
from datetime import datetime
import logging


class Main:
    __ENVIRONNEMENT = ENVIRONNEMENT.configuration()
    logger = None

    def __init__(self) -> None:
        """Init main class"""

        try:
            self.__debug_mode__()
            self.__setup_log__()
            # self.__run__()

        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] {e}")
            else:
                print(f"[ERROR] {e}")
    def __setup_log__(self):
        """Log main application events"""

        try:
             if not self.__ENVIRONNEMENT.get("log_enabled"):
                self.logger.error("[CONFIG ERROR]")
                return
        except Exception as e:
            raise e
    def __debug_mode__(self) -> None:
        """Enable debug mode"""

        '''
        self.logger.debug("this is a debug message !")
        self.logger.info("this is an info message !")
        self.logger.warning("this is a warning message !")
        self.logger.error("this is an error message !")
        self.logger.critical("this is a critical message !")
        '''

        try:
            if self.__ENVIRONNEMENT["debug_mode"]:
                level_value = getattr(
                    logging, self.__ENVIRONNEMENT["LOG_LEVEL"].upper(), logging.INFO
                )
                self.logger = logging.getLogger(self.__class__.__name__)

                logging.basicConfig(
                    level=level_value,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%H:%M:%S",
                )
                
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

    def __stop__(self, message=None):
        """Stop main application"""

        try:
            pass
        except Exception as e:
            raise e

    def __restart__(self):
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
        
    def __log__(self):
        """Log main application events"""

        try:
            pass
        except Exception as e:
            raise e

    def __get_timestamp(self):
        """Get current timestamp"""

        try:
            return
            return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        except Exception as e:
            raise e

if __name__ == "__main__":
    Main()
