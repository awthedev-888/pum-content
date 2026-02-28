"""Content brief YAML loader for PUM Indonesia content generation.

Loads structured content briefs (story ideas, statistics, upcoming events)
from a YAML file and formats them as readable text for AI input.

Follows the source module interface: returns str, never raises.
"""

import logging
import os

import yaml

logger = logging.getLogger(__name__)


def load_content_brief(filepath: str = "content_brief.yaml") -> str:
    """Load and format a content brief YAML file as readable text.

    Args:
        filepath: Path to the YAML content brief file.
                  Defaults to "content_brief.yaml" in the current directory.

    Returns:
        Formatted text string with story ideas, statistics, and events.
        Returns empty string if file is missing, empty, or on any error.
    """
    try:
        if not os.path.exists(filepath):
            logger.info("Content brief file not found: %s", filepath)
            return ""

        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None or not isinstance(data, dict) or len(data) == 0:
            logger.info("Content brief is empty: %s", filepath)
            return ""

        sections = []

        # Story Ideas section
        story_ideas = data.get("story_ideas")
        if story_ideas and isinstance(story_ideas, list):
            lines = []
            for idea in story_ideas:
                title = idea.get("title", "")
                description = idea.get("description", "")
                if title:
                    lines.append(f"- {title}: {description}" if description else f"- {title}")
            if lines:
                sections.append("Story Ideas:\n" + "\n".join(lines))

        # Key Statistics section
        stats = data.get("stats")
        if stats and isinstance(stats, list):
            lines = []
            for stat in stats:
                number = stat.get("number", "")
                context = stat.get("context", "")
                if number:
                    lines.append(f"- {number} {context}" if context else f"- {number}")
            if lines:
                sections.append("Key Statistics:\n" + "\n".join(lines))

        # Upcoming Events section
        events = data.get("events")
        if events and isinstance(events, list):
            lines = []
            for event in events:
                name = event.get("name", "")
                date = event.get("date", "")
                details = event.get("details", "")
                if name:
                    lines.append(f"- {name} ({date}): {details}")
            if lines:
                sections.append("Upcoming Events:\n" + "\n".join(lines))

        return "\n\n".join(sections)

    except Exception as e:
        logger.warning("Failed to load content brief from %s: %s", filepath, e)
        return ""
