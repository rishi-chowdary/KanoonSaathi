import asyncio
import logging
import random
import time
from typing import TypeVar
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.config import settings
from app.providers.base import LLMProvider

logger = logging.getLogger("ai_engine.gemini_provider")
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self._api_key = api_key or settings.gemini_api_key
        self._model_name = model_name or settings.gemini_model or "gemini-1.5-flash"
        self._client = None
        if self._api_key and not self._api_key.startswith("replace_with"):
            self._client = genai.Client(api_key=self._api_key)

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        system_prompt: str | None = None,
        temperature: float = 0.1,
    ) -> T:
        if not self._client:
            raise RuntimeError(
                "Gemini API key is not configured. Please supply GEMINI_API_KEY in .env or switch to Ollama."
            )

        max_retries = 3
        base_delay = 1.5

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=temperature,
            system_instruction=system_prompt if system_prompt else None,
        )

        for attempt in range(max_retries + 1):
            start_time = time.perf_counter()
            try:
                # Run synchronous SDK call in thread pool to avoid blocking async event loop
                response = await asyncio.to_thread(
                    self._client.models.generate_content,
                    model=self._model_name,
                    contents=prompt,
                    config=config,
                )

                latency_ms = (time.perf_counter() - start_time) * 1000.0

                prompt_tokens = getattr(getattr(response, "usage_metadata", None), "prompt_token_count", None)
                candidate_tokens = getattr(getattr(response, "usage_metadata", None), "candidates_token_count", None)

                logger.info(
                    "gemini call completed in %.2f ms (prompt_tokens=%s, candidate_tokens=%s, model=%s)",
                    latency_ms,
                    prompt_tokens,
                    candidate_tokens,
                    self._model_name,
                )

                raw_text = response.text or "{}"
                return schema.model_validate_json(raw_text)

            except APIError as e:
                status_code = getattr(e, "code", 500)
                is_retryable = status_code in (429, 500, 502, 503, 504)

                if is_retryable and attempt < max_retries:
                    delay = base_delay * (2 ** attempt) + random.uniform(0.1, 0.5)
                    logger.warning(
                        "gemini call failed with HTTP %s (attempt %d/%d). Retrying in %.2f seconds. Error: %s",
                        status_code,
                        attempt + 1,
                        max_retries,
                        delay,
                        e,
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error("gemini call failed permanently: %s", e)
                    raise
            except Exception as e:
                logger.error("unexpected error during gemini call: %s", e)
                raise

