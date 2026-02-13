#!/usr/bin/env python3
"""Run Théoria SaaS API Server."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import uvicorn
from ai_voicer.saas_api_server import create_saas_api_app
from ai_voicer.config import load_config
from ai_voicer.logging_setup import setup_logging


def main():
    config = load_config()
    if not config.mistral_api_key:
        raise RuntimeError("MISTRAL_API_KEY is required to run the SaaS API server.")
    setup_logging(config.log_level)
    
    app = create_saas_api_app()
    
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level=config.log_level.lower()
    )


if __name__ == "__main__":
    main()
