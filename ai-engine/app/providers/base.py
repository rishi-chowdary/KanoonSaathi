from abc import ABC, abstractmethod
from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract interface for LLM backends (Gemini, Ollama, and test Mock)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """The identifier of the provider (e.g., 'gemini', 'ollama')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The model version being utilized."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        system_prompt: str | None = None,
        temperature: float = 0.1,
    ) -> T:
        """Execute a prompt and return a validated Pydantic model instance."""
        pass
