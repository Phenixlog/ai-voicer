#!/usr/bin/env python3
"""Run Theoria desktop control app."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Ensure relative files (.env, scripts) resolve against repository root.
os.chdir(str(ROOT))

from ai_voicer.desktop.app import launch_desktop_app


def main() -> None:
    launch_desktop_app(project_root=ROOT)


if __name__ == "__main__":
    main()
