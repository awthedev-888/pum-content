# Features Research: Automated Content Generation Pipeline

## Table Stakes (Must Have)

These are the minimum features for a usable content pipeline.

### Content Generation
| Feature | Complexity | Description |
|---------|------------|-------------|
| AI caption generation | Medium | Generate engaging captions from content inputs |
| Hashtag generation | Low | Relevant hashtags for reach |
| Content pillar rotation | Low | Rotate through defined themes (stories, tips, stats, promos) |
| Bilingual output | Medium | Bahasa Indonesia + English in same caption |

### Image Generation
| Feature | Complexity | Description |
|---------|------------|-------------|
| Branded image templates | Medium | 1080x1080 images with brand colors, fonts, logo |
| Multiple template types | Medium | At least 2-3 layouts (quote, list, stats) |
| Logo watermark | Low | Brand logo placed consistently on all images |
| Text wrapping | Low | Long text fits within image boundaries |

### Delivery
| Feature | Complexity | Description |
|---------|------------|-------------|
| Email delivery | Medium | Send generated content to team for review |
| Image attachment | Low | Post image attached to email |
| Caption in email body | Low | Ready-to-copy caption text |
| Daily scheduling | Low | Automated cron trigger |

### Configuration
| Feature | Complexity | Description |
|---------|------------|-------------|
| Brand config file | Low | Central config for colors, fonts, logo path |
| Content pillars config | Low | Define themes and rotation schedule |

## Differentiators (Nice to Have)

### Content Intelligence
| Feature | Complexity | Dependencies |
|---------|------------|--------------|
| Web research before generation | High | BeautifulSoup, Gemini grounding |
| PUM website scraping | Medium | BeautifulSoup, RSS |
| Google Sheets content input | Medium | gspread, Google auth |
| Content brief file support | Low | YAML/JSON file |
| Trending topic awareness | High | Google Trends API |
| Content calendar view | Medium | Google Sheets output |

### Image Quality
| Feature | Complexity | Dependencies |
|---------|------------|--------------|
| Dynamic background patterns | Medium | Pillow drawing |
| Photo backgrounds with overlay | Medium | Stock photo integration |
| Carousel/multi-image posts | High | Multiple Pillow renders |
| Template randomization | Low | Random template selection |

### Delivery Enhancement
| Feature | Complexity | Dependencies |
|---------|------------|--------------|
| HTML email with preview | Medium | email.mime HTML |
| Posting time suggestion | Low | Gemini recommendation |
| Weekly content calendar email | Medium | Batch generation |
| Approval workflow (reply to approve) | High | Email parsing |

## Anti-Features (Do NOT Build)

| Feature | Reason |
|---------|--------|
| Auto-posting to Instagram | Account flagging risk, requires Facebook Business, removes human review |
| User authentication | Single-user tool, no login needed |
| Web dashboard | Over-engineering — email delivery is sufficient |
| Database/persistence | Stateless runs are simpler, Google Sheets covers input data |
| Real-time generation | Daily batch is sufficient, avoids complexity |
| Video/Reels generation | High complexity, out of scope for v1 |
| Multi-platform posting | Focus on Instagram only for v1 |
| Analytics tracking | Manual tracking is fine for 114-follower account |

## Feature Dependencies

```
Brand Config ──→ Image Templates ──→ Email Delivery
                      ↑
Content Pillars ──→ AI Caption Gen ──→ Email Body
                      ↑
Content Research ──┘ (optional enhancement)
    ↑
Web Scraping / Google Sheets / Content Brief
```

**Build order implication:** Brand config and content pillars must be defined first. Image templates and caption generation can be built in parallel. Email delivery ties them together. Content research sources (scraping, sheets) can be layered on after core pipeline works.

---
*Researched: 2026-02-28*
