import os
import tempfile
from typing import Annotated

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile

from .config import AppConfig
from .mistral_service import MistralTranscriptionService


def create_api_app(config: AppConfig) -> FastAPI:
    app = FastAPI(title="AI Voicer API", version="0.1.0")
    service = MistralTranscriptionService(config)

    def require_auth(x_api_key: Annotated[str | None, Header()] = None) -> None:
        if not config.api_auth_token:
            return
        if x_api_key != config.api_auth_token:
            raise HTTPException(status_code=401, detail="Invalid API key")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/transcribe")
    async def transcribe(
        _: Annotated[None, Depends(require_auth)],
        audio: UploadFile = File(...),
        structured: bool = True,
    ) -> dict[str, str]:
        suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(prefix="ai-voicer-api-", suffix=suffix, delete=False) as tmp:
            data = await audio.read()
            tmp.write(data)
            path = tmp.name

        try:
            transcript = service.transcribe_file(path)
            final_text = service.structure_text(transcript) if structured else transcript
            return {"transcript": transcript, "text": final_text}
        except Exception as exc:
            # Surface provider/network failures as 502 instead of opaque 500.
            raise HTTPException(
                status_code=502,
                detail=f"Upstream transcription error: {exc.__class__.__name__}",
            ) from exc
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    return app
