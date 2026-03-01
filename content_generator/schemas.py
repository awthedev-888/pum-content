"""Pydantic models for Gemini structured output.

Defines the data contract between AI content generation and the image
template engine. GeneratedPost is the top-level response schema passed
to Gemini's response_schema parameter. Template-specific schemas
(QuoteStoryData, TipsListData, ImpactStatsData) validate template_data
after generation to ensure compatibility with Phase 2 template render()
contracts.
"""

from typing import Optional, List

from pydantic import BaseModel, Field


class StatItem(BaseModel):
    """A single impact statistic."""

    number: str = Field(
        description="Formatted number string, e.g. '1.200+', '30+', '45 tahun'"
    )
    label: str = Field(
        description="Context label in Bahasa Indonesia, e.g. 'ahli sukarelawan'"
    )


class QuoteStoryData(BaseModel):
    """Template data for QuoteStoryTemplate.render()"""

    headline: str = Field(
        description="Short attention-grabbing headline in Bahasa Indonesia, max 60 chars"
    )
    headline_short: Optional[str] = Field(
        None,
        description="Very short headline for image overlay (2-4 words/line, max 3 lines, use \\n for line breaks)"
    )
    body: str = Field(
        description="2-4 sentence story or testimonial in Bahasa Indonesia"
    )
    attribution: str = Field(
        description="Attribution line, e.g. '--- Bapak Sutrisno, Petani Yogyakarta'"
    )


class TipsListData(BaseModel):
    """Template data for TipsListTemplate.render()"""

    title: str = Field(
        description="List title in Bahasa Indonesia, e.g. '5 Tips Ekspor untuk UMKM'"
    )
    headline_short: Optional[str] = Field(
        None,
        description="Very short headline for image overlay (2-4 words/line, max 3 lines, use \\n for line breaks)"
    )
    items: list[str] = Field(
        description="3-5 actionable tips in Bahasa Indonesia"
    )


class ImpactStatsData(BaseModel):
    """Template data for ImpactStatsTemplate.render()"""

    title: str = Field(
        description="Stats title in Bahasa Indonesia, e.g. 'Dampak PUM di Indonesia'"
    )
    headline_short: Optional[str] = Field(
        None,
        description="Very short headline for image overlay (2-4 words/line, max 3 lines, use \\n for line breaks)"
    )
    stats: list[StatItem] = Field(
        description="1-3 impact statistics with number and label"
    )


class TemplateData(BaseModel):
    """Union of all template fields. Gemini fills the relevant ones based on template_type."""

    # Shared field for 3-zone layout
    headline_short: Optional[str] = Field(
        None, description="Very short headline for image overlay (2-4 words/line, max 3 lines, use \\n for line breaks)"
    )
    # QuoteStory fields
    headline: Optional[str] = Field(
        None, description="Short headline in Bahasa Indonesia, max 60 chars (quote_story)"
    )
    body: Optional[str] = Field(
        None, description="2-4 sentence story in Bahasa Indonesia (quote_story)"
    )
    attribution: Optional[str] = Field(
        None, description="Attribution line, e.g. '--- Name, Title' (quote_story)"
    )
    # TipsList fields
    title: Optional[str] = Field(
        None, description="List or stats title in Bahasa Indonesia (tips_list / impact_stats)"
    )
    items: Optional[List[str]] = Field(
        None, description="3-5 actionable tips in Bahasa Indonesia (tips_list)"
    )
    # ImpactStats fields
    stats: Optional[List[StatItem]] = Field(
        None, description="1-3 impact statistics with number and label (impact_stats)"
    )


class GeneratedPost(BaseModel):
    """Complete structured output from Gemini for one Instagram post.

    This is the top-level response schema passed to Gemini's response_schema
    parameter. The template_data field contains fields matching the
    render() contract of the template specified by template_type.
    """

    content_pillar: str = Field(
        description="Content pillar: success_stories, expert_tips, impact_stats, or event_promos"
    )
    template_type: str = Field(
        description="Template type: quote_story, tips_list, or impact_stats"
    )
    template_data: TemplateData = Field(
        description="Template fields matching the template_type's render() contract"
    )
    caption_id: str = Field(
        description="Full Instagram caption in Bahasa Indonesia (150-300 words)"
    )
    caption_en: str = Field(
        description="Full Instagram caption in English (150-300 words)"
    )
    hashtags: list[str] = Field(
        description="8-15 relevant hashtags without # prefix"
    )
    posting_suggestion: str = Field(
        description="Suggested posting time and content theme note"
    )
    cta_text: str = Field(
        default="TOGETHER WE GROW",
        description="CTA banner text (2-5 words, English, ALL CAPS), e.g. 'READ THE WHOLE STORY', 'SHARING KNOWLEDGE'"
    )
    photo_keywords: list[str] = Field(
        default_factory=list,
        description="3-5 English keywords for stock photo search, e.g. ['indonesia', 'farmer', 'agriculture']"
    )


def validate_template_data(template_type: str, template_data: dict) -> dict:
    """Validate template_data against the appropriate template schema.

    Args:
        template_type: One of 'quote_story', 'tips_list', 'impact_stats'
        template_data: Dict from GeneratedPost.template_data

    Returns:
        Validated dict ready for template.render()

    Raises:
        ValueError: If template_type is unknown or data is invalid
    """
    schema_map = {
        "quote_story": QuoteStoryData,
        "tips_list": TipsListData,
        "impact_stats": ImpactStatsData,
    }
    schema_class = schema_map.get(template_type)
    if not schema_class:
        raise ValueError(
            f"Unknown template type: {template_type}. "
            f"Must be one of: {list(schema_map.keys())}"
        )
    validated = schema_class.model_validate(template_data)
    return validated.model_dump()
