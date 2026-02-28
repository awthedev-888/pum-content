"""PUM.nl web scraper for content research pipeline.

Scrapes the pum.nl news listing page and individual article pages
to extract article titles and body text as source material for
the AI content generator.

Follows source module interface: returns str, never raises.
"""

import logging
import time

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

PUM_NEWS_URL = "https://www.pum.nl/news/"
PUM_BASE_URL = "https://www.pum.nl"
REQUEST_TIMEOUT = 15
USER_AGENT = "PUM-Content-Generator/1.0"


def fetch_pum_news(max_articles: int = 3) -> str:
    """Scrape latest news articles from pum.nl.

    Args:
        max_articles: Maximum number of articles to scrape (default 3).

    Returns:
        Formatted article text with ### headers, or empty string on failure.
    """
    try:
        headers = {"User-Agent": USER_AGENT}

        # Step 1: Get article links from news listing page
        response = requests.get(PUM_NEWS_URL, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Find article links - pattern: /article/{slug}/
        article_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/article/" in href:
                # Prepend base URL if relative
                if not href.startswith("http"):
                    href = PUM_BASE_URL + href
                # Deduplicate
                if href not in article_links:
                    article_links.append(href)

        # Step 2: Scrape each article (up to max_articles)
        articles = []
        for url in article_links[:max_articles]:
            try:
                # Polite delay between fetches (pum.nl is a small nonprofit site)
                if articles:
                    time.sleep(1)

                resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                article_soup = BeautifulSoup(resp.text, "html.parser")

                # Extract title from <h1>
                title_tag = article_soup.find("h1")
                title_text = title_tag.get_text(strip=True) if title_tag else "Untitled"

                # Extract body paragraphs (only substantial ones)
                paragraphs = article_soup.find_all("p")
                body = "\n".join(
                    p.get_text(strip=True) for p in paragraphs
                    if len(p.get_text(strip=True)) > 30
                )

                if body:
                    articles.append(f"### {title_text}\n{body}")
            except Exception as e:
                logger.warning("Failed to scrape %s: %s", url, e)
                continue

        return "\n\n".join(articles)

    except Exception as e:
        logger.warning("pum.nl scraper failed: %s", e)
        return ""
