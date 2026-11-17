import asyncio
import json
import logging
import random
import time
from typing import TypeVar
import httpx
from pydantic import BaseModel

from app.config import settings
from app.providers.base import LLMProvider

logger = logging.getLogger("ai_engine.ollama_provider")
T = TypeVar("T", bound=BaseModel)


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str | None = None, model_name: str | None = None):
        self._base_url = (base_url or settings.ollama_base_url or "http://localhost:11434").rstrip("/")
        self._model_name = model_name or settings.ollama_model or "llama3"

    @property
    def provider_name(self) -> str:
        return "ollama"

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
        max_retries = 3
        base_delay = 1.0

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Ollama supports JSON Schema directly via the format parameter
        payload = {
            "model": self._model_name,
            "messages": messages,
            "format": schema.model_json_schema(),
            "options": {"temperature": temperature},
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=600.0) as client:
            for attempt in range(max_retries + 1):
                start_time = time.perf_counter()
                try:
                    resp = await client.post(f"{self._base_url}/api/chat", json=payload)
                    latency_ms = (time.perf_counter() - start_time) * 1000.0

                    if resp.status_code >= 500 or resp.status_code == 429:
                        if attempt < max_retries:
                            delay = base_delay * (2 ** attempt) + random.uniform(0.1, 0.4)
                            logger.warning(
                                "ollama returned %d. Retrying in %.2fs (attempt %d/%d)",
                                resp.status_code,
                                delay,
                                attempt + 1,
                                max_retries,
                            )
                            await asyncio.sleep(delay)
                            continue

                    resp.raise_for_status()
                    data = resp.json()

                    eval_count = data.get("eval_count")
                    prompt_eval_count = data.get("prompt_eval_count")
                    logger.info(
                        "ollama call completed in %.2f ms (eval_tokens=%s, prompt_tokens=%s, model=%s)",
                        latency_ms,
                        eval_count,
                        prompt_eval_count,
                        self._model_name,
                    )

                    content = data.get("message", {}).get("content", "{}")
                    return schema.model_validate_json(content)

                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt) + random.uniform(0.1, 0.4)
                        logger.warning(
                            "ollama request error: %s. Retrying in %.2fs (attempt %d/%d)",
                            e,
                            delay,
                            attempt + 1,
                            max_retries,
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error("ollama call failed after retries: %s", e)
                        raise
