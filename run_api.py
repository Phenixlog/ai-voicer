#!/usr/bin/env python3
"""Backward-compatible entrypoint for Railway and local runs."""

import os

from run_saas_api import main as run_saas_api_main


def main() -> None:
    """Bridge legacy run_api.py usage to SaaS API server."""
    railway_port = os.getenv("PORT")
    if railway_port:
        # Railway requires binding to 0.0.0.0 and its injected PORT.
        os.environ.setdefault("AI_VOICER_API_HOST", "0.0.0.0")
        os.environ.setdefault("AI_VOICER_API_PORT", railway_port)

    run_saas_api_main()


if __name__ == "__main__":
    main()
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import uvicorn

from ai_voicer.api_server import create_api_app
from ai_voicer.config import load_config
from ai_voicer.logging_setup import setup_logging


def main() -> None:
    config = load_config()
    setup_logging(config.log_level)
    app = create_api_app(config)
    uvicorn.run(app, host=config.api_host, port=config.api_port)


if __name__ == "__main__":
    main()
