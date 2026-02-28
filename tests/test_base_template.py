#!/usr/bin/env python3
"""Smoke test for BaseTemplate - verifies all shared layout utilities.

Tests canvas creation, gradient backgrounds, background patterns, KrabbelBabbel
decoration overlays, PUM logo watermark, pixel-based text wrapping, font loading
at multiple sizes, and brand color access.

Usage:
    python3 tests/test_base_template.py
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def main():
    project_root = _project_root
    errors = []

    # 1. Import BaseTemplate
    try:
        from templates.base import BaseTemplate
        from PIL import Image, ImageDraw
        print("[OK] BaseTemplate imported successfully")
    except Exception as e:
        print(f"[FAIL] Import: {e}")
        return 1

    # 2. Instantiate BaseTemplate (loads brand config, fonts, logos, decorations)
    try:
        bt = BaseTemplate()
        assert bt.config is not None, "Config not loaded"
        assert bt.font_heading is not None, "Heading font not loaded"
        assert bt.font_body is not None, "Body font not loaded"
        assert bt.font_decorative is not None, "Decorative font not loaded"
        assert bt.logo_primary is not None, "Primary logo not loaded"
        assert bt.logo_white is not None, "White logo not loaded"
        assert len(bt.decorations) == 3, f"Expected 3 decorations, got {len(bt.decorations)}"
        print("[OK] BaseTemplate instantiated with all assets")
    except Exception as e:
        print(f"[FAIL] Instantiation: {e}")
        errors.append(str(e))

    # 3. Create canvas
    try:
        img = bt.create_canvas()
        assert img.size == (1080, 1080), f"Wrong size: {img.size}"
        assert img.mode == "RGBA", f"Wrong mode: {img.mode}"
        print("[OK] Canvas created: 1080x1080 RGBA")
    except Exception as e:
        print(f"[FAIL] Canvas creation: {e}")
        errors.append(str(e))

    # 4. Draw gradient
    try:
        img = bt.draw_gradient(img, "#0E5555", "#D2E8D7")
        assert img.size == (1080, 1080)
        # Verify gradient: top pixel should be close to dark green, bottom to mint
        top_pixel = img.getpixel((540, 0))
        bottom_pixel = img.getpixel((540, 1079))
        assert top_pixel[0] < 50, f"Top pixel R too high for dark green: {top_pixel}"
        assert bottom_pixel[1] > 200, f"Bottom pixel G too low for mint: {bottom_pixel}"
        print(f"[OK] Gradient rendered (top={top_pixel[:3]}, bottom={bottom_pixel[:3]})")
    except Exception as e:
        print(f"[FAIL] Gradient: {e}")
        errors.append(str(e))

    # 5. Add dot pattern
    try:
        img = bt.add_dot_pattern(img)
        assert img.size == (1080, 1080)
        assert img.mode == "RGBA"
        print("[OK] Dot pattern overlay applied")
    except Exception as e:
        print(f"[FAIL] Dot pattern: {e}")
        errors.append(str(e))

    # 6. Add diagonal lines
    try:
        img = bt.add_diagonal_lines(img)
        assert img.size == (1080, 1080)
        assert img.mode == "RGBA"
        print("[OK] Diagonal line overlay applied")
    except Exception as e:
        print(f"[FAIL] Diagonal lines: {e}")
        errors.append(str(e))

    # 7. Add decoration (all 3 KrabbelBabbel decorations)
    try:
        img = bt.add_decoration(img, deco_index=0, position=(50, 50), size=200, opacity=0.2)
        img = bt.add_decoration(img, deco_index=1, position=(800, 100), size=150, opacity=0.15)
        img = bt.add_decoration(img, deco_index=2, position=(100, 800), size=180, opacity=0.2)
        assert img.size == (1080, 1080)
        print("[OK] All 3 KrabbelBabbel decorations applied at reduced opacity")
    except Exception as e:
        print(f"[FAIL] Decorations: {e}")
        errors.append(str(e))

    # 8. Add watermark (both primary and white)
    try:
        img = bt.add_watermark(img)
        assert img.size == (1080, 1080)
        # Test white logo variant too (on a copy)
        img_white = bt.add_watermark(img.copy(), use_white=True)
        assert img_white.size == (1080, 1080)
        print("[OK] Watermark applied (tested both primary and white logos)")
    except Exception as e:
        print(f"[FAIL] Watermark: {e}")
        errors.append(str(e))

    # 9. Text wrapping with Indonesian text
    try:
        test_text = (
            "Bapak Sutrisno berhasil meningkatkan produksi pertanian "
            "sebesar 40% setelah mendapat bimbingan dari ahli PUM Belanda "
            "selama 3 bulan di Yogyakarta, Indonesia."
        )
        lines = bt.wrap_text(test_text, bt.font_body, 920)
        assert len(lines) >= 2, f"Expected at least 2 lines, got {len(lines)}"
        assert all(isinstance(line, str) for line in lines)
        assert all(len(line) > 0 for line in lines)
        # Verify no line exceeds max width
        for line in lines:
            line_width = bt.font_body.getlength(line)
            assert line_width <= 920, f"Line exceeds max_width: '{line}' = {line_width}px"
        print(f"[OK] Text wrapping: {len(lines)} lines from Indonesian text, all within 920px")
    except Exception as e:
        print(f"[FAIL] Text wrapping: {e}")
        errors.append(str(e))

    # 10. Draw wrapped text on image
    try:
        draw = ImageDraw.Draw(img)
        headline = "Kisah Sukses PUM Indonesia"
        headline_font = bt.get_font("heading", bt.FONT_SIZES["heading_large"])
        draw.text(
            (bt.MARGIN, bt.HEADER_TOP),
            headline,
            font=headline_font,
            fill="#FFFFFF",
        )

        body_lines = bt.wrap_text(test_text, bt.font_body, bt.CONTENT_WIDTH)
        y = bt.CONTENT_TOP
        line_height = bt.font_body.getbbox("Ag")[3]
        for line in body_lines:
            draw.text((bt.MARGIN, y), line, font=bt.font_body, fill="#FFFFFF")
            y += line_height + 10
        print("[OK] Wrapped text drawn on image with heading and body")
    except Exception as e:
        print(f"[FAIL] Drawing text: {e}")
        errors.append(str(e))

    # 11. get_font() at multiple sizes
    try:
        font_heading_large = bt.get_font("heading", bt.FONT_SIZES["heading_large"])
        font_body_small = bt.get_font("body", bt.FONT_SIZES["body_small"])
        font_stat = bt.get_font("heading", bt.FONT_SIZES["stat_number"])
        font_deco = bt.get_font("decorative", bt.FONT_SIZES["decorative"])

        # Verify they render text
        assert font_heading_large.getlength("Test") > 0
        assert font_body_small.getlength("Test") > 0
        assert font_stat.getlength("1.200+") > 0
        assert font_deco.getlength("Test") > 0

        # Verify different sizes produce different widths
        w_large = font_heading_large.getlength("Test")
        w_small = font_body_small.getlength("Test")
        assert w_large > w_small, f"Large font ({w_large}px) should be wider than small ({w_small}px)"
        print(f"[OK] get_font() works at multiple sizes (heading_large={w_large:.0f}px, body_small={w_small:.0f}px)")
    except Exception as e:
        print(f"[FAIL] get_font(): {e}")
        errors.append(str(e))

    # 12. get_color() returns valid hex strings
    try:
        primary_colors = {
            "mint_green": bt.get_color("primary", "mint_green"),
            "dark_green": bt.get_color("primary", "dark_green"),
            "orange": bt.get_color("primary", "orange"),
        }
        secondary_colors = {
            "blue": bt.get_color("secondary", "blue"),
            "warm_brown": bt.get_color("secondary", "warm_brown"),
        }
        for name, color in {**primary_colors, **secondary_colors}.items():
            assert isinstance(color, str), f"{name} is not a string: {color}"
            assert color.startswith("#") and len(color) == 7, f"Invalid hex: {name} = {color}"
        print(f"[OK] get_color() returns valid hex: primary={list(primary_colors.values())}")
    except Exception as e:
        print(f"[FAIL] get_color(): {e}")
        errors.append(str(e))

    # 13. get_text_block_height() returns positive integer
    try:
        lines = bt.wrap_text("Test line one. Test line two is longer.", bt.font_body, 920)
        height = bt.get_text_block_height(lines, bt.font_body)
        assert isinstance(height, int), f"Height is not int: {type(height)}"
        assert height > 0, f"Height should be positive: {height}"
        # Empty lines should return 0
        empty_height = bt.get_text_block_height([], bt.font_body)
        assert empty_height == 0, f"Empty lines height should be 0: {empty_height}"
        print(f"[OK] get_text_block_height() = {height}px for {len(lines)} lines")
    except Exception as e:
        print(f"[FAIL] get_text_block_height(): {e}")
        errors.append(str(e))

    # 14. render() raises NotImplementedError
    try:
        bt.render({})
        print("[FAIL] render() should raise NotImplementedError")
        errors.append("render() did not raise NotImplementedError")
    except NotImplementedError:
        print("[OK] render() raises NotImplementedError (abstract method)")
    except Exception as e:
        print(f"[FAIL] render() unexpected error: {e}")
        errors.append(str(e))

    # 15. Save output and verify file
    try:
        output_path = project_root / "output" / "test" / "base_smoke_test.png"
        bt.save(img, output_path)
        assert output_path.exists(), f"Output file not found: {output_path}"
        file_size = output_path.stat().st_size
        assert file_size > 10240, f"Output file too small ({file_size} bytes), may be corrupt"

        # Verify it's a valid PNG by reopening
        verify_img = Image.open(str(output_path))
        assert verify_img.size == (1080, 1080), f"Reopened image wrong size: {verify_img.size}"
        assert verify_img.mode == "RGBA", f"Reopened image wrong mode: {verify_img.mode}"
        print(f"[OK] Saved to {output_path} ({file_size:,} bytes, valid 1080x1080 RGBA PNG)")
    except Exception as e:
        print(f"[FAIL] Save/verify: {e}")
        errors.append(str(e))

    # Results
    if errors:
        print(f"\n=== {len(errors)} check(s) FAILED ===")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\n=== All BaseTemplate smoke tests passed (15/15) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
