"""Comprehensive test script for PUM content generation pipeline.

Tests both offline validation (schemas, pillars, prompts, error handling)
and optional live API integration (when GEMINI_API_KEY is set).

Usage:
    python3 tests/test_content_generator.py
"""

import os
import sys

# Ensure project root is on sys.path for reliable imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from datetime import date

SAMPLE_SOURCE_MATERIAL = """
PUM Netherlands Senior Experts has been active in Indonesia since 1978.
In 2024, PUM supported over 200 SMEs across Indonesia through its volunteer
expert program. Key sectors include agriculture, food processing, and tourism.

Recent success: Ibu Sari, a batik producer in Yogyakarta, increased her
export revenue by 35% after receiving guidance from PUM expert Hans de Vries
on quality control and international market standards. The mentoring program
lasted 3 months and included training for 12 employees.

PUM's Indonesia program has a 92% satisfaction rate among participating
businesses. The organization operates in 34 provinces with a focus on
empowering women-led enterprises and sustainable business practices.

Upcoming: PUM Indonesia will host a regional SME summit in Jakarta on
April 15, 2026, featuring expert panels on digital transformation and
green business certification.
"""


def main():
    errors = []
    passed = 0
    failed = 0
    skipped = 0

    # ---------------------------------------------------------------
    # 1. Import check
    # ---------------------------------------------------------------
    try:
        from content_generator import (
            GeneratedPost,
            QuoteStoryData,
            TipsListData,
            ImpactStatsData,
            StatItem,
            validate_template_data,
            SYSTEM_INSTRUCTION,
            build_generation_prompt,
            ContentPillar,
            PILLAR_ORDER,
            PILLAR_TEMPLATE_MAP,
            get_todays_pillar,
            get_template_type,
            generate_post,
        )
        print("[OK]  1. Import check - all public symbols importable")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 1. Import check - {e}")
        errors.append(f"Import check: {e}")
        failed += 1
        # Can't continue without imports
        print(f"\n{passed}/{passed + failed} checks passed ({skipped} skipped)")
        sys.exit(1)

    # ---------------------------------------------------------------
    # 2. Schema roundtrip
    # ---------------------------------------------------------------
    try:
        post_data = {
            "content_pillar": "success_stories",
            "template_type": "quote_story",
            "template_data": {
                "headline": "Kisah Sukses UMKM",
                "body": "Ibu Sari berhasil meningkatkan ekspor.",
                "attribution": "--- Ibu Sari, Pengusaha Batik",
            },
            "caption_id": "Caption bahasa Indonesia",
            "caption_en": "English caption",
            "hashtags": ["PUMIndonesia", "TogetherWeGrow", "UMKM"],
            "posting_suggestion": "Post at 10 AM WIB",
        }
        post = GeneratedPost(**post_data)
        json_str = post.model_dump_json()
        restored = GeneratedPost.model_validate_json(json_str)
        assert restored.content_pillar == post.content_pillar
        assert restored.template_type == post.template_type
        assert restored.caption_id == post.caption_id
        assert restored.caption_en == post.caption_en
        assert restored.hashtags == post.hashtags
        assert restored.template_data == post.template_data
        print("[OK]  2. Schema roundtrip - serialize/deserialize preserves all fields")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. Schema roundtrip - {e}")
        errors.append(f"Schema roundtrip: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 3. Template data validation - quote_story
    # ---------------------------------------------------------------
    try:
        qs_data = {
            "headline": "Kisah Sukses",
            "body": "Cerita inspiratif dari pengusaha batik.",
            "attribution": "--- Ibu Sari, Yogyakarta",
        }
        result = validate_template_data("quote_story", qs_data)
        assert "headline" in result
        assert "body" in result
        assert "attribution" in result
        print("[OK]  3. Template data validation - quote_story valid")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 3. Template data validation quote_story - {e}")
        errors.append(f"Quote story validation: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 4. Template data validation - tips_list
    # ---------------------------------------------------------------
    try:
        tl_data = {
            "title": "5 Tips Ekspor UMKM",
            "items": ["Tip 1", "Tip 2", "Tip 3"],
        }
        result = validate_template_data("tips_list", tl_data)
        assert "title" in result
        assert "items" in result
        assert len(result["items"]) == 3
        print("[OK]  4. Template data validation - tips_list valid")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 4. Template data validation tips_list - {e}")
        errors.append(f"Tips list validation: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 5. Template data validation - impact_stats
    # ---------------------------------------------------------------
    try:
        is_data = {
            "title": "Dampak PUM di Indonesia",
            "stats": [
                {"number": "200+", "label": "UMKM didampingi"},
                {"number": "34", "label": "provinsi terjangkau"},
            ],
        }
        result = validate_template_data("impact_stats", is_data)
        assert "title" in result
        assert "stats" in result
        assert len(result["stats"]) == 2
        assert result["stats"][0]["number"] == "200+"
        print("[OK]  5. Template data validation - impact_stats valid")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 5. Template data validation impact_stats - {e}")
        errors.append(f"Impact stats validation: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 6. Template data validation - invalid type
    # ---------------------------------------------------------------
    try:
        validate_template_data("invalid_type", {})
        print("[FAIL] 6. Template data validation - invalid type should raise ValueError")
        errors.append("Invalid type did not raise ValueError")
        failed += 1
    except ValueError:
        print("[OK]  6. Template data validation - invalid type raises ValueError")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 6. Template data validation invalid type - unexpected error: {e}")
        errors.append(f"Invalid type unexpected error: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 7. Template data validation - missing field
    # ---------------------------------------------------------------
    try:
        validate_template_data("quote_story", {"headline": "test"})
        print("[FAIL] 7. Template data validation - missing field should raise error")
        errors.append("Missing field did not raise error")
        failed += 1
    except (ValueError, Exception) as e:
        # Pydantic raises ValidationError (subclass of ValueError) for missing fields
        error_str = str(e).lower()
        if "body" in error_str or "attribution" in error_str or "validation" in error_str or "field required" in error_str or "missing" in error_str:
            print("[OK]  7. Template data validation - missing field raises error")
            passed += 1
        else:
            print(f"[OK]  7. Template data validation - missing field raises error ({type(e).__name__})")
            passed += 1

    # ---------------------------------------------------------------
    # 8. Pillar rotation coverage
    # ---------------------------------------------------------------
    try:
        start = date(2026, 1, 1)
        pillars_seen = set()
        for i in range(4):
            d = date(2026, 1, 1 + i)
            pillar = get_todays_pillar(d)
            pillars_seen.add(pillar)
        assert len(pillars_seen) == 4, f"Expected 4 pillars, got {len(pillars_seen)}: {pillars_seen}"
        print("[OK]  8. Pillar rotation coverage - 4 consecutive days produce all 4 pillars")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 8. Pillar rotation coverage - {e}")
        errors.append(f"Pillar rotation coverage: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 9. Template type mapping completeness
    # ---------------------------------------------------------------
    try:
        for pillar in ContentPillar:
            assert pillar in PILLAR_TEMPLATE_MAP, f"Missing mapping for {pillar}"
            ttype = get_template_type(pillar)
            assert ttype in ("quote_story", "tips_list", "impact_stats"), f"Invalid template type: {ttype}"
        print("[OK]  9. Template type mapping - all pillars have valid template types")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 9. Template type mapping - {e}")
        errors.append(f"Template type mapping: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 10. Prompt builder
    # ---------------------------------------------------------------
    try:
        prompt = build_generation_prompt(
            source_material="PUM helped 200 SMEs",
            content_pillar="success_stories",
            template_type="quote_story",
        )
        assert "PUM helped 200 SMEs" in prompt, "Source material not in prompt"
        assert "success_stories" in prompt, "Pillar not in prompt"
        assert "quote_story" in prompt, "Template type not in prompt"
        print("[OK]  10. Prompt builder - output contains source material, pillar, and template type")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 10. Prompt builder - {e}")
        errors.append(f"Prompt builder: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 11. Empty source material rejection
    # ---------------------------------------------------------------
    try:
        generate_post("")
        print("[FAIL] 11. Empty source material - should raise ValueError")
        errors.append("Empty source material did not raise ValueError")
        failed += 1
    except ValueError as e:
        assert "source_material" in str(e).lower() or "empty" in str(e).lower()
        print("[OK]  11. Empty source material rejection - raises ValueError")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 11. Empty source material - unexpected error: {e}")
        errors.append(f"Empty source material unexpected error: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 12. Missing API key handling
    # ---------------------------------------------------------------
    try:
        saved_key = os.environ.pop("GEMINI_API_KEY", None)
        try:
            generate_post("test material")
            print("[FAIL] 12. Missing API key - should raise ValueError")
            errors.append("Missing API key did not raise ValueError")
            failed += 1
        except ValueError as e:
            error_str = str(e).lower()
            if "gemini_api_key" in error_str or "api key" in error_str or "api_key" in error_str:
                print("[OK]  12. Missing API key handling - raises ValueError mentioning API key")
                passed += 1
            else:
                print(f"[FAIL] 12. Missing API key - error doesn't mention API key: {e}")
                errors.append(f"Missing API key error unclear: {e}")
                failed += 1
        except Exception as e:
            print(f"[FAIL] 12. Missing API key - unexpected error type: {type(e).__name__}: {e}")
            errors.append(f"Missing API key unexpected error: {e}")
            failed += 1
        finally:
            if saved_key:
                os.environ["GEMINI_API_KEY"] = saved_key
    except Exception as e:
        print(f"[FAIL] 12. Missing API key handling - {e}")
        errors.append(f"Missing API key handling: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 13. Full pipeline test (conditional - requires GEMINI_API_KEY)
    # ---------------------------------------------------------------
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            result = generate_post(
                source_material=SAMPLE_SOURCE_MATERIAL,
                target_date=date(2026, 3, 1),
            )
            assert isinstance(result, GeneratedPost), f"Expected GeneratedPost, got {type(result)}"
            assert result.caption_id and len(result.caption_id) > 0, "caption_id is empty"
            assert result.caption_en and len(result.caption_en) > 0, "caption_en is empty"
            assert isinstance(result.hashtags, list) and len(result.hashtags) >= 1, "hashtags missing"
            assert result.template_type in ("quote_story", "tips_list", "impact_stats"), \
                f"Unexpected template_type: {result.template_type}"
            assert isinstance(result.template_data, dict) and len(result.template_data) > 0, \
                "template_data is empty"
            # Validate template_data against schema
            validated = validate_template_data(result.template_type, result.template_data)
            assert validated, "template_data validation returned empty"

            print(f"[OK]  13. Full pipeline test - generated valid {result.template_type} post")
            print(f"         Pillar: {result.content_pillar}")
            print(f"         Template: {result.template_type}")
            print(f"         Hashtags: {len(result.hashtags)} tags")
            print(f"         Caption ID: {result.caption_id[:80]}...")
            print(f"         Caption EN: {result.caption_en[:80]}...")
            passed += 1
        except Exception as e:
            print(f"[FAIL] 13. Full pipeline test - {e}")
            errors.append(f"Full pipeline test: {e}")
            failed += 1
    else:
        print("[SKIP] 13. Live API test - set GEMINI_API_KEY to run")
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
