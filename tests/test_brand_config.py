#!/usr/bin/env python3
"""Verify brand config and all asset paths resolve correctly.

This script is the Phase 1 smoke test for the PUM Indonesia Content Generator.
It validates that brand_config.yaml is correct and every referenced asset exists
and loads properly.

Usage:
    python3 tests/test_brand_config.py
"""
import sys
import re
import yaml
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "brand_config.yaml"
    errors = []

    # 1. Config loads
    try:
        assert config_path.exists(), f"brand_config.yaml not found at {config_path}"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        print("[OK] brand_config.yaml loaded successfully")
    except Exception as e:
        print(f"[FAIL] brand_config.yaml failed to load: {e}")
        return 1

    # 2. Color format validation
    try:
        for group_name, group in config["colors"].items():
            for color_name, hex_val in group.items():
                assert isinstance(hex_val, str), \
                    f"Color {group_name}.{color_name} is not a string: {hex_val}"
                assert hex_val.startswith("#") and len(hex_val) == 7, \
                    f"Invalid hex color: {group_name}.{color_name} = {hex_val}"
                assert re.match(r"^#[0-9A-Fa-f]{6}$", hex_val), \
                    f"Invalid hex characters: {group_name}.{color_name} = {hex_val}"
        print("[OK] All color values are valid hex format")
    except AssertionError as e:
        print(f"[FAIL] Color validation: {e}")
        errors.append(str(e))

    # 3. Font files exist
    try:
        for font_name, font_info in config["fonts"].items():
            font_path = project_root / font_info["file"]
            assert font_path.exists(), f"Font not found: {font_name} -> {font_path}"
        print("[OK] All font files exist")
    except AssertionError as e:
        print(f"[FAIL] Font file check: {e}")
        errors.append(str(e))

    # 4. Logo files exist
    try:
        for logo_name, logo_path_str in config["logos"].items():
            logo_path = project_root / logo_path_str
            assert logo_path.exists(), f"Logo not found: {logo_name} -> {logo_path}"
        print("[OK] All logo files exist")
    except AssertionError as e:
        print(f"[FAIL] Logo file check: {e}")
        errors.append(str(e))

    # 5. Icon files exist
    try:
        icons_dir = project_root / config["icons"]["directory"]
        icon_count = 0
        for icon_key, icon_filename in config["icons"]["sectors"].items():
            icon_path = icons_dir / icon_filename
            assert icon_path.exists(), f"Icon not found: {icon_key} -> {icon_path}"
            icon_count += 1
        print(f"[OK] All {icon_count} sector icon files exist")
    except AssertionError as e:
        print(f"[FAIL] Icon file check: {e}")
        errors.append(str(e))

    # 6. Decoration files exist
    try:
        decorations_dir = project_root / config["decorations"]["directory"]
        for deco_filename in config["decorations"]["krabbelbabbel"]:
            deco_path = decorations_dir / deco_filename
            assert deco_path.exists(), f"Decoration not found: {deco_path}"
        print(f"[OK] All {len(config['decorations']['krabbelbabbel'])} KrabbelBabbel decoration files exist")
    except AssertionError as e:
        print(f"[FAIL] Decoration file check: {e}")
        errors.append(str(e))

    # 7. Font loading with Pillow
    try:
        from PIL import ImageFont

        sample_text = "PUM Indonesia \u2014 Bersama Kita Tumbuh"
        for font_name, font_info in config["fonts"].items():
            font_path = project_root / font_info["file"]
            font = ImageFont.truetype(str(font_path), size=24)
            bbox = font.getbbox(sample_text)
            assert bbox is not None, f"Font '{font_name}' returned None bbox for sample text"
            print(f"[OK] Font '{font_name}' loads in Pillow and renders text (bbox={bbox})")
    except Exception as e:
        print(f"[FAIL] Font Pillow loading: {e}")
        errors.append(str(e))

    # 8. Logo loading with Pillow
    try:
        from PIL import Image

        for logo_name, logo_path_str in config["logos"].items():
            logo_path = project_root / logo_path_str
            img = Image.open(logo_path)
            img.verify()
            print(f"[OK] Logo '{logo_name}' loads and verifies in Pillow")
    except Exception as e:
        print(f"[FAIL] Logo Pillow loading: {e}")
        errors.append(str(e))

    # 9. No secrets check
    try:
        config_content = config_path.read_text(encoding="utf-8")
        assert "API_KEY" not in config_content, \
            "brand_config.yaml contains 'API_KEY'"
        assert "password" not in config_content.lower(), \
            "brand_config.yaml contains 'password'"
        print("[OK] No secrets detected in brand_config.yaml")
    except AssertionError as e:
        print(f"[FAIL] Secrets check: {e}")
        errors.append(str(e))

    if errors:
        print(f"\n=== {len(errors)} check(s) FAILED ===")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\n=== All brand asset checks passed ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
