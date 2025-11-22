"""
Module for managing environment variables and configuration settings.
"""

from dotenv import load_dotenv
import os

def auto_cast(value) -> bool | int | float | str | None:  # Python is stupid can't do this natively :)
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
    '''Class to manage environment variables and configuration.'''

    load_dotenv()
    
    __configuration = {
        k: auto_cast(os.getenv(k))
        for k in ["server_log", "client_log", "global_log", "debug_mode", "LOG_LEVEL"]
    }

    @staticmethod
    def configuration(var_name=None) -> dict | str | int | bool | float | None:
        """Returns the configuration dictionary or a specific value if a
        key is provided."""
        if var_name and var_name not in ["server_log", "client_log", "global_log", "debug_mode", "LOG_LEVEL"]:
            raise KeyError(f"La clé '{var_name}' n'existe pas dans la configuration")
        else:   
            if var_name:
                return ENVIRONNEMENT.__configuration.get(var_name)
            return ENVIRONNEMENT.__configuration
