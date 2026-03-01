"""TipsListTemplate - branded Instagram tips/list post template.

Generates 1080x1080 RGBA PNG images using the 3-zone layout:
- Top: solid color headline zone with short headline + KrabbelBabbel mark
- Middle: stock photo (or gradient+icon fallback) with white corner brackets
- Bottom: orange CTA banner with PermanentMarker text + PUM logo

Tips items and detailed text go in the caption only, not on the image.

Usage:
    from templates.tips_list import TipsListTemplate

    tl = TipsListTemplate()
    img = tl.render({
        "headline_short": "Tips Ekspor\\nuntuk UMKM",
        "title": "5 Tips Ekspor untuk UMKM",
        "items": ["Pahami regulasi ekspor...", ...],
        "sector": "manufacturing",
        "cta_text": "SHARING KNOWLEDGE",
    }, photo=pexels_image)
    tl.save(img, "output/tips_list.png")
"""

from templates.base import BaseTemplate


class TipsListTemplate(BaseTemplate):
    """Tips/List template for numbered actionable advice Instagram posts.

    Uses the 3-zone layout: headline / photo / CTA banner.
    Numbered tips items are rendered in the caption, not on the image.
    """

    def render(self, data, photo=None):
        """Render a tips/list post with the 3-zone layout.

        Args:
            data: Dictionary with keys:
                - headline_short (str | None): Very short headline for image.
                - title (str): Full title (fallback if headline_short missing).
                - items (list[str]): Tip strings (caption only, not rendered on image).
                - sector (str | None): Optional sector key for fallback icon.
                - cta_text (str | None): CTA banner text.
            photo: Optional PIL Image for the photo zone.

        Returns:
            PIL Image (1080x1080 RGBA).
        """
        headline = data.get("headline_short") or data.get("title", "")[:30]
        sector = data.get("sector")
        cta_text = data.get("cta_text", "SHARING KNOWLEDGE")

        img = self.create_canvas()
        img, _ = self.draw_headline_zone(img, headline)
        img = self.draw_photo_zone(img, photo=photo, sector=sector)
        img = self.draw_cta_banner(img, cta_text)

        return img
