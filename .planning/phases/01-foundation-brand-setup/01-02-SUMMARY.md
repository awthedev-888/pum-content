---
phase: 01-foundation-brand-setup
plan: 02
subsystem: assets
tags: [pillow, google-fonts, noto-sans, permanent-marker, brand-kit, png, ttf]

# Dependency graph
requires:
  - phase: none
    provides: "Brand kit files from Canva export in Downloads folder"
provides:
  - "2 PUM logo PNGs in assets/logos/"
  - "22 sector icon PNGs in assets/icons/"
  - "3 KrabbelBabbel decoration PNGs in assets/decorations/"
  - "3 Google Font TTFs in assets/fonts/ (Noto Sans Regular, Bold, Permanent Marker)"
affects: [01-03-brand-config, 02-image-templates]

# Tech tracking
tech-stack:
  added: []
  patterns: ["assets/ directory structure: logos/, icons/, decorations/, fonts/"]

key-files:
  created:
    - "assets/logos/PUM_logo-donkergroen-rgb.png"
    - "assets/logos/PUM_logo-slogan-alternatief-wit-rgb_1.png"
    - "assets/icons/ (22 sector icon PNGs)"
    - "assets/decorations/ (3 KrabbelBabbel PNGs)"
    - "assets/fonts/NotoSans-Regular.ttf"
    - "assets/fonts/NotoSans-Bold.ttf"
    - "assets/fonts/PermanentMarker-Regular.ttf"
  modified: []

key-decisions:
  - "Used Noto Sans variable font renamed as static files (NotoSans-Regular.ttf, NotoSans-Bold.ttf) since Google Fonts no longer distributes static Noto Sans TTFs"
  - "PermanentMarker-Regular.ttf downloaded as static TTF from Google Fonts GitHub (only one weight exists)"

patterns-established:
  - "Asset organization: assets/{logos,icons,decorations,fonts}/ at project root"
  - "Font files named NotoSans-Regular.ttf and NotoSans-Bold.ttf (same variable font, weight set at runtime)"

requirements-completed: [IMG-02]

# Metrics
duration: 3min
completed: 2026-02-28
---

# Phase 1 Plan 2: Brand Asset Preparation Summary

**PUM brand assets (logos, 22 sector icons, KrabbelBabbel decorations) and Google Fonts (Noto Sans variable, Permanent Marker) organized in assets/ directory**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-28T04:59:43Z
- **Completed:** 2026-02-28T05:03:07Z
- **Tasks:** 2
- **Files created:** 30

## Accomplishments
- Copied 2 PUM logo PNGs, 22 sector icon PNGs, and 3 KrabbelBabbel decoration PNGs from brand kit to assets/
- Downloaded Noto Sans (variable font) and Permanent Marker (static TTF) from Google Fonts GitHub
- All 27 PNGs verified as valid images via Pillow Image.verify()
- All 3 TTFs verified loadable in Pillow ImageFont.truetype() with Indonesian text rendering

## Task Commits

Each task was committed atomically:

1. **Task 1: Copy brand assets from PUM Brand Kit into project** - `ab8b2fd` (feat)
2. **Task 2: Download Google Fonts (Noto Sans and Permanent Marker) as static TTF files** - `45310a1` (feat)

## Files Created/Modified
- `assets/logos/PUM_logo-donkergroen-rgb.png` - Primary dark green PUM logo watermark (1744x852)
- `assets/logos/PUM_logo-slogan-alternatief-wit-rgb_1.png` - White PUM logo with slogan (1848x1019)
- `assets/icons/*.png` - 22 sector icon PNGs (circular dark green with mint fill, ~297x297)
- `assets/decorations/KrabbelBabbel-Extra-01.png` - KrabbelBabbel scribble decoration (4243x2634)
- `assets/decorations/KrabbelBabbel-Extra-01 (1).png` - KrabbelBabbel variant (4243x2634)
- `assets/decorations/KrabbelBabbel-Extra-01 (2).png` - KrabbelBabbel variant (4243x2634)
- `assets/fonts/NotoSans-Regular.ttf` - Noto Sans variable font (body text, weight=400)
- `assets/fonts/NotoSans-Bold.ttf` - Noto Sans variable font (headings, weight=700 at runtime)
- `assets/fonts/PermanentMarker-Regular.ttf` - Permanent Marker static TTF (decorative/CTA text)

## Decisions Made
- **Variable font as static file replacement:** Google Fonts no longer distributes static Noto Sans Regular/Bold TTFs separately. Downloaded the variable font (`NotoSans[wdth,wght].ttf`) and saved it as `NotoSans-Regular.ttf` and `NotoSans-Bold.ttf`. Both are the same variable font file; the heading/body weight distinction (400 vs 700) is applied at runtime via Pillow's variation axis API. This approach maintains the file naming convention expected by brand_config.yaml in Plan 01-03.
- **Direct GitHub download:** Google Fonts download API returned HTML instead of ZIP files. Used GitHub repository direct download URLs as the plan's alternative approach.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Google Fonts download API returns HTML instead of ZIP**
- **Found during:** Task 2 (font download)
- **Issue:** `https://fonts.google.com/download?family=Noto+Sans` returns an HTML page rather than a ZIP file (likely requires browser-based authentication/JavaScript)
- **Fix:** Used alternative GitHub direct download URLs as specified in the plan's fallback approach. Downloaded variable font from `github.com/google/fonts/raw/main/ofl/notosans/` and Permanent Marker from `github.com/google/fonts/raw/main/apache/permanentmarker/`
- **Files modified:** assets/fonts/NotoSans-Regular.ttf, assets/fonts/NotoSans-Bold.ttf, assets/fonts/PermanentMarker-Regular.ttf
- **Verification:** All 3 fonts load in Pillow and render Indonesian text
- **Committed in:** 45310a1 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Font download source changed from Google Fonts ZIP to GitHub direct URL. Result is identical -- valid TTF files that load in Pillow. No scope creep.

## Issues Encountered
- Google Fonts static Noto Sans TTFs no longer available as separate downloads; the repo only has the variable font. Used variable font renamed to match expected filenames. Plan 01-03 brand_config.yaml will reference these actual filenames.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All brand assets are in place for brand_config.yaml (Plan 01-03) to reference
- Font paths: `assets/fonts/NotoSans-Regular.ttf`, `assets/fonts/NotoSans-Bold.ttf`, `assets/fonts/PermanentMarker-Regular.ttf`
- Logo paths: `assets/logos/PUM_logo-donkergroen-rgb.png`, `assets/logos/PUM_logo-slogan-alternatief-wit-rgb_1.png`
- Icon directory: `assets/icons/` with 22 sector PNGs
- Decoration directory: `assets/decorations/` with 3 KrabbelBabbel PNGs
- Note for Plan 01-03: Font config should reference actual filenames (not variable font bracket notation) since files are named NotoSans-Regular.ttf and NotoSans-Bold.ttf

## Self-Check: PASSED

All 30 files verified present on disk. Both commit hashes (ab8b2fd, 45310a1) confirmed in git log. SUMMARY.md exists.

---
*Phase: 01-foundation-brand-setup*
*Completed: 2026-02-28*
