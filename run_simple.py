#!/usr/bin/env python3
"""
AI Voicer - Version SIMPLE & ROBUSTE avec DEBOUNCE
"""

import os
import sys
import signal
import time
import traceback
import tempfile
import wave
import threading
import queue
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union

import sounddevice as sd
from pynput import keyboard
from mistralai import Mistral

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class Config:
    mistral_api_key: str
    hotkey: str = "shift_r"
    sample_rate: int = 16000
    channels: int = 1
    min_seconds: float = 0.3
    max_seconds: float = 90.0
    duck_audio: bool = True
    show_hud: bool = True
    log_file: Optional[Path] = None
    debounce_ms: float = 100.0  # Ignorer les appuis dans les 100ms après un événement


def load_config() -> Config:
    env_path = Path(__file__).parent / ".env"
    env = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip().split("#")[0].strip()
    
    api_key = env.get("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY manquante dans .env")
    
    hotkey = env.get("AI_VOICER_HOTKEY", "shift_r").lower()
    
    return Config(
        mistral_api_key=api_key,
        hotkey=hotkey,
        duck_audio=env.get("AI_VOICER_DUCK_OUTPUT_AUDIO", "true").lower() == "true",
        show_hud=env.get("AI_VOICER_HUD_ENABLED", "true").lower() == "true",
        log_file=Path.home() / "Library" / "Logs" / "ai-voicer" / "simple.log",
        debounce_ms=float(env.get("AI_VOICER_DEBOUNCE_MS", "100")),
    )


# =============================================================================
# LOGGING
# =============================================================================

def setup_logging(log_file: Optional[Path]):
    import logging
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.DEBUG,  # Debug pour voir les events fantômes
            format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")


# =============================================================================
# AUDIO CAPTURE
# =============================================================================

class AudioCapture:
    def __init__(self, config: Config):
        self.config = config
        self._lock = threading.Lock()
        self._chunks: list[bytes] = []
        self._stream: Optional[sd.InputStream] = None
        self.is_recording = False
        self._started_at: float = 0.0
    
    def _callback(self, indata, frames, time_info, status):
        with self._lock:
            self._chunks.append(indata.copy().tobytes())
    
    def start(self) -> bool:
        try:
            with self._lock:
                self._chunks = []
            
            self._stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype="int16",
                callback=self._callback,
                blocksize=1024,
            )
            self._stream.start()
            self.is_recording = True
            self._started_at = time.monotonic()
            return True
        except Exception as e:
            import logging
            logging.error(f"Failed to start recording: {e}")
            self._cleanup()
            return False
    
    def stop(self) -> Optional[str]:
        if not self.is_recording:
            return None
        
        self.is_recording = False
        self._cleanup()
        
        with self._lock:
            chunks = self._chunks
            self._chunks = []
        
        if not chunks:
            return None
        
        raw = b"".join(chunks)
        duration = len(raw) / (2 * self.config.channels * self.config.sample_rate)
        
        if duration < self.config.min_seconds:
            import logging
            logging.info(f"Recording too short: {duration:.2f}s")
            return None
        
        fd, path = tempfile.mkstemp(prefix="ai-voicer-", suffix=".wav")
        os.close(fd)
        
        try:
            with wave.open(path, "wb") as wf:
                wf.setnchannels(self.config.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.config.sample_rate)
                wf.writeframes(raw)
            import logging
            logging.info(f"Saved audio: {duration:.1f}s")
            return path
        except Exception as e:
            import logging
            logging.error(f"Failed to save WAV: {e}")
            try:
                os.unlink(path)
            except:
                pass
            return None
    
    def _cleanup(self):
        stream = self._stream
        self._stream = None
        if stream:
            try:
                stream.stop()
            except:
                pass
            try:
                stream.close()
            except:
                pass
    
    def get_duration(self) -> float:
        if not self.is_recording:
            return 0.0
        return time.monotonic() - self._started_at


# =============================================================================
# TRANSCRIPTION
# =============================================================================

class Transcriber:
    def __init__(self, api_key: str):
        self.client = Mistral(api_key=api_key)
    
    def transcribe(self, audio_path: str) -> tuple[str, str]:
        import logging
        
        logging.info("Transcribing...")
        t0 = time.time()
        
        with open(audio_path, "rb") as f:
            response = self.client.audio.transcriptions.complete(
                model="voxtral-mini-latest",
                file={"content": f, "file_name": os.path.basename(audio_path)},
                language="fr",
            )
        
        transcript = self._extract_text(response)
        t1 = time.time()
        logging.info(f"Transcription: {t1-t0:.1f}s")
        
        if not transcript.strip():
            return "", ""
        
        logging.info("Structuring...")
        response = self.client.chat.complete(
            model="mistral-small-latest",
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu nettoies une transcription vocale. "
                        "Corrige l'orthographe, ajoute la ponctuation. "
                        "RETOURNE UNIQUEMENT LE TEXTE NETTOYÉ."
                    ),
                },
                {"role": "user", "content": transcript},
            ],
        )
        
        structured = self._extract_chat_text(response).strip()
        t2 = time.time()
        logging.info(f"Structuring: {t2-t1:.1f}s")
        
        return transcript, structured or transcript
    
    def _extract_text(self, response) -> str:
        for attr in ("text", "transcript"):
            val = getattr(response, attr, None)
            if isinstance(val, str):
                return val
        if hasattr(response, "model_dump"):
            data = response.model_dump()
            return data.get("text", "")
        return ""
    
    def _extract_chat_text(self, response) -> str:
        choices = getattr(response, "choices", [])
        if choices:
            msg = getattr(choices[0].message, "content", "")
            return str(msg) if msg else ""
        return ""


# =============================================================================
# PASTE
# =============================================================================

def paste_text(text: str, max_retries: int = 3) -> bool:
    import logging
    
    try:
        old_clipboard = subprocess.run(
            ["pbpaste"], capture_output=True, text=True, timeout=5
        ).stdout
    except:
        old_clipboard = ""
    
    for attempt in range(max_retries):
        try:
            subprocess.run(
                ["pbcopy"], input=text, text=True, check=True, timeout=5
            )
            break
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to copy: {e}")
                return False
            time.sleep(0.1)
    
    for attempt in range(max_retries):
        try:
            subprocess.run(
                ["osascript", "-e", 
                 'tell application "System Events" to keystroke "v" using command down'],
                check=True, timeout=5
            )
            break
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to paste: {e}")
                subprocess.run(["pbcopy"], input=old_clipboard, text=True, check=False)
                return False
            time.sleep(0.1)
    
    time.sleep(0.2)
    subprocess.run(["pbcopy"], input=old_clipboard, text=True, check=False)
    return True


# =============================================================================
# AUDIO DUCK
# =============================================================================

class AudioDuck:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self._was_muted: Optional[bool] = None
        self._volume: int = 50
    
    def duck(self):
        if not self.enabled:
            return
        try:
            result = subprocess.run(
                ["osascript", "-e", "get volume settings"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                output = result.stdout.lower()
                for part in output.split(","):
                    if "output volume:" in part:
                        self._volume = int(part.split(":")[1].strip())
                    if "muted:" in part:
                        self._was_muted = "true" in part
            
            subprocess.run(
                ["osascript", "-e", "set volume output muted true"],
                check=False, timeout=5
            )
        except Exception as e:
            import logging
            logging.warning(f"Audio duck failed: {e}")
    
    def restore(self):
        if not self.enabled or self._was_muted is None:
            return
        try:
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {self._volume}"],
                check=False, timeout=5
            )
            muted_str = "true" if self._was_muted else "false"
            subprocess.run(
                ["osascript", "-e", f"set volume output muted {muted_str}"],
                check=False, timeout=5
            )
        except Exception as e:
            import logging
            logging.warning(f"Audio restore failed: {e}")


# =============================================================================
# HUD
# =============================================================================

class SimpleHUD:
    def __init__(self, enabled: bool):
        self.enabled = enabled
    
    def recording(self):
        if self.enabled:
            self._notify("🎙️ Écoute...", f"Max {Config.max_seconds}s")
    
    def transcribing(self):
        if self.enabled:
            self._notify("⏳ Transcription...", "Traitement...")
    
    def done(self):
        if self.enabled:
            self._notify("✅ Collé !", "", sound=False)
    
    def error(self, msg: str):
        if self.enabled:
            self._notify("❌ Erreur", msg)
    
    def _notify(self, title: str, subtitle: str, sound: bool = True):
        try:
            script = f'display notification "{subtitle}" with title "{title}"'
            if sound:
                script += ' sound name "Glass"'
            subprocess.run(
                ["osascript", "-e", script],
                check=False, capture_output=True, timeout=5
            )
        except:
            pass


# =============================================================================
# DAEMON AVEC DEBOUNCE ET PROTECTION ANTI-FANTÔME
# =============================================================================

class VoicerDaemon:
    """
    Daemon avec protection contre les events fantômes.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.transcriber = Transcriber(config.mistral_api_key)
        self.capture = AudioCapture(config)
        self.duck = AudioDuck(config.duck_audio)
        self.hud = SimpleHUD(config.show_hud)
        
        self._stopped = threading.Event()
        self._job_queue: queue.Queue[str] = queue.Queue()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        
        # Hotkey
        self._hotkey = self._parse_hotkey(config.hotkey)
        self._listener: Optional[keyboard.Listener] = None
        
        # === PROTECTIONS ANTI-FANTÔME ===
        self._last_press_time: float = 0.0
        self._last_release_time: float = 0.0
        self._debounce_seconds = config.debounce_ms / 1000.0
        self._press_count = 0  # Compteur pour détecter les patterns bizarres
        
        import logging
        logging.info(f"Hotkey: {config.hotkey}")
        logging.info(f"Debounce: {config.debounce_ms}ms")
    
    def _parse_hotkey(self, key: str):
        key = key.lower().strip()
        
        mapping = {
            "shift_r": keyboard.Key.shift_r,
            "right_shift": keyboard.Key.shift_r,
            "rshift": keyboard.Key.shift_r,
            "shift_l": keyboard.Key.shift_l,
            "left_shift": keyboard.Key.shift_l,
            "lshift": keyboard.Key.shift_l,
            "shift": keyboard.Key.shift_l,
            "cmd_r": keyboard.Key.cmd_r,
            "right_cmd": keyboard.Key.cmd_r,
            "rcmd": keyboard.Key.cmd_r,
            "cmd_l": keyboard.Key.cmd_l,
            "left_cmd": keyboard.Key.cmd_l,
            "lcmd": keyboard.Key.cmd_l,
            "cmd": keyboard.Key.cmd,
            "command": keyboard.Key.cmd,
            "alt_r": keyboard.Key.alt_r,
            "right_alt": keyboard.Key.alt_r,
            "ralt": keyboard.Key.alt_r,
            "option_r": keyboard.Key.alt_r,
            "alt_l": keyboard.Key.alt_l,
            "left_alt": keyboard.Key.alt_l,
            "lalt": keyboard.Key.alt_l,
            "alt": keyboard.Key.alt,
            "option": keyboard.Key.alt,
            "ctrl_r": keyboard.Key.ctrl_r,
            "right_ctrl": keyboard.Key.ctrl_r,
            "rctrl": keyboard.Key.ctrl_r,
            "ctrl_l": keyboard.Key.ctrl_l,
            "left_ctrl": keyboard.Key.ctrl_l,
            "lctrl": keyboard.Key.ctrl_l,
            "ctrl": keyboard.Key.ctrl,
            "control": keyboard.Key.ctrl,
            "caps_lock": keyboard.Key.caps_lock,
            "capslock": keyboard.Key.caps_lock,
            "esc": keyboard.Key.esc,
            "escape": keyboard.Key.esc,
            "f1": keyboard.Key.f1,
            "f2": keyboard.Key.f2,
            "f3": keyboard.Key.f3,
            "f4": keyboard.Key.f4,
            "f5": keyboard.Key.f5,
            "f6": keyboard.Key.f6,
            "f7": keyboard.Key.f7,
            "f8": keyboard.Key.f8,
            "f9": keyboard.Key.f9,
            "f10": keyboard.Key.f10,
            "f11": keyboard.Key.f11,
            "f12": keyboard.Key.f12,
        }
        
        if key in mapping:
            return mapping[key]
        
        if len(key) == 1:
            return keyboard.KeyCode.from_char(key)
        
        try:
            return getattr(keyboard.Key, key)
        except AttributeError:
            raise ValueError(f"Hotkey non supportée: {key}. "
                           f"Essayez: shift_r, shift_l, cmd_r, cmd_l, alt_r, esc, caps_lock, f1-f12")
    
    def _key_matches(self, current) -> bool:
        if current == self._hotkey:
            return True
        if isinstance(self._hotkey, keyboard.KeyCode) and isinstance(current, keyboard.KeyCode):
            return current.char == self._hotkey.char
        return False
    
    def _on_press(self, key):
        import logging
        
        if not self._key_matches(key):
            return
        
        now = time.monotonic()
        time_since_last_press = now - self._last_press_time
        time_since_last_release = now - self._last_release_time
        
        self._press_count += 1
        
        # === DÉTECTION DES EVENTS FANTÔMES ===
        
        # 1. Debounce: ignorer si on a eu un événement récent
        if time_since_last_press < self._debounce_seconds:
            logging.debug(f"DEBOUNCE: Ignoring press ({time_since_last_press*1000:.1f}ms since last)")
            return
        
        # 2. Event fantôme: appui qui arrive juste après un relâchement (moins de 50ms)
        # C'est typique d'un sticky key ou d'un remapping bizarre
        if time_since_last_release < 0.05 and self._last_release_time > 0:
            logging.warning(f"GHOST DETECTED: Press {time_since_last_release*1000:.1f}ms after release, ignoring")
            return
        
        # 3. Déjà en cours d'enregistrement = double-activation bizarre
        if self.capture.is_recording:
            logging.warning(f"Already recording, ignoring press #{self._press_count}")
            return
        
        # === DÉMARRAGE LÉGITIME ===
        self._last_press_time = now
        logging.info(f">>> PRESS #{self._press_count} ACCEPTED <<<")
        
        self.duck.duck()
        if self.capture.start():
            self.hud.recording()
            logging.info("Recording started")
        else:
            self.duck.restore()
            self.hud.error("Micro inaccessible")
    
    def _on_release(self, key):
        import logging
        
        if not self._key_matches(key):
            return
        
        now = time.monotonic()
        self._last_release_time = now
        
        # Temps depuis l'appui
        press_duration = now - self._last_press_time if self._last_press_time > 0 else 0
        
        logging.info(f">>> RELEASE (pressed for {press_duration:.2f}s) <<<")
        
        if not self.capture.is_recording:
            logging.debug("Release but not recording, ignoring")
            return
        
        # Arrêter et traiter
        self.duck.restore()
        audio_path = self.capture.stop()
        
        if audio_path:
            logging.info(f"Audio captured, queuing")
            self.hud.transcribing()
            self._job_queue.put(audio_path)
        else:
            logging.info("No audio (too short)")
    
    def _worker(self):
        import logging
        
        while not self._stopped.is_set():
            try:
                audio_path = self._job_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            
            try:
                _, text = self.transcriber.transcribe(audio_path)
                
                if text.strip():
                    if paste_text(text):
                        logging.info("SUCCESS: Text pasted")
                        self.hud.done()
                    else:
                        logging.error("FAILED: Paste failed")
                        self.hud.error("Collage échoué")
                else:
                    logging.info("Empty transcript")
                    self.hud.error("Rien entendu")
                    
            except Exception as e:
                logging.error(f"Transcription failed: {e}")
                self.hud.error("Erreur transcription")
            
            finally:
                try:
                    os.unlink(audio_path)
                except:
                    pass
    
    def run(self):
        import logging
        
        logging.info("=" * 50)
        logging.info("AI Voicer Simple - Starting")
        logging.info("=" * 50)
        
        self._worker_thread.start()
        
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=False,
        )
        self._listener.start()
        
        logging.info(f"🎙️  Hotkey: {self.config.hotkey}")
        logging.info(f"⏱️   Max duration: {self.config.max_seconds}s")
        logging.info(f"🛡️  Debounce: {self.config.debounce_ms}ms")
        logging.info("")
        logging.info("👉 Appuie et MAINTIENS la hotkey pour parler")
        logging.info("👉 Relâche pour envoyer")
        logging.info("")
        logging.info("Press Ctrl+C to quit")
        
        # Boucle avec failsafe max duration
        while not self._stopped.is_set():
            if self.capture.is_recording:
                duration = self.capture.get_duration()
                if duration > self.config.max_seconds:
                    logging.warning(f"MAX DURATION ({duration:.1f}s), forcing stop")
                    self._on_release(self._hotkey)
            
            time.sleep(0.2)
    
    def stop(self):
        import logging
        logging.info("Stopping...")
        
        self._stopped.set()
        self.capture.stop()
        self.duck.restore()
        
        if self._listener:
            self._listener.stop()


# =============================================================================
# MAIN
# =============================================================================

def main():
    config = load_config()
    setup_logging(config.log_file)
    
    daemon = VoicerDaemon(config)
    
    def on_signal(sig, frame):
        daemon.stop()
    
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)
    
    try:
        daemon.run()
    except Exception as e:
        import logging
        logging.error(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
