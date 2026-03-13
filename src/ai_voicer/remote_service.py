import os

import httpx


class RemoteTranscriptionService:
    def __init__(self, backend_url: str, api_token: str | None = None):
        self.backend_url = backend_url.rstrip("/")
        self.api_token = api_token

    def transcribe_and_structure_file(self, audio_path: str) -> tuple[str, str]:
        headers: dict[str, str] = {}
        if self.api_token:
            headers["x-api-key"] = self.api_token

        with open(audio_path, "rb") as file_obj:
            files = {"audio": (os.path.basename(audio_path), file_obj, "audio/wav")}
            response = httpx.post(
                f"{self.backend_url}/v1/transcribe",
                headers=headers,
                files=files,
                params={"structured": "true"},
                timeout=120.0,
            )
        if response.status_code >= 400:
            detail = response.text.strip()
            raise RuntimeError(
                f"Backend transcription failed ({response.status_code}): {detail}"
            )
        payload = response.json()
        transcript = payload.get("transcript", "") or ""
        text = payload.get("text", "") or transcript
        return transcript, text
