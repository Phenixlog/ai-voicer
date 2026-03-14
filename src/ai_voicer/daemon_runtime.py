import logging
import os
import queue
import signal
import threading
import time
import traceback
from typing import Union

from pynput import keyboard
from Quartz import CGEventSourceKeyState, kCGEventSourceStateHIDSystemState

from .audio_capture import AudioCaptureConfig, HoldToRecordCapture
from .config import AppConfig
from .macos_audio_duck import SystemAudioDucker
from .macos_paste import paste_text_to_active_app
from .mistral_service import MistralTranscriptionService
from .logging_setup import log_transcription
from .status_overlay import OverlayConfig, StatusOverlay


# macOS virtual key codes for modifier keys (left + right variants)
_MODIFIER_KEYCODES: dict[str, list[int]] = {
    "alt": [0x3A, 0x3D],       # left option, right option
    "cmd": [0x37, 0x36],       # left cmd, right cmd
    "ctrl": [0x3B, 0x3E],      # left ctrl, right ctrl
    "shift": [0x38, 0x3C],     # left shift, right shift
}

# Map hotkey to all matching pynput Key variants (left, right, generic)
_MODIFIER_GROUPS: dict[keyboard.Key, list[keyboard.Key]] = {
    keyboard.Key.alt: [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr],
    keyboard.Key.cmd: [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r],
    keyboard.Key.ctrl: [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r],
    keyboard.Key.shift: [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r],
}


def resolve_hotkey(hotkey_name: str) -> Union[keyboard.Key, keyboard.KeyCode]:
    if len(hotkey_name) == 1:
        return keyboard.KeyCode.from_char(hotkey_name)
    key_attr = hotkey_name
    if hotkey_name in {"cmd", "command"}:
        key_attr = "cmd"
    if hotkey_name == "option":
        key_attr = "alt"
    if hotkey_name == "return":
        key_attr = "enter"
    key = getattr(keyboard.Key, key_attr, None)
    if key is None:
        raise ValueError(f"Unsupported hotkey: {hotkey_name}")
    return key


def _quartz_key_attr(hotkey_name: str) -> str:
    if hotkey_name in {"cmd", "command"}:
        return "cmd"
    if hotkey_name == "option":
        return "alt"
    return hotkey_name


def is_key_physically_pressed(hotkey_name: str) -> bool:
    """Check physical key state via macOS Quartz — the ground truth."""
    attr = _quartz_key_attr(hotkey_name)
    codes = _MODIFIER_KEYCODES.get(attr)
    if codes:
        return any(
            CGEventSourceKeyState(kCGEventSourceStateHIDSystemState, code)
            for code in codes
        )
    return True


def key_matches(current: keyboard.Key, target: Union[keyboard.Key, keyboard.KeyCode]) -> bool:
    """Match key event handling left/right modifier variants."""
    if isinstance(target, keyboard.KeyCode):
        return isinstance(current, keyboard.KeyCode) and current.char == target.char
    group = _MODIFIER_GROUPS.get(target)
    if group:
        return current in group
    return current == target


class PushToTalkDaemon:
    def __init__(self, config: AppConfig, service_override=None):
        self.config = config
        if service_override is not None:
            self.service = service_override
            logging.info("Daemon mode: injected transcription service.")
        else:
            self.service = MistralTranscriptionService(config)
            logging.info("Daemon mode: local direct Mistral.")
        self.capture = HoldToRecordCapture(
            AudioCaptureConfig(
                sample_rate=config.sample_rate,
                channels=config.channels,
                min_seconds=config.min_seconds,
            )
        )
        self.hotkey = resolve_hotkey(config.hotkey)
        self.audio_ducker = SystemAudioDucker(enabled=config.duck_output_audio)
        self.overlay = StatusOverlay(OverlayConfig(enabled=config.hud_enabled))
        self.stopped = threading.Event()
        self.job_queue: queue.Queue[str] = queue.Queue()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._last_press_ts = 0.0
        self._debounce_s = 0.15
        # Lock to prevent concurrent _stop_and_queue calls from multiple threads
        self._stop_lock = threading.Lock()
        # Failsafe: cap at configured max (default 120s)
        self._max_record_seconds = max(0.0, float(config.max_record_seconds))
        self._recording_started_at: float | None = None
        self._overlay_is_recording = False  # track overlay state for desync detection

    def start(self) -> None:
        logging.info(
            "Daemon started. Hotkey='%s' mode='%s'. Failsafe=%ds.",
            self.config.hotkey,
            self.config.trigger_mode,
            int(self._max_record_seconds),
        )
        self.worker.start()
        self.overlay.start()
        self.listener.start()
        while not self.stopped.is_set():
            self._check_recording_failsafe()
            self._check_overlay_desync()
            time.sleep(0.25)

    def stop(self) -> None:
        logging.info("Stopping daemon.")
        self.stopped.set()
        try:
            self.listener.stop()
        except Exception:
            pass
        self.capture.stop_discard()
        self._recording_started_at = None
        self.audio_ducker.restore()
        self.overlay.stop()

    def _on_press(self, key) -> None:
        if not key_matches(key, self.hotkey):
            return
        now = time.monotonic()

        if self.config.trigger_mode == "toggle":
            if (now - self._last_press_ts) < self._debounce_s:
                return
            self._last_press_ts = now
            if self.capture.is_recording:
                self._stop_and_queue()
            else:
                self._start_recording()
            return

        # Hold mode: debounce press to prevent ghost starts
        if (now - self._last_press_ts) < self._debounce_s:
            return
        self._last_press_ts = now

        if self.capture.is_recording:
            logging.warning("Recovery: press while recording, forcing stop.")
            self._stop_and_queue()
        else:
            self._start_recording()

    def _on_release(self, key) -> None:
        if not key_matches(key, self.hotkey):
            return
        if self.config.trigger_mode == "toggle":
            return
        if self.capture.is_recording:
            logging.info("Key release detected via pynput.")
            self._stop_and_queue()

    def _start_recording(self) -> None:
        try:
            self.audio_ducker.duck()
            self.capture.start()
            self._recording_started_at = time.monotonic()
            logging.info("Recording started.")
            self.overlay.recording()
            self._overlay_is_recording = True
            # Start Quartz polling as safety net for missed release events
            if self.config.trigger_mode == "hold":
                threading.Thread(
                    target=self._poll_key_release, daemon=True
                ).start()
        except Exception:
            logging.error("Failed to start recording:\n%s", traceback.format_exc())
            self.audio_ducker.restore()
            self._recording_started_at = None
            self._overlay_is_recording = False
            self.overlay.error("Erreur micro")

    def _poll_key_release(self) -> None:
        """Safety net: poll physical key state via macOS Quartz API."""
        try:
            time.sleep(0.2)  # grace period
            while self.capture.is_recording and not self.stopped.is_set():
                time.sleep(0.05)
                if not is_key_physically_pressed(self.config.hotkey):
                    if self.capture.is_recording:
                        logging.info("Key release detected via Quartz polling.")
                        self._stop_and_queue()
                    return
        except Exception:
            logging.error("Polling thread crashed:\n%s", traceback.format_exc())

    def _stop_and_queue(self) -> None:
        # Lock prevents double-stop from concurrent threads (wait up to 1s)
        if not self._stop_lock.acquire(timeout=1.0):
            logging.warning("_stop_and_queue: lock timeout — forcing overlay reset.")
            self._ensure_overlay_idle()
            return
        try:
            if not self.capture.is_recording:
                logging.debug("_stop_and_queue: already stopped, syncing overlay.")
                self._ensure_overlay_idle()
                return
            try:
                audio_path = self.capture.stop_to_wav()
            except Exception:
                logging.error("Failed to stop recording:\n%s", traceback.format_exc())
                try:
                    self.capture.stop_discard()
                except Exception:
                    logging.error("Failed to force-reset:\n%s", traceback.format_exc())
                self.audio_ducker.restore()
                self.overlay.error("Erreur audio")
                self._recording_started_at = None
                self._overlay_is_recording = False
                return
            self.audio_ducker.restore()
            self._recording_started_at = None
            self._overlay_is_recording = False
            if audio_path:
                logging.info("Recording stopped. Queued for transcription.")
                self.job_queue.put(audio_path)
                self.overlay.transcribing()
            else:
                logging.info("Recording ignored (too short or empty).")
                self.overlay.ready("Trop court")
        finally:
            self._stop_lock.release()

    def _ensure_overlay_idle(self) -> None:
        """Reset overlay if recording is not active — prevents HUD desync."""
        if not self.capture.is_recording:
            self.audio_ducker.restore()
            self._recording_started_at = None
            self._overlay_is_recording = False
            self.overlay.ready()

    def _check_recording_failsafe(self) -> None:
        if self._max_record_seconds <= 0:
            return
        if not self.capture.is_recording:
            return
        if self._recording_started_at is None:
            self._recording_started_at = time.monotonic()
            return

        elapsed = time.monotonic() - self._recording_started_at
        if elapsed < self._max_record_seconds:
            return

        logging.warning(
            "Failsafe: force-stopping after %.1fs without release.",
            elapsed,
        )
        self._stop_and_queue()

    def _check_overlay_desync(self) -> None:
        """If overlay shows recording but capture is idle, force reset."""
        if self._overlay_is_recording and not self.capture.is_recording:
            logging.warning("Overlay desync detected: HUD shows recording but capture is idle. Resetting.")
            self._ensure_overlay_idle()

    def _worker_loop(self) -> None:
        while not self.stopped.is_set():
            try:
                audio_path = self.job_queue.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                transcript, final_text = self.service.transcribe_and_structure_file(audio_path)
                latency_total = getattr(self.service, "last_latency_ms", None)
                latency_transcribe = getattr(self.service, "last_transcribe_ms", None)
                latency_structure = getattr(self.service, "last_structure_ms", None)
                if latency_total is not None:
                    logging.info(
                        "Latency: total=%sms transcribe=%sms structure=%sms",
                        latency_total,
                        latency_transcribe if latency_transcribe is not None else "n/a",
                        latency_structure if latency_structure is not None else "n/a",
                    )
                if not transcript.strip():
                    logging.info("Empty transcript.")
                    self.overlay.ready("Vide")
                    continue
                log_transcription(transcript, final_text)
                paste_text_to_active_app(final_text)
                logging.info("Text pasted: %s", final_text[:80])
                self.overlay.ready("Collé")
            except Exception:
                logging.error("Worker failed:\n%s", traceback.format_exc())
                self.overlay.error("Echec")
            finally:
                try:
                    os.remove(audio_path)
                except OSError:
                    pass


def run_daemon(config: AppConfig, service_override=None) -> None:
    daemon = PushToTalkDaemon(config, service_override=service_override)

    def handle_signal(sig, frame):
        del sig, frame
        daemon.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    daemon.start()
