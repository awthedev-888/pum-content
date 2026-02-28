#!/usr/bin/env python3
"""Comprehensive smoke test for all three PUM Instagram template types.

Validates that QuoteStoryTemplate, TipsListTemplate, and ImpactStatsTemplate
produce correct 1080x1080 RGBA PNG output with Indonesian content, watermarks,
and visual variation across renders.

Usage:
    python3 tests/test_templates.py
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from templates import ImpactStatsTemplate, QuoteStoryTemplate, TipsListTemplate


# --- Sample data (Indonesian) ---

QUOTE_DATA = {
    "headline": "Kisah Sukses PUM Indonesia",
    "body": (
        "Bapak Sutrisno berhasil meningkatkan produksi pertanian sebesar 40% "
        "setelah mendapat bimbingan dari ahli PUM Belanda selama 3 bulan. "
        "Program pendampingan ini membantu petani kecil di Yogyakarta "
        "mengadopsi teknik pertanian modern yang ramah lingkungan."
    ),
    "attribution": "--- Bapak Sutrisno, Petani Yogyakarta",
    "sector": "agriculture",
}

TIPS_DATA = {
    "title": "5 Tips Ekspor untuk UMKM",
    "items": [
        "Pahami regulasi ekspor negara tujuan",
        "Siapkan sertifikasi produk yang diperlukan",
        "Manfaatkan program pendampingan PUM",
        "Bangun jaringan dengan buyer internasional",
        "Mulai dari pasar ASEAN terdekat",
    ],
    "sector": "manufacturing",
}

IMPACT_DATA = {
    "title": "Dampak PUM di Indonesia",
    "stats": [
        {"number": "1.200+", "label": "ahli sukarelawan"},
        {"number": "30+", "label": "negara aktif"},
        {"number": "45+", "label": "tahun pengalaman"},
    ],
}


def main():
    errors = []
    total_checks = 0
    passed_checks = 0

    output_dir = project_root / "output" / "test"

    # ===== 1. Import check =====
    total_checks += 1
    try:
        # Imports already done at module level; confirm classes are callable
        assert callable(QuoteStoryTemplate)
        assert callable(TipsListTemplate)
        assert callable(ImpactStatsTemplate)
        print("[OK] All three template classes imported successfully")
        passed_checks += 1
    except Exception as e:
        print(f"[FAIL] Import check: {e}")
        errors.append(f"Import check: {e}")

    # ===== 2. Quote/Story test =====
    total_checks += 1
    try:
        qt = QuoteStoryTemplate()
        img = qt.render(QUOTE_DATA)
        assert img.size == (1080, 1080), f"Wrong size: {img.size}"
        assert img.mode == "RGBA", f"Wrong mode: {img.mode}"
        out_path = output_dir / "smoke_quote_story.png"
        qt.save(img, out_path)
        assert out_path.exists(), "Output file not created"
        assert out_path.stat().st_size > 10000, (
            f"Output too small: {out_path.stat().st_size} bytes"
        )
        print("[OK] Quote/Story renders 1080x1080 RGBA, file > 10KB")
        passed_checks += 1
    except Exception as e:
        print(f"[FAIL] Quote/Story basic render: {e}")
        errors.append(f"Quote/Story basic render: {e}")

    # Quote/Story with long Indonesian text (adaptive sizing)
    total_checks += 1
    try:
        long_body = (
            "Ibu Sari adalah pengusaha kecil di Surabaya yang memulai bisnis "
            "kerajinan tangan dari rumah. Setelah bergabung dengan program PUM, "
            "beliau mendapat bimbingan langsung dari ahli pemasaran Belanda "
            "yang membantu mengembangkan strategi ekspor ke pasar Eropa. "
            "Dalam waktu 6 bulan, omzet usaha meningkat 200% dan produknya "
            "kini diekspor ke 5 negara Eropa. Program pendampingan PUM "
            "memberikan dampak yang signifikan bagi UMKM Indonesia."
        )
        img_long = qt.render({
            "headline": "Keberhasilan UMKM Bersama PUM",
            "body": long_body,
            "attribution": "--- Ibu Sari, Pengusaha Kerajinan Surabaya",
        })
        assert img_long.size == (1080, 1080)
        print("[OK] Quote/Story adaptive sizing with long text - no crash")
        passed_checks += 1
    except Exception as e:
        print(f"[FAIL] Quote/Story long text: {e}")
        errors.append(f"Quote/Story long text: {e}")

    # ===== 3. Tips/List test =====
    total_checks += 1
    try:
        tl = TipsListTemplate()
        img = tl.render(TIPS_DATA)
        assert img.size == (1080, 1080), f"Wrong size: {img.size}"
        assert img.mode == "RGBA", f"Wrong mode: {img.mode}"
        out_path = output_dir / "smoke_tips_list.png"
        tl.save(img, out_path)
        assert out_path.exists(), "Output file not created"
        assert out_path.stat().st_size > 10000, (
            f"Output too small: {out_path.stat().st_size} bytes"
        )
        print("[OK] Tips/List renders 1080x1080 RGBA, file > 10KB")
        passed_checks += 1
    except Exception as e:
        print(f"[FAIL] Tips/List basic render: {e}")
        errors.append(f"Tips/List basic render: {e}")

    # Tips/List with 3 items (minimum)
    total_checks += 1
    try:
        img_min = tl.render({
            "title": "3 Langkah Memulai Ekspor",
            "items": [
                "Riset pasar internasional",
                "Siapkan dokumen ekspor",
                "Hubungi buyer potensial",
            ],
        })
        assert img_min.size == (1080, 1080)
        print("[OK] Tips/List with 3 items - no crash")
        passed_checks += 1
    except Exception as e:
        print(f"[FAIL] Tips/List 3 items: {e}")
        errors.append(f"Tips/List 3 items: {e}")

    # ===== 4. Impact Stats test =====
    total_checks += 1
    try:
        ist = ImpactStatsTemplate()
        img = ist.render(IMPACT_DATA)
        assert img.size == (1080, 1080), f"Wrong size: {img.size}"
        assert img.mode == "RGBA", f"Wrong mode: {img.mode}"
        out_path = output_dir / "smoke_impact_stats.png"
        ist.save(img, out_path)
        assert out_path.exists(), "Output file not created"
        assert out_path.stat().st_size > 10000, (
            f"Output too small: {out_path.stat().st_size} bytes"
        )
        print("[OK] Impact Stats renders 1080x1080 RGBA, file > 10KB")
        passed_checks += 1
    except Exception as e:
        print(f"[FAIL] Impact Stats basic render: {e}")
        errors.append(f"Impact Stats basic render: {e}")

    # Impact Stats with 1 stat (minimum)
    total_checks += 1
    try:
        img_single = ist.render({
            "title": "Pencapaian Kami",
            "stats": [
                {"number": "10.000+", "label": "UMKM terbantu di seluruh dunia"},
            ],
        })
        assert img_single.size == (1080, 1080)
        print("[OK] Impact Stats with 1 stat - no crash")
        passed_checks += 1
    except Exception as e:
        print(f"[FAIL] Impact Stats 1 stat: {e}")
        errors.append(f"Impact Stats 1 stat: {e}")

    # ===== 5. Indonesian text with special characters =====
    total_checks += 1
    try:
        special_data = {
            "headline": "Dampak PUM --- Bersama Kita Tumbuh",
            "body": (
                "Program PUM telah membantu 40% UMKM Indonesia: mulai dari "
                "pelatihan (termasuk pemasaran digital), pendampingan ekspor, "
                "hingga sertifikasi produk. \"Kami sangat terbantu,\" kata Ibu "
                "Sari --- pengusaha asal Surabaya."
            ),
            "attribution": "--- Ibu Sari, Pengusaha (Surabaya)",
        }
        img_special = qt.render(special_data)
        assert img_special.size == (1080, 1080)
        print("[OK] Indonesian text with special characters renders correctly")
        passed_checks += 1
    except Exception as e:
        print(f"[FAIL] Special characters: {e}")
        errors.append(f"Special characters: {e}")

    # ===== 6. Watermark presence test =====
    total_checks += 1
    try:
        watermark_pass = True
        templates_to_check = [
            ("QuoteStory", qt, QUOTE_DATA),
            ("TipsList", tl, TIPS_DATA),
            ("ImpactStats", ist, IMPACT_DATA),
        ]
        for name, tmpl, data in templates_to_check:
            img = tmpl.render(data)
            # Check bottom-right corner region (last 150x80 pixels)
            corner = img.crop((
                img.width - 150,
                img.height - 80,
                img.width,
                img.height,
            ))
            pixels = list(corner.getdata())
            unique_pixels = set(pixels)
            if len(unique_pixels) <= 1:
                watermark_pass = False
                errors.append(
                    f"Watermark missing on {name}: "
                    "bottom-right corner is uniform color"
                )
                print(f"[FAIL] Watermark presence ({name}): uniform corner")

        if watermark_pass:
            print("[OK] Watermark detected in bottom-right corner for all templates")
            passed_checks += 1
    except Exception as e:
        print(f"[FAIL] Watermark presence check: {e}")
        errors.append(f"Watermark presence check: {e}")

    # ===== 7. Multiple renders produce visual variation =====
    total_checks += 1
    try:
        renders = []
        for _ in range(3):
            img = qt.render(QUOTE_DATA)
            out_tmp = output_dir / f"variation_test_{len(renders)}.png"
            qt.save(img, out_tmp)
            renders.append(out_tmp.stat().st_size)

        # At least 2 of 3 renders should have different file sizes
        # (proves gradient randomization is working)
        unique_sizes = len(set(renders))
        if unique_sizes >= 2:
            print(
                f"[OK] Multiple renders produce variation "
                f"({unique_sizes} unique sizes from 3 renders)"
            )
            passed_checks += 1
        else:
            # Even if file sizes match, check pixel data
            imgs = [qt.render(QUOTE_DATA) for _ in range(3)]
            pixel_samples = [img.getpixel((100, 100)) for img in imgs]
            unique_pixels = len(set(pixel_samples))
            if unique_pixels >= 2:
                print(
                    f"[OK] Multiple renders produce variation "
                    f"({unique_pixels} unique pixel samples from 3 renders)"
                )
                passed_checks += 1
            else:
                print(
                    "[FAIL] Multiple renders are identical "
                    "(no gradient randomization detected)"
                )
                errors.append("Multiple renders identical")

        # Clean up variation test files
        for i in range(3):
            tmp = output_dir / f"variation_test_{i}.png"
            if tmp.exists():
                tmp.unlink()
    except Exception as e:
        print(f"[FAIL] Multiple renders variation: {e}")
        errors.append(f"Multiple renders variation: {e}")

    # ===== Summary =====
    print(f"\n{'=' * 50}")
    print(f"{passed_checks}/{total_checks} template checks passed")
    print(f"{'=' * 50}")

    if errors:
        print("\nFailed checks:")
        for err in errors:
            print(f"  - {err}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
