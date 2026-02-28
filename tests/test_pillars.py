#!/usr/bin/env python3
"""Verify content pillar rotation and template type mapping.

This script validates that the ContentPillar enum, deterministic rotation,
and pillar-to-template mapping work correctly.

Usage:
    python3 tests/test_pillars.py
"""
import sys
from pathlib import Path
from datetime import date

# Project root for imports
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)


def main():
    errors = []

    # 1. Import check
    try:
        from content_generator.pillars import (
            ContentPillar,
            get_todays_pillar,
            get_template_type,
            PILLAR_ORDER,
            PILLAR_TEMPLATE_MAP,
        )
        print("[OK] All imports successful")
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return 1

    # 2. Enum values: All 4 pillar values exist and are strings
    try:
        expected = {"success_stories", "expert_tips", "impact_stats", "event_promos"}
        actual = {p.value for p in ContentPillar}
        assert actual == expected, f"Expected {expected}, got {actual}"
        for p in ContentPillar:
            assert isinstance(p.value, str), f"{p.name} value is not a string"
        print("[OK] All 4 pillar enum values exist and are strings")
    except Exception as e:
        errors.append(f"Enum values: {e}")
        print(f"[FAIL] Enum values: {e}")

    # 3. Deterministic rotation: Same date produces same pillar on repeated calls
    try:
        test_date = date(2026, 1, 1)
        result1 = get_todays_pillar(test_date)
        result2 = get_todays_pillar(test_date)
        assert result1 == result2, f"Non-deterministic: {result1} != {result2}"
        assert isinstance(result1, ContentPillar), f"Not a ContentPillar: {type(result1)}"
        print("[OK] Deterministic rotation: same date returns same pillar")
    except Exception as e:
        errors.append(f"Deterministic rotation: {e}")
        print(f"[FAIL] Deterministic rotation: {e}")

    # 4. 4-day cycle: 4 consecutive days produce 4 different pillars (complete coverage)
    try:
        pillars_in_cycle = set()
        for day_offset in range(4):
            test_date = date(2026, 1, 1 + day_offset)
            pillar = get_todays_pillar(test_date)
            pillars_in_cycle.add(pillar)
        assert len(pillars_in_cycle) == 4, (
            f"Expected 4 unique pillars in 4-day cycle, got {len(pillars_in_cycle)}: "
            f"{[p.value for p in pillars_in_cycle]}"
        )
        print("[OK] 4-day cycle produces all 4 different pillars")
    except Exception as e:
        errors.append(f"4-day cycle: {e}")
        print(f"[FAIL] 4-day cycle: {e}")

    # 5. Template mapping: Each pillar maps to expected template type
    try:
        mapping_checks = [
            (ContentPillar.SUCCESS_STORIES, "quote_story"),
            (ContentPillar.EXPERT_TIPS, "tips_list"),
            (ContentPillar.IMPACT_STATS, "impact_stats"),
            (ContentPillar.EVENT_PROMOS, "quote_story"),
        ]
        for pillar, expected_type in mapping_checks:
            actual_type = get_template_type(pillar)
            assert actual_type == expected_type, (
                f"{pillar.value} -> {actual_type}, expected {expected_type}"
            )
        print("[OK] All pillar-to-template mappings correct")
    except Exception as e:
        errors.append(f"Template mapping: {e}")
        print(f"[FAIL] Template mapping: {e}")

    # 6. Default date: get_todays_pillar() with no arg returns same as date.today()
    try:
        default_result = get_todays_pillar()
        explicit_result = get_todays_pillar(date.today())
        assert default_result == explicit_result, (
            f"Default {default_result} != explicit today {explicit_result}"
        )
        print("[OK] Default date matches date.today()")
    except Exception as e:
        errors.append(f"Default date: {e}")
        print(f"[FAIL] Default date: {e}")

    # 7. Template types are valid: All mapped types in valid set
    try:
        valid_types = {"quote_story", "tips_list", "impact_stats"}
        for pillar, template_type in PILLAR_TEMPLATE_MAP.items():
            assert template_type in valid_types, (
                f"{pillar.value} maps to invalid type: {template_type}"
            )
        print("[OK] All mapped template types are valid")
    except Exception as e:
        errors.append(f"Valid template types: {e}")
        print(f"[FAIL] Valid template types: {e}")

    # 8. Full year coverage: All 4 pillars appear at least once in 365 days
    try:
        year_pillars = set()
        for day in range(1, 366):
            test_date = date(2026, 1, 1) + __import__("datetime").timedelta(days=day - 1)
            year_pillars.add(get_todays_pillar(test_date))
        assert len(year_pillars) == 4, (
            f"Expected all 4 pillars in 365 days, got {len(year_pillars)}"
        )
        print("[OK] Full year coverage: all 4 pillars appear in 365 days")
    except Exception as e:
        errors.append(f"Full year coverage: {e}")
        print(f"[FAIL] Full year coverage: {e}")

    # Summary
    if errors:
        print(f"\n{len(errors)} check(s) failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"\nAll 8 checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
