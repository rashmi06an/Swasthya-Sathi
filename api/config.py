from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Swasthya Sathi"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    streamlit_port: int = 8501
    default_language: str = "en"
    whisper_model: str = "openai/whisper-tiny"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    openfda_base_url: str = "https://api.fda.gov/drug/label.json"
    backend_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
