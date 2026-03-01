# Phase 6: Orchestration & CI/CD - Research

**Researched:** 2026-03-01
**Domain:** Python pipeline orchestration, GitHub Actions CI/CD, cron scheduling, structured logging, error handling
**Confidence:** HIGH

## Summary

Phase 6 wires together all existing modules into a single `main.py` orchestrator and a GitHub Actions workflow that runs it daily. The four pipeline stages are already implemented as clean, independent Python packages: `research_sources.gather_source_material()` aggregates content from 5 sources with graceful degradation, `content_generator.generate_post()` calls Gemini API with structured output, `templates` renders branded 1080x1080 PNG images, and `email_sender.send_post_email()` delivers via Gmail SMTP. The orchestrator simply calls these in sequence, handling errors and logging at each step.

GitHub Actions provides free cron scheduling on public repositories (2,000 min/month). The workflow uses `schedule` with POSIX cron syntax in UTC. Since the target audience is in Indonesia (WIB = UTC+7), the cron must be set 7 hours behind the desired WIB posting time. The workflow also supports `workflow_dispatch` for manual triggering. All secrets (GEMINI_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL, GSHEET_CREDENTIALS, GOOGLE_SHEET_ID) are stored as GitHub Actions repository secrets and injected as environment variables.

No new Python dependencies are needed. The orchestrator uses Python standard library `logging` module configured at the entry point. The GitHub Actions workflow uses `actions/checkout@v4`, `actions/setup-python@v5` with pip caching, and runs `python main.py`. The project already uses Python 3.9 compatibility locally (Pillow 11.3.0, Optional[str] type hints), but GitHub Actions should use Python 3.11 for better performance and error messages as recommended in the project's research summary.

**Primary recommendation:** Create a simple sequential `main.py` that calls the four pipeline stages in order with try/except around each stage, structured logging to stdout (captured by GitHub Actions), and a non-zero exit code on failure. The GitHub Actions workflow triggers daily via cron and supports manual dispatch. No new pip dependencies required.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | GitHub Actions cron triggers pipeline daily | GitHub Actions `schedule` event with POSIX cron syntax runs on UTC time; WIB (UTC+7) conversion needed; `workflow_dispatch` added for manual triggering; scheduled workflows run only on default branch |
| INFRA-03 | Pipeline handles errors gracefully and logs failures | Python standard `logging` module with `basicConfig()` at entry point; try/except around each pipeline stage; non-zero exit code via `sys.exit(1)` on failure; each module already uses `logging.getLogger(__name__)`; secrets never logged |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| [logging](https://docs.python.org/3/library/logging.html) | stdlib | Structured pipeline logging with levels and module names | Python standard library; all existing modules already use `logging.getLogger(__name__)`; `basicConfig()` in main.py configures entire hierarchy |
| [sys](https://docs.python.org/3/library/sys.html) | stdlib | `sys.exit(1)` for non-zero exit code on pipeline failure | GitHub Actions marks step as failed when process exits with non-zero code |
| [os](https://docs.python.org/3/library/os.html) | stdlib | `os.environ.get()` for reading secrets from environment variables | Consistent with project convention used by gemini_client.py, sheets_reader.py, smtp_client.py, composer.py |
| [dotenv](https://pypi.org/project/python-dotenv/) | >=1.0.0 | Load `.env` file for local development (already in requirements.txt) | Already a project dependency; `load_dotenv()` in main.py enables local runs without exporting env vars manually |
| [actions/checkout](https://github.com/actions/checkout) | v4 | Check out repository code in GitHub Actions | Standard first step in any GitHub Actions workflow; v4 is stable and widely used |
| [actions/setup-python](https://github.com/actions/setup-python) | v5 | Install Python with pip dependency caching | Built-in `cache: 'pip'` eliminates need for separate cache action; v5 is current stable |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| [datetime](https://docs.python.org/3/library/datetime.html) | stdlib | Timestamping output file names (e.g., `pum_post_2026-03-01.png`) | Used in image output path and logging |
| [pathlib](https://docs.python.org/3/library/pathlib.html) | stdlib | Cross-platform path handling for output directory | Consistent with project's established pattern from templates/base.py |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib logging | structlog | More features (JSON output, processors) but adds dependency; stdlib logging is sufficient for single-pipeline stdout logging captured by GitHub Actions |
| Sequential main.py | Task runner (invoke, nox) | Over-engineering for 4 sequential steps; adds dependency; main.py is simpler and more transparent |
| GitHub Actions cron | External cron service (cron-job.org, EasyCron) | Adds external dependency; GitHub Actions is already free and integrated with the repository |
| python-dotenv | direnv / manual export | dotenv already in requirements.txt; `load_dotenv()` is a single line; no additional setup for local development |

**Installation:**
```bash
# No new installation required -- all dependencies already in requirements.txt
pip install -r requirements.txt
```

## Architecture Patterns

### Recommended Project Structure
```
pum-content/
    main.py                      # Pipeline orchestrator (entry point)
    .github/
        workflows/
            daily-content.yml    # GitHub Actions cron workflow
    research_sources/            # Stage 1: Content research (existing)
    content_generator/           # Stage 2: AI generation (existing)
    templates/                   # Stage 3: Image rendering (existing)
    email_sender/                # Stage 4: Email delivery (existing)
    output/                      # Generated images (gitignored)
    tests/
        test_main.py             # Orchestrator unit tests
```

### Pattern 1: Sequential Pipeline with Stage Isolation
**What:** Each pipeline stage is wrapped in its own try/except block. Failure in one stage logs the error and either skips downstream stages (if data is unavailable) or continues (if the stage is optional). The orchestrator returns a non-zero exit code if any critical stage fails.
**When to use:** Always -- this is the core orchestration pattern.
**Example:**
```python
# Source: Project architecture (research_sources/__init__.py, content_generator/generator.py, email_sender/composer.py)
import sys
import logging
from datetime import date

logger = logging.getLogger(__name__)

def run_pipeline():
    """Execute the full content pipeline: research -> generate -> render -> email."""

    # Stage 1: Research
    logger.info("Stage 1: Gathering source material...")
    try:
        from research_sources import gather_source_material
        import os
        sheet_id = os.environ.get("GOOGLE_SHEET_ID")
        source_material = gather_source_material(sheet_id=sheet_id)
        logger.info("Source material gathered: %d chars", len(source_material))
    except Exception as e:
        logger.error("Stage 1 FAILED: %s", e)
        return False

    # Stage 2: Generate
    logger.info("Stage 2: Generating content...")
    try:
        from content_generator import generate_post
        post = generate_post(source_material)
        logger.info("Content generated: pillar=%s, template=%s",
                     post.content_pillar, post.template_type)
    except Exception as e:
        logger.error("Stage 2 FAILED: %s", e)
        return False

    # Stage 3: Render image
    logger.info("Stage 3: Rendering image...")
    try:
        # Template selection based on post.template_type
        image_path = render_image(post)
        logger.info("Image rendered: %s", image_path)
    except Exception as e:
        logger.error("Stage 3 FAILED: %s", e)
        return False

    # Stage 4: Send email
    logger.info("Stage 4: Sending email...")
    try:
        from email_sender import send_post_email
        send_post_email(post, image_path)
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error("Stage 4 FAILED: %s", e)
        return False

    return True

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    success = run_pipeline()
    sys.exit(0 if success else 1)
```

### Pattern 2: Template Type Dispatch
**What:** Map `post.template_type` string to the correct template class, instantiate it, call `.render(post.template_data)`, and save the output PNG.
**When to use:** In the render stage of the orchestrator.
**Example:**
```python
# Source: templates/__init__.py, content_generator/schemas.py
from templates import QuoteStoryTemplate, TipsListTemplate, ImpactStatsTemplate

TEMPLATE_MAP = {
    "quote_story": QuoteStoryTemplate,
    "tips_list": TipsListTemplate,
    "impact_stats": ImpactStatsTemplate,
}

def render_image(post):
    """Render post image using the appropriate template.

    Args:
        post: GeneratedPost with template_type and template_data.

    Returns:
        str: Path to saved PNG image.

    Raises:
        ValueError: If template_type is unknown.
    """
    template_class = TEMPLATE_MAP.get(post.template_type)
    if not template_class:
        raise ValueError(f"Unknown template type: {post.template_type}")

    template = template_class()
    img = template.render(post.template_data)

    output_path = f"output/pum_post_{date.today().isoformat()}.png"
    template.save(img, output_path)
    return output_path
```

### Pattern 3: GitHub Actions Workflow with Cron + Manual Dispatch
**What:** A single workflow file that triggers on both `schedule` (cron) and `workflow_dispatch` (manual). All secrets are passed as environment variables.
**When to use:** The `.github/workflows/daily-content.yml` file.
**Example:**
```yaml
# Source: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule
name: Daily Content Pipeline

on:
  schedule:
    # Run at 00:00 UTC = 07:00 WIB daily
    - cron: '0 0 * * *'
  workflow_dispatch:  # Manual trigger from GitHub UI

jobs:
  generate-content:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run content pipeline
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GMAIL_ADDRESS: ${{ secrets.GMAIL_ADDRESS }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
          GSHEET_CREDENTIALS: ${{ secrets.GSHEET_CREDENTIALS }}
          GOOGLE_SHEET_ID: ${{ secrets.GOOGLE_SHEET_ID }}
        run: python main.py
```

### Pattern 4: Logging Configuration at Entry Point
**What:** Call `logging.basicConfig()` once in `main.py` to configure the root logger. All downstream modules use `logging.getLogger(__name__)` which automatically inherits the root configuration.
**When to use:** At the top of `main.py` before any pipeline code runs.
**Example:**
```python
# Source: https://docs.python.org/3/library/logging.html
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# All downstream loggers (research_sources, content_generator,
# email_sender, templates) automatically use this config because
# they call logging.getLogger(__name__) which inherits from root.
```

### Anti-Patterns to Avoid
- **Catching and silencing all exceptions:** Each stage should catch exceptions to log them, but critical failures must propagate to cause a non-zero exit code. Never use bare `except: pass`.
- **Logging secrets:** Never log GEMINI_API_KEY, GMAIL_APP_PASSWORD, or GSHEET_CREDENTIALS. GitHub Actions auto-redacts secrets in logs, but code should still avoid logging them explicitly.
- **Importing everything at module level:** Import pipeline modules inside the stage functions or at the top of `run_pipeline()`. This prevents import-time failures from blocking error reporting.
- **Using print() instead of logging:** The project already uses `logging.getLogger(__name__)` in all modules. The orchestrator must use the same pattern for consistent output.
- **Hardcoding the cron schedule without comments:** Always comment the WIB equivalent next to the UTC cron expression (e.g., `# 00:00 UTC = 07:00 WIB`).
- **Missing workflow_dispatch:** Without `workflow_dispatch`, the only way to manually trigger is pushing a commit or waiting for cron. Always include it.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pipeline logging | Custom file logger with rotation | `logging.basicConfig()` to stdout | GitHub Actions captures stdout automatically; file logging adds complexity with no benefit in CI |
| Secret management | Custom config file parser for secrets | `os.environ.get()` + GitHub Actions secrets | Secrets context in workflow YAML injects as env vars; dotenv handles local development |
| CI/CD scheduling | External cron service or self-hosted runner | GitHub Actions `schedule` event | Built into GitHub; free for public repos; no infrastructure to maintain |
| Retry logic for pipeline stages | Custom retry decorator | Existing retry logic in each module | `generate_post()` already retries on 429; `gather_source_material()` already degrades gracefully; adding another retry layer creates confusion |
| Template dispatch | if/elif chain for template selection | Dictionary mapping `{type_str: TemplateClass}` | Cleaner, extensible, fewer lines, no missed branches |

**Key insight:** The orchestrator should be thin. All complexity is in the existing modules. The orchestrator's job is to call them in order, log progress, and report success/failure. Any logic beyond that belongs in the modules themselves.

## Common Pitfalls

### Pitfall 1: Cron Runs in UTC, Not WIB
**What goes wrong:** Content is generated at the wrong time of day for the Indonesian audience. Schedule says "7 AM" but it runs at 7 AM UTC = 2 PM WIB.
**Why it happens:** GitHub Actions cron expressions always use UTC. Developers forget to convert from local timezone.
**How to avoid:** Convert WIB to UTC by subtracting 7 hours. Document the conversion in a YAML comment. For 7 AM WIB posting, use `cron: '0 0 * * *'` (midnight UTC). WIB does not observe daylight saving time, so the offset is always +7.
**Warning signs:** Emails arriving at unexpected times; team feedback about wrong delivery time.

### Pitfall 2: Scheduled Workflows Disabled After 60 Days of Inactivity
**What goes wrong:** The cron stops running silently after 60 days without any repository activity (commits, issues, PRs).
**Why it happens:** GitHub automatically disables scheduled workflows on public repositories with no activity to conserve resources. A notification email is sent but can be missed.
**How to avoid:** The pipeline generates commits to the output directory (gitignored), but this does not count as activity since it runs in Actions. Periodically push a small commit (even a README update) or open/close an issue to keep the repository active. Alternatively, the workflow itself can create a small "heartbeat" artifact.
**Warning signs:** Emails stop arriving; no workflow runs visible in the Actions tab; GitHub notification email about disabled workflows.

### Pitfall 3: Secrets Not Configured in Repository Settings
**What goes wrong:** Pipeline fails immediately with `ValueError: Missing environment variables` on the first run.
**Why it happens:** Secrets must be manually added in the GitHub repository settings (Settings > Secrets and variables > Actions). They are not automatically created from `.env.example`.
**How to avoid:** Document the exact secret names in the README or workflow comments. List all 6 required secrets: `GEMINI_API_KEY`, `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `RECIPIENT_EMAIL`, `GSHEET_CREDENTIALS`, `GOOGLE_SHEET_ID`.
**Warning signs:** First CI run fails; error messages mention missing environment variables.

### Pitfall 4: Output Directory Not Created
**What goes wrong:** `FileNotFoundError` when saving the rendered image because `output/` directory does not exist in the fresh checkout.
**Why it happens:** The `output/` directory is in `.gitignore` so it is not checked into the repository. A fresh `actions/checkout` does not create it.
**How to avoid:** The `BaseTemplate.save()` method already calls `output_path.parent.mkdir(parents=True, exist_ok=True)`, which creates the directory. Verify this works in CI by checking the save path. Alternatively, add `mkdir -p output` as a workflow step.
**Warning signs:** Pipeline fails at Stage 3 (render) with "No such file or directory" error.

### Pitfall 5: Import Errors Due to Missing sys.path Setup
**What goes wrong:** `ModuleNotFoundError: No module named 'research_sources'` when running `python main.py` from the project root.
**Why it happens:** Python's import system requires the project root to be on `sys.path`. When running `python main.py` from the project root, the current directory is usually on `sys.path` automatically, but edge cases exist.
**How to avoid:** Place `main.py` in the project root (same level as the package directories). Running `python main.py` from the project root should work without `sys.path` manipulation. The test scripts already use `sys.path.insert(0, project_root)` as a project convention, but `main.py` should not need this if run from the correct directory.
**Warning signs:** ImportError in CI but not locally; different working directory in Actions checkout.

### Pitfall 6: GitHub Actions Cron Timing is Approximate
**What goes wrong:** Workflow runs at 00:12 UTC instead of 00:00 UTC, or is delayed by up to 15 minutes during peak hours.
**Why it happens:** GitHub Actions does not guarantee exact cron timing. Workflows are queued and may experience delays, especially at the top of each hour when many workflows are scheduled.
**How to avoid:** This is a known limitation and is acceptable for this use case (daily content generation). The exact time does not matter as long as the email arrives before the team's posting window. Choose an off-peak time (not exactly on the hour) like `cron: '17 0 * * *'` to reduce queueing delays.
**Warning signs:** Inconsistent run times in the Actions tab; occasional 10-15 minute delays.

## Code Examples

Verified patterns from project modules and official documentation:

### Complete main.py Orchestrator
```python
# Source: Project modules (research_sources, content_generator, templates, email_sender)
"""PUM Indonesia Content Generator - Main Pipeline Orchestrator.

Runs the complete content pipeline: research -> generate -> render -> email.
Designed to be called by GitHub Actions cron or manually via python main.py.
"""

import os
import sys
import logging
from datetime import date

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def render_image(post):
    """Render post image using the appropriate template.

    Maps post.template_type to the correct template class, renders the
    image, and saves to output/ directory.

    Args:
        post: GeneratedPost with template_type and template_data.

    Returns:
        str: Path to saved PNG image.

    Raises:
        ValueError: If template_type is unknown.
    """
    from templates import QuoteStoryTemplate, TipsListTemplate, ImpactStatsTemplate

    template_map = {
        "quote_story": QuoteStoryTemplate,
        "tips_list": TipsListTemplate,
        "impact_stats": ImpactStatsTemplate,
    }

    template_class = template_map.get(post.template_type)
    if not template_class:
        raise ValueError(f"Unknown template type: {post.template_type}")

    template = template_class()
    img = template.render(post.template_data)

    output_path = f"output/pum_post_{date.today().isoformat()}.png"
    template.save(img, output_path)
    return output_path


def run_pipeline():
    """Execute the content pipeline: research -> generate -> render -> email.

    Returns:
        bool: True if pipeline completed successfully, False otherwise.
    """
    # Stage 1: Research
    logger.info("=" * 50)
    logger.info("Stage 1: Gathering source material")
    logger.info("=" * 50)
    try:
        from research_sources import gather_source_material
        sheet_id = os.environ.get("GOOGLE_SHEET_ID")
        source_material = gather_source_material(sheet_id=sheet_id)
        logger.info("Source material gathered: %d characters", len(source_material))
    except Exception as e:
        logger.error("Stage 1 FAILED - Research: %s", e)
        return False

    # Stage 2: Generate content
    logger.info("=" * 50)
    logger.info("Stage 2: Generating content with Gemini")
    logger.info("=" * 50)
    try:
        from content_generator import generate_post
        post = generate_post(source_material)
        logger.info(
            "Content generated: pillar=%s, template=%s, hashtags=%d",
            post.content_pillar,
            post.template_type,
            len(post.hashtags),
        )
    except Exception as e:
        logger.error("Stage 2 FAILED - Generation: %s", e)
        return False

    # Stage 3: Render image
    logger.info("=" * 50)
    logger.info("Stage 3: Rendering branded image")
    logger.info("=" * 50)
    try:
        image_path = render_image(post)
        logger.info("Image saved: %s", image_path)
    except Exception as e:
        logger.error("Stage 3 FAILED - Render: %s", e)
        return False

    # Stage 4: Send email
    logger.info("=" * 50)
    logger.info("Stage 4: Sending email")
    logger.info("=" * 50)
    try:
        from email_sender import send_post_email
        send_post_email(post, image_path)
        logger.info("Pipeline complete - email sent successfully")
    except Exception as e:
        logger.error("Stage 4 FAILED - Email: %s", e)
        return False

    return True


def main():
    """Entry point: configure logging, load env, run pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("PUM Indonesia Content Generator - Starting pipeline")
    logger.info("Date: %s", date.today().isoformat())

    # Load .env for local development (no-op if .env doesn't exist)
    load_dotenv()

    success = run_pipeline()

    if success:
        logger.info("Pipeline completed successfully")
    else:
        logger.error("Pipeline failed - check logs above for details")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

### GitHub Actions Workflow File
```yaml
# Source: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
# File: .github/workflows/daily-content.yml
name: Daily Content Pipeline

on:
  schedule:
    # 00:00 UTC = 07:00 WIB (Western Indonesia Time)
    # WIB is UTC+7, no daylight saving time
    - cron: '0 0 * * *'
  workflow_dispatch:  # Allow manual trigger from GitHub UI

jobs:
  generate-content:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run content pipeline
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GMAIL_ADDRESS: ${{ secrets.GMAIL_ADDRESS }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
          GSHEET_CREDENTIALS: ${{ secrets.GSHEET_CREDENTIALS }}
          GOOGLE_SHEET_ID: ${{ secrets.GOOGLE_SHEET_ID }}
        run: python main.py
```

### Testing the Orchestrator (Unit Tests)
```python
# Source: Project test patterns (tests/test_content_generator.py, tests/test_email_sender.py)
"""Tests for main.py orchestrator.

Mocks all external dependencies (API calls, SMTP, file I/O) to verify
pipeline flow, error handling, and logging without network access.
"""
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import date

# Project convention: add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@patch("main.render_image")
@patch("content_generator.generate_post")
@patch("research_sources.gather_source_material")
@patch("email_sender.send_post_email")
def test_pipeline_success(mock_send, mock_gather, mock_generate, mock_render):
    """Full pipeline succeeds when all stages succeed."""
    mock_gather.return_value = "source material text"
    mock_generate.return_value = MagicMock(
        content_pillar="success_stories",
        template_type="quote_story",
        template_data={"headline": "Test", "body": "Test body", "attribution": "Test"},
        hashtags=["pum", "indonesia"],
    )
    mock_render.return_value = "output/test.png"

    from main import run_pipeline
    assert run_pipeline() is True
    mock_send.assert_called_once()


@patch("research_sources.gather_source_material")
def test_pipeline_fails_on_research_error(mock_gather):
    """Pipeline returns False when research stage fails."""
    mock_gather.side_effect = RuntimeError("All sources failed")

    from main import run_pipeline
    assert run_pipeline() is False
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `actions/checkout@v3` | `actions/checkout@v4` | 2023 | v4 uses Node 20; v3 deprecated |
| `actions/setup-python@v4` | `actions/setup-python@v5` | 2024 | v5 uses Node 20; built-in pip caching improved |
| Manual pip cache with `actions/cache` | `cache: 'pip'` in setup-python | 2021 | One-line caching; no separate action needed |
| `logging.basicConfig(filename=...)` for CI | `logging.basicConfig()` to stdout | Current best practice | CI systems capture stdout; file logging adds complexity |
| Separate `on: push` and `on: schedule` workflows | Single workflow with multiple triggers | Always possible | Simpler maintenance; one file to manage |

**Deprecated/outdated:**
- `actions/checkout@v2` and `v3`: Use `v4` (Node 20 runtime). GitHub will eventually remove Node 16 support.
- `actions/setup-python@v3` and `v4`: Use `v5` for Node 20 and improved caching.
- Python `print()` for logging: Use `logging` module for structured, filterable output.

## Open Questions

1. **Optimal posting time for Instagram Indonesia**
   - What we know: The cron is set to 00:00 UTC = 07:00 WIB as a starting point. This means the email arrives by morning so the team can review and post during the day.
   - What's unclear: Whether 7 AM WIB is the ideal time for the team to receive the email. Some teams prefer evening review for next-morning posting.
   - Recommendation: Start with 07:00 WIB. The cron time is easily adjustable by editing one line in the workflow file. No code changes needed.

2. **GitHub Actions minutes usage**
   - What we know: Public repos get 2,000 free minutes/month. The pipeline should take under 2 minutes per run (pip install with cache + API calls + image render + email send). That is approximately 60 minutes/month for daily runs.
   - What's unclear: Whether external API call latency (Gemini, pum.nl scraping) could push runs beyond 5 minutes on bad days.
   - Recommendation: Add a `timeout-minutes: 10` to the job to prevent runaway minutes consumption. Monitor initial runs.

3. **GSHEET_CREDENTIALS and GOOGLE_SHEET_ID optionality**
   - What we know: `gather_source_material()` only calls `read_content_sheet()` if `sheet_id` is not None. If `GOOGLE_SHEET_ID` is not set, Google Sheets source is simply skipped.
   - What's unclear: Whether `GSHEET_CREDENTIALS` being unset causes an import-time error in `sheets_reader.py` or only fails when called.
   - Recommendation: Make both Google Sheets env vars optional in the workflow and orchestrator. The pipeline should work without them (graceful degradation is already built into `gather_source_material()`).

## Sources

### Primary (HIGH confidence)
- [GitHub Actions Workflow Syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions) - `schedule` event, cron syntax, `workflow_dispatch`, secrets context, env mapping
- [GitHub Actions Events That Trigger Workflows](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule) - Schedule event limitations, UTC timezone, 60-day inactivity rule, approximate timing
- [Python logging documentation](https://docs.python.org/3/library/logging.html) - `basicConfig()`, `getLogger(__name__)`, log levels, format strings
- [actions/setup-python](https://github.com/actions/setup-python) - v5, `cache: 'pip'`, `python-version` parameter
- [actions/checkout](https://github.com/actions/checkout) - v4, default branch checkout behavior
- [GitHub Encrypted Secrets](https://docs.github.com/actions/security-guides/encrypted-secrets) - Repository secrets, `${{ secrets.NAME }}` syntax, auto-redaction in logs

### Secondary (MEDIUM confidence)
- [Run Python Scripts with GitHub Actions](https://davidmuraya.com/blog/schedule-python-scripts-github-actions/) - End-to-end Python cron workflow tutorial, confirmed current patterns
- [Python Logging Best Practices (Better Stack)](https://betterstack.com/community/guides/logging/python/python-logging-best-practices/) - Structured logging patterns, stdout for CI environments
- [GitHub Actions Secrets Best Practices (Blacksmith)](https://www.blacksmith.sh/blog/best-practices-for-managing-secrets-in-github-actions) - Secret rotation, naming conventions, access control

### Tertiary (LOW confidence)
- None -- all findings verified with official documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All stdlib + existing dependencies; GitHub Actions well-documented; no version ambiguity
- Architecture: HIGH - Linear pipeline already proven in module design; orchestrator is a thin wrapper; template dispatch is deterministic
- Pitfalls: HIGH - UTC/WIB conversion is well-documented; 60-day inactivity is officially documented; secrets handling is standard GitHub practice

**Research date:** 2026-03-01
**Valid until:** 2026-06-01 (GitHub Actions and Python logging are stable; unlikely to change)
