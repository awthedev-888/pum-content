"""BaseTemplate - shared layout utilities for branded 1080x1080 Instagram images.

Provides canvas creation, gradient backgrounds, dynamic background patterns,
logo watermark placement, KrabbelBabbel decoration overlays, pixel-based text
wrapping, and font/color access. All template subclasses inherit from this class.

Usage:
    from templates.base import BaseTemplate

    class MyTemplate(BaseTemplate):
        def render(self, data):
            img = self.create_canvas()
            img = self.draw_gradient(img, *self.random_gradient())
            img = self.add_watermark(img)
            return img
"""

import random
from pathlib import Path

import yaml
from PIL import Image, ImageColor, ImageDraw, ImageFont


class BaseTemplate:
    """Base class for all PUM branded Instagram image templates.

    Handles brand config loading, canvas creation, gradient backgrounds,
    dynamic background patterns, logo watermark placement, KrabbelBabbel
    decoration overlays, text wrapping, and font/color access.
    """

    # Canvas dimensions (Instagram square post)
    WIDTH = 1080
    HEIGHT = 1080

    # Layout zones
    MARGIN = 80
    CONTENT_WIDTH = 920  # WIDTH - 2 * MARGIN
    HEADER_TOP = 80
    CONTENT_TOP = 220
    CONTENT_BOTTOM = 900
    FOOTER_TOP = 920

    # Watermark defaults
    WATERMARK_WIDTH = 120
    WATERMARK_PADDING = 30

    # Font size presets (measured for 1080x1080 canvas)
    FONT_SIZES = {
        "heading_large": 52,
        "heading_medium": 44,
        "heading_small": 36,
        "body_large": 30,
        "body_medium": 26,
        "body_small": 22,
        "stat_number": 96,
        "stat_label": 28,
        "decorative": 36,
        "caption": 20,
    }

    # Gradient color combinations from PUM brand palette
    GRADIENT_COMBOS = [
        ("#0E5555", "#D2E8D7"),  # dark green -> mint
        ("#0E5555", "#F8E3B3"),  # dark green -> beige
        ("#FF6900", "#F8E3B3"),  # orange -> beige
        ("#659BD1", "#D2E8D7"),  # blue -> mint
        ("#0E5555", "#659BD1"),  # dark green -> blue
        ("#D69A5F", "#F8E3B3"),  # warm brown -> beige
    ]

    def __init__(self, config_path=None):
        """Initialize BaseTemplate with brand config and assets.

        Args:
            config_path: Path to brand_config.yaml. Defaults to project root.
        """
        self.project_root = Path(__file__).resolve().parent.parent

        if config_path is None:
            config_path = self.project_root / "brand_config.yaml"

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self._load_fonts()
        self._load_logos()
        self._load_decorations()

    def _load_fonts(self):
        """Load brand fonts with correct variable font weights.

        NotoSans-Bold.ttf and NotoSans-Regular.ttf are variable fonts
        renamed to static-style names. They default to weight 400 without
        explicit axis setting. set_variation_by_axes([weight, width]) is
        required to differentiate heading (700) from body (400).
        """
        fonts = self.config["fonts"]

        # Heading font: NotoSans-Bold at weight 700
        heading_path = str(self.project_root / fonts["heading"]["file"])
        self.font_heading = ImageFont.truetype(
            heading_path, size=self.FONT_SIZES["heading_medium"]
        )
        self.font_heading.set_variation_by_axes([700, 100])

        # Body font: NotoSans-Regular at weight 400
        body_path = str(self.project_root / fonts["body"]["file"])
        self.font_body = ImageFont.truetype(
            body_path, size=self.FONT_SIZES["body_medium"]
        )
        self.font_body.set_variation_by_axes([400, 100])

        # Decorative font: PermanentMarker (not a variable font)
        decorative_path = str(self.project_root / fonts["decorative"]["file"])
        self.font_decorative = ImageFont.truetype(
            decorative_path, size=self.FONT_SIZES["decorative"]
        )

    def _load_logos(self):
        """Load PUM logo images for watermark placement."""
        logos = self.config["logos"]

        self.logo_primary = Image.open(
            str(self.project_root / logos["primary"])
        ).convert("RGBA")

        self.logo_white = Image.open(
            str(self.project_root / logos["white_with_slogan"])
        ).convert("RGBA")

    def _load_decorations(self):
        """Load KrabbelBabbel decoration PNGs for decorative overlays."""
        deco_config = self.config["decorations"]
        deco_dir = self.project_root / deco_config["directory"]

        self.decorations = []
        for deco_file in deco_config["krabbelbabbel"]:
            deco = Image.open(str(deco_dir / deco_file)).convert("RGBA")
            self.decorations.append(deco)

    def create_canvas(self, bg_color="#D2E8D7"):
        """Create a 1080x1080 RGBA canvas with solid background color.

        Args:
            bg_color: Hex color string for background. Defaults to mint green.

        Returns:
            PIL Image in RGBA mode.
        """
        return Image.new("RGBA", (self.WIDTH, self.HEIGHT), bg_color)

    def draw_gradient(self, img, color1, color2, direction="vertical"):
        """Draw gradient background using efficient line strip paste.

        Uses 1px-high (or 1px-wide) strip paste method instead of putpixel
        for performance. Interpolates linearly between color1 and color2.

        Args:
            img: PIL Image to draw gradient on.
            color1: Start color hex string.
            color2: End color hex string.
            direction: "vertical" (top to bottom) or "horizontal" (left to right).

        Returns:
            Modified PIL Image with gradient background.
        """
        c1 = ImageColor.getrgb(color1)
        c2 = ImageColor.getrgb(color2)

        if direction == "vertical":
            for y in range(self.HEIGHT):
                t = y / (self.HEIGHT - 1) if self.HEIGHT > 1 else 0
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                strip = Image.new("RGB", (self.WIDTH, 1), (r, g, b))
                img.paste(strip, (0, y))
        else:
            for x in range(self.WIDTH):
                t = x / (self.WIDTH - 1) if self.WIDTH > 1 else 0
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                strip = Image.new("RGB", (1, self.HEIGHT), (r, g, b))
                img.paste(strip, (x, 0))

        return img

    def random_gradient(self):
        """Return a random gradient color combination from the brand palette.

        Returns:
            Tuple of (color1, color2) hex strings.
        """
        return random.choice(self.GRADIENT_COMBOS)

    def add_dot_pattern(self, img, color_rgba=(255, 255, 255, 30), spacing=60):
        """Add subtle dot pattern overlay to the image.

        Creates small ellipses (radius 3px) at regular grid spacing on a
        transparent overlay, then composites onto the image.

        Args:
            img: PIL Image (must be RGBA mode).
            color_rgba: RGBA tuple for dot color. Default is white at ~12% opacity.
            spacing: Pixel spacing between dots.

        Returns:
            Composited PIL Image with dot pattern overlay.
        """
        overlay = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for x in range(0, self.WIDTH, spacing):
            for y in range(0, self.HEIGHT, spacing):
                draw.ellipse(
                    [(x - 3, y - 3), (x + 3, y + 3)],
                    fill=color_rgba,
                )

        return Image.alpha_composite(img, overlay)

    def add_diagonal_lines(
        self, img, color_rgba=(255, 255, 255, 20), spacing=40, width=1
    ):
        """Add subtle diagonal line pattern overlay to the image.

        Draws diagonal lines from top-left to bottom-right at regular spacing
        on a transparent overlay, then composites onto the image.

        Args:
            img: PIL Image (must be RGBA mode).
            color_rgba: RGBA tuple for line color. Default is white at ~8% opacity.
            spacing: Pixel spacing between lines.
            width: Line width in pixels.

        Returns:
            Composited PIL Image with diagonal line overlay.
        """
        overlay = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Draw diagonals covering full canvas. Lines go from top-left to bottom-right.
        # Start offset range must cover enough to fill the entire canvas.
        total_range = self.WIDTH + self.HEIGHT
        for offset in range(-total_range, total_range, spacing):
            start_x = offset
            start_y = 0
            end_x = offset + self.HEIGHT
            end_y = self.HEIGHT
            draw.line(
                [(start_x, start_y), (end_x, end_y)],
                fill=color_rgba,
                width=width,
            )

        return Image.alpha_composite(img, overlay)

    def add_decoration(self, img, deco_index=0, position=(0, 0), size=200, opacity=0.2):
        """Add a KrabbelBabbel decoration overlay at reduced opacity.

        Resizes the decoration maintaining aspect ratio, adjusts alpha channel
        for opacity control, and pastes with alpha mask.

        Args:
            img: PIL Image to add decoration to.
            deco_index: Index into self.decorations list (0, 1, or 2).
            position: (x, y) tuple for placement.
            size: Target width in pixels (height scales proportionally).
            opacity: Opacity multiplier (0.0 to 1.0). Default 0.2 (20%).

        Returns:
            Modified PIL Image with decoration overlay.
        """
        deco = self.decorations[deco_index].copy()

        # Resize maintaining aspect ratio
        aspect = deco.height / deco.width
        new_height = int(size * aspect)
        deco = deco.resize((size, new_height), Image.LANCZOS)

        # Adjust alpha for opacity
        r, g, b, a = deco.split()
        a = a.point(lambda x: int(x * opacity))
        deco = Image.merge("RGBA", (r, g, b, a))

        # Paste with alpha mask
        img.paste(deco, position, deco)
        return img

    def add_watermark(self, img, padding=None, width=None, use_white=False):
        """Add PUM logo watermark to bottom-right corner.

        Args:
            img: PIL Image to add watermark to.
            padding: Pixels from canvas edge. Defaults to WATERMARK_PADDING.
            width: Logo width in pixels. Defaults to WATERMARK_WIDTH.
            use_white: If True, use white logo; otherwise use dark green logo.

        Returns:
            Modified PIL Image with watermark.
        """
        if padding is None:
            padding = self.WATERMARK_PADDING
        if width is None:
            width = self.WATERMARK_WIDTH

        logo = self.logo_white if use_white else self.logo_primary

        # Calculate aspect ratio and resize
        aspect = logo.height / logo.width
        logo_h = int(width * aspect)
        logo = logo.resize((width, logo_h), Image.LANCZOS)

        # Position at bottom-right with padding
        pos = (self.WIDTH - width - padding, self.HEIGHT - logo_h - padding)

        # Paste with alpha mask for transparency
        img.paste(logo, pos, logo)
        return img

    def wrap_text(self, text, font, max_width):
        """Word-wrap text to fit within max_width pixels.

        Uses font.getlength() for pixel-accurate measurement instead of
        character counting. Handles single words longer than max_width by
        placing them on their own line.

        Args:
            text: String to wrap.
            font: PIL ImageFont for pixel measurement.
            max_width: Maximum line width in pixels.

        Returns:
            List of strings, one per line.
        """
        words = text.split()
        if not words:
            return []

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

    def get_text_block_height(self, lines, font, line_spacing=10):
        """Calculate total pixel height of a wrapped text block.

        Uses font.getbbox("Ag") to capture both ascender and descender height,
        which is more accurate than measuring single characters.

        Args:
            lines: List of text strings (from wrap_text).
            font: PIL ImageFont for height measurement.
            line_spacing: Extra pixels between lines.

        Returns:
            Total height in pixels.
        """
        if not lines:
            return 0

        line_height = font.getbbox("Ag")[3]
        return len(lines) * line_height + (len(lines) - 1) * line_spacing

    def get_font(self, style, size):
        """Load a brand font at a specific size.

        Loads the font file for the requested style and applies correct
        variable font weight axes.

        Args:
            style: "heading", "body", or "decorative".
            size: Font size in pixels.

        Returns:
            PIL ImageFont.FreeTypeFont object.
        """
        fonts = self.config["fonts"]

        if style == "heading":
            font_path = str(self.project_root / fonts["heading"]["file"])
            font = ImageFont.truetype(font_path, size=size)
            font.set_variation_by_axes([700, 100])
        elif style == "body":
            font_path = str(self.project_root / fonts["body"]["file"])
            font = ImageFont.truetype(font_path, size=size)
            font.set_variation_by_axes([400, 100])
        elif style == "decorative":
            font_path = str(self.project_root / fonts["decorative"]["file"])
            font = ImageFont.truetype(font_path, size=size)
        else:
            raise ValueError(f"Unknown font style: {style}. Use 'heading', 'body', or 'decorative'.")

        return font

    def get_color(self, group, name):
        """Get hex color string from brand config.

        Args:
            group: Color group ("primary" or "secondary").
            name: Color name within the group (e.g., "dark_green", "orange").

        Returns:
            Hex color string (e.g., "#0E5555").
        """
        return self.config["colors"][group][name]

    def render(self, data):
        """Render a template with the given data. Must be overridden by subclasses.

        Args:
            data: Dictionary of content data for the template.

        Raises:
            NotImplementedError: Always - subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement render()")

    def save(self, img, output_path):
        """Save image as PNG file, creating parent directories as needed.

        Args:
            img: PIL Image to save.
            output_path: Path (string or Path object) for output file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG")
