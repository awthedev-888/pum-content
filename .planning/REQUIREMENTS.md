# Requirements: PUM Indonesia Content Generator

**Defined:** 2026-02-28
**Core Value:** Consistent, research-backed branded content delivered daily to email — so the PUM Indonesia team just reviews, copies, and posts in 30 seconds.

## v1 Requirements

### Content Research

- [x] **RSRCH-01**: System scrapes pum.nl for latest news, stories, and updates
- [x] **RSRCH-02**: System parses PUM blog RSS feed for recent articles
- [x] **RSRCH-03**: System reads content brief YAML file for manual story ideas, stats, and events
- [x] **RSRCH-04**: System reads content inputs from a shared Google Sheet
- [x] **RSRCH-05**: System searches the internet (via Gemini grounding) for recent PUM Indonesia news

### AI Generation

- [x] **AIGEN-01**: Gemini generates captions based on researched content (never from nothing)
- [x] **AIGEN-02**: Captions are bilingual — Bahasa Indonesia primary, English secondary
- [x] **AIGEN-03**: Gemini generates relevant hashtags for each post
- [x] **AIGEN-04**: Content rotates daily across 4 pillars: success stories, expert tips, impact stats, event promos
- [x] **AIGEN-05**: Gemini selects appropriate template type based on content pillar

### Image Generation

- [x] **IMG-01**: System generates 1080x1080 branded Instagram images using Pillow
- [x] **IMG-02**: Brand config YAML file defines colors, fonts, and logo path
- [x] **IMG-03**: 3 template types: Quote/Story, Tips/List, Impact Stats
- [x] **IMG-04**: PUM logo watermark on every generated image
- [x] **IMG-05**: Templates use PUM brand kit colors, fonts, and icons
- [x] **IMG-06**: Templates include dynamic background patterns or gradients

### Email Delivery

- [x] **EMAIL-01**: System sends email with generated post image as attachment
- [x] **EMAIL-02**: Email body contains ready-to-copy bilingual caption and hashtags
- [x] **EMAIL-03**: Email includes posting suggestion (time and content theme)

### Infrastructure

- [ ] **INFRA-01**: GitHub Actions cron triggers pipeline daily
- [x] **INFRA-02**: All secrets (API keys, passwords) stored as GitHub Actions secrets
- [ ] **INFRA-03**: Pipeline handles errors gracefully and logs failures

## v2 Requirements

### Enhanced Delivery

- **DELV2-01**: HTML formatted email with inline image preview
- **DELV2-02**: Weekly content calendar email (batch of 7 posts)
- **DELV2-03**: Email approval workflow (reply to approve and auto-post)

### Enhanced Images

- **IMGV2-01**: Carousel/multi-image post generation
- **IMGV2-02**: Template randomization within type
- **IMGV2-03**: Photo backgrounds with overlay support

### Analytics

- **ANLV2-01**: Track which posts performed best (manual input)
- **ANLV2-02**: AI adjusts content strategy based on performance data

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-posting to Instagram | Account flagging risk, requires Facebook Business account, removes human review |
| Video/Reels generation | High complexity, static images sufficient for v1 |
| Multi-platform posting | Focus on Instagram only |
| Web dashboard | Over-engineering — email delivery is sufficient |
| User authentication | Single-user/team tool, no login needed |
| Database/persistence | Stateless runs are simpler, Google Sheets covers data |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| RSRCH-01 | Phase 4 | Complete |
| RSRCH-02 | Phase 4 | Complete |
| RSRCH-03 | Phase 4 | Complete |
| RSRCH-04 | Phase 4 | Complete |
| RSRCH-05 | Phase 4 | Complete |
| AIGEN-01 | Phase 3 | Complete |
| AIGEN-02 | Phase 3 | Complete |
| AIGEN-03 | Phase 3 | Complete |
| AIGEN-04 | Phase 3 | Complete |
| AIGEN-05 | Phase 3 | Complete |
| IMG-01 | Phase 2 | Complete |
| IMG-02 | Phase 1 | Complete |
| IMG-03 | Phase 2 | Complete |
| IMG-04 | Phase 2 | Complete |
| IMG-05 | Phase 2 | Complete |
| IMG-06 | Phase 2 | Complete |
| EMAIL-01 | Phase 5 | Complete |
| EMAIL-02 | Phase 5 | Complete |
| EMAIL-03 | Phase 5 | Complete |
| INFRA-01 | Phase 6 | Pending |
| INFRA-02 | Phase 1 | Complete |
| INFRA-03 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-28*
*Last updated: 2026-02-28 after roadmap creation*
