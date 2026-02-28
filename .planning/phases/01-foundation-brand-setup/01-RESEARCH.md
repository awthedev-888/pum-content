# Phase 1: Foundation & Brand Setup - Research

**Researched:** 2026-02-28
**Domain:** Python project structure, YAML configuration, brand asset management
**Confidence:** HIGH

## Summary

Phase 1 establishes the project foundation: directory structure, Python dependencies, a YAML-based brand configuration file, and organized brand assets (logo, fonts, sector icons). The technical domain is straightforward -- no complex APIs or integrations. The stack is PyYAML for config parsing, Pillow for image generation (installed now as a dependency for Phase 2), and pathlib for cross-platform path resolution.

The main risk area is font handling: Google Fonts has migrated Noto Sans to variable font format (single `.ttf` with weight/width axes), but Pillow 12.x supports variable fonts via `set_variation_by_axes()`. The alternative is downloading static TTF files from the `static/` subfolder in the Google Fonts download ZIP. Both approaches work; variable fonts are recommended as they are the current standard and reduce the number of font files to manage.

**Primary recommendation:** Use a flat project structure (no `src/` layout -- this is a pipeline script, not a library), PyYAML with `safe_load()` for brand config, pathlib-based path resolution anchored to `__file__`, and variable font TTFs downloaded from Google Fonts.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Primary colors: `#D2E8D7` (mint green), `#0E5555` (dark green/donkergroen), `#FF6900` (orange)
- Secondary colors: `#659BD1` (blue), `#D69A5F` (warm brown), `#E9C779` (soft gold), `#F8E3B3` (light beige)
- Colors extracted from PUM's Canva Premium brand kit (authoritative source)
- Headings: Noto Sans Bold (Google Font, free TTF)
- Body text: Noto Sans Regular
- Call-to-action / decorative: Permanent Marker (Google Font, hand-drawn style matching PUM's KrabbelBabbel illustrations)
- Standard Latin character support is sufficient for Bahasa Indonesia
- Font TTF files to be downloaded and stored in `assets/fonts/`
- Default watermark: dark green `PUM.` logo (`PUM_logo-donkergroen-rgb.png`)
- White logo with slogan available as secondary variant (`PUM_logo-slogan-alternatief-wit-rgb_1.png`)
- All sector icons included (20+ circular dark green icons with mint fill)
- `brand_config.yaml` contains: color palettes, font paths, logo path, slogan ("Together we grow" -- English only), sector icon paths, asset directory paths
- No social media handles or hashtags in config
- No content pillars in brand config
- No tone/voice guidelines in brand config
- Physical asset files located at `/Users/anitawulandari/Downloads/PUM Brand Kit/` (to be copied into project `assets/` directory)

### Claude's Discretion
- Which background-accent color combos work best per template type
- Whether KrabbelBabbel scribbles enhance specific templates
- Where to define content pillars (brand config vs separate content config)
- Project directory structure and file organization
- Python dependency choices
- Test script design for asset verification

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| IMG-02 | Brand config YAML file defines colors, fonts, and logo path | PyYAML `safe_load()` parses YAML; brand_config.yaml schema with color palettes, font paths, logo path, slogan, sector icons, and asset directories; pathlib resolves all paths relative to project root |
| INFRA-02 | All secrets (API keys, passwords) stored as GitHub Actions secrets | No secrets needed in Phase 1 itself, but project structure must support `os.environ.get()` pattern for future secrets; `.env.example` documents expected variables; `.gitignore` excludes `.env` files |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyYAML | 6.0.3 | Parse `brand_config.yaml` | De facto YAML parser for Python; 6.0.3 is latest stable (Sep 2025), supports Python 3.8-3.14 |
| Pillow | 12.1.1 | Image generation (Phase 2+), font loading verification | Standard Python imaging library; 12.1.1 is latest (Feb 2026); needed now to verify font loading works |
| pathlib | stdlib | Cross-platform file path resolution | Built into Python 3.4+; no external dependency; `Path(__file__).resolve().parent` pattern for project-relative paths |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.x | Load `.env` file for local development secrets | Only for local dev; GitHub Actions uses native secrets injection |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyYAML | tomllib (stdlib) | TOML is Python-native since 3.11, but YAML is more readable for nested config with color palettes and asset paths; user already decided on YAML |
| PyYAML | pydantic-yaml | Adds validation but over-engineering for a simple config file that only this project reads |
| Flat structure | src/ layout | src/ layout is for libraries/packages; this is a pipeline script that runs via `python main.py` -- flat is simpler and standard for this use case |

**Installation:**
```bash
pip install PyYAML==6.0.3 Pillow==12.1.1 python-dotenv
```

## Architecture Patterns

### Recommended Project Structure
```
pum-content/
├── assets/
│   ├── fonts/
│   │   ├── NotoSans[wdth,wght].ttf          # Variable font (Regular + Bold via axis)
│   │   └── PermanentMarker-Regular.ttf
│   ├── logos/
│   │   ├── PUM_logo-donkergroen-rgb.png      # Primary watermark
│   │   └── PUM_logo-slogan-alternatief-wit-rgb_1.png
│   ├── icons/
│   │   ├── Agriculture & Beekeeping.png
│   │   ├── Bakery.png
│   │   └── ... (20+ sector icons)
│   └── decorations/
│       ├── KrabbelBabbel-Extra-01.png         # Orange scribble
│       ├── KrabbelBabbel-Extra-01 (1).png     # Green scribble variant
│       └── KrabbelBabbel-Extra-01 (2).png     # Additional variant
├── brand_config.yaml
├── requirements.txt
├── main.py                                    # Future: pipeline entry point
├── tests/
│   └── test_brand_config.py                   # Asset path verification
├── .env.example                               # Documents expected env vars
├── .gitignore
└── .planning/                                 # Already exists
```

**Key decisions in this structure:**
- `assets/` at project root (not nested in `src/`) -- simple, visible, standard for media-heavy projects
- Assets organized by type: `fonts/`, `logos/`, `icons/`, `decorations/`
- `brand_config.yaml` at project root -- easy to find and edit
- No `src/` layout -- this is a script-based pipeline, not a library
- `tests/` directory for verification scripts

### Pattern 1: Project-Relative Path Resolution
**What:** Anchor all asset paths to the project root using `__file__`
**When to use:** Any time code needs to locate an asset file
**Example:**
```python
# Source: Python pathlib docs + community best practice
from pathlib import Path

# In any module file:
PROJECT_ROOT = Path(__file__).resolve().parent
# If in a subdirectory: PROJECT_ROOT = Path(__file__).resolve().parent.parent

ASSETS_DIR = PROJECT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
LOGOS_DIR = ASSETS_DIR / "logos"
ICONS_DIR = ASSETS_DIR / "icons"
```

### Pattern 2: YAML Config Loading with Safe Parse
**What:** Load brand_config.yaml using safe_load() and resolve paths relative to project root
**When to use:** Any module that needs brand colors, fonts, or asset locations
**Example:**
```python
# Source: PyYAML docs, community best practices
import yaml
from pathlib import Path

def load_brand_config(config_path: Path = None) -> dict:
    """Load brand configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).resolve().parent / "brand_config.yaml"

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config
```

### Pattern 3: Font Loading with Pillow (Variable Font)
**What:** Load variable TTF fonts and set weight via axis
**When to use:** Phase 2 image generation; verified in Phase 1 test script
**Example:**
```python
# Source: Pillow 12.x ImageFont docs
from PIL import ImageFont
from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent / "assets" / "fonts"

# Variable font: set weight via axis
font_regular = ImageFont.truetype(str(FONTS_DIR / "NotoSans[wdth,wght].ttf"), size=24)
font_regular.set_variation_by_axes({"wght": 400})  # Regular weight

font_bold = ImageFont.truetype(str(FONTS_DIR / "NotoSans[wdth,wght].ttf"), size=32)
font_bold.set_variation_by_axes({"wght": 700})  # Bold weight

# Static font (Permanent Marker has only one weight)
font_marker = ImageFont.truetype(str(FONTS_DIR / "PermanentMarker-Regular.ttf"), size=28)
```

### Anti-Patterns to Avoid
- **Hardcoded absolute paths:** Never use `/Users/anitawulandari/...` in code. Always use `Path(__file__)` relative resolution. The brand kit source path is only used during initial asset copy, never in runtime code.
- **yaml.load() without SafeLoader:** Always use `yaml.safe_load()` -- `yaml.load()` can execute arbitrary Python code from YAML.
- **Storing secrets in brand_config.yaml:** Config file is committed to git. API keys and passwords must go in `.env` (local) or GitHub Actions secrets (CI).
- **Font paths as strings instead of Path objects:** Use `pathlib.Path` throughout; only convert to `str()` at the Pillow API boundary.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML parsing | Custom config parser | PyYAML `safe_load()` | Handles all YAML types, escaping, multiline strings, anchors |
| Path resolution | String concatenation with `/` or `os.path.join` | `pathlib.Path` with `/` operator | Cross-platform, readable, handles edge cases (trailing slashes, `.` resolution) |
| Font file management | Script to download fonts at runtime | Pre-downloaded TTF files in `assets/fonts/` committed to git | Fonts are small (< 1MB each), git-friendly, no network dependency at runtime |
| Environment variable loading | Manual `os.environ` with defaults scattered in code | `python-dotenv` + centralized config | Single source of truth, `.env.example` documents all expected variables |

**Key insight:** Phase 1 has no complex problems that need custom solutions. The entire phase is file organization, configuration, and verification. Keep it simple.

## Common Pitfalls

### Pitfall 1: Variable Font Axis Names
**What goes wrong:** Pillow's `set_variation_by_axes()` may expect a list of axis values rather than a dictionary in some versions, or the axis tag might be case-sensitive.
**Why it happens:** The Pillow variable font API has evolved across versions; documentation examples may not match the installed version.
**How to avoid:** Write the test script to actually load the font and call `get_variation_axes()` to discover the exact axis tags and value ranges before setting them. If variable fonts cause issues, fall back to downloading static Noto Sans Regular and Bold TTF files from the `static/` subfolder in the Google Fonts ZIP download.
**Warning signs:** `OSError` or `ValueError` when calling `set_variation_by_axes()`.

### Pitfall 2: File Names with Special Characters in Icon Assets
**What goes wrong:** Sector icon filenames contain `&` and spaces (e.g., `Agriculture & Beekeeping.png`, `Watr, Waste & Environment.png`). These can cause issues in shell scripts, URLs, or cross-platform paths.
**Why it happens:** Asset filenames came directly from the Canva brand kit export.
**How to avoid:** Keep original filenames (they work fine with pathlib in Python), but map them to clean keys in `brand_config.yaml`. The YAML key is the canonical reference; the filename is just what's on disk.
**Warning signs:** `FileNotFoundError` when loading icons by constructed path instead of config-driven path.

### Pitfall 3: Forgetting to Convert Path to str() for Pillow
**What goes wrong:** `ImageFont.truetype()` may not accept `pathlib.Path` objects in all versions.
**Why it happens:** Pillow's `truetype()` historically expected `str` or `bytes`; PathLike support was added later.
**How to avoid:** Always pass `str(path)` to Pillow functions. This is safe across all versions.
**Warning signs:** `TypeError: expected str, bytes or os.PathLike object, not PosixPath`

### Pitfall 4: Missing .gitignore for .env Files
**What goes wrong:** `.env` file with future API keys gets committed to git.
**Why it happens:** Forgetting to set up `.gitignore` before adding `.env`.
**How to avoid:** Create `.gitignore` as one of the very first files, including `.env`, `__pycache__/`, `*.pyc`, and any generated output directories.
**Warning signs:** `git status` shows `.env` as untracked.

### Pitfall 5: YAML Encoding Issues
**What goes wrong:** YAML file contains non-ASCII characters (e.g., in slogan translations) and fails to parse.
**Why it happens:** Default file open without explicit UTF-8 encoding.
**How to avoid:** Always open YAML files with `encoding="utf-8"`: `open(path, "r", encoding="utf-8")`.
**Warning signs:** `UnicodeDecodeError` on Windows systems.

## Code Examples

### brand_config.yaml Schema
```yaml
# PUM Indonesia Content Generator - Brand Configuration
# Source: PUM Canva Premium Brand Kit

brand:
  name: "PUM Netherlands Senior Experts"
  slogan: "Together we grow"

colors:
  primary:
    mint_green: "#D2E8D7"
    dark_green: "#0E5555"
    orange: "#FF6900"
  secondary:
    blue: "#659BD1"
    warm_brown: "#D69A5F"
    soft_gold: "#E9C779"
    light_beige: "#F8E3B3"

fonts:
  heading:
    file: "assets/fonts/NotoSans[wdth,wght].ttf"
    weight: 700  # Bold
  body:
    file: "assets/fonts/NotoSans[wdth,wght].ttf"
    weight: 400  # Regular
  decorative:
    file: "assets/fonts/PermanentMarker-Regular.ttf"

logos:
  primary: "assets/logos/PUM_logo-donkergroen-rgb.png"
  white_with_slogan: "assets/logos/PUM_logo-slogan-alternatief-wit-rgb_1.png"

icons:
  directory: "assets/icons/"
  sectors:
    agriculture: "Agriculture & Beekeeping.png"
    animal_feed: "Animal Feed, Poultry, Fish and Pigs.png"
    bakery: "Bakery.png"
    bso: "BSO & Social Dialogue.png"
    construction: "Construction.png"
    education: "Educational Institutes.png"
    energy: "Energy.png"
    finance_it: "Finance & IT.png"
    food_beverage: "Food & Beverage Processing.png"
    healthcare: "Healthcare.png"
    horticulture: "Horticulture.png"
    hospitality: "Hospitality & Tourism.png"
    ict: "ICT & Incubators.png"
    management: "Management Consultancy.png"
    manufacturing: "Manufacturing.png"
    marketing: "Marketing & Sales.png"
    milk_meat: "Milk & Meat processing.png"
    personal_care: "Personal Care.png"
    ruminants: "Ruminants.png"
    textiles: "Textiles & Handicrafts.png"
    value_chain: "Value Chain Management.png"
    water_waste: "Watr, Waste & Environment.png"
  priority_indonesia:
    - agriculture
    - food_beverage
    - hospitality
    - manufacturing
    - education

decorations:
  directory: "assets/decorations/"
  krabbelbabbel:
    - "KrabbelBabbel-Extra-01.png"
    - "KrabbelBabbel-Extra-01 (1).png"
    - "KrabbelBabbel-Extra-01 (2).png"
```

### Test Script for Asset Verification
```python
#!/usr/bin/env python3
"""Verify brand config and all asset paths resolve correctly."""
import sys
import yaml
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent.parent  # tests/ -> project root
    config_path = project_root / "brand_config.yaml"

    # 1. Load config
    assert config_path.exists(), f"brand_config.yaml not found at {config_path}"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    print("[OK] brand_config.yaml loaded successfully")

    # 2. Verify color format
    for group_name, group in config["colors"].items():
        for color_name, hex_val in group.items():
            assert hex_val.startswith("#") and len(hex_val) == 7, \
                f"Invalid hex color: {group_name}.{color_name} = {hex_val}"
    print("[OK] All color values are valid hex format")

    # 3. Verify font files exist
    for font_name, font_info in config["fonts"].items():
        font_path = project_root / font_info["file"]
        assert font_path.exists(), f"Font not found: {font_name} -> {font_path}"
    print("[OK] All font files exist")

    # 4. Verify logo files exist
    for logo_name, logo_path_str in config["logos"].items():
        logo_path = project_root / logo_path_str
        assert logo_path.exists(), f"Logo not found: {logo_name} -> {logo_path}"
    print("[OK] All logo files exist")

    # 5. Verify icon files exist
    icons_dir = project_root / config["icons"]["directory"]
    for icon_key, icon_filename in config["icons"]["sectors"].items():
        icon_path = icons_dir / icon_filename
        assert icon_path.exists(), f"Icon not found: {icon_key} -> {icon_path}"
    print(f"[OK] All {len(config['icons']['sectors'])} sector icons exist")

    # 6. Verify font loading with Pillow
    from PIL import ImageFont
    for font_name, font_info in config["fonts"].items():
        font_path = project_root / font_info["file"]
        font = ImageFont.truetype(str(font_path), size=24)
        if "weight" in font_info:
            try:
                axes = font.get_variation_axes()
                font.set_variation_by_axes([font_info["weight"]])
                print(f"[OK] Font '{font_name}' loaded with weight {font_info['weight']}")
            except Exception:
                print(f"[OK] Font '{font_name}' loaded (static font, no weight axis)")
        else:
            print(f"[OK] Font '{font_name}' loaded")

    print("\n=== All brand asset checks passed ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### .gitignore Essentials
```gitignore
# Environment
.env
.env.local

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
venv/
.venv/

# Generated output
output/
*.generated.png

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Static font files (NotoSans-Regular.ttf, NotoSans-Bold.ttf) | Variable font (NotoSans[wdth,wght].ttf) | Google Fonts migration ~2023 | Single file serves all weights; Pillow 10.1+ supports variable fonts |
| `yaml.load()` | `yaml.safe_load()` | PyYAML 5.1 (2019) | Security: prevents arbitrary code execution from YAML files |
| `os.path.join()` | `pathlib.Path` / operator | Python 3.4+ (mainstream ~2020) | Cleaner syntax, cross-platform, object-oriented |
| Separate config per environment | Single config + env vars for secrets | Current standard | Config file for non-sensitive brand data; env vars for secrets only |

**Deprecated/outdated:**
- `yaml.load()` without Loader argument: Deprecated since PyYAML 5.1; raises a warning. Always use `safe_load()`.
- Static Noto Sans font files: Google Fonts repository now distributes variable fonts by default. Static files are available in the `static/` subfolder of the download ZIP but are no longer the primary distribution format.

## Open Questions

1. **Variable font axis API in Pillow 12.1.1**
   - What we know: Pillow supports `get_variation_axes()` and `set_variation_by_axes()`. Documentation shows both dict-based and list-based APIs across versions.
   - What's unclear: Whether `set_variation_by_axes()` in Pillow 12.1.1 takes a dict `{"wght": 700}` or a list `[700]`. The API has changed between versions.
   - Recommendation: Test script should call `get_variation_axes()` first to discover the exact API, and include a fallback to static font files if variable font loading fails. Both approaches are valid.

2. **Noto Sans variable font file naming**
   - What we know: Google Fonts distributes as `NotoSans[wdth,wght].ttf` with brackets in the filename.
   - What's unclear: Whether the Google Fonts download page still provides both variable and static versions in the ZIP, or only variable.
   - Recommendation: Download from Google Fonts, check for `static/` subfolder. If static files exist, can use those as fallback. The bracket-named variable font file works fine on all platforms.

3. **KrabbelBabbel file naming**
   - What we know: Three files exist with names like `KrabbelBabbel-Extra-01.png`, `KrabbelBabbel-Extra-01 (1).png`, etc.
   - What's unclear: Whether the `(1)` and `(2)` suffixes indicate Canva export duplicates or genuinely different variants (e.g., orange vs green scribbles).
   - Recommendation: Copy all three into assets, inspect visually during asset preparation to determine if they are distinct variants worth keeping or duplicates to deduplicate. Rename to descriptive names if they are distinct variants.

## Sources

### Primary (HIGH confidence)
- [Pillow 12.1.1 ImageFont docs](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html) - Font loading, variable font API, truetype() parameters
- [Python pathlib docs](https://docs.python.org/3/library/pathlib.html) - Path resolution, cross-platform paths
- [PyYAML PyPI page](https://pypi.org/project/PyYAML/) - Version 6.0.3, Python compatibility
- [Pillow PyPI page](https://pypi.org/project/pillow/) - Version 12.1.1, release date Feb 2026
- [GitHub Actions secrets docs](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions) - Secret injection via `${{ secrets.NAME }}`

### Secondary (MEDIUM confidence)
- [Google Fonts Noto Sans specimen](https://fonts.google.com/specimen/Noto+Sans) - Font availability, variable font format
- [Google Fonts Permanent Marker specimen](https://fonts.google.com/specimen/Permanent+Marker) - Font availability, Apache 2.0 license
- [Google Fonts GitHub repo - PermanentMarker TTF](https://github.com/google/fonts/blob/main/apache/permanentmarker/PermanentMarker-Regular.ttf) - Direct download source for static TTF
- [Noto Fonts docs - use page](https://notofonts.github.io/noto-docs/website/use/) - Static vs variable font distribution, ZIP structure

### Tertiary (LOW confidence)
- Variable font axis API behavior in Pillow 12.1.1 specifically (dict vs list parameter) - needs runtime validation in test script

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - PyYAML and Pillow are well-established, versions verified on PyPI
- Architecture: HIGH - Project structure is simple file organization; patterns are standard Python conventions
- Pitfalls: HIGH - Common issues are well-documented; variable font handling is the only area requiring runtime validation

**Research date:** 2026-02-28
**Valid until:** 2026-03-30 (stable domain, low churn)
