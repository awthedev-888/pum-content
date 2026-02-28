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

__all__ = [
    "GeneratedPost",
    "ImpactStatsData",
    "QuoteStoryData",
    "StatItem",
    "TipsListData",
    "validate_template_data",
    "SYSTEM_INSTRUCTION",
    "build_generation_prompt",
]
