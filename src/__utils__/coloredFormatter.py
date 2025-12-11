"""
Module providing a colored log formatter for enhanced log readability.
"""
from colorama import init, Fore, Style
init()
import logging

class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }

    RESET = Style.RESET_ALL

    
    def format(self, record) -> str:
        '''Format the log message with colors based on the log level.'''
        
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"