from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import threading
from dataclasses import dataclass


@dataclass
class OverlayConfig:
    enabled: bool


class StatusOverlay:
    """Controls a separate HUD process to avoid GUI main-thread issues."""

    def __init__(self, config: OverlayConfig):
        self.config = config
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        if not self.config.enabled:
            return
        if self._proc and self._proc.poll() is None:
            return

        script_path = os.path.join(os.path.dirname(__file__), "hud_process.py")
        try:
            # Cleanup potential orphan HUD helper from previous runs.
            subprocess.run(
                ["pkill", "-f", "ai_voicer/hud_process.py"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._proc = subprocess.Popen(
                [sys.executable, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
        except Exception:
            logging.warning("HUD disabled: failed to launch HUD process.")
            self._proc = None

    def stop(self) -> None:
        self._send("close")
        proc = self._proc
        self._proc = None
        if not proc:
            return
        try:
            proc.terminate()
        except Exception:
            pass

    def recording(self) -> None:
        self._send("recording", "Ecoute...")

    def transcribing(self) -> None:
        self._send("transcribing", "Transcription...")

    def ready(self, text: str = "Pret") -> None:
        self._send("ready", text)

    def error(self, text: str = "Erreur") -> None:
        self._send("error", text)

    def _send(self, state: str, text: str | None = None) -> None:
        proc = self._proc
        if not proc or proc.poll() is not None or not proc.stdin:
            return

        payload = json.dumps({"state": state, "text": text}, ensure_ascii=True)
        with self._lock:
            try:
                proc.stdin.write(payload + "\n")
                proc.stdin.flush()
            except Exception:
                pass
