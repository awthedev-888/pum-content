# PUM Indonesia Content Generator

## What This Is

An automated content pipeline for @pum_indonesia Instagram that researches PUM's latest activities, generates branded bilingual (Bahasa Indonesia + English) post images and captions daily, and emails them for manual review before posting. Built entirely on free-tier services: GitHub Actions, Gemini API, Pillow, and Gmail SMTP.

## Core Value

Consistent, research-backed branded content delivered daily to email — so the PUM Indonesia team just reviews, copies, and posts in 30 seconds.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] GitHub Actions cron triggers daily content generation
- [ ] Gemini API researches PUM activities before generating content (web search, pum.nl, RSS)
- [ ] Gemini generates bilingual captions (Bahasa Indonesia + English) with hashtags
- [ ] Pillow generates branded Instagram images (1080x1080) using PUM brand kit
- [ ] 3 post templates: Quote/Story, Tips/List, Impact Stats
- [ ] Content brief file support (manual story ideas, stats, events for AI to use)
- [ ] Google Sheets integration for content inputs
- [ ] Email delivery with image attachment + caption + hashtags
- [ ] Brand config file (colors, fonts, logo) drives all visual output
- [ ] Content rotates across 4 pillars: success stories, expert tips, impact stats, event promos

### Out of Scope

- Auto-posting to Instagram — manual review required, avoids account risk
- Facebook Business account / Instagram Graph API — too complex, requires Meta developer setup
- Canva API integration — brand templates built in code with Pillow instead
- Video/Reels generation — static image posts only for v1
- Carousel posts — single image per post for v1
- Real-time posting — daily batch via email, not on-demand

## Context

**About PUM:**
- PUM Netherlands Senior Experts — Dutch NGO, 45+ years, based in The Hague
- Tagline: "Together we grow"
- 1,200 volunteer experts advising SMEs in 30+ countries
- Indonesia focus: supporting UMKM (small/medium enterprise) development
- Core values: committed, equal, connected, skilled
- SDG focus: decent work & economic growth, gender equality, climate action, food security
- 22 sectors: agriculture, food processing, textiles, healthcare, ICT, construction, hospitality, etc.

**Current @pum_indonesia state:**
- 29 posts, 114 followers — low posting consistency
- This tool aims to make daily posting effortless

**Content research sources (Gemini should use before generating):**
- pum.nl website (latest news, stories, updates)
- Google Search (recent PUM Indonesia news, events)
- RSS/news feeds from PUM blog
- Content brief file maintained by the team
- Google Sheets with content inputs (stories, stats, events)

**Content language:** Bilingual — Bahasa Indonesia primary, English secondary

**Brand assets:** Available in Canva team account, need to export:
- Logo PNG
- Brand hex colors
- Brand fonts (or Google Fonts equivalent)

## Constraints

- **Budget**: Zero additional cost — all services must be free tier
- **Tech stack**: Python + GitHub Actions (no server infrastructure)
- **Gemini API**: Free tier rate limits (15 RPM on Flash) — sufficient for 1 daily post
- **GitHub Actions**: 2,000 min/month on public repo
- **Email**: Gmail SMTP with App Password (500 emails/day free)
- **No Instagram API**: Content delivered via email for manual posting

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Email delivery instead of auto-post | Avoids Instagram account flagging, allows human review, no Facebook Business account needed | — Pending |
| Pillow over Canva API | Canva Connect API requires developer approval, Pillow is free and fully controlled | — Pending |
| Gemini over ChatGPT | Free tier is more generous, good enough for content generation | — Pending |
| Research-first content generation | AI must research PUM's actual activities before creating content — no hallucinated stories | — Pending |
| Bilingual captions | Target both Indonesian SME audience and international stakeholders | — Pending |
| Daily single post | Consistent cadence without overwhelming, fits within all free tier limits | — Pending |

---
*Last updated: 2026-02-28 after initialization*
