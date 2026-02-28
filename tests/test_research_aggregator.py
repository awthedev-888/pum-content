"""Offline test suite for web search module and source material aggregator.

Tests web search with mocked Gemini API and the gather_source_material()
aggregator with all 5 sources mocked for graceful degradation.

Usage:
    python3 tests/test_research_aggregator.py
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Ensure project root is on sys.path for reliable imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from research_sources.web_search import search_pum_indonesia_news
from research_sources import gather_source_material


def main():
    errors = []
    passed = 0
    failed = 0

    # ---------------------------------------------------------------
    # 1. search_pum_indonesia_news returns "" when GEMINI_API_KEY not set
    # ---------------------------------------------------------------
    try:
        saved = os.environ.pop("GEMINI_API_KEY", None)
        try:
            result = search_pum_indonesia_news()
            assert result == "", f"Expected '', got: {repr(result[:100])}"
            print("[OK]  1. search_pum_indonesia_news returns '' without API key")
            passed += 1
        finally:
            if saved:
                os.environ["GEMINI_API_KEY"] = saved
    except Exception as e:
        print(f"[FAIL] 1. search_pum_indonesia_news no API key - {e}")
        errors.append(f"No API key: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 2. search_pum_indonesia_news returns "" on API error
    # ---------------------------------------------------------------
    try:
        os.environ["GEMINI_API_KEY"] = "test-key"
        try:
            with patch("research_sources.web_search.genai") as mock_genai:
                mock_client = MagicMock()
                mock_client.models.generate_content.side_effect = Exception("API error")
                mock_genai.Client.return_value = mock_client
                result = search_pum_indonesia_news()
                assert result == "", f"Expected '', got: {repr(result[:100])}"
                print("[OK]  2. search_pum_indonesia_news returns '' on API error")
                passed += 1
        finally:
            os.environ.pop("GEMINI_API_KEY", None)
    except Exception as e:
        print(f"[FAIL] 2. search_pum_indonesia_news API error - {e}")
        errors.append(f"API error: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 3. search_pum_indonesia_news returns text on success
    # ---------------------------------------------------------------
    try:
        os.environ["GEMINI_API_KEY"] = "test-key"
        try:
            with patch("research_sources.web_search.genai") as mock_genai:
                mock_response = MagicMock()
                mock_response.text = "PUM experts visited Jakarta"
                mock_client = MagicMock()
                mock_client.models.generate_content.return_value = mock_response
                mock_genai.Client.return_value = mock_client
                result = search_pum_indonesia_news()
                assert result == "PUM experts visited Jakarta", (
                    f"Expected 'PUM experts visited Jakarta', got: {repr(result)}"
                )
                print("[OK]  3. search_pum_indonesia_news returns text on success")
                passed += 1
        finally:
            os.environ.pop("GEMINI_API_KEY", None)
    except Exception as e:
        print(f"[FAIL] 3. search_pum_indonesia_news success - {e}")
        errors.append(f"Success response: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 4. gather_source_material raises RuntimeError when ALL sources fail
    # ---------------------------------------------------------------
    try:
        with patch("research_sources.fetch_pum_news", return_value=""), \
             patch("research_sources.parse_rss_feed", return_value=""), \
             patch("research_sources.load_content_brief", return_value=""), \
             patch("research_sources.read_content_sheet", return_value=""), \
             patch("research_sources.search_pum_indonesia_news", return_value=""):
            try:
                gather_source_material(sheet_id="test-id")
                assert False, "Expected RuntimeError but none was raised"
            except RuntimeError as e:
                assert "AIGEN-01" in str(e), f"Expected AIGEN-01 in message, got: {e}"
                print("[OK]  4. gather_source_material raises RuntimeError when all fail")
                passed += 1
    except Exception as e:
        print(f"[FAIL] 4. gather_source_material all-fail RuntimeError - {e}")
        errors.append(f"All-fail RuntimeError: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 5. gather_source_material returns text when one source succeeds
    # ---------------------------------------------------------------
    try:
        with patch("research_sources.fetch_pum_news", return_value="PUM news article"), \
             patch("research_sources.parse_rss_feed", return_value=""), \
             patch("research_sources.load_content_brief", return_value=""), \
             patch("research_sources.read_content_sheet", return_value=""), \
             patch("research_sources.search_pum_indonesia_news", return_value=""):
            result = gather_source_material(sheet_id="test-id")
            assert "## Recent PUM News" in result, (
                f"Expected '## Recent PUM News' in output, got: {result[:200]}"
            )
            assert "PUM news article" in result, (
                f"Expected 'PUM news article' in output, got: {result[:200]}"
            )
            print("[OK]  5. gather_source_material returns text with one source")
            passed += 1
    except Exception as e:
        print(f"[FAIL] 5. gather_source_material one source - {e}")
        errors.append(f"One source: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 6. gather_source_material output has correct section headers
    #    for 3 successful sources (scraper, brief, web search)
    # ---------------------------------------------------------------
    try:
        with patch("research_sources.fetch_pum_news", return_value="News content"), \
             patch("research_sources.parse_rss_feed", return_value=""), \
             patch("research_sources.load_content_brief", return_value="Brief content"), \
             patch("research_sources.read_content_sheet", return_value=""), \
             patch("research_sources.search_pum_indonesia_news", return_value="Web results"):
            result = gather_source_material(sheet_id="test-id")
            # Should have 3 section headers
            assert "## Recent PUM News" in result, "Missing '## Recent PUM News'"
            assert "## Content Brief" in result, "Missing '## Content Brief'"
            assert "## Recent Web Results" in result, "Missing '## Recent Web Results'"
            # Should NOT have headers for failed sources
            assert "## PUM Blog Articles" not in result, (
                "Should not have '## PUM Blog Articles' (RSS returned empty)"
            )
            assert "## Content Inputs" not in result, (
                "Should not have '## Content Inputs' (Sheets returned empty)"
            )
            print("[OK]  6. gather_source_material has correct section headers for 3 sources")
            passed += 1
    except Exception as e:
        print(f"[FAIL] 6. gather_source_material section headers - {e}")
        errors.append(f"Section headers: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 7. gather_source_material skips sheets when sheet_id is None
    # ---------------------------------------------------------------
    try:
        with patch("research_sources.fetch_pum_news", return_value="News"), \
             patch("research_sources.parse_rss_feed", return_value=""), \
             patch("research_sources.load_content_brief", return_value=""), \
             patch("research_sources.read_content_sheet") as mock_sheets, \
             patch("research_sources.search_pum_indonesia_news", return_value=""):
            gather_source_material(sheet_id=None)
            mock_sheets.assert_not_called()
            print("[OK]  7. gather_source_material skips sheets when sheet_id=None")
            passed += 1
    except Exception as e:
        print(f"[FAIL] 7. gather_source_material sheet_id=None - {e}")
        errors.append(f"sheet_id=None: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 8. gather_source_material calls sheets when sheet_id provided
    # ---------------------------------------------------------------
    try:
        with patch("research_sources.fetch_pum_news", return_value="News"), \
             patch("research_sources.parse_rss_feed", return_value=""), \
             patch("research_sources.load_content_brief", return_value=""), \
             patch("research_sources.read_content_sheet", return_value="Sheet data") as mock_sheets, \
             patch("research_sources.search_pum_indonesia_news", return_value=""):
            result = gather_source_material(sheet_id="test-id")
            mock_sheets.assert_called_once_with("test-id")
            assert "## Content Inputs (Sheets)" in result, (
                "Expected sheets section header in output"
            )
            print("[OK]  8. gather_source_material calls sheets with sheet_id")
            passed += 1
    except Exception as e:
        print(f"[FAIL] 8. gather_source_material sheet_id provided - {e}")
        errors.append(f"sheet_id provided: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 9. Integration: real content_brief.yaml with network mocked
    # ---------------------------------------------------------------
    try:
        with patch("research_sources.fetch_pum_news", return_value=""), \
             patch("research_sources.parse_rss_feed", return_value=""), \
             patch("research_sources.read_content_sheet", return_value=""), \
             patch("research_sources.search_pum_indonesia_news", return_value=""):
            result = gather_source_material()
            assert len(result) > 0, "Expected non-empty result from content_brief.yaml"
            assert "## Content Brief" in result, "Expected '## Content Brief' header"
            assert "Batik" in result, "Expected 'Batik' from sample content_brief.yaml"
            print("[OK]  9. Integration: real content_brief.yaml with network mocked")
            passed += 1
    except Exception as e:
        print(f"[FAIL] 9. Integration with real content brief - {e}")
        errors.append(f"Integration: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 10. gather_source_material includes all successful sources
    # ---------------------------------------------------------------
    try:
        with patch("research_sources.fetch_pum_news", return_value="Scraper news"), \
             patch("research_sources.parse_rss_feed", return_value="RSS articles"), \
             patch("research_sources.load_content_brief", return_value="Brief data"), \
             patch("research_sources.read_content_sheet", return_value="Sheets data"), \
             patch("research_sources.search_pum_indonesia_news", return_value="Web data"):
            result = gather_source_material(sheet_id="all-test")
            assert "## Recent PUM News" in result, "Missing scraper section"
            assert "Scraper news" in result, "Missing scraper content"
            assert "## PUM Blog Articles" in result, "Missing RSS section"
            assert "RSS articles" in result, "Missing RSS content"
            assert "## Content Brief" in result, "Missing brief section"
            assert "Brief data" in result, "Missing brief content"
            assert "## Content Inputs (Sheets)" in result, "Missing sheets section"
            assert "Sheets data" in result, "Missing sheets content"
            assert "## Recent Web Results" in result, "Missing web section"
            assert "Web data" in result, "Missing web content"
            print("[OK]  10. gather_source_material includes all 5 successful sources")
            passed += 1
    except Exception as e:
        print(f"[FAIL] 10. gather_source_material all sources - {e}")
        errors.append(f"All sources: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 11. Conditional live test (only with RUN_LIVE_TESTS=1)
    # ---------------------------------------------------------------
    if os.environ.get("RUN_LIVE_TESTS") == "1":
        try:
            result = gather_source_material()
            assert len(result) > 0, "Live: expected non-empty result"
            print(f"[OK]  11. LIVE: gather_source_material returned {len(result)} chars")
            passed += 1
        except Exception as e:
            print(f"[FAIL] 11. LIVE: gather_source_material - {e}")
            errors.append(f"Live test: {e}")
            failed += 1
    else:
        print("[SKIP] 11. Live test (set RUN_LIVE_TESTS=1 to run)")

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    total = passed + failed
    print(f"\n{passed}/{total} checks passed")

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
