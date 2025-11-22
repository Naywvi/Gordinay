"""""
Screenshot feature with change detection and metadata logging functionality. - For Educational Use Only
"""

from PIL import ImageGrab
from datetime import datetime
from pathlib import Path
import numpy as np
import ctypes, cv2, time, threading, json


class Screenshot:
    '''Screenshot feature class with change detection'''
    
    def __init__(self, output_dir="screenshots", interval=60, 
                 change_detection=False, change_threshold=5.0, 
                 quality=85, capture_area=None) -> None:
        """
        Initialize the screenshot capture
        Args:
            output_dir: Directory to save screenshots
            interval: Seconds between screenshots
            change_detection: Only capture when screen changes significantly
            change_threshold: Percentage of change required (0-100)
            quality: JPEG quality (1-100, higher = better quality)
            capture_area: Tuple (x1, y1, x2, y2) to capture specific area, None for full screen
        """

        try:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self.interval = interval
            self.change_detection = change_detection
            self.change_threshold = change_threshold
            self.quality = quality
            self.capture_area = capture_area
            self.running = False
            self.capture_thread = None
            self.previous_screenshot = None
            self.last_capture_time = None
            
            # Folder for metadata
            self.metadata_file = self.output_dir / "metadata.json"
            if not self.metadata_file.exists():
                self.metadata_file.write_text("[]", encoding="utf-8")
        except Exception as e:
            raise Exception(f"Screenshot Initialization Error in __init__ function: {e}")
    
    def _get_active_window(self) -> str:
        """Get the title of the active window"""

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
            raise Exception(f"Error getting active window: {e}")
    
    def _detect_change(self, current_screenshot) -> bool:
        """Detect if screen has changed significantly"""

        try:
            if self.previous_screenshot is None:
                return True
            
            try:
                # Convert to NumPy arrays and resize for quick comparison
                current_small = current_screenshot.resize((320, 240))
                previous_small = self.previous_screenshot.resize((320, 240))
                
                current_array = np.array(current_small)
                previous_array = np.array(previous_small)
                
                # Calculate the difference
                diff = cv2.absdiff(current_array, previous_array)
                
                # Calculate the percentage of change
                change_percent = (np.count_nonzero(diff) / diff.size) * 100
                
                return change_percent > self.change_threshold
                
            except Exception as e:
                # print(f"Error detecting change: {e}") # Only for debug purposes
                return True
        except Exception as e:
            raise Exception(f"Error in _detect_change function: {e}")
    
    def _capture_screenshot(self, force=False) -> Path | None:
        """Capture a single screenshot"""

        try:
            try:
                # Capture the screen (specific area or full screen)
                if self.capture_area:
                    screenshot = ImageGrab.grab(bbox=self.capture_area)
                else:
                    screenshot = ImageGrab.grab()
                
                # Check for changes if enabled
                if self.change_detection and not force:
                    if not self._detect_change(screenshot):
                        return None
                
                # Check the minimum interval
                now = datetime.now()
                if self.last_capture_time and not force:
                    elapsed = (now - self.last_capture_time).total_seconds()
                    if elapsed < self.interval:
                        return None
                
                # Generate the filename
                filename = f"screenshot_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = self.output_dir / filename
                
                # Save the image (JPEG to save space)
                screenshot.save(filepath, 'JPEG', quality=self.quality, optimize=True)
                
                # Save metadata
                metadata = {
                    "timestamp": now.isoformat(),
                    "filename": filename,
                    "filepath": str(filepath),
                    "window": self._get_active_window(),
                    "resolution": f"{screenshot.width}x{screenshot.height}",
                    "change_detected": self.change_detection,
                    "capture_area": self.capture_area
                }
                
                self._save_metadata(metadata)
                
                # Update the previous screenshot
                self.previous_screenshot = screenshot
                self.last_capture_time = now
                
                return filepath
                
            except Exception as e:
                # print(f"Error capturing screenshot: {e}") # Only for debug purposes
                return None
        except Exception as e:
            raise Exception(f"Error in _capture_screenshot function: {e}")
    
    def _save_metadata(self, metadata) -> None:
        """Save screenshot metadata to JSON"""

        try:
            try:
                existing_data = json.loads(self.metadata_file.read_text(encoding="utf-8"))
                existing_data.append(metadata)
                
                self.metadata_file.write_text(
                    json.dumps(existing_data, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
            except Exception as e:
                pass
                # print(f"Error saving metadata: {e}") # Only for debug purposes
        except Exception as e:
            raise Exception(f"Error in _save_metadata function: {e}")
    
    def _capture_loop(self) -> None:
        """Main capture loop running in thread"""

        try:
            while self.running:
                if self.change_detection:
                    # Detection mode: check more frequently
                    self._capture_screenshot()
                    time.sleep(2)  # Check every 2s
                else:
                    # Fixed interval mode
                    self._capture_screenshot()
                    time.sleep(self.interval)
        except Exception as e:
            raise Exception(f"Error in _capture_loop function: {e}")
    
    def start(self) -> None:
        """Start capturing screenshots"""

        try:
            if self.running:
                return
            
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
        except Exception as e:
            raise Exception(f"Error in start function: {e}")
    
    def stop(self) -> None:
        """Stop capturing screenshots"""

        try:
            self.running = False
            
            if self.capture_thread:
                self.capture_thread.join(timeout=5)
        except Exception as e:
            raise Exception(f"Error in stop function: {e}")
        
    def capture_now(self) -> None:
        """Capture a single screenshot immediately"""
        
        try:
            return self._capture_screenshot(force=True)
        except Exception as e:
            raise Exception(f"Error in capture_now function: {e}")
    
    def capture_window(self, window_title) :
        """Capture a specific window by title (bonus feature)"""

        try:
            try:
                import win32gui
                import win32ui
                import win32con
                
                hwnd = win32gui.FindWindow(None, window_title)
                if not hwnd:
                    return None
                
                # Get window dimensions
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                # Capture the window
                hwndDC = win32gui.GetWindowDC(hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
                
                # Convert to PIL Image
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                screenshot = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
                
                # Cleanup
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                return screenshot
                
            except Exception as e:
                # print(f"Error capturing window: {e}") # Only for debug purposes
                return None
        except Exception as e:
            raise Exception(f"Error in capture_window function: {e}")