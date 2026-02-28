# Pitfalls Research: Automated Content Generation Pipeline

## Critical Pitfalls

### 1. AI Hallucination in NGO Content
**Risk:** HIGH — Gemini generates fake PUM stories, fabricated statistics, or non-existent programs
**Warning signs:** Content mentions specific people, projects, or numbers not found in source material
**Prevention:**
- Always pass real source material (scraped content) to Gemini — never ask it to generate from nothing
- Prompt instructs Gemini to ONLY use provided context, never invent
- Email delivery allows human verification before posting
- Add disclaimer in email: "Verify facts before posting"
**Phase:** AI Generation (Phase 3)

### 2. Pillow Font Rendering Issues
**Risk:** MEDIUM — Fonts not found, wrong encoding for Indonesian characters (accents, special chars), text overflow
**Warning signs:** Boxes instead of characters, text running off image edges, ugly fallback fonts
**Prevention:**
- Use Google Fonts (Montserrat, Inter, Noto Sans) — guaranteed Unicode/Indonesian support
- Store .ttf files in repo (don't rely on system fonts — GitHub Actions runners have minimal fonts)
- Test with Indonesian text containing special characters early
- Implement text wrapping with size calculation before rendering
**Phase:** Image Templates (Phase 2)

### 3. Gmail SMTP Authentication Failures
**Risk:** MEDIUM — Google blocks "less secure app" access, App Password not set up correctly
**Warning signs:** SMTP connection refused, authentication error in GitHub Actions logs
**Prevention:**
- Use Gmail App Password (not regular password) — requires 2FA enabled on Google account
- Store as GitHub Actions secret `GMAIL_APP_PASSWORD`
- Test SMTP connection in isolation before integrating
- Gmail may block from unfamiliar IP (GitHub Actions runner) — send a test email first to "allow"
**Phase:** Email Delivery (Phase 5)

### 4. GitHub Actions Cron Timing Unreliability
**Risk:** LOW — GitHub Actions cron jobs can be delayed 5-30 minutes, sometimes skipped during high load
**Warning signs:** Posts arriving at inconsistent times
**Prevention:**
- This is acceptable — we're generating content for manual posting, exact timing doesn't matter
- The email arrives sometime in the morning, user posts when ready
- Don't build logic that depends on exact execution time
**Phase:** Orchestration (Phase 6)

### 5. Gemini API Free Tier Rate Limits
**Risk:** LOW — Hitting rate limits during content generation
**Warning signs:** 429 errors from Gemini API
**Prevention:**
- We only make 2-3 API calls per day (research prompt + generation prompt) — well within 15 RPM
- Add retry with exponential backoff (just in case)
- Use gemini-2.0-flash (highest free tier limits)
**Phase:** AI Generation (Phase 3)

### 6. Web Scraping Breakage
**Risk:** MEDIUM — pum.nl changes HTML structure, scraper breaks silently
**Warning signs:** Empty research results, scraper returns no content
**Prevention:**
- Design scraper to be resilient (try multiple selectors)
- If scraping fails, fall back to content brief file / Google Sheets
- Log scraping results so failures are visible in GitHub Actions logs
- Don't make the entire pipeline depend on scraping — it's one input among several
**Phase:** Content Research (Phase 4)

### 7. Brand Inconsistency Across Templates
**Risk:** MEDIUM — Templates look different from each other, don't feel like same brand
**Warning signs:** Inconsistent spacing, color usage, logo placement across templates
**Prevention:**
- Single brand_config.yaml is the source of truth for ALL templates
- Define shared constants: margins, padding, logo position, text areas
- Build a base template class that all templates inherit from
- Review all 3 templates side by side before shipping
**Phase:** Image Templates (Phase 2)

### 8. Bilingual Caption Quality
**Risk:** MEDIUM — AI generates awkward Bahasa Indonesia or mixing languages incorrectly
**Warning signs:** Unnatural phrasing, formal/stiff Indonesian, incorrect grammar
**Prevention:**
- Provide example captions in the Gemini prompt (few-shot learning)
- Specify tone: "casual professional, Instagram-friendly, not formal/academic"
- Structure: Indonesian first, then English translation (separated by line break)
- Human review catches this — that's why we email instead of auto-post
**Phase:** AI Generation (Phase 3)

### 9. Google Sheets API Authentication in CI
**Risk:** MEDIUM — Service account setup is confusing, credentials file management
**Warning signs:** Authentication errors, "insufficient permissions" from Sheets API
**Prevention:**
- Create Google Cloud service account (free)
- Share the Google Sheet with the service account email
- Store the service account JSON as a GitHub Actions secret
- Use `gspread` library which handles auth cleanly
**Phase:** Content Research (Phase 4)

### 10. Large Image Files in Git
**Risk:** LOW — Generated images or large brand assets bloating the repo
**Warning signs:** Repo size growing, slow clones
**Prevention:**
- Add `output/` to .gitignore (generated images are ephemeral)
- Keep brand assets small (logo PNG < 500KB, fonts < 1MB each)
- Don't commit generated content — it's delivered via email
**Phase:** Foundation (Phase 1)

## Summary Priority Matrix

| Pitfall | Impact | Likelihood | Priority |
|---------|--------|------------|----------|
| AI hallucination | High | High | P0 — Must address |
| Font rendering | Medium | Medium | P1 — Address in Phase 2 |
| Gmail SMTP auth | Medium | Medium | P1 — Test early |
| Bilingual quality | Medium | Medium | P1 — Prompt engineering |
| Brand inconsistency | Medium | Medium | P1 — Design system |
| Web scraping breakage | Medium | Medium | P2 — Build fallbacks |
| Google Sheets auth | Medium | Low | P2 — Follow guide |
| Cron timing | Low | Medium | P3 — Accept it |
| Rate limits | Low | Low | P3 — Add retry |
| Large files in git | Low | Low | P3 — Gitignore |

---
*Researched: 2026-02-28*
