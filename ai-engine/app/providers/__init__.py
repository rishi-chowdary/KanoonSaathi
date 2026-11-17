import os
from app.config import settings
from app.providers.base import LLMProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.mock_provider import MockProvider


def get_llm_provider(name: str | None = None) -> LLMProvider:
    provider_name = (name or os.environ.get("LLM_PROVIDER") or settings.llm_provider or "gemini").lower()

    # If running unit tests or explicitly set to mock
    if os.environ.get("USE_MOCK_LLM") == "true" or provider_name == "mock":
        return MockProvider()

    if provider_name == "ollama":
        return OllamaProvider()

    return GeminiProvider()


__all__ = ["LLMProvider", "GeminiProvider", "OllamaProvider", "MockProvider", "get_llm_provider"]

