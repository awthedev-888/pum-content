"""PUM Indonesia Content Generator - AI Content Generation Package.

Provides Gemini API integration for generating structured Instagram content
with bilingual captions, hashtags, and template-specific data.
"""

from content_generator.schemas import (
    GeneratedPost,
    ImpactStatsData,
    QuoteStoryData,
    StatItem,
    TipsListData,
    validate_template_data,
)
from content_generator.prompts import SYSTEM_INSTRUCTION, build_generation_prompt
from content_generator.pillars import (
    ContentPillar,
    PILLAR_ORDER,
    PILLAR_TEMPLATE_MAP,
    get_todays_pillar,
    get_template_type,
)
from content_generator.generator import generate_post

__all__ = [
    # Schemas (Plan 03-01)
    "GeneratedPost",
    "ImpactStatsData",
    "QuoteStoryData",
    "StatItem",
    "TipsListData",
    "validate_template_data",
    # Prompts (Plan 03-01)
    "SYSTEM_INSTRUCTION",
    "build_generation_prompt",
    # Pillars (Plan 03-02)
    "ContentPillar",
    "PILLAR_ORDER",
    "PILLAR_TEMPLATE_MAP",
    "get_todays_pillar",
    "get_template_type",
    # Generator (Plan 03-03)
    "generate_post",
]
