# Roadmap: PUM Indonesia Content Generator

## Overview

Build an automated content pipeline that researches PUM's activities, generates branded bilingual Instagram content, and delivers it via email daily. Starting with project foundation and brand setup, then building image templates, AI generation, content research sources, email delivery, and finally wiring everything together with GitHub Actions.

## Phases

- [ ] **Phase 1: Foundation & Brand Setup** - Project structure, dependencies, brand config, and assets
- [ ] **Phase 2: Image Template Engine** - Pillow-based branded image generation with 3 templates
- [ ] **Phase 3: AI Content Generation** - Gemini API integration for research-first bilingual content
- [ ] **Phase 4: Content Research Sources** - pum.nl scraper, RSS parser, Google Sheets, content brief
- [ ] **Phase 5: Email Delivery** - Gmail SMTP with image attachment and formatted caption
- [ ] **Phase 6: Orchestration & CI/CD** - Main pipeline script and GitHub Actions daily cron

## Phase Details

### Phase 1: Foundation & Brand Setup
**Goal**: Project has clean structure, all dependencies defined, brand config loaded, and PUM assets (logo, fonts, colors, icons) ready to use in code
**Depends on**: Nothing (first phase)
**Requirements**: IMG-02, INFRA-02
**Success Criteria** (what must be TRUE):
  1. `requirements.txt` installs all dependencies without errors
  2. `brand_config.yaml` contains PUM brand colors, font paths, and logo path
  3. Brand assets (logo PNG, fonts TTF, icons) exist in `assets/` directory
  4. A test script can load brand config and verify all asset paths resolve
**Plans**: 3 plans

Plans:
- [ ] 01-01: Project structure and dependencies
- [ ] 01-02: Brand config schema and YAML file
- [ ] 01-03: Asset preparation (logo, fonts, icons)

### Phase 2: Image Template Engine
**Goal**: Pillow generates 3 types of branded 1080x1080 Instagram post images with PUM brand identity, logo watermark, and dynamic backgrounds
**Depends on**: Phase 1
**Requirements**: IMG-01, IMG-03, IMG-04, IMG-05, IMG-06
**Success Criteria** (what must be TRUE):
  1. Quote/Story template renders with headline, body text, PUM logo, and brand colors
  2. Tips/List template renders numbered items with PUM styling and icons
  3. Impact Stats template renders large numbers with context text
  4. All templates include PUM logo watermark in consistent position
  5. Templates use dynamic background patterns or gradients
  6. Indonesian text with special characters renders correctly
**Plans**: 4 plans

Plans:
- [ ] 02-01: Base template engine with shared layout logic
- [ ] 02-02: Quote/Story template implementation
- [ ] 02-03: Tips/List template implementation
- [ ] 02-04: Impact Stats template implementation

### Phase 3: AI Content Generation
**Goal**: Gemini API generates structured content (template type, bilingual captions, hashtags) based on provided context, rotating across 4 content pillars
**Depends on**: Phase 1
**Requirements**: AIGEN-01, AIGEN-02, AIGEN-03, AIGEN-04, AIGEN-05
**Success Criteria** (what must be TRUE):
  1. Gemini generates bilingual caption (ID + EN) from provided source material
  2. Gemini selects appropriate template type based on content pillar
  3. Hashtags are relevant to PUM Indonesia and the specific content
  4. Content pillars rotate daily: success stories → expert tips → impact stats → event promos
  5. Output is structured JSON parseable by downstream modules
**Plans**: 3 plans

Plans:
- [ ] 03-01: Gemini API client and prompt engineering
- [ ] 03-02: Content pillar rotation and template selection logic
- [ ] 03-03: Structured output parsing and validation

### Phase 4: Content Research Sources
**Goal**: Pipeline can gather real PUM content from multiple sources (website, RSS, Google Sheets, content brief, web search) to feed the AI generator
**Depends on**: Phase 1
**Requirements**: RSRCH-01, RSRCH-02, RSRCH-03, RSRCH-04, RSRCH-05
**Success Criteria** (what must be TRUE):
  1. Scraper extracts latest news/stories from pum.nl
  2. RSS parser returns recent PUM blog articles
  3. Content brief YAML file is loaded and parsed correctly
  4. Google Sheets reader fetches content inputs from shared spreadsheet
  5. Gemini grounding returns recent PUM Indonesia web results
  6. If any source fails, pipeline continues with remaining sources
**Plans**: 4 plans

Plans:
- [ ] 04-01: pum.nl web scraper
- [ ] 04-02: RSS feed parser
- [ ] 04-03: Google Sheets reader with service account auth
- [ ] 04-04: Content brief file loader and Gemini web search

### Phase 5: Email Delivery
**Goal**: Generated post (image + caption + hashtags + posting suggestion) is delivered via email ready to copy-paste and post
**Depends on**: Phase 2, Phase 3
**Requirements**: EMAIL-01, EMAIL-02, EMAIL-03
**Success Criteria** (what must be TRUE):
  1. Email arrives with post image as attachment
  2. Email body contains bilingual caption ready to copy
  3. Email body contains hashtags ready to copy
  4. Email includes suggested posting time and content theme
  5. Email sends successfully via Gmail SMTP with App Password
**Plans**: 2 plans

Plans:
- [ ] 05-01: Gmail SMTP client with App Password auth
- [ ] 05-02: Email template with attachment, caption, and metadata

### Phase 6: Orchestration & CI/CD
**Goal**: Complete pipeline runs end-to-end on a daily GitHub Actions cron, handling errors gracefully
**Depends on**: Phase 2, Phase 3, Phase 4, Phase 5
**Requirements**: INFRA-01, INFRA-03
**Success Criteria** (what must be TRUE):
  1. `main.py` orchestrates: research → generate → render → email
  2. GitHub Actions workflow triggers daily at configured time (WIB)
  3. Pipeline logs each step and reports errors without crashing
  4. Secrets (API keys, Gmail password) are read from environment variables
  5. End-to-end test: cron triggers → email arrives with branded post
**Plans**: 3 plans

Plans:
- [ ] 06-01: Main orchestrator script (main.py)
- [ ] 06-02: GitHub Actions workflow (daily cron)
- [ ] 06-03: Error handling, logging, and end-to-end testing

## Progress

**Execution Order:**
Phases 1 first, then 2/3/4 can run in parallel, then 5, then 6.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Brand Setup | 0/3 | Not started | - |
| 2. Image Template Engine | 0/4 | Not started | - |
| 3. AI Content Generation | 0/3 | Not started | - |
| 4. Content Research Sources | 0/4 | Not started | - |
| 5. Email Delivery | 0/2 | Not started | - |
| 6. Orchestration & CI/CD | 0/3 | Not started | - |
