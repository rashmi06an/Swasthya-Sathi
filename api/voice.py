from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from tempfile import NamedTemporaryFile

from gtts import gTTS
from transformers import pipeline

from api.config import get_settings


@lru_cache
def get_asr_pipeline():
    settings = get_settings()
    return pipeline(
        task="automatic-speech-recognition",
        model=settings.whisper_model,
        chunk_length_s=20,
        device="cpu",
    )


def transcribe_audio(audio_bytes: bytes) -> str:
    with NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_bytes)
        temp_path = Path(temp_file.name)
    try:
        result = get_asr_pipeline()(str(temp_path))
        return str(result["text"]).strip()
    finally:
        temp_path.unlink(missing_ok=True)


def synthesize_speech(text: str, language: str) -> bytes:
    tts_language = "hi" if language == "hi" else "en"
    with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_path = Path(temp_file.name)
    try:
        gTTS(text=text, lang=tts_language).save(str(temp_path))
        return temp_path.read_bytes()
    finally:
        temp_path.unlink(missing_ok=True)
