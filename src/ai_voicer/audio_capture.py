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
        self._lock = threading.Lock()
        self._audio_chunks: list[bytes] = []
        self._stream: Optional[sd.InputStream] = None
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _audio_callback(self, indata, frames, callback_time, status) -> None:
        del frames, callback_time, status
        with self._lock:
            if self._recording:
                self._audio_chunks.append(indata.copy().tobytes())

    def start(self) -> None:
        with self._lock:
            self._audio_chunks = []
            self._stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype="int16",
                callback=self._audio_callback,
            )
            self._stream.start()
            self._recording = True

    def stop_to_wav(self) -> Optional[str]:
        with self._lock:
            stream = self._stream
            self._stream = None
            self._recording = False
            chunks = list(self._audio_chunks)
            self._audio_chunks = []

        if stream is not None:
            try:
                stream.stop()
            finally:
                stream.close()

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
        with self._lock:
            stream = self._stream
            self._stream = None
            self._recording = False
            self._audio_chunks = []

        if stream is not None:
            try:
                stream.stop()
            finally:
                stream.close()
