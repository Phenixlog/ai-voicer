import logging
import os
import queue
import signal
import threading
import time
import traceback
from typing import Union

from pynput import keyboard

from .audio_capture import AudioCaptureConfig, HoldToRecordCapture
from .config import AppConfig
from .macos_audio_duck import SystemAudioDucker
from .macos_paste import paste_text_to_active_app
from .mistral_service import MistralTranscriptionService
from .status_overlay import OverlayConfig, StatusOverlay


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


def key_matches(current: keyboard.Key, target: Union[keyboard.Key, keyboard.KeyCode]) -> bool:
    if isinstance(target, keyboard.KeyCode):
        return isinstance(current, keyboard.KeyCode) and current.char == target.char
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
        self._pressed_once = False
        # Hold mode safety latch:
        # if key release is missed by the OS, a new press force-stops recording.
        # then we ignore extra presses until the user releases once.
        self._hold_ignore_presses_until_release = False
        # Tracks the physical key-down state in hold mode to ignore OS key-repeat.
        self._hold_key_is_down = False
        # Time of last hotkey press event seen in hold mode.
        self._hold_last_press_ts = 0.0
        # Gap required to treat a new press as recovery for missed release.
        self._hold_recovery_press_gap_s = 0.8

    def start(self) -> None:
        logging.info(
            "Daemon started. Hotkey='%s' mode='%s'.",
            self.config.hotkey,
            self.config.trigger_mode,
        )
        self.worker.start()
        self.overlay.start()
        self.listener.start()
        while not self.stopped.is_set():
            time.sleep(0.25)

    def stop(self) -> None:
        logging.info("Stopping daemon.")
        self.stopped.set()
        self._hold_ignore_presses_until_release = False
        self._hold_key_is_down = False
        self._hold_last_press_ts = 0.0
        try:
            self.listener.stop()
        except Exception:
            pass
        self.capture.stop_discard()
        self.audio_ducker.restore()
        self.overlay.stop()

    def _on_press(self, key) -> None:
        if not key_matches(key, self.hotkey):
            return
        if self.config.trigger_mode == "toggle":
            if self._pressed_once:
                return
            self._pressed_once = True
            if self.capture.is_recording:
                self._stop_and_queue()
            else:
                self._start_recording()
            return

        now = time.monotonic()
        if self._hold_ignore_presses_until_release:
            self._hold_last_press_ts = now
            return

        if self._hold_key_is_down:
            # If release was missed, a fresh press after a short gap recovers safely.
            if (
                self.capture.is_recording
                and (now - self._hold_last_press_ts) >= self._hold_recovery_press_gap_s
            ):
                logging.warning(
                    "Hold mode recovery triggered: forcing stop after missed key release."
                )
                self._hold_last_press_ts = now
                self._stop_and_queue()
                self._hold_ignore_presses_until_release = True
                return
            # Ignore repeated on_press events while key is still held.
            self._hold_last_press_ts = now
            return
        self._hold_key_is_down = True
        self._hold_last_press_ts = now

        if self.capture.is_recording:
            logging.warning(
                "Hold mode fallback triggered: forcing stop after missed key release."
            )
            self._stop_and_queue()
            self._hold_ignore_presses_until_release = True
            return

        self._start_recording()

    def _on_release(self, key) -> None:
        if not key_matches(key, self.hotkey):
            return
        if self.config.trigger_mode == "toggle":
            self._pressed_once = False
            return
        self._hold_key_is_down = False
        self._hold_last_press_ts = 0.0
        if self._hold_ignore_presses_until_release:
            self._hold_ignore_presses_until_release = False
            return
        if not self.capture.is_recording:
            return
        self._stop_and_queue()

    def _start_recording(self) -> None:
        try:
            self.audio_ducker.duck()
            self.capture.start()
            logging.info("Recording started.")
            self.overlay.recording()
        except Exception:
            logging.error("Failed to start recording:\n%s", traceback.format_exc())
            self.audio_ducker.restore()
            self.overlay.error("Erreur micro")

    def _stop_and_queue(self) -> None:
        try:
            audio_path = self.capture.stop_to_wav()
        except Exception:
            logging.error("Failed to stop recording:\n%s", traceback.format_exc())
            self.audio_ducker.restore()
            return
        self.audio_ducker.restore()
        if audio_path:
            logging.info("Recording stopped. Queued for transcription.")
            self.job_queue.put(audio_path)
            self.overlay.transcribing()
        else:
            logging.info("Recording ignored (too short or empty).")
            self.overlay.ready("Trop court")

    def _worker_loop(self) -> None:
        while not self.stopped.is_set():
            try:
                audio_path = self.job_queue.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                transcript, final_text = self.service.transcribe_and_structure_file(audio_path)
                if not transcript.strip():
                    logging.info("Empty transcript.")
                    self.overlay.ready("Vide")
                    continue
                paste_text_to_active_app(final_text)
                logging.info("Text pasted in active app.")
                self.overlay.ready("Colle")
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
