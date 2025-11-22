"""
Module for displaying ASCII art
"""

import os

class AsciiArt:
    @staticmethod
    def __display__() -> None:
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