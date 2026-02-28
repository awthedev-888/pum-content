"""PUM Indonesia Content Generator - Research Sources Package.

Provides content research from 5 sources: pum.nl scraper, RSS feed parser,
content brief YAML, Google Sheets, and Gemini web search grounding.

The gather_source_material() function aggregates all sources with graceful
degradation -- if individual sources fail, the pipeline continues with
remaining sources. Only raises if ALL sources return empty (AIGEN-01).
"""

import logging
from typing import Optional

from research_sources.scraper import fetch_pum_news
from research_sources.rss_reader import parse_rss_feed
from research_sources.content_brief import load_content_brief
from research_sources.sheets_reader import read_content_sheet
from research_sources.web_search import search_pum_indonesia_news

logger = logging.getLogger(__name__)


def gather_source_material(
    content_brief_path: str = "content_brief.yaml",
    sheet_id: Optional[str] = None,
) -> str:
    """Aggregate content from all research sources with graceful degradation.

    Calls each source module in order, collects successful results with
    section headers, and returns the combined text. If any single source
    fails, the pipeline continues with remaining sources.

    Args:
        content_brief_path: Path to YAML content brief file.
        sheet_id: Google Sheets spreadsheet ID (skipped if None).

    Returns:
        Concatenated source material with section headers.

    Raises:
        RuntimeError: If ALL sources return empty (AIGEN-01 enforcement).
    """
    sections = []

    # Source 1: PUM.nl website scraper
    try:
        result = fetch_pum_news()
        if result and result.strip():
            sections.append(f"## Recent PUM News\n\n{result}")
            logger.info("pum.nl scraper: %d chars", len(result))
        else:
            logger.warning("pum.nl scraper returned empty")
    except Exception as e:
        logger.warning("pum.nl scraper error: %s", e)

    # Source 2: RSS feed
    try:
        result = parse_rss_feed()
        if result and result.strip():
            sections.append(f"## PUM Blog Articles\n\n{result}")
            logger.info("RSS feed: %d chars", len(result))
        else:
            logger.warning("RSS feed returned empty")
    except Exception as e:
        logger.warning("RSS feed error: %s", e)

    # Source 3: Content brief YAML
    try:
        result = load_content_brief(filepath=content_brief_path)
        if result and result.strip():
            sections.append(f"## Content Brief\n\n{result}")
            logger.info("Content brief: %d chars", len(result))
        else:
            logger.warning("Content brief returned empty")
    except Exception as e:
        logger.warning("Content brief error: %s", e)

    # Source 4: Google Sheets (only if sheet_id provided)
    if sheet_id is not None:
        try:
            result = read_content_sheet(sheet_id)
            if result and result.strip():
                sections.append(f"## Content Inputs (Sheets)\n\n{result}")
                logger.info("Google Sheets: %d chars", len(result))
            else:
                logger.warning("Google Sheets returned empty")
        except Exception as e:
            logger.warning("Google Sheets error: %s", e)

    # Source 5: Gemini web search grounding
    try:
        result = search_pum_indonesia_news()
        if result and result.strip():
            sections.append(f"## Recent Web Results\n\n{result}")
            logger.info("Web search: %d chars", len(result))
        else:
            logger.warning("Web search returned empty")
    except Exception as e:
        logger.warning("Web search error: %s", e)

    # AIGEN-01: Never pass empty source material to generator
    if not sections:
        raise RuntimeError(
            "All content research sources failed or returned empty. "
            "Cannot generate content without source material (AIGEN-01)."
        )

    return "\n\n".join(sections)


__all__ = [
    "gather_source_material",
    "fetch_pum_news",
    "parse_rss_feed",
    "load_content_brief",
    "read_content_sheet",
    "search_pum_indonesia_news",
]
