import re
import subprocess
from dataclasses import dataclass


@dataclass
class VolumeState:
    output_volume: int
    output_muted: bool


class SystemAudioDucker:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self._previous_state: VolumeState | None = None
        self._is_ducked = False

    def duck(self) -> None:
        if not self.enabled or self._is_ducked:
            return
        state = self._read_volume_state()
        if state is None:
            return
        self._previous_state = state
        subprocess.run(
            ["osascript", "-e", "set volume output muted true"],
            check=False,
            capture_output=True,
            text=True,
        )
        self._is_ducked = True

    def restore(self) -> None:
        if not self.enabled or not self._is_ducked:
            return
        prev = self._previous_state
        if prev is not None:
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {prev.output_volume}"],
                check=False,
                capture_output=True,
                text=True,
            )
            muted = "true" if prev.output_muted else "false"
            subprocess.run(
                ["osascript", "-e", f"set volume output muted {muted}"],
                check=False,
                capture_output=True,
                text=True,
            )
        self._is_ducked = False

    def _read_volume_state(self) -> VolumeState | None:
        proc = subprocess.run(
            ["osascript", "-e", "get volume settings"],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return None
        raw = proc.stdout.strip().lower()
        volume_match = re.search(r"output volume:(\d+)", raw)
        muted_match = re.search(r"output muted:(true|false)", raw)
        if not volume_match or not muted_match:
            return None
        return VolumeState(
            output_volume=int(volume_match.group(1)),
            output_muted=(muted_match.group(1) == "true"),
        )
