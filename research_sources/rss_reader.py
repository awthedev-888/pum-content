"""PUM RSS feed parser for content research pipeline.

Parses the pum.nl RSS feed to extract article titles, summaries,
and links as source material for the AI content generator.

Note: The pum.nl/feed/ RSS feed currently contains zero items
(as of 2026-02-28). This module handles both populated and empty
feeds gracefully.

Follows source module interface: returns str, never raises.
"""

import logging

import feedparser

logger = logging.getLogger(__name__)


def parse_rss_feed(feed_url: str = "https://www.pum.nl/feed/") -> str:
    """Parse PUM RSS feed for recent articles.

    Args:
        feed_url: URL of the RSS feed (default pum.nl/feed/).

    Returns:
        Formatted article text with ### headers, or empty string on failure
        or if the feed has no entries.
    """
    try:
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            return ""

        articles = []
        for entry in feed.entries[:5]:
            title = entry.get("title", "Untitled")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            published = entry.get("published", "")

            article_text = f"### {title}"
            if published:
                article_text += f" ({published})"
            article_text += f"\n{summary}"
            if link:
                article_text += f"\nSource: {link}"
            articles.append(article_text)

        return "\n\n".join(articles)

    except Exception as e:
        logger.warning("RSS parser failed: %s", e)
        return ""
