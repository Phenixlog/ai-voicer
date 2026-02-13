import json
import logging
import os
import re
import time
from typing import Any

import httpx
from mistralai import Mistral

from .config import AppConfig


def _extract_transcript_text(response: Any) -> str:
    for attr in ("text", "transcript"):
        value = getattr(response, attr, None)
        if isinstance(value, str) and value.strip():
            return value.strip()

    dumped: dict[str, Any]
    if hasattr(response, "model_dump"):
        dumped = response.model_dump()
    elif isinstance(response, dict):
        dumped = response
    else:
        dumped = {}

    for key in ("text", "transcript"):
        value = dumped.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _extract_chat_text(response: Any) -> str:
    choices = getattr(response, "choices", None)
    if choices:
        first = choices[0]
        message = getattr(first, "message", None)
        if message is not None:
            content = getattr(message, "content", None)
            if isinstance(content, str):
                return content.strip()
            if isinstance(content, list):
                parts: list[str] = []
                for item in content:
                    txt = getattr(item, "text", None)
                    if isinstance(txt, str):
                        parts.append(txt)
                    elif isinstance(item, dict):
                        v = item.get("text")
                        if isinstance(v, str):
                            parts.append(v)
                if parts:
                    return "\n".join(parts).strip()
    if hasattr(response, "model_dump"):
        return json.dumps(response.model_dump(), ensure_ascii=True)
    return str(response)


class MistralTranscriptionService:
    def __init__(self, config: AppConfig):
        if not config.mistral_api_key:
            raise RuntimeError(
                "MISTRAL_API_KEY is required for local direct Mistral transcription mode."
            )
        self.config = config
        self.client = Mistral(api_key=config.mistral_api_key)

    def transcribe_file(self, audio_path: str) -> str:
        kwargs: dict[str, Any] = {"model": self.config.transcribe_model}
        if self.config.language:
            kwargs["language"] = self.config.language
        if self.config.context_bias:
            kwargs["context_bias"] = self.config.context_bias

        response = None
        for attempt in range(3):
            try:
                with open(audio_path, "rb") as file_obj:
                    response = self.client.audio.transcriptions.complete(
                        file={"content": file_obj, "file_name": os.path.basename(audio_path)},
                        **kwargs,
                    )
                break
            except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                if attempt == 2:
                    raise
                delay = 0.8 * (attempt + 1)
                logging.warning(
                    "Transient network error during transcription (%s). Retry in %.1fs.",
                    exc.__class__.__name__,
                    delay,
                )
                time.sleep(delay)

        return _extract_transcript_text(response)

    def structure_text(self, transcript: str) -> str:
        if not self.config.enable_structuring or not transcript.strip():
            return transcript

        response = None
        for attempt in range(3):
            try:
                response = self.client.chat.complete(
                    model=self.config.structure_model,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Tu es un moteur de nettoyage de transcription. "
                                "Tache: retourner UNIQUEMENT le texte final nettoye. "
                                "Interdictions strictes: ne jamais expliquer, commenter, "
                                "analyser, ajouter une preface, ajouter des parentheses, "
                                "ou decrire ce que tu fais. "
                                "Regles: conserver exactement le sens, corriger orthographe, "
                                "ponctuation et mise en forme, structurer legement si necessaire, "
                                "ne rien inventer."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                "Nettoie la transcription suivante et retourne uniquement "
                                "le texte final.\n\n"
                                f"{transcript}"
                            ),
                        },
                    ],
                )
                break
            except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                if attempt == 2:
                    raise
                delay = 0.8 * (attempt + 1)
                logging.warning(
                    "Transient network error during structuring (%s). Retry in %.1fs.",
                    exc.__class__.__name__,
                    delay,
                )
                time.sleep(delay)
        formatted = _extract_chat_text(response).strip()
        cleaned = self._strip_meta_artifacts(formatted)
        return cleaned or transcript

    def _strip_meta_artifacts(self, text: str) -> str:
        if not text:
            return text

        lines = text.splitlines()
        kept: list[str] = []
        for line in lines:
            normalized = line.strip().lower()
            # Remove common assistant meta markers occasionally produced by LLMs.
            if re.fullmatch(r"\[\s*fin du texte\s*\]", normalized):
                continue
            if re.fullmatch(r"\[\s*end of text\s*\]", normalized):
                continue
            if re.fullmatch(r"\(\s*fin du texte\s*\)", normalized):
                continue
            if re.fullmatch(r"\(\s*end of text\s*\)", normalized):
                continue
            kept.append(line)

        return "\n".join(kept).strip()

    def transcribe_and_structure_file(self, audio_path: str) -> tuple[str, str]:
        transcript = self.transcribe_file(audio_path)
        final_text = self.structure_text(transcript)
        return transcript, final_text
