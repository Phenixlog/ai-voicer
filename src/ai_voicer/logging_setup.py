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
