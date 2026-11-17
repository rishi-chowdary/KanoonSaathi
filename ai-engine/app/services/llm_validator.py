import logging
from typing import TypeVar
from pydantic import BaseModel, ValidationError

from app.providers.base import LLMProvider

logger = logging.getLogger("ai_engine.llm_validator")
T = TypeVar("T", bound=BaseModel)


async def generate_with_retry(
    provider: LLMProvider,
    prompt: str,
    schema: type[T],
    system_prompt: str | None = None,
    temperature: float = 0.1,
    max_retries: int = 2,
) -> T:
    """Execute LLM structured generation with automatic error feedback retry on schema violations."""
    current_prompt = prompt
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            result = await provider.generate_structured(
                prompt=current_prompt,
                schema=schema,
                system_prompt=system_prompt,
                temperature=temperature,
            )
            return result
        except (ValidationError, ValueError) as val_err:
            last_error = val_err
            if attempt < max_retries:
                logger.warning(
                    "schema validation failed on attempt %d/%d: %s. Retrying with error feedback.",
                    attempt + 1,
                    max_retries,
                    val_err,
                )
                current_prompt = (
                    f"{prompt}\n\n"
                    f"PREVIOUS ATTEMPT FAILED SCHEMA VALIDATION:\n"
                    f"{str(val_err)}\n"
                    f"Please correct the output so that it strictly adheres to the requested JSON schema."
                )
            else:
                logger.error("schema validation permanently failed after %d retries: %s", max_retries, val_err)
                raise
        except Exception as e:
            logger.error("unhandled error during LLM generation attempt %d: %s", attempt + 1, e)
            raise

    raise RuntimeError(f"failed to generate valid structured response after {max_retries} attempts: {last_error}")

