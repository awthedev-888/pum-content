---
phase: 02-image-template-engine
plan: 03
subsystem: templates
tags: [pillow, image-generation, tips-list, numbered-items, badges, instagram, adaptive-sizing]

# Dependency graph
requires:
  - phase: 02-01
    provides: "BaseTemplate class with canvas, gradient, patterns, decorations, watermark, text wrapping, font access"
provides:
  - "templates/tips_list.py with TipsListTemplate class for numbered tips/list Instagram posts"
  - "TipsListTemplate: title, 3-5 numbered items with orange circle badges, gradient background, diagonal lines, sector icon, watermark"
affects: [03-ai-content-generation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Numbered item layout with orange circle badge + body text beside badge"
    - "Adaptive font sizing: reduce body font by 2px + spacing by 5px when items overflow available height"
    - "Background brightness detection for dynamic text color contrast (white vs dark_green)"

key-files:
  created:
    - "templates/tips_list.py"
  modified:
    - "templates/__init__.py"

key-decisions:
  - "Badge diameter 40px with number font 22px Bold centered using anchor='mm' for clean visual appearance"
  - "Adaptive sizing reduces body font from 26px down to 20px minimum and item spacing from 30px to 15px minimum when content overflows"
  - "Text color determined by gradient start color brightness: white on dark backgrounds, dark_green on light backgrounds"

patterns-established:
  - "Numbered item layout pattern: badge ellipse + centered number + offset text wrapping"
  - "Adaptive content sizing pattern reusable for variable-length content in other templates"
  - "Sector icon loading from brand_config.yaml with graceful fallback if icon file missing"

requirements-completed: [IMG-03]

# Metrics
duration: 2min
completed: 2026-02-28
---

# Phase 2 Plan 3: Tips/List Template Summary

**TipsListTemplate with orange numbered badges, adaptive item sizing, gradient backgrounds, and sector icons for branded Instagram tips posts**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-28T11:29:44Z
- **Completed:** 2026-02-28T11:32:10Z
- **Tasks:** 1
- **Files created/modified:** 2

## Accomplishments
- Implemented TipsListTemplate rendering title + 3-5 numbered items with orange circle badges containing white centered numbers
- Adaptive font sizing automatically reduces body text (26px to 20px) and spacing (30px to 15px) when items overflow available vertical space
- Gradient background with diagonal line texture varies per render for visual variety
- Optional sector icon loaded from brand_config.yaml and placed bottom-left at 60x60
- KrabbelBabbel decoration at 15% opacity in top-right corner for brand consistency
- Dynamic text color (white vs dark_green) based on background brightness for readability
- Works correctly with 3, 4, and 5 items without overflow

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement TipsListTemplate with render() method** - `29d0e57` (feat)

## Files Created/Modified
- `templates/tips_list.py` - TipsListTemplate class with render(), _get_background_brightness(), _calculate_items_height(), _draw_sector_icon() methods
- `templates/__init__.py` - Added TipsListTemplate to package exports

## Decisions Made
- **Badge design:** 40px diameter orange (#FF6900) filled circle with 22px Bold white number centered using `anchor="mm"` for pixel-perfect centering
- **Adaptive sizing:** Body font reduces by 2px per iteration (floor: 20px) and item spacing reduces by 5px (floor: 15px) when total items height exceeds available space (Y 200-900)
- **Text color contrast:** Uses perceived brightness formula (0.299*R + 0.587*G + 0.114*B) on gradient start color to choose white or dark_green text

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - implementation followed plan specifications and all verification checks passed on first attempt.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- TipsListTemplate is ready for use by Phase 3 AI content generation
- Template follows same BaseTemplate inheritance pattern as QuoteStoryTemplate
- Adaptive sizing ensures variable-length AI-generated content will render correctly
- Sector icon integration ready for AI to specify relevant sector per post

## Self-Check: PASSED

---
*Phase: 02-image-template-engine*
*Completed: 2026-02-28*
