"""
Audio Recorder - Record audio from microphone
For educational purposes only - For Educational Use Only
"""

from pathlib import Path
from datetime import datetime
import sounddevice as sd
import numpy as np
import threading, time, json ,wave

class AudioRecorder:
    """Record audio from system microphone"""
    
    def __init__(self, output_dir="logs/audio", duration=10, sample_rate=44100, channels=1) -> None:
        """
        Initialize audio recorder
        Args:
            output_dir: Directory to save recordings
            duration: Duration of each recording in seconds
            sample_rate: Audio sample rate (Hz)
            channels: Number of audio channels (1=mono, 2=stereo)
        """

        try:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self.duration = duration
            self.sample_rate = sample_rate
            self.channels = channels
            
            self.recording = False
            self.thread = None
            self.current_recording = None
            
            # Check available devices
            self._check_devices()
        except Exception as e:
            raise Exception(f"AudioRecorder initialization error in __init__ function: {e}")
    
    def _check_devices(self) -> None:
        """Check available audio input devices"""
        #Uncomment for debugging

        try:
            try:
                devices = sd.query_devices()
                # print(f"[*] Available audio devices: {len(devices)}")
                
                # Find default input device
                default_input = sd.query_devices(kind='input')
                # print(f"[*] Default input device: {default_input['name']}")
                
            except Exception as e:
                pass
                # print(f"[!] Error checking audio devices: {e}") # Only for debug
        except Exception as e:
            raise Exception(f"AudioRecorder initialization error in _check_devices function: {e}")
    
    def start(self, continuous=True, interval=60) -> None:
        """
        Start audio recording
        Args:
            continuous: If True, record continuously with interval
            interval: Seconds between recordings (if continuous)
        """
        #Uncomment for debugging

        try:
            if self.recording:
                # print("[!] Audio recorder already running")
                return
            
            self.recording = True
            
            if continuous:
                self.thread = threading.Thread(
                    target=self._continuous_recording,
                    args=(interval,),
                    daemon=True
                )
            else:
                self.thread = threading.Thread(
                    target=self._single_recording,
                    daemon=True
                )
            
            self.thread.start()
            # print(f"[+] Audio recorder started (duration: {self.duration}s)")
        except Exception as e:
            raise Exception(f"AudioRecorder start error in start function: {e}")
    
    def stop(self) -> None:
        """Stop audio recording"""
        #Uncomment for debugging

        try:
            self.recording = False
            
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2)
            # print("[+] Audio recorder stopped")
        except Exception as e:
            raise Exception(f"AudioRecorder stop error in stop function: {e}")
    
    def record_now(self) -> Path:
        """
        Record audio immediately (blocking)
        Returns:
            Path: Path to saved audio file
        """
        # Let's not overdo it, these are the tries :)

        return self._record()
    
    def _continuous_recording(self, interval: int) -> None:
        """Continuous recording loop"""
        #Uncomment for debugging

        try:
            while self.recording:
                try:
                    self._record()
                    # filepath = self._record() # /!\ must be replaced by self._record() if this line is uncommented
                    # print(f"[+] Audio recorded: {filepath}")
                    
                    # Wait interval before next recording
                    time.sleep(interval)
                
                except Exception as e:
                    # print(f"[!] Recording error: {e}") # Only for debug
                    time.sleep(5)
        except Exception as e:
            raise Exception(f"AudioRecorder error in _continuous_recording function: {e}")
    
    def _single_recording(self) -> None:
        """Single recording"""
        #Uncomment for debugging

        try:
            try:
                self._record()
                # filepath = self._record() # /!\ must be replaced by self._record() if this line is uncommented
                # print(f"[+] Audio recorded: {filepath}")
            except Exception as e:
                # print(f"[!] Recording error: {e}") # Only for debug
                pass
        except Exception as e:
            raise Exception(f"AudioRecorder error in _single_recording function: {e}")
    
    def _record(self) -> Path:
        """
        Record audio
        Returns:
            Path: Path to saved audio file
        """
        #Uncomment for debugging

        try:
            # print(f"[*] Recording audio for {self.duration} seconds...")
            
            # Record audio
            recording = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16'
            )
            
            # Wait for recording to complete
            sd.wait()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.wav"
            filepath = self.output_dir / filename
            
            # Save as WAV file
            self._save_wav(filepath, recording)
            
            # Save metadata
            self._save_metadata(filepath, recording)
            
            # print(f"[+] Audio saved: {filepath}")
            return filepath
        
        except Exception as e:
            raise Exception(f"AudioRecorder error in _record function: {e}")
            
    
    def _save_wav(self, filepath, audio_data) -> None:
        """
        Save audio data as WAV file
        Args:
            filepath: Path to save file
            audio_data: Numpy array of audio data
        """

        try:
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio (2 bytes)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
        except Exception as e:
            raise Exception(f"AudioRecorder error in _save_wav function: {e}")
    
    def _save_metadata(self, filepath, audio_data) -> None:
        """
        Save recording metadata
        Args:
            filepath: Path to audio file
            audio_data: Numpy array of audio data
        """

        try:
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'filepath': str(filepath),
                'filename': filepath.name,
                'duration': self.duration,
                'sample_rate': self.sample_rate,
                'channels': self.channels,
                'format': 'WAV',
                'size_bytes': filepath.stat().st_size if filepath.exists() else 0,
                'samples': len(audio_data),
                'max_amplitude': int(np.max(np.abs(audio_data))),
                'mean_amplitude': float(np.mean(np.abs(audio_data)))
            }
            
            # Save metadata JSON
            metadata_file = filepath.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            raise Exception(f"AudioRecorder error in _save_metadata function: {e}")
    
    def get_device_info(self) -> dict:
        """
        Get information about audio devices
        Returns:
            dict: Device information
        """

        try:
            try:
                devices = sd.query_devices()
                default_input = sd.query_devices(kind='input')
                
                return {
                    'success': True,
                    'devices': [
                        {
                            'name': dev['name'],
                            'channels': dev['max_input_channels'],
                            'sample_rate': dev['default_samplerate']
                        }
                        for dev in devices if dev['max_input_channels'] > 0
                    ],
                    'default_device': default_input['name'],
                    'default_sample_rate': default_input['default_samplerate']
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        except Exception as e:
            raise Exception(f"AudioRecorder error in get_device_info function: {e}")


class AudioRecorderAdvanced:
    """
    Advanced audio recorder with voice activity detection
    """
    
    def __init__(self, output_dir="logs/audio", threshold=500, sample_rate=44100) -> None:
        """
        Initialize advanced audio recorder
        Args:
            output_dir: Directory to save recordings
            threshold: Voice activity detection threshold
            sample_rate: Audio sample rate
        """

        try:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            self.threshold = threshold
            self.sample_rate = sample_rate
            self.channels = 1
            
            self.recording = False
            self.stream = None
            self.audio_buffer = []
        except Exception as e:
            raise Exception(f"AudioRecorderAdvanced initialization error in __init__ function: {e}")
    
    def start_vad_recording(self, callback=None) -> None:
        """
        Start recording with voice activity detection
        Args:
            callback: Function to call when audio is detected
        """

        try:
            self.recording = True
            self.audio_buffer = []
            
            def audio_callback(indata, status) -> None:
                """Callback for audio stream"""

                try:
                    if status:
                        # print(f"[!] Audio stream status: {status}") # Only for debug
                        pass
                    
                    # Calculate volume
                    volume = np.linalg.norm(indata) * 10
                    
                    # If volume exceeds threshold, record
                    if volume > self.threshold:
                        self.audio_buffer.append(indata.copy())
                        
                        # If buffer is large enough, save
                        if len(self.audio_buffer) > self.sample_rate * 3 / 1024:  # 3 seconds
                            self._save_buffer()
                            if callback:
                                callback(self.current_recording)
                except Exception as e:
                    raise Exception(f"AudioRecorderAdvanced error in audio_callback function: {e}")
            
            try:
                self.stream = sd.InputStream(
                    channels=self.channels,
                    samplerate=self.sample_rate,
                    callback=audio_callback
                )
                self.stream.start()
                # print("[+] Voice activity detection started")
            
            except Exception as e:
                # print(f"[!] Error starting VAD: {e}") # Only for debug
                pass
        except Exception as e:
            raise Exception(f"AudioRecorderAdvanced error in start_vad_recording function: {e}")

    def stop_vad_recording(self) -> None:
        """Stop voice activity detection recording"""

        try:
            self.recording = False
            
            if self.stream:
                self.stream.stop()
                self.stream.close()
        
            # Save any remaining buffer
            if self.audio_buffer:
                self._save_buffer()
            
            # print("[+] Voice activity detection stopped")
        except Exception as e:
            raise Exception(f"AudioRecorderAdvanced error in stop_vad_recording function: {e}")
    
    def _handle_audio_record(self, duration=10, **kwargs) -> dict:
        """Handle audio record command (single recording)"""
        #Uncomment for debugging

        try:
            from __app__.client_app.features.audioRecorder.main import AudioRecorder
            from datetime import datetime
            
            try:
                # Parse duration parameter
                duration = int(duration) if duration else 10
                
                # print(f"[*] Recording audio for {duration} seconds...")
                
                # Create recorder instance
                recorder = AudioRecorder(
                    output_dir="logs/audio",
                    duration=duration
                )
                
                # Record NOW (blocking call)
                filepath = recorder.record_now()
                
                # print(f"[+] Audio recorded successfully: {filepath}")
                
                # RETURN result with 'type' field
                result = {
                    'success': True,
                    'type': 'audio_record_result',  # ← CRITICAL !
                    'filepath': str(filepath),
                    'duration': duration,
                    'timestamp': datetime.now().isoformat()
                }
                
                print(f"[DEBUG] Returning result: {result}")
                
                return result
            
            except Exception as e:
                # print(f"[!] Audio recording failed: {e}")
                import traceback
                traceback.print_exc()
                
                # RETURN error with 'type' field
                result = {
                    'success': False,
                    'type': 'audio_record_result',  # ← CRITICAL !
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
                # print(f"[DEBUG] Returning error result: {result}")
                
                return result
        except Exception as e:
            raise Exception(f"AudioRecorderAdvanced error in _handle_audio_record function: {e}")
        
    def _save_buffer(self) -> None:
        """Save audio buffer to file"""

        try:
            if not self.audio_buffer:
                return
            
            try:
                # Concatenate buffer
                audio_data = np.concatenate(self.audio_buffer, axis=0)
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vad_audio_{timestamp}.wav"
                filepath = self.output_dir / filename
                
                # Save
                with wave.open(str(filepath), 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_data.tobytes())
                
                self.current_recording = filepath
                self.audio_buffer = []
                
                print(f"[+] VAD audio saved: {filepath}")
            
            except Exception as e:
                # print(f"[!] Error saving buffer: {e}") # Only for debug
                pass
        except Exception as e:
            raise Exception(f"AudioRecorderAdvanced error in _save_buffer function: {e}")
        
        