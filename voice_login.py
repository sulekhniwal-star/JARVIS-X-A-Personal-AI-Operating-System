import sounddevice as sd
import librosa
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity


class VoiceLogin:
    def __init__(self):
        self.reference_path = "voice_ref.npy"
        self.sample_rate = 22050
        self.duration = 3
    
    def _record_voice(self) -> np.ndarray:
        """Record voice sample."""
        try:
            print("Recording voice... Please speak for 3 seconds.")
            audio = sd.rec(int(self.duration * self.sample_rate), 
                          samplerate=self.sample_rate, 
                          channels=1, 
                          dtype='float64')
            sd.wait()
            return audio.flatten()
        except Exception:
            return np.array([])
    
    def _extract_mfcc(self, audio: np.ndarray) -> np.ndarray:
        """Extract MFCC features from audio."""
        try:
            mfccs = librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=13)
            return np.mean(mfccs.T, axis=0)
        except Exception:
            return np.array([])
    
    def _setup_reference(self):
        """Record and save reference voice."""
        try:
            print("Setting up voice authentication...")
            audio = self._record_voice()
            if len(audio) > 0:
                mfcc = self._extract_mfcc(audio)
                if len(mfcc) > 0:
                    np.save(self.reference_path, mfcc)
                    return True
        except Exception:
            pass
        return False
    
    def authenticate(self) -> bool:
        """Authenticate user using voice recognition."""
        try:
            # Setup reference if not exists
            if not os.path.exists(self.reference_path):
                if not self._setup_reference():
                    return False
            
            # Load reference
            reference_mfcc = np.load(self.reference_path)
            
            # Record live voice
            audio = self._record_voice()
            if len(audio) == 0:
                return False
            
            # Extract MFCC from live voice
            live_mfcc = self._extract_mfcc(audio)
            if len(live_mfcc) == 0:
                return False
            
            # Compute cosine similarity
            similarity = cosine_similarity([reference_mfcc], [live_mfcc])[0][0]
            
            return similarity > 0.75
            
        except Exception:
            return False