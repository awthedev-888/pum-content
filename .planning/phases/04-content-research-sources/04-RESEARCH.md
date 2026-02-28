# Phase 4: Content Research Sources - Research

**Researched:** 2026-02-28
**Domain:** Web scraping, RSS parsing, Google Sheets API, YAML file loading, Gemini grounding with Google Search
**Confidence:** HIGH

## Summary

Phase 4 builds the content research pipeline that feeds source material into the Phase 3 AI generator. The `generate_post()` orchestrator already accepts a `source_material: str` parameter and rejects empty input (AIGEN-01 enforcement). This phase creates 5 source modules -- pum.nl web scraper, RSS feed parser, content brief YAML loader, Google Sheets reader, and Gemini web search grounding -- plus an aggregator that merges all sources into a single text block for the generator.

The pum.nl website is a WordPress site (not Drupal) with a permissive robots.txt (no Disallow rules). It has ~20 articles at `/article/{slug}/` with a sitemap at `article-sitemap.xml`. The RSS feed at `/feed/` exists but currently contains zero items, so the scraper must use HTML parsing as the primary source with RSS as a supplementary/fallback channel. Google Sheets integration uses the `gspread` library with service account authentication via `service_account_from_dict()` for GitHub Actions compatibility. Gemini grounding with Google Search is available on the free tier (500 RPD for Gemini 2.5 Flash) using the existing `google-genai` SDK already in the project.

The critical architectural requirement is graceful degradation: if any source fails, the pipeline must continue with remaining sources. This means each source module must be independently callable with its own error handling, and the aggregator must tolerate partial failures.

**Primary recommendation:** Use `requests` + `beautifulsoup4` for pum.nl scraping, `feedparser` for RSS, `gspread` for Google Sheets (service account auth via JSON dict from environment variable), `PyYAML` (already installed) for content briefs, and the existing `google-genai` SDK with `GoogleSearch()` tool for Gemini grounding. Wrap each source in a try/except that returns empty string on failure, and concatenate all non-empty results into the `source_material` string.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RSRCH-01 | System scrapes pum.nl for latest news, stories, and updates | `requests` + `beautifulsoup4` scrapes `/news/` listing page and individual article pages at `/article/{slug}/`; WordPress site with permissive robots.txt; sitemap at `article-sitemap.xml` provides full article URL list |
| RSRCH-02 | System parses PUM blog RSS feed for recent articles | `feedparser` parses RSS 2.0 feed at `pum.nl/feed/`; feed currently empty but module should handle both populated and empty feeds gracefully |
| RSRCH-03 | System reads content brief YAML file for manual story ideas, stats, and events | `PyYAML` (already in requirements.txt as 6.0.3) with `yaml.safe_load()` reads structured content brief file; schema defines story_ideas, stats, events sections |
| RSRCH-04 | System reads content inputs from a shared Google Sheet | `gspread` 6.2.1 with `service_account_from_dict()` authenticates via JSON credentials stored in GitHub Actions secret `GSHEET_CREDENTIALS`; reads rows from a shared spreadsheet |
| RSRCH-05 | System searches the internet via Gemini grounding for recent PUM Indonesia news | `google-genai` SDK (already installed) with `types.Tool(google_search=types.GoogleSearch())` enables Gemini grounding; free tier allows 500 RPD on Gemini 2.5 Flash; returns grounded text with source citations |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| [requests](https://pypi.org/project/requests/) | >=2.32.0 | HTTP client for pum.nl scraping | De facto Python HTTP library; already widely used; simple API |
| [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) | >=4.12.0 | HTML parsing for article content extraction | Standard HTML parser; handles malformed HTML; CSS selector support |
| [feedparser](https://pypi.org/project/feedparser/) | >=6.0.11 | RSS/Atom feed parsing | Universal feed parser; handles RSS 2.0 (pum.nl format); normalizes feed data |
| [gspread](https://pypi.org/project/gspread/) | >=6.2.0 | Google Sheets API v4 client | Most popular Python Sheets library; service account auth built-in; MIT license |
| [PyYAML](https://pypi.org/project/PyYAML/) | ==6.0.3 | YAML content brief file loading | Already in requirements.txt; safe_load() for secure parsing |
| [google-genai](https://pypi.org/project/google-genai/) | >=1.0.0 | Gemini API with Google Search grounding | Already in requirements.txt; GoogleSearch tool for web grounding |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| google-auth | >=1.12.0 | Service account credential handling | Auto-installed as gspread dependency; used by service_account_from_dict() |
| lxml | >=4.9.0 | Fast HTML parser backend for BeautifulSoup | Optional but recommended for speed; use `features="lxml"` if installed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| requests + beautifulsoup4 | scrapy | Over-engineered for scraping 1-2 pages; adds massive dependency tree |
| requests + beautifulsoup4 | httpx + selectolax | Faster but less community support; BeautifulSoup is more forgiving with malformed HTML |
| feedparser | atoma | Smaller footprint but less battle-tested; feedparser handles more edge cases |
| gspread | google-api-python-client | Lower-level; requires manual Sheets API wiring; gspread abstracts boilerplate |
| PyYAML safe_load | pydantic-yaml | Extra dependency for simple file loading; PyYAML is already installed |

**Installation:**
```bash
pip install requests>=2.32.0 beautifulsoup4>=4.12.0 feedparser>=6.0.11 gspread>=6.2.0
```
Note: `google-auth` is auto-installed as a dependency of `gspread`. `PyYAML` and `google-genai` are already in requirements.txt.

## Architecture Patterns

### Recommended Project Structure
```
research_sources/
    __init__.py               # Public API: gather_source_material()
    scraper.py                # pum.nl web scraper (RSRCH-01)
    rss_reader.py             # RSS feed parser (RSRCH-02)
    content_brief.py          # YAML content brief loader (RSRCH-03)
    sheets_reader.py          # Google Sheets reader (RSRCH-04)
    web_search.py             # Gemini grounding with Google Search (RSRCH-05)
content_brief.yaml            # Content brief file (project root)
```

### Pattern 1: Source Module Interface
**What:** Each source module exposes a single function that returns a string (source material text) or empty string on failure.
**When to use:** Every source module follows this pattern for uniform aggregation.
**Example:**
```python
# Each source module has the same signature
def fetch_pum_news() -> str:
    """Scrape latest news from pum.nl. Returns text or empty string on failure."""
    try:
        # ... scraping logic ...
        return extracted_text
    except Exception as e:
        logger.warning("pum.nl scraper failed: %s", e)
        return ""

def parse_rss_feed() -> str:
    """Parse PUM RSS feed. Returns text or empty string on failure."""
    try:
        # ... parsing logic ...
        return feed_text
    except Exception as e:
        logger.warning("RSS parser failed: %s", e)
        return ""
```

### Pattern 2: Graceful Degradation Aggregator
**What:** Aggregator calls all sources, collects non-empty results, concatenates into a single source_material string. If all sources fail, raises an error rather than passing empty string to the generator (which would violate AIGEN-01).
**When to use:** The main entry point for Phase 4, called before `generate_post()`.
**Example:**
```python
import logging

logger = logging.getLogger(__name__)

def gather_source_material(
    content_brief_path: str = "content_brief.yaml",
    sheet_id: str | None = None,
) -> str:
    """Gather content from all research sources.

    Calls each source independently. If any source fails, continues
    with remaining sources. Raises RuntimeError only if ALL sources
    return empty results.

    Returns:
        Concatenated source material text from all successful sources.

    Raises:
        RuntimeError: If no source returned any content.
    """
    sections = []

    # 1. pum.nl scraper
    news = fetch_pum_news()
    if news:
        sections.append(f"## Recent PUM News\n{news}")
        logger.info("pum.nl scraper: collected %d chars", len(news))
    else:
        logger.warning("pum.nl scraper: no content")

    # 2. RSS feed
    rss = parse_rss_feed()
    if rss:
        sections.append(f"## PUM Blog Articles\n{rss}")
        logger.info("RSS parser: collected %d chars", len(rss))
    else:
        logger.warning("RSS parser: no content")

    # 3. Content brief
    brief = load_content_brief(content_brief_path)
    if brief:
        sections.append(f"## Content Brief\n{brief}")
        logger.info("Content brief: collected %d chars", len(brief))
    else:
        logger.warning("Content brief: no content")

    # 4. Google Sheets
    if sheet_id:
        sheets = read_content_sheet(sheet_id)
        if sheets:
            sections.append(f"## Content Inputs (Sheets)\n{sheets}")
            logger.info("Google Sheets: collected %d chars", len(sheets))
        else:
            logger.warning("Google Sheets: no content")

    # 5. Gemini web search
    web = search_pum_indonesia_news()
    if web:
        sections.append(f"## Recent Web Results\n{web}")
        logger.info("Web search: collected %d chars", len(web))
    else:
        logger.warning("Web search: no content")

    if not sections:
        raise RuntimeError(
            "All content research sources failed or returned empty. "
            "Cannot generate content without source material (AIGEN-01)."
        )

    return "\n\n".join(sections)
```

### Pattern 3: WordPress Article Scraping
**What:** Scrape pum.nl news listing and individual articles using requests + BeautifulSoup.
**When to use:** RSRCH-01 implementation.
**Example:**
```python
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

PUM_NEWS_URL = "https://www.pum.nl/news/"
PUM_BASE_URL = "https://www.pum.nl"
REQUEST_TIMEOUT = 15
USER_AGENT = "PUM-Content-Generator/1.0 (+https://github.com/pum-content)"

def fetch_pum_news(max_articles: int = 3) -> str:
    """Scrape latest news articles from pum.nl."""
    headers = {"User-Agent": USER_AGENT}

    # Step 1: Get article links from news listing
    response = requests.get(PUM_NEWS_URL, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    # Find article links -- pattern: /article/{slug}/
    article_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/article/" in href and href not in article_links:
            if not href.startswith("http"):
                href = PUM_BASE_URL + href
            article_links.append(href)

    # Step 2: Scrape each article
    articles = []
    for url in article_links[:max_articles]:
        try:
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            article_soup = BeautifulSoup(resp.text, "html.parser")

            title = article_soup.find("h1")
            title_text = title.get_text(strip=True) if title else "Untitled"

            # Extract article body paragraphs
            paragraphs = article_soup.find_all("p")
            body = "\n".join(
                p.get_text(strip=True) for p in paragraphs
                if len(p.get_text(strip=True)) > 30
            )

            if body:
                articles.append(f"### {title_text}\n{body}")
        except Exception as e:
            logger.warning("Failed to scrape %s: %s", url, e)
            continue

    return "\n\n".join(articles)
```

### Pattern 4: Google Sheets Service Account from Dict
**What:** Authenticate to Google Sheets using credentials stored as a JSON string in an environment variable.
**When to use:** RSRCH-04 implementation, especially for GitHub Actions.
**Example:**
```python
import os
import json
import gspread
import logging

logger = logging.getLogger(__name__)

def read_content_sheet(sheet_id: str) -> str:
    """Read content inputs from a Google Sheet.

    Authenticates via GSHEET_CREDENTIALS environment variable
    (JSON string of service account credentials).
    """
    creds_json = os.environ.get("GSHEET_CREDENTIALS")
    if not creds_json:
        logger.warning("GSHEET_CREDENTIALS not set, skipping Google Sheets")
        return ""

    credentials = json.loads(creds_json)
    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_key(sheet_id)
    worksheet = spreadsheet.sheet1

    # Get all records as list of dicts (first row = headers)
    records = worksheet.get_all_records()

    # Format records as text for the AI generator
    lines = []
    for row in records:
        line_parts = [f"{k}: {v}" for k, v in row.items() if v]
        if line_parts:
            lines.append("; ".join(line_parts))

    return "\n".join(lines)
```

### Pattern 5: Gemini Grounding with Google Search
**What:** Use the existing google-genai SDK to query Gemini with Google Search grounding for recent PUM Indonesia news.
**When to use:** RSRCH-05 implementation.
**Example:**
```python
# Source: https://ai.google.dev/gemini-api/docs/google-search
from google import genai
from google.genai import types, errors
import os
import logging

logger = logging.getLogger(__name__)

def search_pum_indonesia_news() -> str:
    """Search for recent PUM Indonesia news using Gemini grounding."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set, skipping web search")
        return ""

    client = genai.Client(api_key=api_key)
    google_search_tool = types.Tool(google_search=types.GoogleSearch())

    query = (
        "Find recent news and updates about PUM Netherlands Senior Experts "
        "activities in Indonesia in 2025-2026. Include any SME support programs, "
        "expert visits, events, or partnerships involving PUM Indonesia."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            ),
        )
        return response.text
    except errors.APIError as e:
        if e.code == 429:
            logger.warning("Gemini rate limit hit during web search: %s", e.message)
        else:
            logger.warning("Gemini API error during web search (%d): %s", e.code, e.message)
        return ""
    except Exception as e:
        logger.warning("Web search failed: %s", e)
        return ""
```

### Anti-Patterns to Avoid
- **Letting one source failure crash the entire pipeline:** Each source MUST catch its own exceptions and return empty string on failure. Never let a scraping error prevent the content brief from being read.
- **Scraping without User-Agent header:** pum.nl uses WordPress/Yoast. Always send a descriptive User-Agent string. Omitting it may get blocked.
- **Using yaml.load() instead of yaml.safe_load():** `yaml.load()` allows arbitrary code execution. Always use `yaml.safe_load()` for content brief files.
- **Storing Google Sheets credentials as a file in the repo:** Service account JSON must never be committed. Use `GSHEET_CREDENTIALS` environment variable with `service_account_from_dict()`.
- **Making Gemini grounding call without error handling:** Grounding uses API quota (500 RPD free tier, shared with Flash-Lite). Must handle rate limits and not crash if quota exhausted.
- **Scraping too aggressively:** Add a 1-2 second delay between article fetches. Only scrape 2-3 articles per run. pum.nl is a small nonprofit site.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RSS parsing | Custom XML parser with ElementTree | `feedparser` | Handles RSS 0.9x/1.0/2.0, Atom, CDF; normalizes dates; handles encoding edge cases |
| HTML parsing | Regex-based content extraction | `beautifulsoup4` | Handles malformed HTML; CSS selectors; text extraction methods |
| Google Sheets auth | Custom OAuth2 flow with google-auth | `gspread.service_account_from_dict()` | Handles token refresh, scoping, credential validation |
| Feed date normalization | Custom date parsing for RSS dates | `feedparser.entries[i].published_parsed` | RFC 822, ISO 8601, and many other date formats handled automatically |
| HTTP session management | Custom retry/timeout logic for requests | `requests.Session()` with timeout parameter | Connection pooling, cookie persistence, consistent headers |

**Key insight:** Every source type (web, RSS, sheets, YAML, API) has a mature Python library. The real engineering challenge is not parsing -- it is the graceful degradation pattern and aggregation logic that ensures the pipeline never runs without source material.

## Common Pitfalls

### Pitfall 1: pum.nl RSS Feed Is Currently Empty
**What goes wrong:** RSS parser returns zero articles, developer assumes the module is broken.
**Why it happens:** The PUM WordPress RSS feed at `pum.nl/feed/` currently contains channel metadata but zero `<item>` elements. This may change when PUM starts publishing blog posts.
**How to avoid:** RSS module must handle empty feeds gracefully (return empty string, not raise). Log a warning, not an error. Include fallback to the HTML scraper. Test with both empty and populated feeds.
**Warning signs:** `feedparser.parse().entries` returns empty list.

### Pitfall 2: WordPress Theme Changes Breaking Scraper
**What goes wrong:** CSS selectors or HTML structure changes after a WordPress theme update, breaking article extraction.
**Why it happens:** pum.nl uses a custom WordPress theme (`wp-content/themes/pum/`). Theme updates can change HTML structure.
**How to avoid:** Use robust selectors (semantic tags like `<h1>`, `<p>` rather than specific CSS classes). Extract all paragraphs with `len > 30` chars rather than targeting specific divs. Add a smoke test that verifies scraping still works.
**Warning signs:** Scraper returns empty content but the website visually has articles.

### Pitfall 3: Google Sheets Credentials Format
**What goes wrong:** `json.loads()` fails on the credentials string, or `service_account_from_dict()` raises authentication error.
**Why it happens:** GitHub Actions secrets may have escaped characters, or the service account JSON may be base64-encoded instead of raw JSON.
**How to avoid:** Document the exact format expected: raw JSON string in `GSHEET_CREDENTIALS` env var. Validate JSON parsing before passing to gspread. Include clear error messages.
**Warning signs:** `json.JSONDecodeError` or `google.auth.exceptions.MalformedError`.

### Pitfall 4: Gemini Grounding Quota Exhaustion
**What goes wrong:** Web search grounding call fails with 429 after other pipeline components have already used API quota.
**Why it happens:** Gemini 2.5 Flash free tier shares 500 RPD between all API calls, including both content generation (Phase 3) and grounding (Phase 4). If testing makes many calls, quota depletes.
**How to avoid:** Call grounding BEFORE content generation in the pipeline (gather sources first, then generate). This ensures the most critical API call (content generation) still has quota. Log quota usage warnings.
**Warning signs:** `errors.APIError` with code 429 specifically on grounding calls.

### Pitfall 5: Content Brief File Not Found
**What goes wrong:** `FileNotFoundError` when content_brief.yaml doesn't exist yet or path is wrong.
**Why it happens:** Content brief is a manually-maintained file. It may not exist on first pipeline run. Path may differ between local development and GitHub Actions.
**How to avoid:** Check `os.path.exists()` before loading. Return empty string if file doesn't exist (not an error -- the brief is an optional input). Use relative path from project root.
**Warning signs:** `FileNotFoundError` in logs.

### Pitfall 6: Scraping Timeout on Slow Network
**What goes wrong:** `requests.get()` hangs indefinitely waiting for pum.nl to respond.
**Why it happens:** No timeout specified, or network is slow in GitHub Actions runner.
**How to avoid:** Always pass `timeout=15` (seconds) to `requests.get()`. Use `requests.Session()` for connection reuse. Handle `requests.Timeout` exception.
**Warning signs:** Pipeline takes > 60 seconds in the scraping step.

## Code Examples

Verified patterns from official sources:

### feedparser RSS Parsing
```python
# Source: https://github.com/kurtmckee/feedparser
import feedparser

def parse_rss_feed(feed_url: str = "https://www.pum.nl/feed/") -> str:
    """Parse PUM RSS feed for recent articles."""
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        return ""

    articles = []
    for entry in feed.entries[:5]:
        title = entry.get("title", "Untitled")
        summary = entry.get("summary", "")
        link = entry.get("link", "")
        published = entry.get("published", "")

        article_text = f"### {title}"
        if published:
            article_text += f" ({published})"
        article_text += f"\n{summary}"
        if link:
            article_text += f"\nSource: {link}"
        articles.append(article_text)

    return "\n\n".join(articles)
```

### YAML Content Brief Loading
```python
# Source: PyYAML documentation
import yaml
import os
import logging

logger = logging.getLogger(__name__)

def load_content_brief(filepath: str = "content_brief.yaml") -> str:
    """Load content brief from YAML file.

    Expected structure:
        story_ideas:
          - title: "..."
            description: "..."
        stats:
          - number: "200+"
            context: "SMEs supported in Indonesia"
        events:
          - name: "PUM Indonesia Summit"
            date: "2026-04-15"
            details: "Regional SME summit in Jakarta"
    """
    if not os.path.exists(filepath):
        logger.info("Content brief not found at %s, skipping", filepath)
        return ""

    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        return ""

    sections = []

    # Story ideas
    stories = data.get("story_ideas", [])
    if stories:
        lines = []
        for s in stories:
            title = s.get("title", "")
            desc = s.get("description", "")
            lines.append(f"- {title}: {desc}")
        sections.append("Story Ideas:\n" + "\n".join(lines))

    # Stats
    stats = data.get("stats", [])
    if stats:
        lines = []
        for s in stats:
            num = s.get("number", "")
            ctx = s.get("context", "")
            lines.append(f"- {num} {ctx}")
        sections.append("Key Statistics:\n" + "\n".join(lines))

    # Events
    events = data.get("events", [])
    if events:
        lines = []
        for e in events:
            name = e.get("name", "")
            date = e.get("date", "")
            details = e.get("details", "")
            lines.append(f"- {name} ({date}): {details}")
        sections.append("Upcoming Events:\n" + "\n".join(lines))

    return "\n\n".join(sections)
```

### gspread with Service Account from Dict
```python
# Source: https://docs.gspread.org/en/latest/oauth2.html
import gspread
import json
import os

# For GitHub Actions: store full JSON as secret GSHEET_CREDENTIALS
credentials_json = os.environ.get("GSHEET_CREDENTIALS")
if credentials_json:
    credentials_dict = json.loads(credentials_json)
    gc = gspread.service_account_from_dict(credentials_dict)

    # Open by spreadsheet ID (from the URL)
    spreadsheet = gc.open_by_key("your-spreadsheet-id-here")
    worksheet = spreadsheet.sheet1

    # Get all data as list of dicts (first row = headers)
    records = worksheet.get_all_records()

    # Get all values as list of lists
    all_values = worksheet.get_all_values()
```

### Gemini Grounding with Google Search
```python
# Source: https://ai.google.dev/gemini-api/docs/google-search
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

google_search_tool = types.Tool(
    google_search=types.GoogleSearch()
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Recent PUM Indonesia activities and news 2025-2026",
    config=types.GenerateContentConfig(
        tools=[google_search_tool],
        response_modalities=["TEXT"],
    ),
)

# Text response with grounded information
print(response.text)

# Access grounding metadata (source URLs)
grounding = response.candidates[0].grounding_metadata
if grounding and grounding.grounding_chunks:
    for chunk in grounding.grounding_chunks:
        print(f"Source: {chunk.web.uri}")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `urllib2` + manual HTML parsing | `requests` + `beautifulsoup4` | 2012+ | Standard for Python web scraping; cleaner API |
| `oauth2client` for Google auth | `google-auth` via gspread | 2019 (deprecated) | gspread 6.x uses google-auth internally |
| Custom Google Search API calls | Gemini grounding with `GoogleSearch()` | 2024-2025 | No separate Search API key needed; integrated with Gemini |
| `google-generativeai` SDK | `google-genai` SDK | Nov 2025 (EOL) | New SDK required for grounding tools |
| Manual JSON parsing of API responses | Structured output with Pydantic | 2024-2025 | Not applicable to grounding (returns text, not structured) |

**Deprecated/outdated:**
- `oauth2client`: Deprecated since 2019. gspread 6.x uses `google-auth` internally.
- `google-generativeai`: EOL November 2025. Grounding tools are only in the new `google-genai` SDK.
- Custom Google Search API for content research: Gemini grounding replaces the need for a separate Google Custom Search Engine API key and configuration.

## pum.nl Website Analysis

Key findings from direct investigation of pum.nl:

| Property | Value |
|----------|-------|
| CMS | WordPress (custom theme at `wp-content/themes/pum/`) |
| robots.txt | Permissive -- no Disallow rules; all content scrapable |
| Sitemap | `https://www.pum.nl/sitemap_index.xml` with `article-sitemap.xml` |
| Total articles | ~20 articles in sitemap |
| Article URL pattern | `/article/{slug}/` |
| News listing URL | `/news/` with pagination (7 pages) |
| RSS feed URL | `/feed/` (RSS 2.0 format) |
| RSS feed status | Channel metadata present, but **zero items** currently |
| Article HTML structure | `<h1>` for title, `<p>` for body paragraphs, Schema.org markup |
| Fonts | Noto Sans loaded from theme directory |
| Update frequency | ~1-2 articles per month based on sitemap dates |

## Open Questions

1. **Google Sheets spreadsheet structure**
   - What we know: RSRCH-04 requires reading content inputs from a shared Google Sheet. gspread can read any worksheet.
   - What's unclear: The exact column structure of the content input spreadsheet (headers, data format, which columns contain what).
   - Recommendation: Design the sheets reader to use `get_all_records()` which returns column headers as dict keys. Format each row as "key: value" pairs. This works regardless of column structure. Document expected columns in a README but don't enforce them.

2. **Content brief YAML schema**
   - What we know: RSRCH-03 needs a YAML file with story ideas, stats, and events.
   - What's unclear: Whether the team has existing content briefs or if this is a new format.
   - Recommendation: Define a simple schema (story_ideas, stats, events sections) and create a sample `content_brief.yaml` with example data. The loader should handle missing sections gracefully.

3. **RSS feed population timeline**
   - What we know: pum.nl/feed/ exists as RSS 2.0 but contains zero items currently.
   - What's unclear: Whether PUM plans to publish blog posts via RSS, or if it will remain empty.
   - Recommendation: Build the RSS module anyway. It costs almost nothing (feedparser is lightweight) and will automatically start working if/when PUM populates the feed. Use the HTML scraper as the primary news source.

4. **Google Sheets service account setup**
   - What we know: Need a Google Cloud service account with Sheets API enabled.
   - What's unclear: Whether the user already has a Google Cloud project and service account.
   - Recommendation: Document the setup steps (create project, enable Sheets API, create service account, share spreadsheet with service account email, store credentials as GitHub secret). Handle missing credentials gracefully (skip, don't crash).

## Sources

### Primary (HIGH confidence)
- [pum.nl/robots.txt](https://pum.nl/robots.txt) - Permissive robots.txt, no Disallow rules
- [pum.nl/news/](https://pum.nl/news/) - News listing structure, article URLs, pagination
- [pum.nl/article/queen-maxima-attends-pum-impact-awards/](https://pum.nl/article/queen-maxima-attends-pum-impact-awards/) - Article HTML structure, WordPress CMS identification
- [pum.nl/sitemap_index.xml](https://www.pum.nl/sitemap_index.xml) - Sitemap structure, article-sitemap.xml
- [pum.nl/feed/](https://www.pum.nl/feed/) - RSS 2.0 feed, currently empty
- [Gemini API Google Search Grounding](https://ai.google.dev/gemini-api/docs/google-search) - GoogleSearch tool, grounding API, pricing
- [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing) - Free tier: 500 RPD for Gemini 2.5 Flash grounding
- [gspread Authentication Docs](https://docs.gspread.org/en/latest/oauth2.html) - service_account_from_dict(), service account setup
- [feedparser PyPI](https://pypi.org/project/feedparser/) - Version 6.0.12, Python >=3.6
- [gspread PyPI](https://pypi.org/project/gspread/) - Version 6.2.1, Python >=3.8
- [beautifulsoup4 PyPI](https://pypi.org/project/beautifulsoup4/) - Version 4.14.3, Python >=3.7
- [Gemini Grounded Responses Example](https://geminibyexample.com/024-grounded-responses/) - Complete grounding code pattern

### Secondary (MEDIUM confidence)
- [ScrapeOps feedparser guide](https://scrapeops.io/python-web-scraping-playbook/feedparser/) - feedparser usage patterns and best practices
- [gspread GitHub auth.py](https://github.com/burnash/gspread/blob/master/gspread/auth.py) - service_account_from_dict() implementation details
- [Google Developers Blog on Grounding](https://developers.googleblog.com/en/gemini-api-and-ai-studio-now-offer-grounding-with-google-search/) - Grounding feature announcement and capabilities

### Tertiary (LOW confidence)
- RSS feed empty status: Observed on 2026-02-28; may change at any time. Module should handle both states.
- Gemini grounding pricing details: Free tier is 500 RPD for 2.5 Flash, but Google has changed pricing tiers multiple times. Verify in AI Studio dashboard for current limits.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via PyPI, official docs, and established Python ecosystem patterns
- Architecture: HIGH - Graceful degradation pattern is well-established; source module interface is simple and testable
- Pitfalls: HIGH - Verified through direct website investigation (empty RSS feed, WordPress CMS, robots.txt); pricing verified through official docs
- pum.nl structure: HIGH - Directly fetched and analyzed robots.txt, sitemap, news listing, and article pages

**Research date:** 2026-02-28
**Valid until:** 2026-03-28 (stable domain; pum.nl structure unlikely to change frequently)
