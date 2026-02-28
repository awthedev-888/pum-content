"""Gemini API client wrapper for PUM content generation.

Uses the google-genai SDK (NOT the deprecated google-generativeai package).
Import pattern: `from google import genai` (NOT `import google.generativeai`).
"""

import os

from google import genai
from google.genai import types, errors

from content_generator.schemas import GeneratedPost
from content_generator.prompts import SYSTEM_INSTRUCTION


def create_gemini_client() -> genai.Client:
    """Create Gemini API client from environment variable.

    Returns:
        Configured genai.Client instance.

    Raises:
        ValueError: If GEMINI_API_KEY environment variable is not set.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Get a free key at https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)


def generate_content(
    client: genai.Client,
    prompt: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    max_output_tokens: int = 2048,
) -> GeneratedPost:
    """Generate structured Instagram content using Gemini.

    Args:
        client: Authenticated Gemini client from create_gemini_client().
        prompt: Formatted prompt from build_generation_prompt().
        model: Gemini model name (default: gemini-2.5-flash).
        temperature: Sampling temperature (default: 0.7).
        max_output_tokens: Maximum output tokens (default: 2048).

    Returns:
        Parsed GeneratedPost with template data, captions, and hashtags.

    Raises:
        RuntimeError: On API errors (rate limit, auth, network) or
            unexpected failures during generation.
    """
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=GeneratedPost,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            ),
        )
        return GeneratedPost.model_validate_json(response.text)
    except errors.APIError as e:
        if e.code == 429:
            raise RuntimeError(
                "Gemini rate limit exceeded. "
                "Free tier: 10 RPM, 500 RPD. "
                f"Details: {e.message}"
            )
        raise RuntimeError(f"Gemini API error ({e.code}): {e.message}")
    except Exception as e:
        if isinstance(e, RuntimeError):
            raise
        raise RuntimeError(f"Content generation failed: {e}")
