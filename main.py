"""PUM Indonesia Content Generator - Main Pipeline Orchestrator.

Runs the complete content pipeline: research -> generate -> render -> email.
Designed to be called by GitHub Actions cron or manually via python main.py.
"""

import os
import sys
import logging
from datetime import date

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def render_image(post) -> str:
    """Render a branded image from the generated post data.

    Maps post.template_type to the correct template class via dictionary
    dispatch, renders the image, and saves it to the output directory.

    Args:
        post: GeneratedPost instance with template_type and template_data.

    Returns:
        Path to the saved PNG image.

    Raises:
        ValueError: If post.template_type is not recognized.
    """
    from templates import QuoteStoryTemplate, TipsListTemplate, ImpactStatsTemplate

    template_map = {
        "quote_story": QuoteStoryTemplate,
        "tips_list": TipsListTemplate,
        "impact_stats": ImpactStatsTemplate,
    }

    template_class = template_map.get(post.template_type)
    if template_class is None:
        raise ValueError(f"Unknown template type: {post.template_type}")

    template = template_class()
    img = template.render(post.template_data)
    output_path = f"output/pum_post_{date.today().isoformat()}.png"
    template.save(img, output_path)
    return output_path


def run_pipeline() -> bool:
    """Execute the 4-stage content pipeline.

    Each stage is wrapped in its own try/except block. If any stage fails,
    the error is logged and the function returns False immediately (all
    stages are critical -- downstream stages cannot proceed without
    upstream output).

    Returns:
        True if all stages succeeded, False if any stage failed.
    """
    # Stage 1: Research
    logger.info("=" * 50)
    logger.info("Stage 1: Gathering source material")
    logger.info("=" * 50)
    try:
        from research_sources import gather_source_material

        sheet_id = os.environ.get("GOOGLE_SHEET_ID")
        source_material = gather_source_material(sheet_id=sheet_id)
        logger.info("Source material gathered: %d characters", len(source_material))
    except Exception as e:
        logger.error("Stage 1 FAILED - Research: %s", e)
        return False

    # Stage 2: Generate content
    logger.info("=" * 50)
    logger.info("Stage 2: Generating content with Gemini")
    logger.info("=" * 50)
    try:
        from content_generator import generate_post

        post = generate_post(source_material)
        logger.info(
            "Content generated: pillar=%s, template=%s, hashtags=%d",
            post.content_pillar,
            post.template_type,
            len(post.hashtags),
        )
    except Exception as e:
        logger.error("Stage 2 FAILED - Generation: %s", e)
        return False

    # Stage 3: Render image
    logger.info("=" * 50)
    logger.info("Stage 3: Rendering branded image")
    logger.info("=" * 50)
    try:
        image_path = render_image(post)
        logger.info("Image saved: %s", image_path)
    except Exception as e:
        logger.error("Stage 3 FAILED - Render: %s", e)
        return False

    # Stage 4: Send email
    logger.info("=" * 50)
    logger.info("Stage 4: Sending email")
    logger.info("=" * 50)
    try:
        from email_sender import send_post_email

        send_post_email(post, image_path)
        logger.info("Pipeline complete - email sent successfully")
    except Exception as e:
        logger.error("Stage 4 FAILED - Email: %s", e)
        return False

    return True


def main():
    """Entry point: configure logging, load env, run pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("PUM Indonesia Content Generator - Starting pipeline")
    logger.info("Date: %s", date.today().isoformat())

    # Load .env for local development (no-op if .env doesn't exist)
    load_dotenv()

    success = run_pipeline()

    if success:
        logger.info("Pipeline completed successfully")
    else:
        logger.error("Pipeline failed - check logs above for details")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
