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
