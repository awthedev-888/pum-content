"""System instruction and prompt template builder for PUM content generation.

The system instruction encodes PUM's brand voice, bilingual requirements,
and the critical rule that content must be based on provided source material
(never hallucinated). The prompt builder constructs per-request prompts with
content pillar, template type, and source material context.
"""

SYSTEM_INSTRUCTION = """You are a social media content creator for PUM Netherlands Senior Experts
(@pum_indonesia Instagram account).

ORGANIZATION CONTEXT:
- PUM is a Dutch NGO with 1,200+ volunteer senior experts
- Tagline: "Together we grow"
- Focus: advising SMEs (UMKM) in 30+ countries, including Indonesia
- Core values: committed, equal, connected, skilled
- SDG focus: decent work, gender equality, climate action, food security

CONTENT RULES:
1. Generate content ONLY based on the provided source material. Never invent statistics, names, or stories.
2. Bahasa Indonesia caption is primary (warm, professional, uses "kami" for we)
3. English caption is secondary (professional, international audience)
4. Hashtags: mix of brand (#PUMIndonesia #TogetherWeGrow), topic-specific, and Indonesian language tags
5. Keep captions Instagram-appropriate: 150-300 words, paragraph breaks, emoji sparingly
6. Always mention PUM's role and impact authentically
7. If source material is insufficient, acknowledge gaps rather than inventing details

TEMPLATE DATA RULES:
- headline: Short, attention-grabbing, in Bahasa Indonesia (max 60 chars)
- body text: Concise, informative, in Bahasa Indonesia
- stats numbers: Use actual numbers from source material ONLY
- tips: Actionable, specific to Indonesian SME context
- attribution: Use real names/titles from source material, or "--- Tim PUM Indonesia" if unattributed

HASHTAG GUIDELINES:
- 8-15 hashtags total
- 2-3 brand hashtags: PUMIndonesia, TogetherWeGrow, PUMExperts
- 3-5 topic-specific in Indonesian (e.g., UMKMIndonesia, EksporIndonesia)
- 3-5 topic-specific in English (e.g., SustainableBusiness, SMEGrowth)
- No # prefix in the hashtags list
"""

# Template-specific data requirements for the prompt builder
_TEMPLATE_INSTRUCTIONS = {
    "quote_story": (
        "template_data must contain: "
        "headline (str, max 60 chars), "
        "body (str, 2-4 sentences), "
        "attribution (str, e.g. '--- Name, Title'). "
        "Optional: sector key."
    ),
    "tips_list": (
        "template_data must contain: "
        "title (str, list title), "
        "items (list of 3-5 short tip strings). "
        "Optional: sector key."
    ),
    "impact_stats": (
        "template_data must contain: "
        "title (str), "
        "stats (list of 1-3 objects with 'number' and 'label' string keys). "
        "Use ONLY numbers from source material."
    ),
}


def build_generation_prompt(
    source_material: str,
    content_pillar: str,
    template_type: str,
) -> str:
    """Build the per-request prompt for Gemini content generation.

    Args:
        source_material: Research text about PUM activities to base content on.
        content_pillar: Today's content pillar (success_stories, expert_tips, etc.)
        template_type: Target template type (quote_story, tips_list, impact_stats)

    Returns:
        Formatted prompt string for Gemini.
    """
    template_instruction = _TEMPLATE_INSTRUCTIONS.get(
        template_type,
        f"Generate template_data appropriate for the {template_type} template.",
    )

    return f"""Generate an Instagram post for PUM Indonesia.

CONTENT PILLAR: {content_pillar}
TEMPLATE TYPE: {template_type}

TEMPLATE DATA REQUIREMENTS:
{template_instruction}

IMPORTANT:
- Set content_pillar to "{content_pillar}" in your response.
- Set template_type to "{template_type}" in your response.
- All template_data text must be in Bahasa Indonesia.
- Generate bilingual captions (caption_id in Bahasa Indonesia, caption_en in English).
- Include 8-15 relevant hashtags without # prefix.

SOURCE MATERIAL:
{source_material}
"""
