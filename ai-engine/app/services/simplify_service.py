import logging
from app.prompts import load_prompt
from app.providers.base import LLMProvider
from app.schemas.simplify import (
    GlossaryTerm,
    LLMSimplifyResult,
    SimplifyRequest,
    SimplifyResponse,
)
from app.services.clause_service import validate_numbers_and_dates
from app.services.llm_validator import generate_with_retry

logger = logging.getLogger("ai_engine.simplify_service")


async def simplify_text(
    request: SimplifyRequest,
    provider: LLMProvider,
) -> SimplifyResponse:
    """Simplify arbitrary legal text into one of three modes, extracting glossary terms
    and 'what could be missed' caveats while verifying number and date consistency.
    """
    system_prompt = load_prompt("system_prompt", "v1")
    prompt_template = load_prompt("simplify_prompt", "v1")

    context_str = request.document_context.strip() if request.document_context else "None provided"
    prompt = prompt_template.format(
        document_context=context_str,
        legal_text=request.text.strip(),
        mode=request.mode,
    )

    # Low temperature for precision and adherence to facts
    temp = 0.2 if request.mode == "simple_english" else 0.1

    logger.info(
        "simplifying text (%d chars) in mode '%s' via %s (%s)",
        len(request.text),
        request.mode,
        provider.provider_name,
        provider.model_name,
    )

    llm_result = await generate_with_retry(
        provider=provider,
        prompt=prompt,
        schema=LLMSimplifyResult,
        system_prompt=system_prompt,
        temperature=temp,
    )

    # Post-check: ensure the explanation didn't invent numbers or dates
    is_grounded, consistency_warnings = validate_numbers_and_dates(
        request.text,
        {request.mode: llm_result.explanation},
    )

    warnings: list[str] = list(consistency_warnings)
    if not is_grounded:
        logger.warning(
            "number/date consistency mismatch detected during simplification: %s",
            warnings,
        )

    return SimplifyResponse(
        original_text=request.text,
        mode=request.mode,
        explanation=llm_result.explanation,
        glossary=llm_result.glossary,
        what_could_be_missed=llm_result.what_could_be_missed,
        warnings=warnings,
        is_grounded=is_grounded,
        llm_provider=provider.provider_name,
        llm_model=provider.model_name,
    )

