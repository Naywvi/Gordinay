"""
Audio Recording Feature Module - Record class for audio capture and processing - For Educational Use Only
"""

from scipy.io.wavfile import write
from datetime import datetime
import sounddevice as sd
import numpy as np
import asyncio, queue

class Record:
    '''Audio Recording feature class'''
    
    def __init__(
        self, 
        sample_rate=44100, 
        channels=1,
        threshold=0.02,
        mode="stream",  # "stream" ou "file"
        chunk_duration=0.5
    ) -> None:
        """
        Initialize audio recorder
        
        Args:
            sample_rate: Sampling rate (default 44100 Hz)
            channels: Number of channels (1 = mono, 2 = stereo)
            threshold: Automatic sound detection threshold
            mode: "stream" to send in real-time, "file" to record
            chunk_duration: Duration of each audio segment sent (streaming)
        """
        try: 
            self.sample_rate = sample_rate
            self.channels = channels
            self.threshold = threshold
            self.mode = mode
            self.chunk_duration = chunk_duration
            self.chunk_size = int(sample_rate * chunk_duration)
            
            # État
            self.is_active = False
            self.is_recording = False
            self.stream = None
            
            # Stockage
            self.audio_queue = queue.Queue()
            self.recorded_chunks = []
            
            # Callback pour streaming
            self.on_audio_chunk = None
            
            # Stats
            self.total_duration = 0
            self.chunks_sent = 0
            
            # Task de traitement
            self._processing_task = None
        except Exception as e:
            raise Exception("Record Init Error in __init__ function - " + str(e))
        
    def set_callback(self, callback) -> None:
        """Set the callback function for streaming"""

        self.on_audio_chunk = callback
    
    def _audio_callback(self, indata, frames, time, status) -> None:
        """Internal callback called by sounddevice"""

        try:
            if status:
                # print(f"Audio status: {status}")
                pass
            
            if not self.is_active:
                return
            
            # Calculate the volume (RMS)
            volume = np.linalg.norm(indata) * 10
            
            # Automatic sound detection
            if volume > self.threshold:
                if not self.is_recording:
                    self.is_recording = True
                
                # Add to queue
                self.audio_queue.put((indata.copy(), volume, time.currentTime))
            else:
                if self.is_recording and volume < self.threshold * 0.5:
                    self.is_recording = False
        except Exception as e:
            raise Exception("Record Audio Callback Error in _audio_callback function - " + str(e))
    
    async def start(self) -> None:
        """Start recording"""

        try:
            if self.is_active:
                return
            
            self.is_active = True
            self.is_recording = False
            self.recorded_chunks = []
            self.chunks_sent = 0
            
            # Start audio stream
            self.stream = sd.InputStream(
                callback=self._audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size
            )
            self.stream.start()
            
            # Start asynchronous processing
            self._processing_task = asyncio.create_task(self._process_audio())
        except Exception as e:
            raise Exception("Record Start Error in start function - " + str(e))
    
    async def stop(self) -> None:
        """Stop recording"""

        try: 
            if not self.is_active:
                return
            
            self.is_active = False
            self.is_recording = False
            
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            # wait for processing task to finish
            if self._processing_task:
                await asyncio.sleep(0.5)
                self._processing_task = None
            
            # If file mode, save recording
            if self.mode == "file" and self.recorded_chunks:
                await self._save_recording()
        except Exception as e:
            raise Exception("Record Stop Error in stop function - " + str(e))
    
    async def _process_audio(self) -> None:
        """Process audio chunks in the background"""

        try:
            while self.is_active:
                try:
                    if not self.audio_queue.empty():
                        audio_data, volume, timestamp = self.audio_queue.get_nowait()
                        
                        if self.mode == "stream":
                            await self._handle_stream(audio_data, volume, timestamp)
                        elif self.mode == "file":
                            self.recorded_chunks.append(audio_data)
                        
                        self.chunks_sent += 1
                        self.total_duration += self.chunk_duration
                    
                    await asyncio.sleep(0.01)
                    
                except queue.Empty:
                    await asyncio.sleep(0.1)
                except Exception as e:
                    # print(f"❌ Audio processing error: {e}") # For debug
                    pass 
        except Exception as e:
            raise Exception("Record Processing Error in _process_audio function - " + str(e))
    
    async def _handle_stream(self, audio_data, volume, timestamp) -> None:
        """Handle audio streaming"""

        try:
            if self.on_audio_chunk:
                try:
                    chunk_info = {
                        'timestamp': timestamp,
                        'volume': float(volume),
                        'duration': self.chunk_duration,
                        'sample_rate': self.sample_rate,
                        'channels': self.channels
                    }
                    
                    await self.on_audio_chunk(audio_data, chunk_info)
                    
                except Exception as e:
                    # print(f"Erreur callback streaming: {e}") # For debug
                    pass
        except Exception as e:
            raise Exception("Record Streaming Error in _handle_stream function - " + str(e))
    
    async def _save_recording(self) -> None:
        """save recorded audio to WAV file"""

        try:
            if not self.recorded_chunks:
                return
            
            try:
                audio_data = np.concatenate(self.recorded_chunks, axis=0)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.wav"
                
                write(filename, self.sample_rate, audio_data)
                
                # duration = len(audio_data) / self.sample_rate
                
            except Exception as e:
                # print(f"Erreur sauvegarde: {e}") # For debug
                pass
        except Exception as e:
            raise Exception("Record Save Error in _save_recording function - " + str(e))
    
    def get_stats(self) -> dict:
        """Obtain recording statistics"""
        return {
            'is_active': self.is_active,
            'is_recording': self.is_recording,
            'mode': self.mode,
            'chunks_sent': self.chunks_sent,
            'total_duration': self.total_duration,
            'sample_rate': self.sample_rate
        }
    
    @staticmethod
    def calibrate_threshold(duration=3) -> float:
        """Calibrate the automatic detection threshold"""
        
        try:
            audio = sd.rec(int(duration * 44100), samplerate=44100, channels=1)
            sd.wait()
            
            volume = np.linalg.norm(audio) * 10
            recommended_threshold = volume * 2.5
            
            return recommended_threshold
        except Exception as e:
            raise Exception("Record Calibrate Error in calibrate_threshold function - " + str(e))
    
    async def test_record():
        """Simple test of the recorder"""
        
        try:
            # Callback that displays what it receives
            async def show_audio_info(audio_data, chunk_info):
                # print(f"AUDIO RECEIVED! Volume: {chunk_info['volume']:.3f}, Time: {chunk_info['timestamp']:.2f}s")
                pass
            
            # Create the recorder
            recorder = Record(
                mode="stream",
                threshold=0.02,  # Low threshold for testing
                chunk_duration=0.5
            )
            
            recorder.set_callback(show_audio_info)
            
        
            await recorder.start()
            
            # let it run for 10 seconds
            for i in range(10):
                await asyncio.sleep(1)
                # stats = recorder.get_stats()
                # print(f"[{i+1}s] Chunks reçus: {stats['chunks_sent']}, Durée totale: {stats['total_duration']:.1f}s, Recording: {'x' if stats['is_recording'] else '+'}")
            
            await recorder.stop()
            
            # Résumé
            # final_stats = recorder.get_stats()
            # print(f"\n=== RÉSUMÉ ===")
            # print(f"Total chunks: {final_stats['chunks_sent']}")
            # print(f"Durée totale: {final_stats['total_duration']:.1f}s")
        except Exception as e:
            raise Exception("Record Test Error in test_record function - " + str(e))