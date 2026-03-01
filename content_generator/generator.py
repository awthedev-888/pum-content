"""High-level content generation orchestrator.

Wires together Gemini client, pillar rotation, prompt building,
and output validation into a single generate_post() entry point.
"""

import time
import logging
from datetime import date

from content_generator.gemini_client import create_gemini_client, generate_content
from content_generator.pillars import get_todays_pillar, get_template_type
from content_generator.prompts import build_generation_prompt
from content_generator.schemas import GeneratedPost, validate_template_data

logger = logging.getLogger(__name__)


def generate_post(
    source_material: str,
    target_date: date = None,
    max_retries: int = 3,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.7,
) -> GeneratedPost:
    """Generate a complete Instagram post from source material.

    Orchestration flow:
    1. Determine today's content pillar (date-based rotation)
    2. Map pillar to template type
    3. Build prompt with source material and pillar/template context
    4. Call Gemini API with structured output
    5. Validate template_data against the correct template schema
    6. Return validated GeneratedPost

    Args:
        source_material: Research text about PUM activities. Must not be empty.
        target_date: Date for pillar rotation. Defaults to today.
        max_retries: Max retry attempts on rate limit errors (429). Default 3.
        model: Gemini model name. Default "gemini-2.5-flash".
        temperature: Generation temperature (0.0-1.0). Default 0.7.

    Returns:
        GeneratedPost with validated template_data, bilingual captions, and hashtags.

    Raises:
        ValueError: If source_material is empty or blank.
        ValueError: If GEMINI_API_KEY is not set (propagated from create_gemini_client).
        RuntimeError: If Gemini API fails after all retries.
        ValueError: If generated template_data fails validation.
    """
    # 1. Input validation
    if not source_material or not source_material.strip():
        raise ValueError(
            "source_material must not be empty. "
            "AIGEN-01 requires research-first generation."
        )

    # 2. Pillar rotation
    pillar = get_todays_pillar(target_date)
    template_type = get_template_type(pillar)
    logger.info(
        "Content pillar: %s, template type: %s", pillar.value, template_type
    )

    # 3. Prompt building
    prompt = build_generation_prompt(source_material, pillar.value, template_type)

    # 4. Client creation (raises ValueError if API key missing)
    client = create_gemini_client()

    # 5. Generation with retry on rate limits
    last_error = None
    for attempt in range(max_retries):
        try:
            result = generate_content(
                client, prompt, model=model, temperature=temperature
            )
            break
        except RuntimeError as e:
            last_error = e
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                wait = 2 ** attempt * 10  # 10s, 20s, 40s
                logger.warning(
                    "Rate limit hit, retrying in %ds (attempt %d/%d)",
                    wait, attempt + 1, max_retries,
                )
                time.sleep(wait)
                continue
            raise
    else:
        raise RuntimeError(
            f"Content generation failed after {max_retries} retries: {last_error}"
        )

    # 6. Output validation
    template_dict = result.template_data.model_dump(exclude_none=True)
    validated_data = validate_template_data(result.template_type, template_dict)
    result = result.model_copy(update={"template_data": validated_data})

    # 7. Logging
    logger.info(
        "Generated post: pillar=%s, template=%s, hashtags=%d",
        result.content_pillar, result.template_type, len(result.hashtags),
    )

    return result
