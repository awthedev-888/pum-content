---
phase: 04-content-research-sources
plan: 02
subsystem: research
tags: [yaml, gspread, google-sheets, content-brief, source-module]

# Dependency graph
requires:
  - phase: 03-ai-content-generation
    provides: "content_generator module consuming source_material text"
provides:
  - "load_content_brief() function for YAML content brief parsing"
  - "read_content_sheet() function for Google Sheets reading via service account"
  - "Sample content_brief.yaml with PUM Indonesia story ideas, stats, and events"
  - "Offline test suite for both modules (10 tests)"
affects: [04-content-research-sources, 05-email-delivery]

# Tech tracking
tech-stack:
  added: [gspread, PyYAML]
  patterns: [source-module-interface, graceful-degradation, yaml-content-brief]

key-files:
  created:
    - research_sources/content_brief.py
    - research_sources/sheets_reader.py
    - content_brief.yaml
    - tests/test_research_inputs.py
  modified: []

key-decisions:
  - "gspread module import mocked at module level for testability (patch 'research_sources.sheets_reader.gspread')"
  - "Content brief sections joined with double newline for readable AI input formatting"
  - "Empty values skipped in sheets row formatting (skip blank cells)"

patterns-established:
  - "Source module interface: single function -> str, never raises, logs warnings"
  - "YAML content brief schema: story_ideas, stats, events sections"
  - "Google Sheets auth via GSHEET_CREDENTIALS env var (JSON string)"

requirements-completed: [RSRCH-03, RSRCH-04]

# Metrics
duration: 4min
completed: 2026-02-28
---

# Phase 4 Plan 2: Content Brief & Sheets Reader Summary

**YAML content brief loader and Google Sheets reader with graceful degradation and 10 offline tests**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-28T14:33:27Z
- **Completed:** 2026-02-28T14:37:00Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Content brief loader parses YAML with story ideas, statistics, and events into formatted text for AI input
- Google Sheets reader authenticates via service account and formats spreadsheet rows as readable text
- Both modules follow source module interface: return str, never raise exceptions
- Sample content_brief.yaml with realistic PUM Indonesia data (3 stories, 4 stats, 2 events)
- Comprehensive offline test suite with 10 tests covering all edge cases

## Task Commits

Each task was committed atomically:

1. **Task 1: Content brief loader, sheets reader, and sample YAML**
   - `64a602c` (test: RED - failing tests)
   - `c7ac56a` (feat: GREEN - implementation)
2. **Task 2: Offline test suite for content brief and sheets reader**
   - `4d320df` (test: comprehensive test suite with 10 checks)
3. **Cleanup:** `a36d125` (chore: remove temporary TDD red test file)

_Note: TDD tasks have multiple commits (test -> feat)_

## Files Created/Modified
- `research_sources/content_brief.py` - YAML content brief loader with load_content_brief()
- `research_sources/sheets_reader.py` - Google Sheets reader with read_content_sheet()
- `content_brief.yaml` - Sample PUM Indonesia content brief (3 story ideas, 4 stats, 2 events)
- `tests/test_research_inputs.py` - 10 offline tests covering both modules
- `research_sources/__init__.py` - Package stub (created as Rule 3 fix since 04-01 ran in parallel)

## Decisions Made
- gspread module mocked at module level (`patch('research_sources.sheets_reader.gspread')`) for clean offline testing
- Content brief sections use labeled headers ("Story Ideas:", "Key Statistics:", "Upcoming Events:") for AI readability
- Empty spreadsheet cell values are skipped in row formatting to avoid noise
- YAML content brief defaults to project root `content_brief.yaml` path

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created research_sources/__init__.py package stub**
- **Found during:** Task 1 (content_brief.py and sheets_reader.py creation)
- **Issue:** Plan 04-01 had not yet completed -- research_sources/ directory and __init__.py did not exist
- **Fix:** Created directory and minimal __init__.py stub to unblock module creation
- **Files modified:** research_sources/__init__.py
- **Verification:** Python imports work correctly
- **Committed in:** c7ac56a (part of Task 1 commit)

**2. [Rule 3 - Blocking] Installed gspread dependency**
- **Found during:** Task 1 (sheets_reader.py implementation)
- **Issue:** gspread not in requirements.txt or installed (04-01 handles requirements.txt updates)
- **Fix:** pip3 install gspread>=6.2.0
- **Files modified:** None (runtime dependency only, requirements.txt owned by 04-01)
- **Verification:** `python3 -c "import gspread"` succeeds
- **Committed in:** N/A (runtime install only)

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both fixes necessary because 04-01 and 04-02 executed in parallel. No scope creep.

## Issues Encountered
- Plan 04-01 executing in parallel meant the research_sources/ package and gspread dependency were not yet available. Resolved by creating stub __init__.py and installing gspread via pip3.

## User Setup Required

**External services require manual configuration.** Google Sheets integration requires:
- `GSHEET_CREDENTIALS` env var: Service account JSON key from Google Cloud Console
- `GOOGLE_SHEET_ID` env var: Spreadsheet ID from the Google Sheet URL
- Google Sheets API must be enabled in the Google Cloud project
- The Google Sheet must be shared with the service account email

## Next Phase Readiness
- Content brief loader ready for aggregation in Plan 04-03
- Google Sheets reader ready for aggregation in Plan 04-03
- Both modules return str following source module interface pattern
- Sample content_brief.yaml provides immediate data for testing the full pipeline

## Self-Check: PASSED

- All 5 created files verified on disk
- All 4 commits verified in git log (64a602c, c7ac56a, 4d320df, a36d125)

---
*Phase: 04-content-research-sources*
*Completed: 2026-02-28*
