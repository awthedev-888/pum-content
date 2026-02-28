"""Pydantic models for Gemini structured output.

Defines the data contract between AI content generation and the image
template engine. GeneratedPost is the top-level response schema passed
to Gemini's response_schema parameter. Template-specific schemas
(QuoteStoryData, TipsListData, ImpactStatsData) validate template_data
after generation to ensure compatibility with Phase 2 template render()
contracts.
"""

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
    items: list[str] = Field(
        description="3-5 actionable tips in Bahasa Indonesia"
    )


class ImpactStatsData(BaseModel):
    """Template data for ImpactStatsTemplate.render()"""

    title: str = Field(
        description="Stats title in Bahasa Indonesia, e.g. 'Dampak PUM di Indonesia'"
    )
    stats: list[StatItem] = Field(
        description="1-3 impact statistics with number and label"
    )


class GeneratedPost(BaseModel):
    """Complete structured output from Gemini for one Instagram post.

    This is the top-level response schema passed to Gemini's response_schema
    parameter. The template_data field contains a dict that matches the
    render() contract of the template specified by template_type.
    """

    content_pillar: str = Field(
        description="Content pillar: success_stories, expert_tips, impact_stats, or event_promos"
    )
    template_type: str = Field(
        description="Template type: quote_story, tips_list, or impact_stats"
    )
    template_data: dict = Field(
        description="Data dict matching the template's render() contract"
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
