import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class AppConfig:
    mistral_api_key: str | None
    transcribe_model: str
    structure_model: str
    language: str | None
    context_bias: str | None
    enable_structuring: bool
    sample_rate: int
    channels: int
    min_seconds: float
    hotkey: str
    trigger_mode: str
    max_record_seconds: float
    log_level: str
    hud_enabled: bool
    duck_output_audio: bool


def read_bool(name: str, default: bool) -> bool:
    raw = read_str(name, str(default)).lower()
    return raw in {"1", "true", "yes", "on"}


def read_str(name: str, default: str = "") -> str:
    raw = os.getenv(name, default)
    # Guard against inline comments inside env values, e.g.:
    # KEY=  # comment
    cleaned = raw.split("#", 1)[0].strip()
    return cleaned


def load_config() -> AppConfig:
    load_dotenv()
    api_key = read_str("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY is missing. Set it in .env.")

    return AppConfig(
        mistral_api_key=api_key,
        transcribe_model=read_str("AI_VOICER_TRANSCRIBE_MODEL", "voxtral-mini-latest"),
        structure_model=read_str("AI_VOICER_STRUCTURE_MODEL", "mistral-small-latest"),
        language=(read_str("AI_VOICER_LANGUAGE") or None),
        context_bias=(read_str("AI_VOICER_CONTEXT_BIAS") or None),
        enable_structuring=read_bool("AI_VOICER_ENABLE_STRUCTURING", True),
        sample_rate=int(read_str("AI_VOICER_SAMPLE_RATE", "16000")),
        channels=int(read_str("AI_VOICER_CHANNELS", "1")),
        min_seconds=float(read_str("AI_VOICER_MIN_SECONDS", "0.25")),
        hotkey=read_str("AI_VOICER_HOTKEY", "option").lower(),
        trigger_mode=read_str("AI_VOICER_TRIGGER_MODE", "hold").lower(),
        max_record_seconds=float(read_str("AI_VOICER_MAX_RECORD_SECONDS", "120")),
        log_level=read_str("AI_VOICER_LOG_LEVEL", "INFO").upper(),
        hud_enabled=read_bool("AI_VOICER_HUD_ENABLED", True),
        duck_output_audio=read_bool("AI_VOICER_DUCK_OUTPUT_AUDIO", True),
    )
