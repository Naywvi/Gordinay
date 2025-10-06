import logging

class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",    # Bleu
        "INFO": "\033[92m",     # Vert
        "WARNING": "\033[93m",  # Jaune
        "ERROR": "\033[91m",    # Rouge
        "CRITICAL": "\033[95m", # Magenta
    }

    RESET = "\033[0m"

    
    def format(self, record) -> str:
        '''Format the log message with colors based on the log level.'''
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"