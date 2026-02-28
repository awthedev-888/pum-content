# Research Summary: PUM Indonesia Content Generator

## Stack Recommendation

**Python 3.11+ on GitHub Actions** with:
- `google-genai` — Gemini 2.0 Flash (free tier: 15 RPM, 1M tokens/day)
- `Pillow` — Image generation with brand fonts/colors
- `smtplib` (stdlib) — Gmail SMTP email delivery
- `beautifulsoup4` + `feedparser` — pum.nl scraping + RSS
- `gspread` — Google Sheets content inputs
- `PyYAML` — Brand and content config

All free tier. Total monthly cost: $0. Massive headroom on every service limit.

## Table Stakes Features

1. AI caption generation (bilingual ID + EN) with hashtags
2. Branded 1080x1080 image templates (3 types: quote, tips, stats)
3. Logo watermark on all images
4. Daily email delivery with image + caption
5. Brand config file (single source of truth)
6. Content pillar rotation

## Key Differentiators (Include in v1)

1. **Research-first generation** — AI scrapes pum.nl and reads content brief before generating (prevents hallucination)
2. **Google Sheets integration** — Team can add story ideas/events without touching code
3. **Bilingual output** — Indonesian primary, English secondary

## Architecture

Linear pipeline: Research → Generate → Render → Email

```
Content Sources → Gemini API → Pillow Templates → Gmail SMTP → Inbox
```

6 components, clean separation. Each module testable independently.

## Critical Pitfalls to Address

| # | Pitfall | Mitigation |
|---|---------|------------|
| 1 | AI hallucination | Research-first approach, never generate from nothing |
| 2 | Font rendering | Use Google Fonts (.ttf in repo), test Indonesian chars |
| 3 | Gmail SMTP auth | Use App Password, test in isolation |
| 4 | Brand inconsistency | Shared base template, single config |
| 5 | Bilingual quality | Few-shot examples in prompt, human review via email |

## Build Order

1. **Foundation** — repo structure, brand config, assets
2. **Image Templates** — Pillow engine + 3 templates
3. **AI Generation** — Gemini integration + content pillars
4. **Content Research** — pum.nl scraper, RSS, Sheets, content brief
5. **Email Delivery** — Gmail SMTP + HTML formatting
6. **Orchestration** — main.py + GitHub Actions workflow

---
*Synthesized: 2026-02-28*
