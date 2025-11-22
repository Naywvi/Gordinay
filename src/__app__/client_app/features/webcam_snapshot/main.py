"""
Webcam snapshot feature with motion detection for ClientApp - For Educational Use Only.
"""

from datetime import datetime
from pathlib import Path
import threading, time, cv2, json

class Webcam:
    '''Webcam snapshot feature class with motion detection'''
    
    def __init__(self, output_dir="snapshots", interval=30, camera_index=0, 
                 motion_detection=False, motion_threshold=2000) -> None:
        """
        Initialize the webcam capture
        Args:
            output_dir: Directory to save snapshots
            interval: Seconds between snapshots (or min interval if motion detection)
            camera_index: Camera device index (0 = default webcam)
            motion_detection: Capture only when motion is detected
            motion_threshold: Sensitivity for motion detection (lower = more sensitive)
        """
        try:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self.interval = interval
            self.camera_index = camera_index
            self.motion_detection = motion_detection
            self.motion_threshold = motion_threshold
            self.running = False
            self.capture_thread = None
            self.camera = None
            self.previous_frame = None
            self.last_capture_time = None
            
            #  Metadata file
            self.metadata_file = self.output_dir / "metadata.json"
            if not self.metadata_file.exists():
                self.metadata_file.write_text("[]", encoding="utf-8")
        except Exception as e:
            raise Exception(f"Error initializing Webcam in __init__ function: {e}")
    
    def _get_active_window(self) -> str:
        """Get the title of the active window"""

        try:
            try:
                import ctypes
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
    
    def _detect_motion(self, frame):
        """Detect if there's motion in the frame"""

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # If no previous frame, no motion detected
            if self.previous_frame is None:
                self.previous_frame = gray
                return False
            
            # Calculate the difference
            frame_delta = cv2.absdiff(self.previous_frame, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            
            # Dilate to fill in holes
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            # Count non-zero pixels
            motion_pixels = cv2.countNonZero(thresh)
            
            # Update the previous frame
            self.previous_frame = gray
            
            return motion_pixels > self.motion_threshold
        except Exception as e:
            raise Exception(f"Error detecting motion in _detect_motion function: {e}")
    
    def _capture_snapshot(self, force=False) -> Path | None:
        """Capture a single snapshot"""

        try:
            try:
                # Open the camera if not already opened
                if self.camera is None or not self.camera.isOpened():
                    self.camera = cv2.VideoCapture(self.camera_index)
                    if not self.camera.isOpened():
                        return None
                    # Warmup
                    for _ in range(5):
                        self.camera.read()
                
                # Capture the image
                ret, frame = self.camera.read()
                if not ret:
                    return None
                
                # Check motion if enabled
                if self.motion_detection and not force:
                    if not self._detect_motion(frame):
                        return None
                
                # Check minimum interval
                now = datetime.now()
                if self.last_capture_time and not force:
                    elapsed = (now - self.last_capture_time).total_seconds()
                    if elapsed < self.interval:
                        return None
                
                # Generate the filename
                filename = f"snapshot_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = self.output_dir / filename
                
                # Save the image
                cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                
                # Save metadata
                metadata = {
                    "timestamp": now.isoformat(),
                    "filename": filename,
                    "filepath": str(filepath),
                    "window": self._get_active_window(),
                    "camera_index": self.camera_index,
                    "motion_detected": self.motion_detection
                }
                
                self._save_metadata(metadata)
                self.last_capture_time = now
                
                return filepath
                
            except Exception as e:
                return None
        except Exception as e:
            raise Exception(f"Error capturing snapshot in _capture_snapshot function: {e}")
    
    def _save_metadata(self, metadata) -> None:
        """Save snapshot metadata to JSON"""

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
                #print(f"Error saving metadata: {e}") # Silently ignore metadata save errors only for debugging (development purpose)
        except Exception as e:
            raise Exception(f"Error saving metadata in _save_metadata function: {e}")
    
    def _capture_loop(self) -> None:
        """Main capture loop running in thread"""

        try:
            while self.running:
                if self.motion_detection:
                    # Detection mode: check more frequently
                    self._capture_snapshot()
                    time.sleep(0.5)  # Check every 0.5s
                else:
                    # Fixed interval mode
                    self._capture_snapshot()
                    time.sleep(self.interval)
        except Exception as e:
            raise Exception(f"Error in _capture_loop function: {e}")
    
    def start(self) -> None:
        """Start capturing snapshots"""

        try:
            if self.running:
                return
            
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
        except Exception as e:
            raise Exception(f"Error starting webcam snapshot in start function: {e}")
    
    def stop(self) -> None:
        """Stop capturing snapshots"""

        try:
            self.running = False
            
            if self.capture_thread:
                self.capture_thread.join(timeout=5)
            
            if self.camera:
                self.camera.release()
                self.camera = None
        except Exception as e:
            raise Exception(f"Error stopping webcam snapshot in stop function: {e}")
    
    def capture_now(self) -> None:
        """Capture a single snapshot immediately"""

        try:
            return self._capture_snapshot(force=True)
        except Exception as e:
            raise Exception(f"Error capturing snapshot immediately in capture_now function: {e}")