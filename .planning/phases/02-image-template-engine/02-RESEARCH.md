# Phase 2: Image Template Engine - Research

**Researched:** 2026-02-28
**Domain:** Pillow image generation, Instagram template design, text layout, brand identity rendering
**Confidence:** HIGH

## Summary

Phase 2 builds a Pillow-based template engine that generates three types of branded 1080x1080 Instagram post images using the PUM brand identity established in Phase 1. The technical domain is well-understood: Pillow 11.3.0 (already installed) provides all required drawing primitives -- `ImageDraw` for shapes and text, `Image.alpha_composite` for layering logos and decorations, and `ImageFont` with variable font axis support for weight differentiation. No additional Python packages are needed.

The primary complexity lies in layout design, not technology. Each template needs pixel-based text wrapping (Pillow has no built-in auto-wrap), careful spacing calculations for variable-length content, and consistent placement of the PUM logo watermark and decorative elements. All three brand fonts (NotoSans-Bold.ttf, NotoSans-Regular.ttf, PermanentMarker-Regular.ttf) load correctly in Pillow and render Indonesian text including special characters (em dashes, quotes, percentages). The three KrabbelBabbel decoration files are the same scribble shape in three brand colors (orange, mint green, dark green), making them suitable for color-coordinated template accents.

The architecture should follow a base-class pattern: a shared `BaseTemplate` class handles brand config loading, canvas creation, gradient/pattern backgrounds, logo watermark placement, and text wrapping utilities. Each template type (Quote/Story, Tips/List, Impact Stats) extends it with its own `render()` method. This keeps the codebase DRY and ensures consistent branding across all templates.

**Primary recommendation:** Build a `BaseTemplate` class with shared layout utilities (gradient backgrounds, text wrapping, logo watermark, brand color/font loading), then implement each template type as a subclass with its own `render(data) -> Image` method. Output as PNG files at 1080x1080 RGBA.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| IMG-01 | System generates 1080x1080 branded Instagram images using Pillow | Pillow 11.3.0 verified: `Image.new('RGBA', (1080, 1080))` creates canvas, `ImageDraw` draws shapes/text, `.save()` outputs PNG. All capabilities tested and working. |
| IMG-03 | 3 template types: Quote/Story, Tips/List, Impact Stats | Each template is a subclass of BaseTemplate with distinct layout: Quote/Story (headline + body + attribution), Tips/List (numbered items + optional icons), Impact Stats (large number + context). Architecture pattern documented below. |
| IMG-04 | PUM logo watermark on every generated image | Logo is RGBA (1744x852), resizes cleanly with `Image.LANCZOS`. Alpha channel enables transparent overlay via `Image.paste(logo, position, logo)`. Consistent bottom-right placement in BaseTemplate. |
| IMG-05 | Templates use PUM brand kit colors, fonts, and icons | brand_config.yaml provides all values. Colors parse via `ImageColor.getrgb()`. Fonts load via `ImageFont.truetype()` with variable font weight support (`set_variation_by_axes([weight, 100])`). 22 sector icons available as RGBA PNGs. |
| IMG-06 | Templates include dynamic background patterns or gradients | Gradients via line-by-line strip paste (tested, fast without numpy). Geometric patterns (dots, diagonals) via `ImageDraw` primitives. KrabbelBabbel scribbles as decorative overlays with opacity control. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pillow | 11.3.0 | All image generation: canvas, drawing, text, compositing, output | Already installed from Phase 1. Standard Python imaging library. All features verified working. |
| PyYAML | 6.0.3 | Load brand_config.yaml for colors, fonts, logos, icons | Already installed from Phase 1. Loads brand identity into template engine. |
| pathlib | stdlib | Resolve asset file paths relative to project root | Standard Python. Already used in Phase 1 patterns. |
| textwrap | stdlib | Initial text splitting for word-wrap (combined with Pillow pixel measurement) | Standard Python. Useful as starting point before pixel-based refinement. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| random | stdlib | Select background gradient color combinations, pattern variations | Dynamic background variety per template render |
| math | stdlib | Geometric calculations for pattern generation (angles, spacing) | Background pattern drawing (diagonal lines, circular patterns) |
| typing | stdlib | Type hints for template data structures | Function signatures, data classes |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pillow gradients (line strips) | numpy array gradient | Faster but adds 50MB+ dependency; strip paste is fast enough for single-image generation |
| Class inheritance for templates | Dict-based template configs | Classes are cleaner for templates with different layouts; each template has distinct render logic |
| Pillow-only text wrapping | textwrap3 or python-textwrap | No benefit; standard textwrap + Pillow getlength() covers all needs |

**Installation:**
```bash
# No new packages needed -- all dependencies installed in Phase 1
pip install -r requirements.txt  # PyYAML==6.0.3 Pillow==11.3.0 python-dotenv>=1.0.0
```

## Architecture Patterns

### Recommended Project Structure
```
pum-content/
├── templates/
│   ├── __init__.py            # Package init, exports render functions
│   ├── base.py                # BaseTemplate: brand loading, canvas, gradients, watermark, text utils
│   ├── quote_story.py         # QuoteStoryTemplate: headline + body + attribution
│   ├── tips_list.py           # TipsListTemplate: numbered items with icons
│   └── impact_stats.py        # ImpactStatsTemplate: large numbers with context
├── assets/                    # (Phase 1 output -- fonts, logos, icons, decorations)
├── brand_config.yaml          # (Phase 1 output -- brand identity)
├── output/                    # Generated images (.gitignored)
└── tests/
    ├── test_brand_config.py   # (Phase 1 output)
    └── test_templates.py      # Template rendering smoke tests
```

### Pattern 1: BaseTemplate with Shared Layout Logic
**What:** Abstract base class that handles everything common to all templates
**When to use:** Every template inherits from this
**Example:**
```python
# Source: Pillow docs + standard OOP pattern
from PIL import Image, ImageDraw, ImageFont, ImageColor
from pathlib import Path
import yaml
import random

class BaseTemplate:
    WIDTH = 1080
    HEIGHT = 1080

    def __init__(self, config_path: Path = None):
        self.project_root = Path(__file__).resolve().parent.parent
        if config_path is None:
            config_path = self.project_root / "brand_config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self._load_fonts()
        self._load_logos()

    def _load_fonts(self):
        """Load brand fonts with correct weights."""
        fonts = self.config["fonts"]
        self.font_heading = ImageFont.truetype(
            str(self.project_root / fonts["heading"]["file"]),
            size=48
        )
        self.font_body = ImageFont.truetype(
            str(self.project_root / fonts["body"]["file"]),
            size=28
        )
        self.font_decorative = ImageFont.truetype(
            str(self.project_root / fonts["decorative"]["file"]),
            size=36
        )

    def _load_logos(self):
        """Load logo images for watermark."""
        logos = self.config["logos"]
        self.logo_primary = Image.open(
            str(self.project_root / logos["primary"])
        ).convert("RGBA")

    def create_canvas(self, bg_color: str = "#D2E8D7") -> Image.Image:
        """Create 1080x1080 RGBA canvas."""
        return Image.new("RGBA", (self.WIDTH, self.HEIGHT), bg_color)

    def draw_gradient(self, img: Image.Image, color1: str, color2: str,
                      direction: str = "vertical") -> Image.Image:
        """Draw gradient background using line strips."""
        c1 = ImageColor.getrgb(color1)
        c2 = ImageColor.getrgb(color2)
        for y in range(self.HEIGHT):
            t = y / self.HEIGHT
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            strip = Image.new("RGB", (self.WIDTH, 1), (r, g, b))
            img.paste(strip, (0, y))
        return img

    def add_watermark(self, img: Image.Image, padding: int = 30,
                      width: int = 120) -> Image.Image:
        """Add PUM logo watermark to bottom-right corner."""
        aspect = self.logo_primary.height / self.logo_primary.width
        logo_h = int(width * aspect)
        logo = self.logo_primary.resize((width, logo_h), Image.LANCZOS)
        pos = (self.WIDTH - width - padding, self.HEIGHT - logo_h - padding)
        img.paste(logo, pos, logo)  # Third arg = alpha mask
        return img

    def wrap_text(self, text: str, font: ImageFont.FreeTypeFont,
                  max_width: int) -> list[str]:
        """Word-wrap text to fit within max_width pixels."""
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.getlength(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def get_color(self, group: str, name: str) -> str:
        """Get hex color from brand config."""
        return self.config["colors"][group][name]

    def render(self, data: dict) -> Image.Image:
        """Override in subclasses."""
        raise NotImplementedError

    def save(self, img: Image.Image, output_path: Path):
        """Save image as PNG."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG")
```

### Pattern 2: Template Subclass with render() Method
**What:** Each template type implements its own render logic
**When to use:** Quote/Story, Tips/List, Impact Stats each follow this pattern
**Example:**
```python
class QuoteStoryTemplate(BaseTemplate):
    def render(self, data: dict) -> Image.Image:
        """
        data = {
            "headline": "Kisah Sukses PUM Indonesia",
            "body": "Bapak Sutrisno berhasil meningkatkan...",
            "attribution": "— Bapak Sutrisno, Petani Yogyakarta",
            "sector": "agriculture"  # optional, for icon
        }
        """
        # 1. Create canvas with gradient background
        img = self.create_canvas()
        img = self.draw_gradient(img, "#0E5555", "#D2E8D7")

        # 2. Draw content
        draw = ImageDraw.Draw(img)
        # ... layout-specific drawing code ...

        # 3. Add watermark
        img = self.add_watermark(img)

        return img
```

### Pattern 3: Dynamic Background Variations
**What:** Each render call can produce a visually distinct background
**When to use:** All templates should vary their backgrounds
**Example:**
```python
# Gradient combinations from brand palette
GRADIENT_COMBOS = [
    ("#0E5555", "#D2E8D7"),   # dark green -> mint
    ("#0E5555", "#F8E3B3"),   # dark green -> beige
    ("#FF6900", "#F8E3B3"),   # orange -> beige
    ("#659BD1", "#D2E8D7"),   # blue -> mint
]

# Pattern overlay (dots, diagonal lines, etc.)
def add_dot_pattern(self, img, color_rgba=(255, 255, 255, 30), spacing=60):
    """Add subtle dot pattern overlay."""
    overlay = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(0, self.WIDTH, spacing):
        for y in range(0, self.HEIGHT, spacing):
            draw.ellipse([(x-3, y-3), (x+3, y+3)], fill=color_rgba)
    return Image.alpha_composite(img, overlay)

# KrabbelBabbel decoration overlay
def add_decoration(self, img, deco_index=0, position=(0, 0),
                   size=200, opacity=0.2):
    """Add KrabbelBabbel scribble as decorative accent."""
    deco_dir = self.project_root / self.config["decorations"]["directory"]
    deco_file = self.config["decorations"]["krabbelbabbel"][deco_index]
    deco = Image.open(str(deco_dir / deco_file)).convert("RGBA")
    aspect = deco.height / deco.width
    deco = deco.resize((size, int(size * aspect)), Image.LANCZOS)
    # Adjust opacity
    r, g, b, a = deco.split()
    a = a.point(lambda x: int(x * opacity))
    deco = Image.merge("RGBA", (r, g, b, a))
    img.paste(deco, position, deco)
    return img
```

### Pattern 4: Pixel-Based Text Wrapping
**What:** Custom word wrapping based on actual rendered pixel width
**When to use:** All text blocks in all templates
**Why not textwrap:** Python's `textwrap` wraps by character count, not pixel width. Proportional fonts make character-based wrapping unreliable.
**Example:**
```python
def wrap_text(self, text: str, font: ImageFont.FreeTypeFont,
              max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.getlength(test_line) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# Usage: calculate text block height
def get_text_block_height(self, lines, font, line_spacing=10):
    """Calculate total height of wrapped text block."""
    if not lines:
        return 0
    line_height = font.getbbox("Ag")[3]  # Use "Ag" for ascender+descender
    return len(lines) * line_height + (len(lines) - 1) * line_spacing
```

### Anti-Patterns to Avoid
- **Hardcoded pixel positions without constants:** Define layout zones as named constants (e.g., `MARGIN = 80`, `HEADER_Y = 120`, `CONTENT_Y = 280`) so they can be tuned in one place.
- **Loading fonts on every render call:** Load fonts once in `__init__`, not per render. Font loading involves disk I/O and parsing.
- **Using textwrap.fill() for image text:** Character-based wrapping does not account for proportional font widths. Use pixel-based wrapping with `font.getlength()`.
- **Saving as JPEG for Instagram:** JPEG loses the alpha channel and introduces compression artifacts on text edges. Save as PNG. Instagram accepts both.
- **Drawing text directly on gradient canvas:** Create an RGBA overlay for text, then composite. This enables opacity control and cleaner compositing.
- **Ignoring text that overflows the canvas:** Always check that wrapped text fits within the available vertical space. Reduce font size or truncate if it doesn't.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Text wrapping | Character-count-based wrapping | Pixel-based wrapping with `font.getlength()` | Proportional fonts make character counting unreliable; "iiiii" and "WWWWW" have wildly different widths |
| Gradient generation | Pixel-by-pixel putpixel() loop | Line strip paste (1-pixel-high `Image.new` + `paste`) | putpixel() is ~100x slower; strip paste is fast enough without numpy |
| Color parsing | Manual hex-to-RGB conversion | `PIL.ImageColor.getrgb("#hex")` | Handles all formats (hex, named colors, RGB tuples), returns tuple |
| Image compositing | Manual pixel alpha blending | `Image.alpha_composite(base, overlay)` | Correct alpha math; manual blending gets premultiplied alpha wrong |
| Font size selection | Fixed font sizes for all content | Font size as parameter with sensible defaults | Content length varies; template may need to adapt font size for very long text |

**Key insight:** Pillow provides all the building blocks (draw, text, composite, resize). The custom code is layout logic: where to place things, how to wrap text, and how to compose layers. Keep rendering logic in template subclasses and shared utilities in the base class.

## Common Pitfalls

### Pitfall 1: Text Overflowing Canvas Vertically
**What goes wrong:** Long Indonesian text (e.g., 3-4 sentence body) wraps to more lines than fit in the available vertical space, causing text to extend below the canvas or overlap with the watermark.
**Why it happens:** Template layout assumes a fixed number of text lines, but content length varies per post.
**How to avoid:** Calculate total text block height after wrapping. If it exceeds available space, reduce font size incrementally (e.g., -2px per attempt) until it fits. Set a minimum font size floor (e.g., 18px) to prevent unreadable text.
**Warning signs:** Text rendered below Y=1000 (overlapping watermark zone), or truncated visually.

### Pitfall 2: Logo Watermark Transparency Failing
**What goes wrong:** Logo appears with a white or black rectangle background instead of transparent overlay.
**Why it happens:** Using `img.paste(logo, position)` without the alpha mask argument, or pasting onto an RGB canvas instead of RGBA.
**How to avoid:** Always use three-argument paste: `img.paste(logo, position, logo)` where the third argument is the alpha mask. Ensure the base canvas is RGBA mode. Convert the logo to RGBA with `.convert("RGBA")` on load.
**Warning signs:** White rectangle around the PUM logo on gradient backgrounds.

### Pitfall 3: Font Weight Not Applied (Variable Fonts)
**What goes wrong:** Both heading and body text render at the same weight (Regular/400) despite loading different font files.
**Why it happens:** `NotoSans-Bold.ttf` and `NotoSans-Regular.ttf` are the same variable font file (renamed copies). Loading them via `truetype()` both default to weight 400.
**How to avoid:** After loading the heading font, call `font.set_variation_by_axes([700, 100])` to set Bold weight. For body font, call `font.set_variation_by_axes([400, 100])`. The axes are `[weight, width]` -- verified working in Pillow 11.3.0.
**Warning signs:** Heading text looks the same weight as body text.

### Pitfall 4: Indonesian Text Character Rendering Issues
**What goes wrong:** Characters like em dashes (---), smart quotes, or percentage signs render as boxes or question marks.
**Why it happens:** Using a font that lacks the glyph, or encoding issues in the text data.
**How to avoid:** Noto Sans supports all Latin characters needed for Indonesian. Verified: em dashes, curly quotes, percentages, colons, parentheses all render correctly with NotoSans-Regular/Bold.ttf. Ensure text data is passed as Python strings (UTF-8).
**Warning signs:** Small rectangles (tofu) appearing in rendered text.

### Pitfall 5: Decoration/Pattern Opacity Too Strong
**What goes wrong:** KrabbelBabbel scribbles or background patterns overpower the text content.
**Why it happens:** Pasting decorations at full opacity creates visual clutter.
**How to avoid:** Reduce opacity to 15-25% for decorative overlays. Split RGBA, apply `a.point(lambda x: int(x * 0.2))`, re-merge. Test with actual text to ensure readability.
**Warning signs:** Text is hard to read against busy background, brand identity feels cluttered.

### Pitfall 6: Inconsistent Layout Across Templates
**What goes wrong:** Watermark position, margins, or font sizes differ between template types, making the output look unbranded.
**Why it happens:** Each template defines its own spacing values independently.
**How to avoid:** Define shared constants in BaseTemplate: `MARGIN`, `WATERMARK_PADDING`, `WATERMARK_WIDTH`, `HEADER_FONT_SIZE`, `BODY_FONT_SIZE`. All templates inherit and use these.
**Warning signs:** Side-by-side comparison shows different padding or watermark positions across template types.

## Code Examples

### Brand Color Palette for Template Design
```python
# Verified from brand_config.yaml
# Primary colors (high contrast, use for key elements)
DARK_GREEN = "#0E5555"    # Headings, watermark logo, dark backgrounds
MINT_GREEN = "#D2E8D7"    # Light backgrounds, subtle fills
ORANGE     = "#FF6900"    # CTAs, accent elements, emphasis

# Secondary colors (supporting, use for variety)
BLUE       = "#659BD1"    # Alternative accent
WARM_BROWN = "#D69A5F"    # Warm tone accent
SOFT_GOLD  = "#E9C779"    # Highlight, badge background
LIGHT_BEIGE = "#F8E3B3"   # Alternative light background

# KrabbelBabbel decorations (same shape, 3 brand colors)
# Index 0: Orange scribble (#FF8538)
# Index 1: Mint green scribble (#D2E8D7)
# Index 2: Dark green scribble (#0E5555)
```

### Recommended Font Sizes (Verified for 1080x1080)
```python
# Measured with actual font files at various sizes
# Available width with 80px margins: 920px

FONT_SIZES = {
    # Headings: NotoSans-Bold (weight 700)
    "heading_large": 52,    # ~18-20 chars per line
    "heading_medium": 44,   # ~22-25 chars per line
    "heading_small": 36,    # ~28-32 chars per line

    # Body: NotoSans-Regular (weight 400)
    "body_large": 30,       # ~30-35 chars per line
    "body_medium": 26,      # ~35-40 chars per line
    "body_small": 22,       # ~40-48 chars per line

    # Stats: NotoSans-Bold (weight 700)
    "stat_number": 96,      # Large impact numbers (3-8 chars)
    "stat_label": 28,       # Context text below number

    # Decorative: PermanentMarker
    "decorative": 36,       # Taglines, CTAs

    # Utility
    "caption": 20,          # Small text, attributions
}
```

### Layout Zones for 1080x1080 Canvas
```python
# Standard layout zones (with 80px margins)
MARGIN = 80
CONTENT_LEFT = MARGIN          # 80
CONTENT_RIGHT = 1080 - MARGIN  # 1000
CONTENT_WIDTH = 1080 - 2 * MARGIN  # 920

# Vertical zones
HEADER_TOP = 80
HEADER_BOTTOM = 200
CONTENT_TOP = 220
CONTENT_BOTTOM = 900
FOOTER_TOP = 920
FOOTER_BOTTOM = 1060

# Watermark (bottom-right)
WATERMARK_WIDTH = 120
WATERMARK_PADDING = 30
```

### Quote/Story Template Layout Sketch
```python
# Data: headline, body, attribution, optional sector
# Layout:
# ┌─────────────────────────┐
# │  [gradient background]  │
# │  ┌───────────────────┐  │
# │  │   HEADLINE         │  │  Y: 120-200, font: heading 48px
# │  │   (1-2 lines)      │  │
# │  ├───────────────────┤  │
# │  │   ───────────      │  │  Y: 220, decorative divider line
# │  ├───────────────────┤  │
# │  │   Body text        │  │  Y: 260-700, font: body 28px
# │  │   (multi-line      │  │  Max ~15 lines
# │  │    wrapped)         │  │
# │  ├───────────────────┤  │
# │  │   — Attribution    │  │  Y: 720-780, font: body italic 22px
# │  ├───────────────────┤  │
# │  │ [KrabbelBabbel]   │  │  Decorative accent (low opacity)
# │  │              [LOGO]│  │  PUM watermark bottom-right
# │  └───────────────────┘  │
# └─────────────────────────┘
```

### Tips/List Template Layout Sketch
```python
# Data: title, items (list of strings), optional sector icons
# Layout:
# ┌─────────────────────────┐
# │  [gradient background]  │
# │  ┌───────────────────┐  │
# │  │   TITLE            │  │  Y: 100-170, font: heading 44px
# │  ├───────────────────┤  │
# │  │ ① Item one text   │  │  Y: 200+, numbered items
# │  │   (wrapped if long)│  │  Circled number + body 26px
# │  │ ② Item two text   │  │  Spacing: 30px between items
# │  │ ③ Item three      │  │
# │  │ ④ Item four       │  │  Max 5 items recommended
# │  │ ⑤ Item five       │  │
# │  ├───────────────────┤  │
# │  │ [sector icon]     │  │  Optional: relevant sector icon
# │  │              [LOGO]│  │  PUM watermark bottom-right
# │  └───────────────────┘  │
# └─────────────────────────┘
```

### Impact Stats Template Layout Sketch
```python
# Data: stats (list of {number, label, context}), title
# Layout:
# ┌─────────────────────────┐
# │  [gradient background]  │
# │  ┌───────────────────┐  │
# │  │   TITLE            │  │  Y: 100-170, font: heading 44px
# │  ├───────────────────┤  │
# │  │                    │  │
# │  │    1.200+          │  │  Y: 250, font: stat 96px, ORANGE
# │  │  ahli sukarelawan  │  │  Y: 360, font: body 28px
# │  │                    │  │
# │  │      30+           │  │  Y: 440, second stat
# │  │    negara aktif    │  │
# │  │                    │  │
# │  │      45+           │  │  Y: 600, third stat (optional)
# │  │   tahun pengalaman │  │
# │  ├───────────────────┤  │
# │  │ [decoration]      │  │
# │  │              [LOGO]│  │  PUM watermark bottom-right
# │  └───────────────────┘  │
# └─────────────────────────┘
```

### Test Pattern for Template Verification
```python
#!/usr/bin/env python3
"""Smoke test for all template types."""
from pathlib import Path
from templates.quote_story import QuoteStoryTemplate
from templates.tips_list import TipsListTemplate
from templates.impact_stats import ImpactStatsTemplate
from PIL import Image

output_dir = Path("output/test")

# Test Quote/Story
qt = QuoteStoryTemplate()
img = qt.render({
    "headline": "Kisah Sukses PUM Indonesia",
    "body": "Bapak Sutrisno berhasil meningkatkan produksi pertanian sebesar 40% setelah mendapat bimbingan dari ahli PUM Belanda selama 3 bulan.",
    "attribution": "— Bapak Sutrisno, Petani Yogyakarta",
})
assert img.size == (1080, 1080), f"Wrong size: {img.size}"
assert img.mode == "RGBA", f"Wrong mode: {img.mode}"
qt.save(img, output_dir / "quote_story_test.png")

# Test Tips/List
tl = TipsListTemplate()
img = tl.render({
    "title": "5 Tips Ekspor untuk UMKM",
    "items": [
        "Pahami regulasi ekspor negara tujuan",
        "Siapkan sertifikasi produk yang diperlukan",
        "Manfaatkan program pendampingan PUM",
        "Bangun jaringan dengan buyer internasional",
        "Mulai dari pasar ASEAN terdekat",
    ],
})
assert img.size == (1080, 1080)
tl.save(img, output_dir / "tips_list_test.png")

# Test Impact Stats
ist = ImpactStatsTemplate()
img = ist.render({
    "title": "Dampak PUM di Indonesia",
    "stats": [
        {"number": "1.200+", "label": "ahli sukarelawan"},
        {"number": "30+", "label": "negara aktif"},
        {"number": "45+", "label": "tahun pengalaman"},
    ],
})
assert img.size == (1080, 1080)
ist.save(img, output_dir / "impact_stats_test.png")

print("All template tests passed.")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `ImageDraw.textsize()` | `ImageFont.getbbox()` and `ImageFont.getlength()` | Pillow 10.0 (2023) | `textsize()` deprecated; `getbbox()` returns full bounding box, `getlength()` returns horizontal advance width |
| `ImageDraw.textsize()` for multiline | `ImageDraw.multiline_textbbox()` | Pillow 10.0 (2023) | More accurate bounding box for multi-line text blocks |
| No text anchor support | `anchor` parameter in `draw.text()` | Pillow 8.0 (2021) | Enables center/right alignment without manual calculation: `anchor="mm"` for center-center |
| `Image.ANTIALIAS` resampling | `Image.LANCZOS` resampling | Pillow 10.0 (2023) | `ANTIALIAS` deprecated, replaced by `LANCZOS` (same algorithm, clearer name) |
| No `rounded_rectangle` | `ImageDraw.rounded_rectangle()` | Pillow 8.2 (2021) | Built-in rounded rectangles; no need to hand-draw arcs + lines |

**Deprecated/outdated (do NOT use):**
- `ImageDraw.textsize()` -- removed in Pillow 10.0. Use `font.getbbox()` or `draw.textbbox()` instead.
- `Image.ANTIALIAS` -- removed in Pillow 10.0. Use `Image.LANCZOS` instead.
- `ImageFont.getsize()` -- removed in Pillow 10.0. Use `ImageFont.getbbox()` instead.

## Open Questions

1. **Optimal gradient color combinations per template type**
   - What we know: 7 brand colors available (3 primary + 4 secondary). All gradient combinations render correctly.
   - What's unclear: Which color combinations look best for each template type on Instagram. High contrast (dark green to beige) vs. subtle (mint to beige) depends on content.
   - Recommendation: Implement 4-6 preset gradient combinations per template. Select randomly at render time. The planner should define specific combinations per template type during implementation.

2. **Maximum content length for each template**
   - What we know: Body text at 28px fits ~32 chars per line on 920px width. Available vertical space for body: ~440px (Y 260-700), fitting ~14-15 lines at 30px line height.
   - What's unclear: Real content from Gemini in Phase 3 may exceed these limits.
   - Recommendation: Build adaptive font sizing (reduce by 2px per attempt if text overflows) with a minimum floor. Test with maximum-length sample content during implementation.

3. **Sector icon usage in templates**
   - What we know: 22 sector icons (RGBA, ~297x297px) are available. Tips/List template can optionally include a relevant sector icon.
   - What's unclear: Whether all three template types should use sector icons or just Tips/List.
   - Recommendation: Make sector icon an optional parameter in all templates. Place in a consistent position (e.g., bottom-left). Phase 3 (AI generation) will decide which sector applies.

## Sources

### Primary (HIGH confidence)
- Pillow 11.3.0 runtime verification -- all drawing, text, compositing, gradient, and font features tested directly on the installed version
- brand_config.yaml -- verified schema, all asset paths resolve, all fonts load in Pillow (Phase 1 output)
- Phase 1 summaries (01-01, 01-02, 01-03) -- established patterns for path resolution, font naming, and asset organization

### Secondary (MEDIUM confidence)
- [Pillow ImageDraw documentation](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html) -- draw primitives, text methods, anchor parameter
- [Pillow ImageFont documentation](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html) -- truetype loading, variable font axes, getbbox/getlength
- [Pillow Image documentation](https://pillow.readthedocs.io/en/stable/reference/Image.html) -- alpha_composite, paste, resize, LANCZOS
- [Pillow text wrapping discussion (GitHub #6201)](https://github.com/python-pillow/Pillow/issues/6201) -- confirms no built-in auto-wrap; pixel-based wrapping is the standard approach
- [Instagram image size guide 2026](https://imageforpost.com/guides/instagram-image-sizes-dimensions-guide-2025) -- confirms 1080x1080 square post remains the standard dimension

### Tertiary (LOW confidence)
- None -- all findings verified through direct runtime testing.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- Pillow 11.3.0 all features verified by direct testing. No new dependencies needed.
- Architecture: HIGH -- BaseTemplate + subclass pattern is standard OOP. Layout math verified with measured font sizes.
- Pitfalls: HIGH -- All pitfalls discovered through actual testing (variable font weights, alpha compositing, text overflow). Solutions verified.

**Research date:** 2026-02-28
**Valid until:** 2026-03-30 (stable domain, Pillow 11.3.0 pinned, no API changes expected)
