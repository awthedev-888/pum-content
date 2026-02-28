# Architecture Research: Automated Content Generation Pipeline

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Cron)                      │
│                    Trigger: daily 9 AM WIB                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              1. Content Research Module                       │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ pum.nl   │ │ RSS Feed │ │ Google   │ │ Content Brief│   │
│  │ Scraper  │ │ Parser   │ │ Sheets   │ │ File (YAML)  │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
│       └─────────────┴────────────┴──────────────┘            │
│                         │                                    │
│                    Raw Context                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              2. AI Generation Module (Gemini)                │
│                                                              │
│  Input: raw context + content pillar + brand voice           │
│                                                              │
│  Output:                                                     │
│  ├── template_type: "quote" | "tips" | "stats"              │
│  ├── headline: "..."                                         │
│  ├── body_text: "..." (or tips list, or stat number)         │
│  ├── caption_id: "..." (Bahasa Indonesia)                    │
│  ├── caption_en: "..." (English)                             │
│  └── hashtags: ["#pum", "#umkm", ...]                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              3. Image Generation Module (Pillow)             │
│                                                              │
│  Input: AI output + brand_config.yaml                        │
│                                                              │
│  ┌──────────────────────────────────────────┐                │
│  │           Template Engine                 │                │
│  │                                          │                │
│  │  brand_config.yaml ──→ colors, fonts     │                │
│  │  assets/logo.png   ──→ logo overlay      │                │
│  │  assets/fonts/     ──→ text rendering    │                │
│  │                                          │                │
│  │  Templates:                              │                │
│  │  ├── quote_template()                    │                │
│  │  ├── tips_template()                     │                │
│  │  └── stats_template()                    │                │
│  └──────────────────────────────────────────┘                │
│                                                              │
│  Output: post_YYYY-MM-DD.png (1080x1080)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              4. Email Delivery Module                         │
│                                                              │
│  Input: image file + captions + metadata                     │
│                                                              │
│  Compose email:                                              │
│  ├── Subject: "IG Post Ready — Feb 28, 2026"                │
│  ├── Body: caption (ID + EN), hashtags, posting suggestion  │
│  └── Attachment: post image PNG                              │
│                                                              │
│  Send via Gmail SMTP (App Password)                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Boundaries

### 1. Content Research (`scripts/research.py`)
- **Inputs:** pum.nl URL, RSS feed URL, Google Sheets ID, content_brief.yaml
- **Outputs:** dict of raw content (stories, stats, events, tips)
- **Talks to:** External web (pum.nl, Google Sheets API)
- **No dependency on:** Other modules

### 2. AI Generation (`scripts/generate.py`)
- **Inputs:** Raw content from research, content pillar for today, brand voice guidelines
- **Outputs:** Structured JSON with template type, text content, bilingual captions, hashtags
- **Talks to:** Gemini API
- **Depends on:** Content Research output (or falls back to general generation)

### 3. Image Generation (`scripts/image_generator.py`)
- **Inputs:** AI-generated content, brand_config.yaml, assets (logo, fonts)
- **Outputs:** PNG file (1080x1080)
- **Talks to:** Local filesystem only
- **Depends on:** AI Generation output, brand assets

### 4. Email Delivery (`scripts/send_email.py`)
- **Inputs:** PNG file, caption text, metadata
- **Outputs:** Email sent
- **Talks to:** Gmail SMTP
- **Depends on:** Image + AI Generation outputs

### 5. Orchestrator (`scripts/main.py`)
- **Coordinates:** All modules in sequence
- **Handles:** Error recovery, logging, day-of-week content pillar selection
- **Entry point:** Called by GitHub Actions

## Data Flow

```
Content Sources ──→ Research Module ──→ Raw Context (dict)
                                            │
                                            ▼
                                    Gemini API Call
                                            │
                                            ▼
                                    Structured Content (JSON)
                                       │           │
                                       ▼           ▼
                                  Pillow Render   Email Body
                                       │           │
                                       ▼           │
                                    PNG File ──────┘
                                                   │
                                                   ▼
                                              Gmail SMTP
                                                   │
                                                   ▼
                                              Inbox ✓
```

## File Structure

```
pum-content/
├── .github/
│   └── workflows/
│       └── daily_post.yml          # GitHub Actions cron
├── scripts/
│   ├── main.py                     # Orchestrator
│   ├── research.py                 # Content research
│   ├── generate.py                 # Gemini AI generation
│   ├── image_generator.py          # Pillow templates
│   └── send_email.py               # Email delivery
├── templates/
│   ├── quote.py                    # Quote/story template
│   ├── tips.py                     # Tips/list template
│   └── stats.py                    # Impact stats template
├── assets/
│   ├── logo.png                    # PUM logo
│   └── fonts/
│       ├── heading.ttf             # Brand heading font
│       └── body.ttf                # Brand body font
├── config/
│   ├── brand_config.yaml           # Colors, fonts, logo
│   ├── content_pillars.yaml        # Themes, rotation, voice
│   └── content_brief.yaml          # Manual story/event inputs
├── output/                         # Generated images (gitignored)
├── requirements.txt
└── README.md
```

## Build Order (Dependencies)

```
Phase 1: Foundation
├── Project setup (repo structure, requirements.txt)
├── Brand config (YAML schema, load brand assets)
└── No external dependencies

Phase 2: Image Templates
├── Pillow template engine
├── 3 template implementations
├── Depends on: Brand config + assets
└── Can test independently with hardcoded text

Phase 3: AI Content Generation
├── Gemini API integration
├── Content pillar rotation logic
├── Structured output parsing
├── Depends on: Content pillar config
└── Can test independently (print output)

Phase 4: Content Research Sources
├── pum.nl scraper
├── RSS feed parser
├── Google Sheets reader
├── Content brief loader
├── Depends on: Nothing (independent data sources)
└── Feeds into: AI Generation module

Phase 5: Email Delivery
├── Gmail SMTP setup
├── HTML email formatting
├── Image attachment
├── Depends on: Image + AI output

Phase 6: Orchestration & CI/CD
├── main.py pipeline
├── GitHub Actions workflow
├── Error handling, logging
├── Depends on: All previous phases
```

---
*Researched: 2026-02-28*
