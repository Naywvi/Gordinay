import os
from dotenv import load_dotenv


def auto_cast(value):  # Python is stupid can't do this natively :)
    """Convert a string to its appropriate type (bool, int, float, or str)."""
    if value is None:
        return None
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value  # Return as string if no other type matches


class ENVIRONNEMENT:
    load_dotenv()

    __configuration = {
        k: auto_cast(os.getenv(k))
        for k in ["server_log", "client_log", "debug_log", "debug_mode", "LOG_LEVEL"]
    }

    @staticmethod
    def configuration(nom=None):
        """Returns the configuration dictionary or a specific value if a
        key is provided."""
        if nom:
            return ENVIRONNEMENT.__configuration.get(nom)
        return ENVIRONNEMENT.__configuration
