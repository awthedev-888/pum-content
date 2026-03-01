"""Offline test suite for main.py pipeline orchestrator.

Tests pipeline flow, error handling, and template dispatch with fully
mocked external dependencies (API calls, SMTP, file I/O, Pillow).

Usage:
    python3 tests/test_main.py
"""

import os
import sys

# Project convention: add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import logging
from unittest.mock import patch, MagicMock

from main import render_image, run_pipeline


class MockPost:
    """Mock GeneratedPost for testing without content_generator dependency."""
    content_pillar = "success_stories"
    template_type = "quote_story"
    template_data = {"headline": "Test Headline", "body": "Test body text", "attribution": "Test Author"}
    caption_id = "Caption dalam Bahasa Indonesia"
    caption_en = "Caption in English"
    hashtags = ["PUMIndonesia", "UMKM"]
    posting_suggestion = "Best time: 10:00 WIB"


def main():
    errors = []

    # Suppress log output during tests
    logging.disable(logging.CRITICAL)

    # ==================================================================
    # PIPELINE STAGE FAILURE TESTS
    # ==================================================================

    # ===== Test 1: Pipeline returns False when research stage fails =====
    try:
        with patch("research_sources.gather_source_material") as mock_gather:
            mock_gather.side_effect = RuntimeError("All sources failed")
            result = run_pipeline()
            if result is not False:
                errors.append(
                    f"Test 1 (research fails): Expected False, got {result}"
                )
    except Exception as e:
        errors.append(f"Test 1 (research fails): {type(e).__name__}: {e}")

    # ===== Test 2: Pipeline returns False when generation stage fails =====
    try:
        with patch("research_sources.gather_source_material") as mock_gather, \
             patch("content_generator.generate_post") as mock_generate:
            mock_gather.return_value = "source material text"
            mock_generate.side_effect = RuntimeError("API error")
            result = run_pipeline()
            if result is not False:
                errors.append(
                    f"Test 2 (generation fails): Expected False, got {result}"
                )
    except Exception as e:
        errors.append(f"Test 2 (generation fails): {type(e).__name__}: {e}")

    # ===== Test 3: Pipeline returns False when render stage fails =====
    try:
        with patch("research_sources.gather_source_material") as mock_gather, \
             patch("content_generator.generate_post") as mock_generate, \
             patch("main.render_image") as mock_render:
            mock_gather.return_value = "source material text"
            mock_generate.return_value = MockPost()
            mock_render.side_effect = ValueError("Unknown template")
            result = run_pipeline()
            if result is not False:
                errors.append(
                    f"Test 3 (render fails): Expected False, got {result}"
                )
    except Exception as e:
        errors.append(f"Test 3 (render fails): {type(e).__name__}: {e}")

    # ===== Test 4: Pipeline returns False when email stage fails =====
    try:
        with patch("research_sources.gather_source_material") as mock_gather, \
             patch("content_generator.generate_post") as mock_generate, \
             patch("main.render_image") as mock_render, \
             patch("email_sender.send_post_email") as mock_send:
            mock_gather.return_value = "source material text"
            mock_generate.return_value = MockPost()
            mock_render.return_value = "output/test.png"
            mock_send.side_effect = RuntimeError("SMTP error")
            result = run_pipeline()
            if result is not False:
                errors.append(
                    f"Test 4 (email fails): Expected False, got {result}"
                )
    except Exception as e:
        errors.append(f"Test 4 (email fails): {type(e).__name__}: {e}")

    # ==================================================================
    # PIPELINE SUCCESS TEST
    # ==================================================================

    # ===== Test 5: Pipeline returns True when all stages succeed =====
    try:
        with patch("research_sources.gather_source_material") as mock_gather, \
             patch("content_generator.generate_post") as mock_generate, \
             patch("main.render_image") as mock_render, \
             patch("email_sender.send_post_email") as mock_send:
            mock_gather.return_value = "source material text"
            mock_generate.return_value = MockPost()
            mock_render.return_value = "output/test.png"
            result = run_pipeline()
            if result is not True:
                errors.append(
                    f"Test 5 (all succeed): Expected True, got {result}"
                )
            if mock_send.call_count != 1:
                errors.append(
                    f"Test 5 (all succeed): Expected send called once, "
                    f"got {mock_send.call_count}"
                )
    except Exception as e:
        errors.append(f"Test 5 (all succeed): {type(e).__name__}: {e}")

    # ==================================================================
    # PIPELINE ARGUMENT PASSING TEST
    # ==================================================================

    # ===== Test 6: Pipeline passes correct arguments between stages =====
    try:
        with patch("research_sources.gather_source_material") as mock_gather, \
             patch("content_generator.generate_post") as mock_generate, \
             patch("main.render_image") as mock_render, \
             patch("email_sender.send_post_email") as mock_send:
            mock_gather.return_value = "source material text"
            mock_post = MockPost()
            mock_generate.return_value = mock_post
            mock_render.return_value = "output/test.png"

            run_pipeline()

            # Verify gather was called (sheet_id from env, may be None)
            if mock_gather.call_count != 1:
                errors.append(
                    f"Test 6 (arg passing): gather not called once, "
                    f"got {mock_gather.call_count}"
                )

            # Verify generate_post was called with source material
            if mock_generate.call_count != 1:
                errors.append(
                    f"Test 6 (arg passing): generate not called once, "
                    f"got {mock_generate.call_count}"
                )
            else:
                gen_args = mock_generate.call_args[0]
                if gen_args[0] != "source material text":
                    errors.append(
                        f"Test 6 (arg passing): generate called with "
                        f"'{gen_args[0]}' instead of 'source material text'"
                    )

            # Verify send_post_email was called with post and image_path
            if mock_send.call_count != 1:
                errors.append(
                    f"Test 6 (arg passing): send not called once, "
                    f"got {mock_send.call_count}"
                )
            else:
                send_args = mock_send.call_args[0]
                if send_args[0] is not mock_post:
                    errors.append(
                        "Test 6 (arg passing): send not called with post object"
                    )
                if send_args[1] != "output/test.png":
                    errors.append(
                        f"Test 6 (arg passing): send called with "
                        f"'{send_args[1]}' instead of 'output/test.png'"
                    )
    except Exception as e:
        errors.append(f"Test 6 (arg passing): {type(e).__name__}: {e}")

    # ==================================================================
    # PIPELINE CALLS GATHER WITH SHEET_ID FROM ENV
    # ==================================================================

    # ===== Test 7: Pipeline calls gather with sheet_id from environment =====
    try:
        with patch.dict(os.environ, {"GOOGLE_SHEET_ID": "test-sheet-123"}), \
             patch("research_sources.gather_source_material") as mock_gather, \
             patch("content_generator.generate_post") as mock_generate, \
             patch("main.render_image") as mock_render, \
             patch("email_sender.send_post_email"):
            mock_gather.return_value = "source material text"
            mock_generate.return_value = MockPost()
            mock_render.return_value = "output/test.png"

            run_pipeline()

            call_kwargs = mock_gather.call_args[1]
            if call_kwargs.get("sheet_id") != "test-sheet-123":
                errors.append(
                    f"Test 7 (sheet_id): Expected 'test-sheet-123', "
                    f"got '{call_kwargs.get('sheet_id')}'"
                )
    except Exception as e:
        errors.append(f"Test 7 (sheet_id): {type(e).__name__}: {e}")

    # ==================================================================
    # RENDER_IMAGE TEMPLATE DISPATCH TESTS
    # ==================================================================

    # ===== Test 8: render_image dispatches to QuoteStoryTemplate =====
    try:
        with patch("templates.QuoteStoryTemplate") as mock_quote, \
             patch("templates.TipsListTemplate"), \
             patch("templates.ImpactStatsTemplate"):
            mock_instance = MagicMock()
            mock_instance.render.return_value = MagicMock()
            mock_quote.return_value = mock_instance

            post = MockPost()
            post.template_type = "quote_story"
            result = render_image(post)

            mock_quote.assert_called_once()
            mock_instance.render.assert_called_once_with(post.template_data)
            mock_instance.save.assert_called_once()
            if "pum_post_" not in result:
                errors.append(
                    f"Test 8 (quote_story dispatch): 'pum_post_' not in result '{result}'"
                )
    except Exception as e:
        errors.append(f"Test 8 (quote_story dispatch): {type(e).__name__}: {e}")

    # ===== Test 9: render_image dispatches to TipsListTemplate =====
    try:
        with patch("templates.QuoteStoryTemplate"), \
             patch("templates.TipsListTemplate") as mock_tips, \
             patch("templates.ImpactStatsTemplate"):
            mock_instance = MagicMock()
            mock_instance.render.return_value = MagicMock()
            mock_tips.return_value = mock_instance

            post = MockPost()
            post.template_type = "tips_list"
            result = render_image(post)

            mock_tips.assert_called_once()
            mock_instance.render.assert_called_once_with(post.template_data)
            mock_instance.save.assert_called_once()
            if "pum_post_" not in result:
                errors.append(
                    f"Test 9 (tips_list dispatch): 'pum_post_' not in result '{result}'"
                )
    except Exception as e:
        errors.append(f"Test 9 (tips_list dispatch): {type(e).__name__}: {e}")

    # ===== Test 10: render_image dispatches to ImpactStatsTemplate =====
    try:
        with patch("templates.QuoteStoryTemplate"), \
             patch("templates.TipsListTemplate"), \
             patch("templates.ImpactStatsTemplate") as mock_impact:
            mock_instance = MagicMock()
            mock_instance.render.return_value = MagicMock()
            mock_impact.return_value = mock_instance

            post = MockPost()
            post.template_type = "impact_stats"
            result = render_image(post)

            mock_impact.assert_called_once()
            mock_instance.render.assert_called_once_with(post.template_data)
            mock_instance.save.assert_called_once()
            if "pum_post_" not in result:
                errors.append(
                    f"Test 10 (impact_stats dispatch): 'pum_post_' not in result '{result}'"
                )
    except Exception as e:
        errors.append(f"Test 10 (impact_stats dispatch): {type(e).__name__}: {e}")

    # ===== Test 11: render_image raises ValueError for unknown template type =====
    try:
        with patch("templates.QuoteStoryTemplate"), \
             patch("templates.TipsListTemplate"), \
             patch("templates.ImpactStatsTemplate"):
            post = MockPost()
            post.template_type = "invalid_type"
            try:
                render_image(post)
                errors.append(
                    "Test 11 (unknown template): No ValueError raised"
                )
            except ValueError as e:
                if "invalid_type" not in str(e):
                    errors.append(
                        f"Test 11 (unknown template): Error doesn't mention "
                        f"'invalid_type': {e}"
                    )
    except Exception as e:
        errors.append(f"Test 11 (unknown template): {type(e).__name__}: {e}")

    # ===== Test 12: render_image output path contains date =====
    try:
        from datetime import date as date_cls
        with patch("templates.QuoteStoryTemplate") as mock_quote, \
             patch("templates.TipsListTemplate"), \
             patch("templates.ImpactStatsTemplate"):
            mock_instance = MagicMock()
            mock_instance.render.return_value = MagicMock()
            mock_quote.return_value = mock_instance

            post = MockPost()
            post.template_type = "quote_story"
            result = render_image(post)

            today_str = date_cls.today().isoformat()
            if today_str not in result:
                errors.append(
                    f"Test 12 (output date): Today's date '{today_str}' "
                    f"not in output path '{result}'"
                )
    except Exception as e:
        errors.append(f"Test 12 (output date): {type(e).__name__}: {e}")

    # Re-enable logging
    logging.disable(logging.NOTSET)

    # ===== Results =====
    total_tests = 12
    passed = total_tests - len(errors)
    print(f"\nMain Pipeline Tests: {passed}/{total_tests} passed")

    if errors:
        print(f"\nFAILED: {len(errors)} error(s)")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
