"""ImpactStatsTemplate - branded Instagram image for impact statistics.

Renders 1080x1080 RGBA PNG images with large, eye-catching stat numbers in
orange accent color, context labels below each number, a title, gradient
background with dot pattern, KrabbelBabbel decoration, and PUM logo watermark.
Supports 1-3 stats with adaptive font sizing and even vertical spacing.

Usage:
    from templates.impact_stats import ImpactStatsTemplate

    ist = ImpactStatsTemplate()
    img = ist.render({
        "title": "Dampak PUM di Indonesia",
        "stats": [
            {"number": "1.200+", "label": "ahli sukarelawan"},
            {"number": "30+", "label": "negara aktif"},
            {"number": "45+", "label": "tahun pengalaman"},
        ],
    })
    ist.save(img, "output/impact_stats.png")
"""

import random

from PIL import Image, ImageColor, ImageDraw

from templates.base import BaseTemplate


class ImpactStatsTemplate(BaseTemplate):
    """Template for impact statistics Instagram posts.

    Renders large orange numbers as the dominant visual element, with
    context labels below each stat and a title in heading font. Adapts
    layout for 1-3 stats with appropriate font sizes and spacing.
    """

    # Layout constants
    TITLE_Y = 100
    STATS_TOP = 220
    STATS_BOTTOM = 880

    # Number font sizes by stat count
    NUMBER_FONT_SIZES = {
        1: 96,
        2: 80,
        3: 72,
    }

    # Label font size
    LABEL_FONT_SIZE = 28
    LABEL_GAP = 15  # Gap between number and label

    # Divider between stats
    DIVIDER_WIDTH = 100
    DIVIDER_COLOR = "#E9C779"  # soft_gold
    DIVIDER_OPACITY = 80  # Alpha value (0-255)

    # Decoration
    DECORATION_SIZE = 200
    DECORATION_OPACITY = 0.15

    def _get_background_brightness(self, hex_color):
        """Calculate perceived brightness of a hex color (0-255).

        Uses the standard luminance formula for perceived brightness.

        Args:
            hex_color: Hex color string (e.g., "#0E5555").

        Returns:
            Integer brightness value (0=black, 255=white).
        """
        rgb = ImageColor.getrgb(hex_color)
        return int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])

    def render(self, data):
        """Render an Impact Stats template with large numbers and labels.

        Args:
            data: Dictionary with keys:
                - title (str): Headline text (e.g., "Dampak PUM di Indonesia").
                - stats (list[dict]): 1-3 stat dicts, each with:
                    - number (str): Display number (e.g., "1.200+").
                    - label (str): Context label (e.g., "ahli sukarelawan").

        Returns:
            PIL Image in RGBA mode, 1080x1080.
        """
        title = data.get("title", "")
        stats = data.get("stats", [])

        # 1. Background: gradient + subtle dot pattern
        img = self.create_canvas()
        color1, color2 = self.random_gradient()
        img = self.draw_gradient(img, color1, color2)
        img = self.add_dot_pattern(img, color_rgba=(255, 255, 255, 20))

        draw = ImageDraw.Draw(img)

        # Determine text colors based on background brightness
        brightness = self._get_background_brightness(color1)
        is_dark = brightness < 128
        title_color = "#FFFFFF" if is_dark else "#0E5555"
        label_color = "#FFFFFF" if is_dark else "#F8E3B3"
        number_color = "#FF6900"  # Always orange - visual anchor
        use_white_logo = is_dark

        # 2. Title: heading font, centered horizontally
        title_font = self.get_font("heading", 44)
        title_lines = self.wrap_text(title, title_font, self.CONTENT_WIDTH)
        title_y = self.TITLE_Y
        center_x = self.WIDTH // 2

        for line in title_lines:
            draw.text(
                (center_x, title_y),
                line,
                font=title_font,
                fill=title_color,
                anchor="mt",
            )
            line_height = title_font.getbbox("Ag")[3]
            title_y += line_height + 6

        # 3. Stats section: evenly spaced in vertical range
        stat_count = len(stats)
        if stat_count == 0:
            # No stats, just return with title and background
            img = self.add_watermark(img, use_white=use_white_logo)
            return img

        # Clamp to valid range
        stat_count = min(stat_count, 3)

        number_font_size = self.NUMBER_FONT_SIZES.get(stat_count, 72)
        number_font = self.get_font("heading", number_font_size)
        label_font = self.get_font("body", self.LABEL_FONT_SIZE)

        available_height = self.STATS_BOTTOM - self.STATS_TOP
        slot_height = available_height // stat_count

        for i, stat in enumerate(stats[:3]):
            slot_top = self.STATS_TOP + i * slot_height
            slot_center_y = slot_top + slot_height // 2

            # Get text measurements
            number_text = stat.get("number", "")
            label_text = stat.get("label", "")

            number_bbox_height = number_font.getbbox("Ag")[3]
            label_bbox_height = label_font.getbbox("Ag")[3]

            # Total block height: number + gap + label
            block_height = number_bbox_height + self.LABEL_GAP + label_bbox_height

            # Center the block vertically within the slot
            block_top = slot_center_y - block_height // 2

            # a. Draw number: large, orange, centered
            number_y = block_top
            draw.text(
                (center_x, number_y),
                number_text,
                font=number_font,
                fill=number_color,
                anchor="mt",
            )

            # b. Draw label: below number, centered
            label_y = number_y + number_bbox_height + self.LABEL_GAP
            draw.text(
                (center_x, label_y),
                label_text,
                font=label_font,
                fill=label_color,
                anchor="mt",
            )

            # c. Divider line between stats (not after the last one)
            if i < stat_count - 1:
                divider_y = slot_top + slot_height
                divider_half = self.DIVIDER_WIDTH // 2
                # Draw on overlay for opacity control
                overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                divider_rgb = ImageColor.getrgb(self.DIVIDER_COLOR)
                overlay_draw.line(
                    [
                        (center_x - divider_half, divider_y),
                        (center_x + divider_half, divider_y),
                    ],
                    fill=(*divider_rgb, self.DIVIDER_OPACITY),
                    width=1,
                )
                img = Image.alpha_composite(img, overlay)
                # Re-create draw after alpha_composite (new image object)
                draw = ImageDraw.Draw(img)

        # 5. Decoration: KrabbelBabbel at low opacity in bottom-left area
        deco_index = random.randint(0, len(self.decorations) - 1)
        img = self.add_decoration(
            img,
            deco_index=deco_index,
            position=(0, self.HEIGHT - self.DECORATION_SIZE - self.MARGIN),
            size=self.DECORATION_SIZE,
            opacity=self.DECORATION_OPACITY,
        )

        # 6. Watermark: PUM logo bottom-right
        img = self.add_watermark(img, use_white=use_white_logo)

        return img
