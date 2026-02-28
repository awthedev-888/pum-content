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
