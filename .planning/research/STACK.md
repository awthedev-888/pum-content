# Stack Research: Automated Content Generation Pipeline

## Recommended Stack

### Runtime & Scheduler

| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| Language | Python | 3.11+ | High | Best ecosystem for AI APIs, image processing, web scraping |
| Scheduler | GitHub Actions | N/A | High | Free 2,000 min/month (public repo), cron syntax, secrets management |
| Package manager | pip + requirements.txt | N/A | High | Simple, no overhead for a script-based project |

### AI / Content Generation

| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| LLM API | Google Gemini (gemini-2.0-flash) | google-genai 1.x | High | Free tier: 15 RPM, 1M tokens/day. More than enough for 1 daily post |
| Web search | Google Search via Gemini grounding | Built-in | Medium | Gemini can ground responses with web search. Alternative: requests + BeautifulSoup for scraping pum.nl directly |
| Content research | BeautifulSoup4 + requests | bs4 0.0.2, requests 2.31+ | High | Scrape pum.nl news/stories. Lightweight, no headless browser needed |
| RSS parsing | feedparser | 6.0+ | High | Parse PUM blog RSS feeds for latest content |

### Image Generation

| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| Image library | Pillow (PIL) | 10.x+ | High | Industry standard for Python image manipulation. Supports text rendering, compositing, shapes |
| Text wrapping | textwrap (stdlib) | Built-in | High | No external dependency needed |
| Font rendering | Pillow + .ttf files | N/A | High | Store Google Fonts equivalents of brand fonts in repo |

### Email Delivery

| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| SMTP client | smtplib (stdlib) | Built-in | High | No external dependency. Gmail SMTP with App Password |
| Email formatting | email.mime (stdlib) | Built-in | High | Multipart emails with image attachment + HTML body |

### Data Sources

| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| Google Sheets | gspread | 6.x | High | Free, well-maintained. Uses service account (free) |
| Google auth | google-auth | 2.x | High | Required for gspread service account auth |

### Configuration

| Component | Choice | Version | Confidence | Rationale |
|-----------|--------|---------|------------|-----------|
| Config format | YAML | PyYAML 6.x | High | Human-readable brand config, content pillars, templates |
| Secrets | GitHub Actions Secrets | N/A | High | Store Gmail password, Gemini API key, Google Sheets credentials |

## What NOT to Use

| Technology | Why Not |
|-----------|---------|
| Canva Connect API | Requires developer approval, adds complexity. Pillow gives full control |
| OpenAI / ChatGPT | Free tier less generous than Gemini. Gemini Flash is sufficient |
| Selenium / Playwright | Overkill for scraping static pages. BeautifulSoup is lighter |
| Node.js / Sharp | Python ecosystem is better for AI + image generation combo |
| SendGrid / Resend | Gmail SMTP is simpler, no signup, already have account |
| Docker | Unnecessary for GitHub Actions — use setup-python action |
| Database | No persistence needed — each run is stateless, content brief is a file/sheet |

## Dependencies Summary (requirements.txt)

```
google-genai>=1.0.0
Pillow>=10.0.0
PyYAML>=6.0
beautifulsoup4>=4.12.0
requests>=2.31.0
feedparser>=6.0.0
gspread>=6.0.0
google-auth>=2.0.0
```

## Free Tier Limits

| Service | Limit | Our Usage | Headroom |
|---------|-------|-----------|----------|
| GitHub Actions | 2,000 min/month (public) | ~30 min/month (1 run/day x ~1 min) | 98.5% unused |
| Gemini API (Flash) | 15 RPM, 1M tokens/day | ~3 calls/day, ~5K tokens | 99.5% unused |
| Gmail SMTP | 500 emails/day | 1 email/day | 99.8% unused |
| Google Sheets API | 300 requests/min | 1 request/day | ~100% unused |

---
*Researched: 2026-02-28*
