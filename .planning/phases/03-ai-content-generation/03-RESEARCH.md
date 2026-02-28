# Phase 3: AI Content Generation - Research

**Researched:** 2026-02-28
**Domain:** Gemini API integration, structured content generation, bilingual prompt engineering
**Confidence:** HIGH

## Summary

Phase 3 integrates Google's Gemini API to generate structured Instagram content for PUM Indonesia. The core task is: given source material about PUM activities, produce a structured JSON output containing bilingual captions (Bahasa Indonesia + English), relevant hashtags, and a template type selection based on content pillar rotation.

The primary technical components are: (1) a Gemini API client using the `google-genai` SDK with structured output via Pydantic models, (2) a deterministic content pillar rotation system based on date, and (3) output validation ensuring downstream modules (image templates, email delivery) receive well-formed data.

The `google-genai` SDK (v1.65.0) is the current recommended SDK, replacing the deprecated `google-generativeai` package (EOL November 2025). It supports Python 3.9+, which is compatible with this project. The SDK provides native structured output via `response_schema` with Pydantic models, eliminating the need for manual JSON parsing. Gemini 2.5 Flash is the recommended model for this use case -- it is free tier, fast, and well-suited for content generation tasks.

**Primary recommendation:** Use `google-genai` SDK with Gemini 2.5 Flash, Pydantic-based structured output schemas, deterministic date-based pillar rotation, and comprehensive system instructions that encode PUM's brand voice and bilingual requirements.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AIGEN-01 | Gemini generates captions based on researched content (never from nothing) | System instruction enforces source-material-only generation; prompt template requires `source_material` input field; structured output schema includes source attribution |
| AIGEN-02 | Captions are bilingual -- Bahasa Indonesia primary, English secondary | Pydantic schema defines `caption_id` and `caption_en` as separate required fields; system instruction specifies language requirements and tone per language |
| AIGEN-03 | Gemini generates relevant hashtags for each post | Pydantic schema includes `hashtags` as `list[str]`; system instruction provides hashtag guidelines (mix of brand, topic, Indonesian hashtags) |
| AIGEN-04 | Content rotates daily across 4 pillars: success stories, expert tips, impact stats, event promos | Date-based modulo rotation (`day_of_year % 4`) maps to pillar enum; pillar passed to Gemini as context |
| AIGEN-05 | Gemini selects appropriate template type based on content pillar | Pillar-to-template mapping defined in code (not AI-selected); deterministic mapping: success_stories->quote_story, expert_tips->tips_list, impact_stats->impact_stats, event_promos->quote_story |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| [google-genai](https://pypi.org/project/google-genai/) | >=1.65.0 | Gemini API client (replaces deprecated google-generativeai) | Official Google SDK, GA since May 2025, centralized Client API |
| [pydantic](https://pypi.org/project/pydantic/) | >=2.0.0,<3.0.0 | Structured output schemas and response validation | Required dependency of google-genai; native response_schema support |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | >=1.0.0 | Load GEMINI_API_KEY from .env file | Already in requirements.txt; used during local development |
| PyYAML | ==6.0.3 | Load brand_config.yaml for pillar/template configuration | Already in requirements.txt |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| google-genai | google-generativeai (legacy) | Legacy is EOL since Nov 2025; no new features, no security patches |
| google-genai | langchain-google-genai | Over-engineered for single-model, single-call use case; adds unnecessary abstraction |
| Pydantic structured output | Manual JSON parsing with json.loads() | Fragile, no validation, no type safety; structured output is natively supported |
| Gemini 2.5 Flash | Gemini 2.5 Pro | Pro has lower free tier limits (5 RPM, 100 RPD vs Flash's 10 RPM, 500 RPD); unnecessary capability for content generation |

**Installation:**
```bash
pip install google-genai>=1.65.0
```
Note: `pydantic>=2.0.0` is installed automatically as a dependency of `google-genai`.

## Architecture Patterns

### Recommended Project Structure
```
content_generator/
    __init__.py
    gemini_client.py      # Gemini API client wrapper
    prompts.py            # System instruction and prompt templates
    schemas.py            # Pydantic models for structured output
    pillars.py            # Content pillar rotation and template mapping
    generator.py          # High-level generate_content() orchestrator
```

### Pattern 1: Centralized Client with Structured Output
**What:** Single Gemini client instance with Pydantic-based response schemas.
**When to use:** Every content generation call.
**Example:**
```python
# Source: https://googleapis.github.io/python-genai/
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class GeneratedContent(BaseModel):
    """Structured output schema for Instagram content."""
    template_type: str = Field(description="Template type: quote_story, tips_list, or impact_stats")
    caption_id: str = Field(description="Instagram caption in Bahasa Indonesia")
    caption_en: str = Field(description="Instagram caption in English")
    hashtags: list[str] = Field(description="Relevant hashtags without # prefix")
    headline: str = Field(description="Short headline for the image template")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_text,
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=GeneratedContent,
        temperature=0.7,
        max_output_tokens=2048,
    ),
)

# response.text contains JSON; parse with Pydantic
result = GeneratedContent.model_validate_json(response.text)
```

### Pattern 2: Deterministic Pillar Rotation
**What:** Date-based modulo rotation through 4 content pillars.
**When to use:** Every daily pipeline run to determine today's content pillar.
**Example:**
```python
from datetime import date
from enum import Enum

class ContentPillar(str, Enum):
    SUCCESS_STORIES = "success_stories"
    EXPERT_TIPS = "expert_tips"
    IMPACT_STATS = "impact_stats"
    EVENT_PROMOS = "event_promos"

# Deterministic rotation order
PILLAR_ORDER = [
    ContentPillar.SUCCESS_STORIES,
    ContentPillar.EXPERT_TIPS,
    ContentPillar.IMPACT_STATS,
    ContentPillar.EVENT_PROMOS,
]

# Pillar -> template type mapping (deterministic, not AI-selected)
PILLAR_TEMPLATE_MAP = {
    ContentPillar.SUCCESS_STORIES: "quote_story",
    ContentPillar.EXPERT_TIPS: "tips_list",
    ContentPillar.IMPACT_STATS: "impact_stats",
    ContentPillar.EVENT_PROMOS: "quote_story",
}

def get_todays_pillar(target_date: date | None = None) -> ContentPillar:
    """Get today's content pillar based on day of year."""
    d = target_date or date.today()
    index = d.timetuple().tm_yday % len(PILLAR_ORDER)
    return PILLAR_ORDER[index]

def get_template_type(pillar: ContentPillar) -> str:
    """Map content pillar to image template type."""
    return PILLAR_TEMPLATE_MAP[pillar]
```

### Pattern 3: Template-Specific Output Schemas
**What:** Different Pydantic schemas per template type to match each template's render() data contract.
**When to use:** To ensure Gemini output directly feeds into the correct template's render() method.
**Example:**
```python
from pydantic import BaseModel, Field

class QuoteStoryContent(BaseModel):
    """Content for QuoteStoryTemplate.render()"""
    headline: str = Field(description="Short attention-grabbing headline in Bahasa Indonesia")
    body: str = Field(description="2-3 sentence story or testimonial in Bahasa Indonesia")
    attribution: str = Field(description="Attribution line, e.g. '--- Bapak Sutrisno, Petani Yogyakarta'")
    sector: str | None = Field(default=None, description="Sector key from brand config, e.g. 'agriculture'")

class TipsListContent(BaseModel):
    """Content for TipsListTemplate.render()"""
    title: str = Field(description="List title in Bahasa Indonesia, e.g. '5 Tips Ekspor untuk UMKM'")
    items: list[str] = Field(description="3-5 actionable tips in Bahasa Indonesia")
    sector: str | None = Field(default=None, description="Sector key from brand config")

class ImpactStatsContent(BaseModel):
    """Content for ImpactStatsTemplate.render()"""
    title: str = Field(description="Stats title in Bahasa Indonesia, e.g. 'Dampak PUM di Indonesia'")
    stats: list[dict] = Field(description="1-3 stats, each with 'number' (str) and 'label' (str) keys")

class GeneratedPost(BaseModel):
    """Complete generated post output."""
    content_pillar: str = Field(description="Content pillar: success_stories, expert_tips, impact_stats, event_promos")
    template_type: str = Field(description="Template type: quote_story, tips_list, impact_stats")
    template_data: dict = Field(description="Data dict matching the template's render() contract")
    caption_id: str = Field(description="Full Instagram caption in Bahasa Indonesia")
    caption_en: str = Field(description="Full Instagram caption in English")
    hashtags: list[str] = Field(description="8-15 relevant hashtags without # prefix")
    posting_suggestion: str = Field(description="Suggested posting time and content theme note")
```

### Anti-Patterns to Avoid
- **Letting AI choose template type freely:** Template selection must be deterministic based on pillar, not AI-selected. AI is unreliable for consistent rotation patterns.
- **Embedding JSON examples in prompt when using response_schema:** Google docs explicitly warn this degrades output quality. Use the schema parameter only.
- **Hardcoding API key in source code:** Always load from environment variable `GEMINI_API_KEY`.
- **Generating content without source material:** AIGEN-01 requires research-first generation. The prompt must include source material; never let Gemini generate from nothing.
- **Single monolithic prompt:** Separate system instruction (brand voice, rules) from per-request prompt (source material, pillar, template requirements).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON response parsing | Custom regex/string parsing | `response_schema=PydanticModel` in GenerateContentConfig | Gemini natively constrains output to schema; guaranteed valid JSON |
| API retry logic | Custom retry with sleep | `tenacity` or simple retry decorator | Rate limit handling (429) needs exponential backoff with jitter |
| Response validation | Manual dict key checking | Pydantic model `.model_validate_json()` | Type coercion, constraint validation, clear error messages |
| Environment variable loading | `os.environ.get()` everywhere | `python-dotenv` + single config loading point | Already in project; consistent .env handling |

**Key insight:** The `google-genai` SDK + Pydantic combination handles the entire generate-parse-validate pipeline. The structured output feature means Gemini's response is guaranteed to match the schema, eliminating the most common failure mode (malformed JSON).

## Common Pitfalls

### Pitfall 1: Using Deprecated google-generativeai Package
**What goes wrong:** Import errors, missing features, no security updates after Nov 2025 EOL.
**Why it happens:** Many tutorials and Stack Overflow answers still reference the old package.
**How to avoid:** Use `from google import genai` (google-genai), NOT `import google.generativeai as genai` (legacy).
**Warning signs:** `genai.configure()` or `genai.GenerativeModel()` calls indicate legacy SDK usage.

### Pitfall 2: Gemini 2.0 Flash Model Retirement
**What goes wrong:** API calls fail with model-not-found errors after March 31, 2026.
**Why it happens:** Gemini 2.0 Flash and Flash-Lite are deprecated, retiring Q1-Q2 2026.
**How to avoid:** Use `gemini-2.5-flash` as the model name from the start.
**Warning signs:** Model name contains "2.0" in any code or config.

### Pitfall 3: Default Values in Pydantic Response Schemas
**What goes wrong:** API rejects schema with "Default value is not supported in response schema."
**Why it happens:** Gemini's response_schema does not support Pydantic fields with explicit defaults (though this was fixed in recent SDK versions).
**How to avoid:** Avoid `Field(default=...)` in response schema models. Use `Optional[type]` with `None` default if needed. Keep response schemas simple.
**Warning signs:** `ValueError` or `APIError` mentioning "default value" during generation.

### Pitfall 4: Prompt + Schema Duplication
**What goes wrong:** Output quality degrades when JSON examples appear in both the prompt text and the response_schema.
**Why it happens:** Conflicting instructions confuse the model.
**How to avoid:** Use `response_schema` parameter exclusively for structure. Prompt should describe WHAT to generate, not HOW to format it.
**Warning signs:** Prompt text contains `{"template_type": "..."}` examples alongside `response_schema`.

### Pitfall 5: Rate Limit Exhaustion on Free Tier
**What goes wrong:** 429 errors during development/testing when making multiple rapid requests.
**Why it happens:** Gemini 2.5 Flash free tier: 10 RPM, 500 RPD. December 2025 cuts reduced limits significantly.
**How to avoid:** Single daily generation needs only 1 request. During development, add simple retry with backoff. Cache responses during testing.
**Warning signs:** `errors.APIError` with code 429.

### Pitfall 6: Hallucinated NGO Content
**What goes wrong:** Gemini invents fake statistics, names, or stories about PUM that could damage credibility.
**Why it happens:** Without source material grounding, LLMs generate plausible-sounding but fabricated content.
**How to avoid:** System instruction must explicitly state: "Generate content ONLY based on the provided source material. Never invent statistics, names, or stories." Prompt must always include `source_material` field.
**Warning signs:** Generated content contains specific numbers or names not present in source material.

## Code Examples

Verified patterns from official sources:

### Client Initialization with Error Handling
```python
# Source: https://googleapis.github.io/python-genai/
import os
from google import genai
from google.genai import errors, types

def create_gemini_client() -> genai.Client:
    """Create Gemini API client from environment variable."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Get a free key at https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)
```

### System Instruction for PUM Content Generation
```python
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

TEMPLATE DATA RULES:
- headline: Short, attention-grabbing, in Bahasa Indonesia (max 60 chars)
- body text: Concise, informative, in Bahasa Indonesia
- stats numbers: Use actual numbers from source material only
- tips: Actionable, specific to Indonesian SME context
"""
```

### Complete Generation Flow
```python
# Source: https://ai.google.dev/gemini-api/docs/structured-output
def generate_post(
    source_material: str,
    pillar: ContentPillar,
    template_type: str,
) -> GeneratedPost:
    """Generate a complete Instagram post from source material."""
    client = create_gemini_client()

    prompt = f"""Generate an Instagram post for PUM Indonesia.

CONTENT PILLAR: {pillar.value}
TEMPLATE TYPE: {template_type}

SOURCE MATERIAL:
{source_material}

Generate the template_data dict matching the {template_type} template requirements,
bilingual captions, and relevant hashtags."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=GeneratedPost,
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )
        return GeneratedPost.model_validate_json(response.text)
    except errors.APIError as e:
        if e.code == 429:
            raise RuntimeError(f"Gemini rate limit exceeded: {e.message}")
        raise RuntimeError(f"Gemini API error ({e.code}): {e.message}")
```

### Retry Pattern for Rate Limits
```python
import time

def generate_with_retry(
    source_material: str,
    pillar: ContentPillar,
    template_type: str,
    max_retries: int = 3,
) -> GeneratedPost:
    """Generate post with exponential backoff on rate limit errors."""
    for attempt in range(max_retries):
        try:
            return generate_post(source_material, pillar, template_type)
        except RuntimeError as e:
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                wait = 2 ** attempt * 10  # 10s, 20s, 40s
                time.sleep(wait)
                continue
            raise
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `google-generativeai` SDK | `google-genai` SDK | Nov 2025 (EOL) | New import paths, Client-based API, breaking change |
| `genai.GenerativeModel()` | `client.models.generate_content()` | May 2025 (GA) | Centralized client, stateless calls |
| Manual JSON parsing from text | `response_schema=PydanticModel` | 2024-2025 | Guaranteed schema compliance, no parsing errors |
| Gemini 2.0 Flash | Gemini 2.5 Flash | Late 2025 | 2.0 retiring March-June 2026; 2.5 is faster and cheaper |
| `genai.configure(api_key=...)` | `genai.Client(api_key=...)` | May 2025 | Client object pattern, resource management |

**Deprecated/outdated:**
- `google-generativeai` package: EOL November 2025. All tutorials using `import google.generativeai` are outdated.
- `genai.GenerativeModel()` class: Replaced by `client.models.generate_content()`.
- `genai.configure()`: Replaced by `genai.Client(api_key=...)`.
- Gemini 2.0 Flash (`gemini-2.0-flash`): Retiring March-June 2026. Use `gemini-2.5-flash`.

## Open Questions

1. **Template data structure for event_promos pillar**
   - What we know: Event promos map to `quote_story` template type. The QuoteStoryTemplate expects `headline`, `body`, `attribution`, and optional `sector`.
   - What's unclear: Should event promos have a different data structure (e.g., event date, location) or reuse quote_story format with event-specific prompt instructions?
   - Recommendation: Reuse quote_story format for v1. Event-specific fields can be added in v2 if needed. System instruction should guide Gemini to format event info within the existing body text field.

2. **Source material format for Phase 4 integration**
   - What we know: Phase 4 (Content Research Sources) will provide source material from pum.nl, RSS, Google Sheets, and web search.
   - What's unclear: The exact format of source material that Phase 4 will produce.
   - Recommendation: Design the generator to accept a simple string `source_material` parameter. Phase 4 can concatenate its findings into a text block. Keep the interface loose for now.

3. **Hashtag count and language mix**
   - What we know: Instagram allows up to 30 hashtags. Best practices suggest 8-15 for engagement.
   - What's unclear: Exact ratio of Indonesian vs English vs brand hashtags.
   - Recommendation: System instruction targets 8-15 hashtags with mix: 2-3 brand (#PUMIndonesia, #TogetherWeGrow, #PUMExperts), 3-5 topic-specific in Indonesian, 3-5 topic-specific in English.

## Sources

### Primary (HIGH confidence)
- [Google Gen AI SDK PyPI](https://pypi.org/project/google-genai/) - Version 1.65.0, installation, Python requirements
- [Google Gen AI SDK GitHub](https://github.com/googleapis/python-genai) - API surface, Python 3.9+ requirement, pyproject.toml dependencies
- [Google Gen AI SDK Docs](https://googleapis.github.io/python-genai/) - Client API, GenerateContentConfig, system_instruction, response_schema, error handling
- [Gemini API Structured Output Docs](https://ai.google.dev/gemini-api/docs/structured-output) - Pydantic integration, response_mime_type, schema constraints
- [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing) - Free tier models, rate limits
- [Gemini API Migration Guide](https://ai.google.dev/gemini-api/docs/migrate) - Breaking changes from legacy to new SDK

### Secondary (MEDIUM confidence)
- [Gemini 2.0 Flash Deprecation Guide](https://www.isumsoft.com/internet/gemini-2-flash-deprecation-migration-guide.html) - Retirement dates (March-June 2026)
- [Gemini API Rate Limits Blog](https://blog.laozhang.ai/en/posts/gemini-api-free-tier) - Free tier RPM/RPD specifics post-December 2025 cuts
- [Google Structured Outputs Blog](https://blog.google/technology/developers/gemini-api-structured-outputs/) - JSON Schema support announcement

### Tertiary (LOW confidence)
- Free tier exact RPM/RPD numbers vary across sources (5-15 RPM depending on model). Official rate limits page defers to AI Studio dashboard. For production, verify in AI Studio.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official SDK docs, PyPI, GitHub all confirm google-genai as the current recommended SDK
- Architecture: HIGH - Structured output with Pydantic is a documented, first-class feature of the SDK
- Pitfalls: HIGH - Known issues (deprecated SDK, model retirement, default values) verified through GitHub issues and official docs

**Research date:** 2026-02-28
**Valid until:** 2026-03-28 (stable domain; google-genai SDK is GA)
