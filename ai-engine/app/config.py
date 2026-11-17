import shutil
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_workers: int = 1

    internal_api_key: str = "lexilegal_internal_service_key_secret_2026"

    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    log_level: str = "INFO"

    @property
    def tesseract_available(self) -> bool:
        return shutil.which("tesseract") is not None


settings = Settings()

