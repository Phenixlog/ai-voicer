"""Serve static SaaS frontend pages (landing + app shell)."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()
WEB_DIR = Path(__file__).resolve().parents[2] / "web"
ASSETS_DIR = WEB_DIR / "assets"


@router.get("/", include_in_schema=False)
def landing() -> FileResponse:
    target = WEB_DIR / "landing.html"
    if not target.exists():
        raise HTTPException(status_code=404, detail="Landing page not found")
    return FileResponse(target)


@router.get("/app", include_in_schema=False)
def app_page() -> FileResponse:
    target = WEB_DIR / "app.html"
    if not target.exists():
        raise HTTPException(status_code=404, detail="App page not found")
    return FileResponse(target)


@router.get("/assets/{file_path:path}", include_in_schema=False)
def static_asset(file_path: str) -> FileResponse:
    target = (ASSETS_DIR / file_path).resolve()
    if not str(target).startswith(str(ASSETS_DIR.resolve())) or not target.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(target)
