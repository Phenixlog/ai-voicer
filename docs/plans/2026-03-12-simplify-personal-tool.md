# AI Voicer — Simplification Outil Perso

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transformer AI Voicer en outil perso fiable : hold Option → parle → relâche → texte collé. Zéro SaaS.

**Architecture:** Daemon Python local qui écoute le hotkey Option (hold), enregistre l'audio, transcrit via Mistral API directement, et colle le texte. Logs des transcriptions dans `~/.ai-voicer/`.

**Tech Stack:** Python, pynput, sounddevice, Mistral SDK, osascript (macOS paste)

---

### Task 1: Simplifier config.py

**Files:**
- Modify: `src/ai_voicer/config.py`

**Step 1: Remove SaaS fields from AppConfig**

Remove these fields: `api_auth_token`, `api_host`, `api_port`, `backend_url`, `backend_api_key`.
Change default hotkey from `"f8"` to `"option"`.

```python
@dataclass
class AppConfig:
    mistral_api_key: str | None
    transcribe_model: str
    structure_model: str
    language: str | None
    context_bias: str | None
    enable_structuring: bool
    sample_rate: int
    channels: int
    min_seconds: float
    hotkey: str
    trigger_mode: str
    max_record_seconds: float
    log_level: str
    hud_enabled: bool
    duck_output_audio: bool
```

**Step 2: Simplify load_config()**

```python
def load_config() -> AppConfig:
    load_dotenv()
    api_key = read_str("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY is missing. Set it in .env.")

    return AppConfig(
        mistral_api_key=api_key,
        transcribe_model=read_str("AI_VOICER_TRANSCRIBE_MODEL", "voxtral-mini-latest"),
        structure_model=read_str("AI_VOICER_STRUCTURE_MODEL", "mistral-small-latest"),
        language=(read_str("AI_VOICER_LANGUAGE") or None),
        context_bias=(read_str("AI_VOICER_CONTEXT_BIAS") or None),
        enable_structuring=read_bool("AI_VOICER_ENABLE_STRUCTURING", True),
        sample_rate=int(read_str("AI_VOICER_SAMPLE_RATE", "16000")),
        channels=int(read_str("AI_VOICER_CHANNELS", "1")),
        min_seconds=float(read_str("AI_VOICER_MIN_SECONDS", "0.25")),
        hotkey=read_str("AI_VOICER_HOTKEY", "option").lower(),
        trigger_mode=read_str("AI_VOICER_TRIGGER_MODE", "hold").lower(),
        max_record_seconds=float(read_str("AI_VOICER_MAX_RECORD_SECONDS", "120")),
        log_level=read_str("AI_VOICER_LOG_LEVEL", "INFO").upper(),
        hud_enabled=read_bool("AI_VOICER_HUD_ENABLED", True),
        duck_output_audio=read_bool("AI_VOICER_DUCK_OUTPUT_AUDIO", True),
    )
```

**Step 3: Commit**

```bash
git add src/ai_voicer/config.py
git commit -m "simplify: remove SaaS fields, default hotkey to option"
```

---

### Task 2: Fix hold-mode ghost triggering with debounce

**Files:**
- Modify: `src/ai_voicer/daemon_runtime.py`

**Root cause:** pynput on macOS fires duplicate/phantom press events for modifier keys (Option/Alt, Shift). The current recovery logic with `_hold_key_is_down` and `_hold_recovery_press_gap_s` is too complex and gets desynchronized, causing the daemon to re-trigger recording on its own.

**Fix:** Replace all the complex hold-mode state tracking with a simple timestamp-based debounce. The key insight: we only need to track TWO things:
1. Are we currently recording?
2. When did the last event happen? (debounce < 150ms = ignore)

**Step 1: Rewrite _on_press and _on_release**

Replace the entire hold-mode logic in `_on_press` and `_on_release` with:

```python
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
        # Simple debounce: ignore events closer than 150ms apart.
        self._last_event_ts = 0.0
        self._debounce_s = 0.15
        # Failsafe timeout
        self._max_record_seconds = max(0.0, float(config.max_record_seconds))
        self._recording_started_at: float | None = None

    def _on_press(self, key) -> None:
        if not key_matches(key, self.hotkey):
            return
        now = time.monotonic()
        if (now - self._last_event_ts) < self._debounce_s:
            return
        self._last_event_ts = now

        if self.config.trigger_mode == "toggle":
            if self.capture.is_recording:
                self._stop_and_queue()
            else:
                self._start_recording()
            return

        # Hold mode: press = start recording (if not already)
        if not self.capture.is_recording:
            self._start_recording()

    def _on_release(self, key) -> None:
        if not key_matches(key, self.hotkey):
            return
        now = time.monotonic()
        if (now - self._last_event_ts) < self._debounce_s:
            return
        self._last_event_ts = now

        if self.config.trigger_mode == "toggle":
            return

        # Hold mode: release = stop recording
        if self.capture.is_recording:
            self._stop_and_queue()
```

**Step 2: Simplify stop() method**

```python
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
```

**Step 3: Commit**

```bash
git add src/ai_voicer/daemon_runtime.py
git commit -m "fix: replace complex hold-mode logic with simple debounce"
```

---

### Task 3: Fix paste reliability

**Files:**
- Modify: `src/ai_voicer/macos_paste.py`

**Root cause:** The 150ms sleep is too short — the active app doesn't always process the Cmd+V before the clipboard is restored to its previous value. Also, no retry if paste fails.

**Step 1: Rewrite paste function**

```python
import logging
import subprocess
import time


def paste_text_to_active_app(text: str) -> None:
    """Copy text to clipboard, simulate Cmd+V, then restore previous clipboard."""
    previous_clipboard = subprocess.run(
        ["pbpaste"], capture_output=True, text=True, check=False
    ).stdout

    subprocess.run(["pbcopy"], input=text, text=True, check=True)

    for attempt in range(2):
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to keystroke "v" using command down',
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            break
        logging.warning("Paste attempt %d failed: %s", attempt + 1, result.stderr.strip())
        time.sleep(0.3)

    # Wait for the target app to process the paste before restoring clipboard.
    time.sleep(0.4)
    subprocess.run(["pbcopy"], input=previous_clipboard, text=True, check=True)
```

**Step 2: Commit**

```bash
git add src/ai_voicer/macos_paste.py
git commit -m "fix: increase paste delay and add retry for reliability"
```

---

### Task 4: Add transcription file logging

**Files:**
- Modify: `src/ai_voicer/logging_setup.py`
- Modify: `src/ai_voicer/daemon_runtime.py` (worker loop)

**Step 1: Add file logging + transcription logger**

```python
import logging
import os
from datetime import datetime


LOG_DIR = os.path.expanduser("~/.ai-voicer")


def setup_logging(level: str) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

    # File handler for all daemon logs
    daemon_log = logging.FileHandler(os.path.join(LOG_DIR, "daemon.log"))
    daemon_log.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))
    root.addHandler(console)
    root.addHandler(daemon_log)


def log_transcription(transcript: str, final_text: str) -> None:
    """Append transcription to ~/.ai-voicer/transcriptions.log for recovery."""
    path = os.path.join(LOG_DIR, "transcriptions.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n--- {timestamp} ---\n")
        if transcript != final_text:
            f.write(f"[brut] {transcript}\n")
        f.write(f"{final_text}\n")
```

**Step 2: Use log_transcription in worker loop**

In `daemon_runtime.py`, add import and call in `_worker_loop`:

```python
from .logging_setup import log_transcription
```

In `_worker_loop`, after successful transcription:

```python
                if not transcript.strip():
                    logging.info("Empty transcript.")
                    self.overlay.ready("Vide")
                    continue
                log_transcription(transcript, final_text)
                paste_text_to_active_app(final_text)
                logging.info("Text pasted: %s", final_text[:80])
                self.overlay.ready("Collé")
```

**Step 3: Commit**

```bash
git add src/ai_voicer/logging_setup.py src/ai_voicer/daemon_runtime.py
git commit -m "feat: add transcription logging to ~/.ai-voicer/ for text recovery"
```

---

### Task 5: Clean entry point

**Files:**
- Modify: `run.py` (create if needed, or use existing `run_daemon.py`)

**Step 1: Simplify run.py**

Use `run_daemon.py` as the sole entry point. It already does exactly what we need:

```python
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ai_voicer.config import load_config
from ai_voicer.daemon_runtime import run_daemon
from ai_voicer.logging_setup import setup_logging


def main() -> None:
    config = load_config()
    setup_logging(config.log_level)
    print(f"AI Voicer started. Hold [{config.hotkey}] to record. Logs: ~/.ai-voicer/")
    run_daemon(config)


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add run.py
git commit -m "simplify: single clean entry point"
```

---

### Task 6: Update .env

**Files:**
- Modify: `.env` (user's actual env file)
- Modify: `.env.example`

**Step 1: Ensure .env has minimal config**

```env
MISTRAL_API_KEY=your_key_here

# Hotkey: option, cmd, f8, etc.
AI_VOICER_HOTKEY=option
AI_VOICER_TRIGGER_MODE=hold
AI_VOICER_LANGUAGE=fr

# Optional
AI_VOICER_ENABLE_STRUCTURING=true
AI_VOICER_HUD_ENABLED=true
AI_VOICER_DUCK_OUTPUT_AUDIO=true
AI_VOICER_LOG_LEVEL=INFO
```

**Step 2: Commit**

```bash
git add .env.example
git commit -m "simplify: minimal .env for personal tool"
```

---

### Task 7: Test end-to-end

**Step 1: Run the daemon**

```bash
python run.py
```

Expected: `AI Voicer started. Hold [option] to record. Logs: ~/.ai-voicer/`

**Step 2: Test hold-to-talk**

1. Hold Option key → HUD shows "Ecoute..."
2. Say something
3. Release Option → HUD shows "Transcription..." then "Collé"
4. Text appears in active app

**Step 3: Verify no ghost triggering**

1. After text is pasted, wait 10 seconds
2. No recording should start on its own
3. Press and release Option quickly (< 0.25s) → should say "Trop court"

**Step 4: Check logs**

```bash
cat ~/.ai-voicer/transcriptions.log
cat ~/.ai-voicer/daemon.log
```

Transcriptions.log should contain the transcribed text with timestamps.
