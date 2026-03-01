"""BaseTemplate - shared layout utilities for branded 1080x1080 Instagram images.

Provides canvas creation, gradient backgrounds, dynamic background patterns,
logo watermark placement, KrabbelBabbel decoration overlays, pixel-based text
wrapping, font/color access, and the 3-zone layout system (headline / photo / CTA).

Usage:
    from templates.base import BaseTemplate

    class MyTemplate(BaseTemplate):
        def render(self, data, photo=None):
            img = self.create_canvas()
            img, bg = self.draw_headline_zone(img, "Bersama\\nKita Tumbuh")
            img = self.draw_photo_zone(img, photo=photo)
            img = self.draw_cta_banner(img, "TOGETHER WE GROW")
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
    decoration overlays, text wrapping, font/color access, and the 3-zone
    layout system matching @pum_nl Instagram style.
    """

    # Canvas dimensions (Instagram square post)
    WIDTH = 1080
    HEIGHT = 1080

    # 3-zone layout heights
    HEADLINE_ZONE_HEIGHT = 378   # ~35%
    PHOTO_ZONE_HEIGHT = 486      # ~45%
    CTA_ZONE_HEIGHT = 216        # ~20%

    # Legacy layout zones (kept for backward compat)
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

    # Headline zone background color rotation
    HEADLINE_BG_COLORS = [
        "#0E5555",  # dark teal
        "#D2E8D7",  # light mint
        "#F8E3B3",  # light beige
    ]

    # Bracket decoration constants
    BRACKET_LENGTH = 40
    BRACKET_THICKNESS = 3
    BRACKET_INSET = 20  # how far from photo zone edges

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

    # ── 3-Zone Layout Methods ───────────────────────────────────────────

    def draw_headline_zone(self, img, headline_text, bg_color=None):
        """Draw the top headline zone with solid color, bold text, and KrabbelBabbel mark.

        Args:
            img: PIL Image (1080x1080 RGBA).
            headline_text: Short headline, may contain \\n for line breaks.
            bg_color: Hex color for zone background. If None, randomly chosen.

        Returns:
            Tuple of (modified PIL Image, bg_color used).
        """
        if bg_color is None:
            bg_color = random.choice(self.HEADLINE_BG_COLORS)

        # Draw solid color block
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [(0, 0), (self.WIDTH, self.HEADLINE_ZONE_HEIGHT)],
            fill=bg_color,
        )

        # Determine text color based on background brightness
        is_dark = self._is_dark_color(bg_color)
        text_color = "#FFFFFF" if is_dark else "#0E5555"

        # Draw headline text
        headline_font = self.get_font("heading", 56)
        lines = headline_text.split("\\n") if "\\n" in headline_text else [headline_text]

        line_height = headline_font.getbbox("Ag")[3]
        total_text_height = len(lines) * line_height + (len(lines) - 1) * 12
        start_y = (self.HEADLINE_ZONE_HEIGHT - total_text_height) // 2

        text_x = self.MARGIN
        current_y = start_y
        max_text_width = 0

        for line in lines:
            draw.text((text_x, current_y), line, fill=text_color, font=headline_font)
            line_width = headline_font.getlength(line)
            max_text_width = max(max_text_width, line_width)
            current_y += line_height + 12

        # KrabbelBabbel mark beside headline (prominent, ~85% opacity)
        if self.decorations:
            deco_index = random.randint(0, len(self.decorations) - 1)
            deco_size = 120
            deco_x = int(text_x + max_text_width + 30)
            # Clamp to canvas
            if deco_x + deco_size > self.WIDTH - 20:
                deco_x = self.WIDTH - deco_size - 20
            deco_y = (self.HEADLINE_ZONE_HEIGHT - deco_size) // 2
            img = self.add_decoration(
                img,
                deco_index=deco_index,
                position=(deco_x, deco_y),
                size=deco_size,
                opacity=0.85,
            )

        # Orange underline accent under last line of headline
        underline_y = current_y - 4
        underline_width = min(int(max_text_width * 0.6), 300)
        draw = ImageDraw.Draw(img)  # refresh after decoration composite
        draw.rectangle(
            [(text_x, underline_y), (text_x + underline_width, underline_y + 4)],
            fill="#FF6900",
        )

        return img, bg_color

    def draw_photo_zone(self, img, photo=None, sector=None):
        """Draw the middle photo zone with photo or gradient fallback.

        Args:
            img: PIL Image (1080x1080 RGBA).
            photo: PIL Image for the photo, or None for fallback.
            sector: Sector key for fallback icon (e.g., "agriculture").

        Returns:
            Modified PIL Image.
        """
        zone_top = self.HEADLINE_ZONE_HEIGHT
        zone_width = self.WIDTH
        zone_height = self.PHOTO_ZONE_HEIGHT

        if photo is not None:
            from content_generator.photo_service import crop_to_zone
            cropped = crop_to_zone(photo, zone_width, zone_height)
            img.paste(cropped, (0, zone_top))
        else:
            img = self._draw_fallback_photo_zone(img, sector)

        # White corner brackets
        img = self._draw_bracket_decorations(img)

        return img

    def _draw_fallback_photo_zone(self, img, sector=None):
        """Draw gradient + sector icon fallback when no photo is available.

        Args:
            img: PIL Image to draw on.
            sector: Optional sector key for icon overlay.

        Returns:
            Modified PIL Image.
        """
        zone_top = self.HEADLINE_ZONE_HEIGHT
        zone_height = self.PHOTO_ZONE_HEIGHT

        # Gradient fill in the photo zone
        c1 = ImageColor.getrgb("#0E5555")
        c2 = ImageColor.getrgb("#D2E8D7")
        for y in range(zone_height):
            t = y / (zone_height - 1) if zone_height > 1 else 0
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            strip = Image.new("RGB", (self.WIDTH, 1), (r, g, b))
            img.paste(strip, (0, zone_top + y))

        # Add dot pattern to photo zone
        overlay = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        for x in range(0, self.WIDTH, 60):
            for y in range(zone_top, zone_top + zone_height, 60):
                draw_overlay.ellipse(
                    [(x - 2, y - 2), (x + 2, y + 2)],
                    fill=(255, 255, 255, 25),
                )
        img = Image.alpha_composite(img, overlay)

        # Sector icon at 40% opacity in center of photo zone
        if sector:
            icons_config = self.config.get("icons", {})
            sectors = icons_config.get("sectors", {})
            icon_filename = sectors.get(sector)
            if icon_filename:
                icon_dir = self.project_root / icons_config.get("directory", "assets/icons/")
                icon_path = icon_dir / icon_filename
                if icon_path.exists():
                    icon = Image.open(str(icon_path)).convert("RGBA")
                    icon_size = 160
                    aspect = icon.height / icon.width
                    icon_h = int(icon_size * aspect)
                    icon = icon.resize((icon_size, icon_h), Image.LANCZOS)

                    # Set opacity to 40%
                    r_ch, g_ch, b_ch, a_ch = icon.split()
                    a_ch = a_ch.point(lambda x: int(x * 0.4))
                    icon = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch))

                    icon_x = (self.WIDTH - icon_size) // 2
                    icon_y = zone_top + (zone_height - icon_h) // 2
                    img.paste(icon, (icon_x, icon_y), icon)

        return img

    def _draw_bracket_decorations(self, img):
        """Draw white corner brackets around the photo zone edges.

        Creates L-shaped brackets at each corner of the photo zone, matching
        PUM's @pum_nl Instagram style.

        Args:
            img: PIL Image to draw on.

        Returns:
            Modified PIL Image.
        """
        draw = ImageDraw.Draw(img)
        zone_top = self.HEADLINE_ZONE_HEIGHT
        zone_bottom = zone_top + self.PHOTO_ZONE_HEIGHT
        bracket_color = (255, 255, 255, 200)
        inset = self.BRACKET_INSET
        length = self.BRACKET_LENGTH
        thickness = self.BRACKET_THICKNESS

        # Use overlay for semi-transparent brackets
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)

        # Top-left bracket
        od.rectangle([(inset, zone_top + inset), (inset + length, zone_top + inset + thickness)], fill=bracket_color)
        od.rectangle([(inset, zone_top + inset), (inset + thickness, zone_top + inset + length)], fill=bracket_color)

        # Top-right bracket
        od.rectangle([(self.WIDTH - inset - length, zone_top + inset), (self.WIDTH - inset, zone_top + inset + thickness)], fill=bracket_color)
        od.rectangle([(self.WIDTH - inset - thickness, zone_top + inset), (self.WIDTH - inset, zone_top + inset + length)], fill=bracket_color)

        # Bottom-left bracket
        od.rectangle([(inset, zone_bottom - inset - thickness), (inset + length, zone_bottom - inset)], fill=bracket_color)
        od.rectangle([(inset, zone_bottom - inset - length), (inset + thickness, zone_bottom - inset)], fill=bracket_color)

        # Bottom-right bracket
        od.rectangle([(self.WIDTH - inset - length, zone_bottom - inset - thickness), (self.WIDTH - inset, zone_bottom - inset)], fill=bracket_color)
        od.rectangle([(self.WIDTH - inset - thickness, zone_bottom - inset - length), (self.WIDTH - inset, zone_bottom - inset)], fill=bracket_color)

        return Image.alpha_composite(img, overlay)

    def draw_cta_banner(self, img, cta_text="TOGETHER WE GROW"):
        """Draw the bottom orange CTA banner with PermanentMarker text and PUM logo.

        Args:
            img: PIL Image (1080x1080 RGBA).
            cta_text: CTA text string (ALL CAPS, 2-5 words).

        Returns:
            Modified PIL Image.
        """
        zone_top = self.HEADLINE_ZONE_HEIGHT + self.PHOTO_ZONE_HEIGHT
        draw = ImageDraw.Draw(img)

        # Orange rectangle
        draw.rectangle(
            [(0, zone_top), (self.WIDTH, self.HEIGHT)],
            fill="#FF6900",
        )

        # CTA text in PermanentMarker, centered
        cta_font = self.get_font("decorative", 48)
        cta_text_upper = cta_text.upper()
        text_width = cta_font.getlength(cta_text_upper)
        text_height = cta_font.getbbox("Ag")[3]
        text_x = (self.WIDTH - text_width) / 2
        text_y = zone_top + (self.CTA_ZONE_HEIGHT - text_height) / 2 - 10

        draw.text((text_x, text_y), cta_text_upper, fill="#FFFFFF", font=cta_font)

        # Small white PUM logo in bottom-right of CTA zone
        logo = self.logo_white.copy()
        logo_width = 80
        aspect = logo.height / logo.width
        logo_h = int(logo_width * aspect)
        logo = logo.resize((logo_width, logo_h), Image.LANCZOS)
        logo_x = self.WIDTH - logo_width - 30
        logo_y = self.HEIGHT - logo_h - 20
        img.paste(logo, (logo_x, logo_y), logo)

        return img

    # ── Legacy Methods (kept for backward compatibility) ────────────────

    def _is_dark_color(self, hex_color):
        """Check if a hex color is dark based on perceived brightness.

        Args:
            hex_color: Hex color string (e.g., "#0E5555").

        Returns:
            True if the color is dark (brightness < 128).
        """
        rgb = ImageColor.getrgb(hex_color)
        brightness = int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
        return brightness < 128

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
        """Add a KrabbelBabbel decoration overlay at specified opacity.

        Args:
            img: PIL Image to add decoration to.
            deco_index: Index into self.decorations list (0, 1, or 2).
            position: (x, y) tuple for placement.
            size: Target width in pixels (height scales proportionally).
            opacity: Opacity multiplier (0.0 to 1.0).

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

    def render(self, data, photo=None):
        """Render a template with the given data. Must be overridden by subclasses.

        Args:
            data: Dictionary of content data for the template.
            photo: Optional PIL Image for the photo zone.

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
