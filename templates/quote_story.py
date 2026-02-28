"""QuoteStoryTemplate - branded Instagram image for success stories and testimonials.

Generates 1080x1080 RGBA PNG images with headline, multi-line body text,
attribution line, gradient background, PUM logo watermark, and KrabbelBabbel
decoration overlay. Supports adaptive font sizing for variable-length content.

Usage:
    from templates.quote_story import QuoteStoryTemplate

    qt = QuoteStoryTemplate()
    img = qt.render({
        "headline": "Kisah Sukses PUM Indonesia",
        "body": "Bapak Sutrisno berhasil meningkatkan...",
        "attribution": "--- Bapak Sutrisno, Petani Yogyakarta",
        "sector": "agriculture",  # optional
    })
    qt.save(img, "output/quote_story.png")
"""

import random

from PIL import Image, ImageColor, ImageDraw

from templates.base import BaseTemplate


class QuoteStoryTemplate(BaseTemplate):
    """Template for success story and testimonial Instagram posts.

    Renders headline, multi-line body text, attribution line, and optional
    sector icon on a gradient background with PUM branding elements.
    """

    # Layout constants specific to Quote/Story template
    HEADLINE_Y = 120
    DIVIDER_GAP = 20
    DIVIDER_WIDTH = 200
    DIVIDER_LINE_WIDTH = 3
    BODY_START_GAP = 40
    BODY_LINE_SPACING = 10
    BODY_FONT_SIZE_DEFAULT = 28
    BODY_FONT_SIZE_MIN = 20
    BODY_FONT_SIZE_STEP = 2
    ATTRIBUTION_GAP = 30
    ATTRIBUTION_FONT_SIZE = 22
    HEADLINE_FONT_SIZE = 48
    SECTOR_ICON_SIZE = 60
    DECORATION_SIZE = 200
    DECORATION_OPACITY = 0.15
    # Reserve space at bottom for watermark + decoration + margin
    BOTTOM_RESERVE = 180

    def _is_dark_color(self, hex_color):
        """Check if a hex color is dark based on average RGB brightness.

        Args:
            hex_color: Hex color string (e.g., "#0E5555").

        Returns:
            True if the color is dark (average RGB < 128).
        """
        rgb = ImageColor.getrgb(hex_color)
        return sum(rgb) / 3 < 128

    def render(self, data):
        """Render a Quote/Story template with the given data.

        Args:
            data: Dictionary with keys:
                - headline (str): 1-2 line headline text.
                - body (str): Multi-paragraph body text.
                - attribution (str): Attribution line (e.g., "--- Name, Title").
                - sector (str | None): Optional sector key for icon.

        Returns:
            PIL Image in RGBA mode, 1080x1080.
        """
        headline = data.get("headline", "")
        body = data.get("body", "")
        attribution = data.get("attribution", "")
        sector = data.get("sector")

        # 1. Background: gradient + dot pattern
        img = self.create_canvas()
        color1, color2 = self.random_gradient()
        img = self.draw_gradient(img, color1, color2)
        img = self.add_dot_pattern(img)

        draw = ImageDraw.Draw(img)

        # Determine text color based on top gradient color brightness
        dark_top = self._is_dark_color(color1)
        if dark_top:
            text_color = "#FFFFFF"
            divider_color = "#FF6900"
            attribution_color = "#F8E3B3"
            use_white_logo = True
        else:
            text_color = "#0E5555"
            divider_color = "#FF6900"
            attribution_color = "#E9C779"
            use_white_logo = False

        # 2. Headline
        headline_font = self.get_font("heading", self.HEADLINE_FONT_SIZE)
        headline_lines = self.wrap_text(headline, headline_font, self.CONTENT_WIDTH)
        current_y = self.HEADLINE_Y

        for line in headline_lines:
            draw.text((self.MARGIN, current_y), line, fill=text_color, font=headline_font)
            line_height = headline_font.getbbox("Ag")[3]
            current_y += line_height + 6

        # 3. Divider: horizontal orange line below headline
        divider_y = current_y + self.DIVIDER_GAP
        draw.line(
            [(self.MARGIN, divider_y), (self.MARGIN + self.DIVIDER_WIDTH, divider_y)],
            fill=divider_color,
            width=self.DIVIDER_LINE_WIDTH,
        )

        # 4. Body text with adaptive font sizing
        body_top = divider_y + self.BODY_START_GAP
        # Calculate available height: from body_top to (HEIGHT - BOTTOM_RESERVE - attribution space)
        attribution_font = self.get_font("body", self.ATTRIBUTION_FONT_SIZE)
        attribution_lines = self.wrap_text(attribution, attribution_font, self.CONTENT_WIDTH)
        attribution_height = self.get_text_block_height(
            attribution_lines, attribution_font, self.BODY_LINE_SPACING
        )
        available_body_height = (
            self.HEIGHT
            - self.BOTTOM_RESERVE
            - body_top
            - self.ATTRIBUTION_GAP
            - attribution_height
            - self.ATTRIBUTION_GAP
        )

        # Adaptive sizing: reduce font if body overflows
        body_font_size = self.BODY_FONT_SIZE_DEFAULT
        while body_font_size >= self.BODY_FONT_SIZE_MIN:
            body_font = self.get_font("body", body_font_size)
            body_lines = self.wrap_text(body, body_font, self.CONTENT_WIDTH)
            body_height = self.get_text_block_height(
                body_lines, body_font, self.BODY_LINE_SPACING
            )
            if body_height <= available_body_height:
                break
            body_font_size -= self.BODY_FONT_SIZE_STEP

        # Draw body text
        current_y = body_top
        body_line_height = body_font.getbbox("Ag")[3]
        for line in body_lines:
            draw.text((self.MARGIN, current_y), line, fill=text_color, font=body_font)
            current_y += body_line_height + self.BODY_LINE_SPACING

        # 5. Attribution
        attribution_y = current_y + self.ATTRIBUTION_GAP
        for line in attribution_lines:
            draw.text(
                (self.MARGIN, attribution_y),
                line,
                fill=attribution_color,
                font=attribution_font,
            )
            attr_line_height = attribution_font.getbbox("Ag")[3]
            attribution_y += attr_line_height + self.BODY_LINE_SPACING

        # 6. Sector icon (optional)
        if sector:
            sectors = self.config.get("icons", {}).get("sectors", {})
            if sector in sectors:
                icon_filename = sectors[sector]
                icon_dir = self.project_root / self.config["icons"]["directory"]
                icon_path = icon_dir / icon_filename
                if icon_path.exists():
                    icon = Image.open(str(icon_path)).convert("RGBA")
                    icon = icon.resize(
                        (self.SECTOR_ICON_SIZE, self.SECTOR_ICON_SIZE),
                        Image.LANCZOS,
                    )
                    icon_x = self.MARGIN
                    icon_y = self.HEIGHT - self.MARGIN - self.SECTOR_ICON_SIZE
                    img.paste(icon, (icon_x, icon_y), icon)

        # 7. Decoration: KrabbelBabbel at reduced opacity
        deco_index = random.randint(0, len(self.decorations) - 1)
        # Position in a corner that avoids text: bottom-left or top-right
        deco_positions = [
            (self.WIDTH - self.DECORATION_SIZE - self.MARGIN, 0),  # top-right
            (0, self.HEIGHT - self.DECORATION_SIZE - self.MARGIN),  # bottom-left
        ]
        deco_pos = random.choice(deco_positions)
        img = self.add_decoration(
            img,
            deco_index=deco_index,
            position=deco_pos,
            size=self.DECORATION_SIZE,
            opacity=self.DECORATION_OPACITY,
        )

        # 8. Watermark: PUM logo bottom-right
        img = self.add_watermark(img, use_white=use_white_logo)

        return img
