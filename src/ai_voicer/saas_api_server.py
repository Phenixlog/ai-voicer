"""Théoria SaaS API Server - extends base API with auth, billing, usage."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .logging_setup import setup_logging
from .config import load_config
from .saas.database import init_db
from .saas.billing import init_plans
from .saas.routes import router as saas_router
from .saas_web import router as web_router


def create_saas_api_app() -> FastAPI:
    """Create the SaaS API application."""
    config = load_config()
    setup_logging(config.log_level)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        init_db()
        init_plans()
        yield
        # Shutdown
        pass
    
    app = FastAPI(
        title="Théoria API",
        description="Voice-to-text SaaS API with auth, billing, and usage metering",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include SaaS API + web routes
    app.include_router(saas_router)
    app.include_router(web_router)
    
    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "version": "1.0.0", "mode": "saas"}
    
    return app
