import os
import tempfile
import threading
import wave
from dataclasses import dataclass
from typing import Optional

import sounddevice as sd


@dataclass
class AudioCaptureConfig:
    sample_rate: int
    channels: int
    min_seconds: float


class HoldToRecordCapture:
    def __init__(self, config: AudioCaptureConfig):
        self.config = config
        self.audio_lock = threading.Lock()
        self.audio_chunks: list[bytes] = []
        self.stream: Optional[sd.InputStream] = None
        self.is_recording = False

    def _audio_callback(self, indata, frames, callback_time, status) -> None:
        del frames, callback_time, status
        with self.audio_lock:
            self.audio_chunks.append(indata.copy().tobytes())

    def start(self) -> None:
        with self.audio_lock:
            self.audio_chunks = []
        self.stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype="int16",
            callback=self._audio_callback,
        )
        self.stream.start()
        self.is_recording = True

    def stop_to_wav(self) -> Optional[str]:
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.stream = None
        self.is_recording = False

        with self.audio_lock:
            chunks = list(self.audio_chunks)
            self.audio_chunks = []

        if not chunks:
            return None

        raw_bytes = b"".join(chunks)
        duration = len(raw_bytes) / (2 * self.config.channels * self.config.sample_rate)
        if duration < self.config.min_seconds:
            return None

        fd, path = tempfile.mkstemp(prefix="ai-voicer-", suffix=".wav")
        os.close(fd)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(self.config.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.config.sample_rate)
            wf.writeframes(raw_bytes)
        return path

    def stop_discard(self) -> None:
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.stream = None
        self.is_recording = False
        with self.audio_lock:
            self.audio_chunks = []
