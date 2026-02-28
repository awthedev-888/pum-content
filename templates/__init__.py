"""PUM Indonesia Content Generator - Image Templates Package.

Provides branded 1080x1080 Instagram image generation templates.
All templates inherit from BaseTemplate which handles brand config loading,
canvas creation, gradient backgrounds, watermark placement, and text utilities.
"""

from templates.base import BaseTemplate
from templates.quote_story import QuoteStoryTemplate
from templates.tips_list import TipsListTemplate

__all__ = ["BaseTemplate", "QuoteStoryTemplate", "TipsListTemplate"]
