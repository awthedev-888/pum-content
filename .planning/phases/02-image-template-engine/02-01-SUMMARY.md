---
phase: 02-image-template-engine
plan: 01
subsystem: templates
tags: [pillow, image-generation, base-template, gradient, watermark, text-wrapping, variable-fonts, instagram]

# Dependency graph
requires:
  - phase: 01-03
    provides: "brand_config.yaml with PUM brand colors, fonts, logos, decorations"
  - phase: 01-02
    provides: "Brand assets (fonts, logos, icons, decorations) in assets/ directory"
provides:
  - "templates/ package with BaseTemplate class for all shared layout utilities"
  - "BaseTemplate: canvas creation, gradient backgrounds, dot/diagonal patterns, KrabbelBabbel decorations, logo watermark, pixel-based text wrapping, font/color access"
  - "tests/test_base_template.py - 15-check smoke test validating all BaseTemplate methods"
affects: [02-02-quote-story, 02-03-tips-list, 02-04-impact-stats]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "BaseTemplate inheritance pattern: subclasses override render(data) with template-specific layout"
    - "Pixel-based text wrapping via font.getlength() instead of character counting"
    - "Variable font weight differentiation via set_variation_by_axes([weight, width])"
    - "Line strip paste for gradient rendering (1px-high Image.new + paste per row)"
    - "RGBA alpha_composite for transparent pattern/decoration overlays"

key-files:
  created:
    - "templates/__init__.py"
    - "templates/base.py"
    - "tests/test_base_template.py"
  modified: []

key-decisions:
  - "Used font.set_variation_by_axes([700, 100]) for heading Bold weight and [400, 100] for body Regular, since both .ttf files are the same variable font renamed"
  - "Gradient uses HEIGHT-1 divisor for interpolation to ensure exact color2 at the last pixel row"
  - "Diagonal lines span range(-total, total, spacing) to ensure full canvas coverage at all angles"
  - "Test script adds project root to sys.path for reliable imports when run via python3 tests/test_base_template.py"

patterns-established:
  - "templates/ package structure with __init__.py exporting classes"
  - "BaseTemplate.__init__() loads config, fonts, logos, decorations once (not per render)"
  - "All Pillow API calls use modern non-deprecated methods (getbbox, getlength, LANCZOS)"
  - "Test scripts use sys.path.insert(0, project_root) for import reliability"

requirements-completed: [IMG-01, IMG-04, IMG-05, IMG-06]

# Metrics
duration: 4min
completed: 2026-02-28
---

# Phase 2 Plan 1: Base Template Engine Summary

**BaseTemplate class with 1080x1080 RGBA canvas, gradient backgrounds, dot/diagonal patterns, KrabbelBabbel decorations, PUM logo watermark, and pixel-based text wrapping using Pillow**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-28T11:22:01Z
- **Completed:** 2026-02-28T11:25:51Z
- **Tasks:** 2
- **Files created:** 3

## Accomplishments
- Created BaseTemplate class with 17 methods covering all shared layout utilities for branded Instagram image generation
- Gradient backgrounds render via efficient 1px strip paste with 6 brand palette combinations
- PUM logo watermark composites with correct alpha transparency in bottom-right corner (both primary and white variants)
- Pixel-based text wrapping using font.getlength() handles Indonesian text correctly
- All 3 KrabbelBabbel decorations load and render as subtle overlays with configurable opacity
- Variable font weights (Bold=700, Regular=400) correctly applied via set_variation_by_axes()
- Comprehensive smoke test validates 15 checks covering every BaseTemplate method

## Task Commits

Each task was committed atomically:

1. **Task 1: Create templates package with BaseTemplate class** - `104e422` (feat)
2. **Task 2: Verify BaseTemplate with visual smoke test** - `94e3ea2` (feat)

## Files Created/Modified
- `templates/__init__.py` - Package init exporting BaseTemplate class
- `templates/base.py` - BaseTemplate class with 17 methods: canvas creation, gradient rendering, dot/diagonal patterns, KrabbelBabbel decorations, logo watermark, text wrapping, text block height, font loading, color access, render (abstract), save
- `tests/test_base_template.py` - 15-check smoke test: import, instantiation, canvas, gradient, dot pattern, diagonal lines, decorations, watermark, text wrapping, text drawing, get_font, get_color, get_text_block_height, render NotImplementedError, save/verify

## Decisions Made
- **Variable font axis values:** Used `[700, 100]` for heading and `[400, 100]` for body (axes: weight, width). This is critical because both NotoSans-Bold.ttf and NotoSans-Regular.ttf are the same variable font file renamed, defaulting to weight 400 without explicit axis setting.
- **Gradient interpolation:** Used `HEIGHT - 1` as divisor to ensure the last pixel row is exactly `color2`, not a blend. This prevents an off-by-one where the gradient never quite reaches the end color.
- **Test path setup:** Added `sys.path.insert(0, project_root)` at module level in the test script so that `python3 tests/test_base_template.py` works regardless of the current working directory.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Test script initially failed with `ModuleNotFoundError: No module named 'templates'` when run via `python3 tests/test_base_template.py` because the project root was not on `sys.path`. Fixed by adding explicit path setup at the top of the test file (same pattern will be needed for future test scripts).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- BaseTemplate is ready for subclass implementation in Plans 02-02 through 02-04
- All shared utilities (canvas, gradient, patterns, decorations, watermark, text, fonts, colors) are tested and working
- Template subclasses only need to implement `render(data)` with their specific layout logic
- Test pattern established for future template tests

## Self-Check: PASSED

All 3 created files verified present on disk. Both commit hashes (104e422, 94e3ea2) confirmed in git log. base.py has 443 lines (exceeds 150 minimum). Smoke test output PNG exists at output/test/base_smoke_test.png.

---
*Phase: 02-image-template-engine*
*Completed: 2026-02-28*
