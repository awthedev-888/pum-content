"""Offline test suite for PUM research sources: web scraper and RSS parser.

Tests use mocked network calls to verify behavior without hitting pum.nl.
Conditional live test runs only when RUN_LIVE_TESTS=1 is set.

Usage:
    python3 tests/test_research_scraper.py
"""

import os
import sys

# Ensure project root is on sys.path for reliable imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from unittest.mock import patch, MagicMock
import requests


# Sample HTML for mocking pum.nl news listing page
SAMPLE_NEWS_LISTING_HTML = """
<html>
<body>
<div class="news-list">
    <a href="/article/queen-maxima-attends-pum-impact-awards/">Queen Maxima</a>
    <a href="/article/pum-supports-smes-in-indonesia/">PUM Supports SMEs</a>
    <a href="/article/new-partnership-announcement/">New Partnership</a>
    <a href="/article/annual-report-2025/">Annual Report</a>
    <a href="/article/volunteer-stories-jan/">Volunteer Stories</a>
</div>
</body>
</html>
"""

# Sample HTML for mocking an individual article page
SAMPLE_ARTICLE_HTML = """
<html>
<body>
<h1>Queen Maxima Attends PUM Impact Awards</h1>
<p>Short intro that is less than 30 chars</p>
<p>PUM Netherlands Senior Experts hosted the annual Impact Awards ceremony in The Hague, celebrating outstanding volunteer contributions to SME development worldwide.</p>
<p>Her Majesty Queen Maxima of the Netherlands graced the event as guest of honor, recognizing the vital role of senior experts in supporting small businesses across developing countries.</p>
<p>The ceremony highlighted success stories from Indonesia, Kenya, and Colombia where PUM experts made significant impact on local economies.</p>
</body>
</html>
"""


def main():
    errors = []
    passed = 0
    failed = 0
    skipped = 0

    # ---------------------------------------------------------------
    # 1. Import check - scraper
    # ---------------------------------------------------------------
    try:
        from research_sources.scraper import fetch_pum_news
        print("[OK]  1. Import check - fetch_pum_news importable")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 1. Import check scraper - {e}")
        errors.append(f"Import scraper: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 2. Import check - rss_reader
    # ---------------------------------------------------------------
    try:
        from research_sources.rss_reader import parse_rss_feed
        print("[OK]  2. Import check - parse_rss_feed importable")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. Import check rss_reader - {e}")
        errors.append(f"Import rss_reader: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 3. fetch_pum_news returns empty string on ConnectionError
    # ---------------------------------------------------------------
    try:
        from research_sources.scraper import fetch_pum_news
        with patch("research_sources.scraper.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
            result = fetch_pum_news()
            assert result == "", f"Expected empty string, got: {repr(result)}"
            assert isinstance(result, str), f"Expected str, got {type(result)}"
        print("[OK]  3. fetch_pum_news returns empty string on ConnectionError")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 3. fetch_pum_news ConnectionError - {e}")
        errors.append(f"Scraper ConnectionError: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 4. fetch_pum_news returns empty string on Timeout
    # ---------------------------------------------------------------
    try:
        from research_sources.scraper import fetch_pum_news
        with patch("research_sources.scraper.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
            result = fetch_pum_news()
            assert result == "", f"Expected empty string, got: {repr(result)}"
        print("[OK]  4. fetch_pum_news returns empty string on Timeout")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 4. fetch_pum_news Timeout - {e}")
        errors.append(f"Scraper Timeout: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 5. fetch_pum_news extracts articles from sample HTML
    # ---------------------------------------------------------------
    try:
        from research_sources.scraper import fetch_pum_news

        def mock_get_side_effect(url, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status = MagicMock()
            if "/news/" in url:
                mock_resp.text = SAMPLE_NEWS_LISTING_HTML
            else:
                mock_resp.text = SAMPLE_ARTICLE_HTML
            return mock_resp

        with patch("research_sources.scraper.requests.get", side_effect=mock_get_side_effect):
            with patch("research_sources.scraper.time.sleep"):  # Skip sleep in tests
                result = fetch_pum_news(max_articles=2)
                assert isinstance(result, str), f"Expected str, got {type(result)}"
                assert "###" in result, "Output should contain ### headers"
                assert "Queen Maxima" in result, "Output should contain article title"
                assert "Impact Awards" in result, "Output should contain article content"
        print("[OK]  5. fetch_pum_news extracts articles from sample HTML")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 5. fetch_pum_news article extraction - {e}")
        errors.append(f"Scraper extraction: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 6. fetch_pum_news respects max_articles limit
    # ---------------------------------------------------------------
    try:
        from research_sources.scraper import fetch_pum_news

        def mock_get_side_effect(url, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status = MagicMock()
            if "/news/" in url:
                mock_resp.text = SAMPLE_NEWS_LISTING_HTML
            else:
                mock_resp.text = SAMPLE_ARTICLE_HTML
            return mock_resp

        with patch("research_sources.scraper.requests.get", side_effect=mock_get_side_effect):
            with patch("research_sources.scraper.time.sleep"):
                result = fetch_pum_news(max_articles=2)
                # Count ### headers - should be exactly 2
                header_count = result.count("### ")
                assert header_count == 2, f"Expected 2 articles, got {header_count}"
        print("[OK]  6. fetch_pum_news respects max_articles=2 limit")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 6. fetch_pum_news max_articles - {e}")
        errors.append(f"Scraper max_articles: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 7. fetch_pum_news sends correct User-Agent header
    # ---------------------------------------------------------------
    try:
        from research_sources.scraper import fetch_pum_news, USER_AGENT

        def mock_get_side_effect(url, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status = MagicMock()
            mock_resp.text = SAMPLE_NEWS_LISTING_HTML if "/news/" in url else SAMPLE_ARTICLE_HTML
            return mock_resp

        with patch("research_sources.scraper.requests.get", side_effect=mock_get_side_effect) as mock_get:
            with patch("research_sources.scraper.time.sleep"):
                fetch_pum_news(max_articles=1)
                # Check that at least one call had User-Agent header
                assert mock_get.call_count >= 1, "requests.get should have been called"
                first_call = mock_get.call_args_list[0]
                headers = first_call.kwargs.get("headers", {})
                assert "User-Agent" in headers, f"User-Agent not in headers: {headers}"
                assert USER_AGENT in headers["User-Agent"], \
                    f"Expected '{USER_AGENT}' in User-Agent, got: {headers['User-Agent']}"
        print("[OK]  7. fetch_pum_news sends correct User-Agent header")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 7. fetch_pum_news User-Agent - {e}")
        errors.append(f"Scraper User-Agent: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 8. parse_rss_feed returns empty string for empty feed
    # ---------------------------------------------------------------
    try:
        from research_sources.rss_reader import parse_rss_feed

        mock_feed = MagicMock()
        mock_feed.entries = []

        with patch("research_sources.rss_reader.feedparser.parse", return_value=mock_feed):
            result = parse_rss_feed()
            assert result == "", f"Expected empty string for empty feed, got: {repr(result)}"
        print("[OK]  8. parse_rss_feed returns empty string for empty feed")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 8. parse_rss_feed empty feed - {e}")
        errors.append(f"RSS empty feed: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 9. parse_rss_feed returns formatted text for feed with entries
    # ---------------------------------------------------------------
    try:
        from research_sources.rss_reader import parse_rss_feed

        entry1 = MagicMock()
        entry1.get = lambda k, d="": {
            "title": "PUM Annual Report 2025",
            "summary": "PUM Netherlands published its annual report highlighting global impact.",
            "link": "https://www.pum.nl/article/annual-report-2025/",
            "published": "Mon, 15 Jan 2026 10:00:00 GMT",
        }.get(k, d)

        entry2 = MagicMock()
        entry2.get = lambda k, d="": {
            "title": "New Partnership in Indonesia",
            "summary": "PUM signed a partnership with Indonesian SME association.",
            "link": "https://www.pum.nl/article/new-partnership/",
            "published": "Wed, 20 Jan 2026 08:30:00 GMT",
        }.get(k, d)

        mock_feed = MagicMock()
        mock_feed.entries = [entry1, entry2]

        with patch("research_sources.rss_reader.feedparser.parse", return_value=mock_feed):
            result = parse_rss_feed()
            assert isinstance(result, str), f"Expected str, got {type(result)}"
            assert len(result) > 0, "Expected non-empty result"
            assert "PUM Annual Report 2025" in result, "Missing article title"
            assert "New Partnership in Indonesia" in result, "Missing second title"
            assert "###" in result, "Missing ### header format"
        print("[OK]  9. parse_rss_feed returns formatted text for entries")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 9. parse_rss_feed with entries - {e}")
        errors.append(f"RSS with entries: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 10. parse_rss_feed returns empty string on network error
    # ---------------------------------------------------------------
    try:
        from research_sources.rss_reader import parse_rss_feed

        with patch("research_sources.rss_reader.feedparser.parse", side_effect=Exception("Network error")):
            result = parse_rss_feed()
            assert result == "", f"Expected empty string on error, got: {repr(result)}"
        print("[OK]  10. parse_rss_feed returns empty string on network error")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 10. parse_rss_feed network error - {e}")
        errors.append(f"RSS network error: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 11. Conditional live test (only when RUN_LIVE_TESTS=1)
    # ---------------------------------------------------------------
    if os.environ.get("RUN_LIVE_TESTS") == "1":
        try:
            from research_sources.scraper import fetch_pum_news
            result = fetch_pum_news()
            assert isinstance(result, str), f"Expected str, got {type(result)}"
            assert len(result) > 0, "Live scrape returned empty string"
            assert "###" in result, "Live scrape should contain ### headers"
            print(f"[OK]  11. Live test - fetched {len(result)} chars from pum.nl")
            passed += 1
        except Exception as e:
            print(f"[FAIL] 11. Live test - {e}")
            errors.append(f"Live test: {e}")
            failed += 1
    else:
        print("[SKIP] 11. Live test - set RUN_LIVE_TESTS=1 to run")
        skipped += 1

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    total = passed + failed
    print(f"\n{passed}/{total} checks passed ({skipped} skipped)")

    if errors:
        print("\nFailures:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("All offline checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
