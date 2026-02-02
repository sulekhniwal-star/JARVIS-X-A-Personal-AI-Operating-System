from typing import Any, List
"""Speech-to-text functionality."""

import numpy as np
import sounddevice as sd  # type: ignore
import time
from faster_whisper import WhisperModel  # type: ignore
from config import DEFAULT_LANGUAGE
from utils.logger import logger


class SpeechToText:
    """Class for speech-to-text using faster-whisper."""

    def __init__(self):
        """Initialize the SpeechToText class with faster-whisper model."""
        try:
            self.model: Any = WhisperModel("base", device="cpu", compute_type="int8")
            self.language = DEFAULT_LANGUAGE
            self.supported_languages = ["en", "hi", "auto"]  # English, Hindi, Auto-detect
        except Exception as e:
            logger.error(f"Error initializing WhisperModel: {e}")
            raise

    def set_language(self, lang_code: str):
        """Set the language for speech recognition."""
        if lang_code in self.supported_languages:
            self.language = lang_code
        else:
            logger.warning(f"Unsupported language: {lang_code}. Using auto-detect.")
            self.language = "auto"

    def listen(self) -> str:
        """Capture audio and transcribe to text.

        Returns:
            str: Recognized text in lowercase.
        """
        try:
            samplerate = 16000
            silence_threshold = 0.01
            timeout = 10  # seconds
            chunk_duration = 0.5  # seconds
            audio_chunks: List[Any] = []

            def callback(indata: Any, frames: Any, time_info: Any, status: Any) -> None:
                if status:
                    logger.warning(f"Sounddevice status: {status}")
                audio_chunks.append(indata.copy())

            with sd.InputStream(samplerate=samplerate, channels=1, callback=callback):  # type: ignore
                start_time = time.time()
                last_audio_time = start_time

                while time.time() - start_time < timeout:
                    time.sleep(chunk_duration)
                    if audio_chunks:
                        # Check RMS of the last chunk for silence
                        rms = np.sqrt(np.mean(audio_chunks[-1]**2))  # type: ignore
                        if rms > silence_threshold:
                            last_audio_time = time.time()
                        elif time.time() - last_audio_time > 1.0:  # 1 second of silence
                            break

            if not audio_chunks:
                logger.warning("No audio recorded.")
                return ""

            audio = np.concatenate(audio_chunks).flatten()

            # Transcribe with language detection
            lang = None if self.language == "auto" else self.language
            segments, info = self.model.transcribe(audio, language=lang)
            text = " ".join([segment.text for segment in segments]).strip()

            # Log detected language for auto mode
            if self.language == "auto" and hasattr(info, 'language'):
                logger.info(f"Detected language: {info.language}")

            return text.lower()

        except Exception as e:
            logger.error(f"Error in listen method: {e}")
            return ""
