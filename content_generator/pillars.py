"""Content pillar rotation and template type mapping.

Implements deterministic daily rotation across 4 content pillars using
day-of-year modulo arithmetic. Template type selection is hardcoded
per pillar (not AI-selected) for reliable rotation patterns.
"""

from datetime import date
from enum import Enum


class ContentPillar(str, Enum):
    """The 4 content pillars for PUM Indonesia Instagram posts."""
    SUCCESS_STORIES = "success_stories"
    EXPERT_TIPS = "expert_tips"
    IMPACT_STATS = "impact_stats"
    EVENT_PROMOS = "event_promos"


# Fixed rotation order -- do not change without updating tests
PILLAR_ORDER = [
    ContentPillar.SUCCESS_STORIES,
    ContentPillar.EXPERT_TIPS,
    ContentPillar.IMPACT_STATS,
    ContentPillar.EVENT_PROMOS,
]

# Deterministic mapping: pillar -> template type
# This is hardcoded (not AI-selected) per research recommendation.
# Event promos reuse quote_story format with event-specific prompt instructions.
PILLAR_TEMPLATE_MAP = {
    ContentPillar.SUCCESS_STORIES: "quote_story",
    ContentPillar.EXPERT_TIPS: "tips_list",
    ContentPillar.IMPACT_STATS: "impact_stats",
    ContentPillar.EVENT_PROMOS: "quote_story",
}


def get_todays_pillar(target_date: date = None) -> ContentPillar:
    """Get today's content pillar based on day of year.

    Uses day_of_year % 4 to deterministically rotate through pillars.
    Same date always returns the same pillar.

    Args:
        target_date: Specific date to get pillar for. Defaults to today.

    Returns:
        ContentPillar for the given date.
    """
    d = target_date or date.today()
    index = d.timetuple().tm_yday % len(PILLAR_ORDER)
    return PILLAR_ORDER[index]


def get_template_type(pillar: ContentPillar) -> str:
    """Map content pillar to image template type.

    Args:
        pillar: The content pillar to map.

    Returns:
        Template type string: 'quote_story', 'tips_list', or 'impact_stats'.
    """
    return PILLAR_TEMPLATE_MAP[pillar]
