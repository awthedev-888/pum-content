"""TipsListTemplate - branded Instagram tips/list post template.

Renders numbered actionable advice (e.g., "5 Tips Ekspor untuk UMKM") with
a title, 3-5 numbered items with circled number badges, optional sector icon,
gradient background with diagonal line texture, and PUM logo watermark.

Output: 1080x1080 RGBA PNG suitable for Instagram square posts.

Usage:
    from templates.tips_list import TipsListTemplate

    tl = TipsListTemplate()
    img = tl.render({
        "title": "5 Tips Ekspor untuk UMKM",
        "items": [
            "Pahami regulasi ekspor negara tujuan",
            "Siapkan sertifikasi produk yang diperlukan",
            "Manfaatkan program pendampingan PUM",
        ],
        "sector": "manufacturing",  # optional
    })
    tl.save(img, "output/tips_list.png")
"""

import random

from PIL import Image, ImageColor, ImageDraw

from templates.base import BaseTemplate


class TipsListTemplate(BaseTemplate):
    """Tips/List template for numbered actionable advice Instagram posts.

    Renders a title in heading font followed by 3-5 numbered items with
    orange circled number badges. Each item's text is word-wrapped beside
    its badge. Includes gradient background, diagonal line texture,
    KrabbelBabbel decoration, optional sector icon, and PUM logo watermark.
    """

    # Badge dimensions
    BADGE_DIAMETER = 40
    BADGE_COLOR = "#FF6900"  # PUM orange

    # Item layout
    ITEM_TEXT_OFFSET = 60  # Horizontal offset for text (badge width + gap)
    ITEM_SPACING = 30  # Vertical gap between items
    MIN_ITEM_SPACING = 15  # Minimum spacing for adaptive sizing
    MIN_BODY_FONT_SIZE = 20  # Floor for adaptive font reduction

    # Vertical layout zones for tips
    TITLE_Y = 100
    ITEMS_START_Y = 200
    ITEMS_END_Y = 900  # Bottom boundary before footer

    def render(self, data):
        """Render a tips/list post with numbered items.

        Args:
            data: Dictionary with keys:
                - title (str): Post title, e.g. "5 Tips Ekspor untuk UMKM"
                - items (list[str]): 3-5 tip strings
                - sector (str | None): Optional sector key for icon

        Returns:
            PIL Image (1080x1080 RGBA) with rendered tips/list post.
        """
        # 1. Background: gradient + diagonal line texture
        img = self.create_canvas()
        color1, color2 = self.random_gradient()
        img = self.draw_gradient(img, color1, color2)
        img = self.add_diagonal_lines(img)

        draw = ImageDraw.Draw(img)

        # Determine text color based on background brightness at title area
        # Sample the top-left area color to decide contrast
        bg_brightness = self._get_background_brightness(color1)
        text_color = "white" if bg_brightness < 128 else self.get_color("primary", "dark_green")
        badge_text_color = "white"

        # 2. Title
        title_font = self.get_font("heading", 44)
        title_lines = self.wrap_text(data["title"], title_font, self.CONTENT_WIDTH)
        title_y = self.TITLE_Y
        for line in title_lines:
            draw.text((self.MARGIN, title_y), line, font=title_font, fill=text_color)
            line_height = title_font.getbbox("Ag")[3]
            title_y += line_height + 5

        # 3. Numbered items with adaptive sizing
        items = data.get("items", [])
        body_font_size = 26
        item_spacing = self.ITEM_SPACING
        available_height = self.ITEMS_END_Y - self.ITEMS_START_Y

        # Adaptive sizing: reduce font and spacing if items don't fit
        while body_font_size >= self.MIN_BODY_FONT_SIZE:
            body_font = self.get_font("body", body_font_size)
            total_height = self._calculate_items_height(
                items, body_font, item_spacing
            )
            if total_height <= available_height:
                break
            body_font_size -= 2
            item_spacing = max(self.MIN_ITEM_SPACING, item_spacing - 5)
        else:
            # If we exited the while without breaking, use minimum sizes
            body_font = self.get_font("body", self.MIN_BODY_FONT_SIZE)
            item_spacing = self.MIN_ITEM_SPACING

        # Draw numbered items
        num_font = self.get_font("heading", 22)
        current_y = self.ITEMS_START_Y
        content_width_for_text = self.CONTENT_WIDTH - self.ITEM_TEXT_OFFSET

        for i, item_text in enumerate(items, start=1):
            # a. Number badge: orange filled circle
            badge_x = self.MARGIN
            badge_y = current_y
            draw.ellipse(
                [
                    (badge_x, badge_y),
                    (badge_x + self.BADGE_DIAMETER, badge_y + self.BADGE_DIAMETER),
                ],
                fill=self.BADGE_COLOR,
            )
            # Center number in badge
            badge_center_x = badge_x + self.BADGE_DIAMETER // 2
            badge_center_y = badge_y + self.BADGE_DIAMETER // 2
            draw.text(
                (badge_center_x, badge_center_y),
                str(i),
                font=num_font,
                fill=badge_text_color,
                anchor="mm",
            )

            # b. Item text: wrapped beside badge
            text_x = self.MARGIN + self.ITEM_TEXT_OFFSET
            wrapped_lines = self.wrap_text(item_text, body_font, content_width_for_text)

            # Vertically align first line with badge center
            line_height = body_font.getbbox("Ag")[3]
            text_start_y = badge_y + (self.BADGE_DIAMETER - line_height) // 2

            for line in wrapped_lines:
                draw.text(
                    (text_x, text_start_y),
                    line,
                    font=body_font,
                    fill=text_color,
                )
                text_start_y += line_height + 4  # slight line spacing

            # c. Advance current_y by item height + spacing
            item_total_height = max(
                self.BADGE_DIAMETER,
                len(wrapped_lines) * (line_height + 4) - 4,
            )
            current_y += item_total_height + item_spacing

        # 4. Sector icon (optional)
        sector = data.get("sector")
        if sector:
            self._draw_sector_icon(img, sector)

        # 5. KrabbelBabbel decoration at reduced opacity in top-right corner
        deco_index = random.randint(0, len(self.decorations) - 1)
        img = self.add_decoration(
            img,
            deco_index=deco_index,
            position=(self.WIDTH - 250, 10),
            size=200,
            opacity=0.15,
        )

        # 6. Watermark: PUM logo bottom-right
        # Use white logo on dark backgrounds, primary on light
        use_white = bg_brightness < 128
        img = self.add_watermark(img, use_white=use_white)

        return img

    def _get_background_brightness(self, hex_color):
        """Calculate perceived brightness of a hex color (0-255).

        Uses the standard luminance formula for perceived brightness.

        Args:
            hex_color: Hex color string (e.g., "#0E5555").

        Returns:
            Integer brightness value (0=black, 255=white).
        """
        rgb = ImageColor.getrgb(hex_color)
        # Standard perceived brightness formula
        return int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])

    def _calculate_items_height(self, items, body_font, item_spacing):
        """Calculate total height needed for all numbered items.

        Args:
            items: List of item text strings.
            body_font: PIL ImageFont for body text.
            item_spacing: Vertical gap between items in pixels.

        Returns:
            Total height in pixels.
        """
        content_width_for_text = self.CONTENT_WIDTH - self.ITEM_TEXT_OFFSET
        line_height = body_font.getbbox("Ag")[3]
        total = 0

        for item_text in items:
            wrapped = self.wrap_text(item_text, body_font, content_width_for_text)
            item_height = max(
                self.BADGE_DIAMETER,
                len(wrapped) * (line_height + 4) - 4,
            )
            total += item_height + item_spacing

        # Remove last spacing (no gap after last item)
        if items:
            total -= item_spacing

        return total

    def _draw_sector_icon(self, img, sector_key):
        """Draw optional sector icon in bottom-left area.

        Loads the sector icon from brand config, resizes to 60x60,
        and places it in the bottom-left with padding.

        Args:
            img: PIL Image to draw on.
            sector_key: Sector key string matching brand_config.yaml icons.sectors.
        """
        icons_config = self.config.get("icons", {})
        sectors = icons_config.get("sectors", {})
        icon_filename = sectors.get(sector_key)

        if not icon_filename:
            return

        icon_dir = self.project_root / icons_config.get("directory", "assets/icons/")
        icon_path = icon_dir / icon_filename

        if not icon_path.exists():
            return

        icon = Image.open(str(icon_path)).convert("RGBA")

        # Resize to 60x60 maintaining aspect ratio
        icon_size = 60
        aspect = icon.height / icon.width
        new_height = int(icon_size * aspect)
        icon = icon.resize((icon_size, new_height), Image.LANCZOS)

        # Position: bottom-left with padding
        icon_x = self.MARGIN
        icon_y = self.HEIGHT - new_height - self.WATERMARK_PADDING
        img.paste(icon, (icon_x, icon_y), icon)
