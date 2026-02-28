"""Gemini web search grounding for PUM Indonesia content research.

Uses Google's Gemini API with the GoogleSearch tool to find recent
news and updates about PUM Netherlands Senior Experts in Indonesia.

Follows the source module interface: returns str, never raises.
"""

import logging
import os

from google import genai
from google.genai import errors, types

logger = logging.getLogger(__name__)

SEARCH_QUERY = (
    "Find recent news and updates about PUM Netherlands Senior Experts "
    "activities in Indonesia in 2025-2026. Include any SME support programs, "
    "expert visits, events, or partnerships involving PUM Indonesia."
)


def search_pum_indonesia_news() -> str:
    """Search for recent PUM Indonesia news using Gemini grounding.

    Uses the Gemini API with GoogleSearch tool to find recent web results
    about PUM Netherlands Senior Experts activities in Indonesia.

    Requires GEMINI_API_KEY environment variable to be set.

    Returns:
        Text summary of recent PUM Indonesia news from web search,
        or empty string if API key is missing or on any error.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set, skipping web search")
        return ""

    try:
        client = genai.Client(api_key=api_key)
        google_search_tool = types.Tool(google_search=types.GoogleSearch())

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=SEARCH_QUERY,
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            ),
        )

        result = response.text
        if result:
            logger.info("Web search returned %d chars", len(result))
        return result or ""

    except errors.APIError as e:
        if e.code == 429:
            logger.warning("Gemini rate limit hit during web search: %s", e.message)
        else:
            logger.warning(
                "Gemini API error (code %s): %s", e.code, e.message
            )
        return ""
    except Exception as e:
        logger.warning("Web search failed: %s", e)
        return ""
