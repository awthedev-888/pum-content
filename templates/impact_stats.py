"""ImpactStatsTemplate - branded Instagram image for impact statistics.

Generates 1080x1080 RGBA PNG images using the 3-zone layout:
- Top: solid color headline zone with short headline + KrabbelBabbel mark
- Middle: stock photo (or gradient+icon fallback) with white corner brackets
- Bottom: orange CTA banner with PermanentMarker text + PUM logo

Stat numbers, labels, and detailed data go in the caption only.

Usage:
    from templates.impact_stats import ImpactStatsTemplate

    ist = ImpactStatsTemplate()
    img = ist.render({
        "headline_short": "Dampak PUM\\ndi Indonesia",
        "title": "Dampak PUM di Indonesia",
        "stats": [
            {"number": "1.200+", "label": "ahli sukarelawan"},
        ],
        "cta_text": "TOGETHER WE GROW",
    }, photo=pexels_image)
    ist.save(img, "output/impact_stats.png")
"""

from templates.base import BaseTemplate


class ImpactStatsTemplate(BaseTemplate):
    """Template for impact statistics Instagram posts.

    Uses the 3-zone layout: headline / photo / CTA banner.
    Stat numbers and labels are rendered in the caption, not on the image.
    """

    def render(self, data, photo=None):
        """Render an Impact Stats template with the 3-zone layout.

        Args:
            data: Dictionary with keys:
                - headline_short (str | None): Very short headline for image.
                - title (str): Full title (fallback if headline_short missing).
                - stats (list[dict]): Stats data (caption only, not rendered on image).
                - cta_text (str | None): CTA banner text.
            photo: Optional PIL Image for the photo zone.

        Returns:
            PIL Image in RGBA mode, 1080x1080.
        """
        headline = data.get("headline_short") or data.get("title", "")[:30]
        sector = data.get("sector")
        cta_text = data.get("cta_text", "TOGETHER WE GROW")

        img = self.create_canvas()
        img, _ = self.draw_headline_zone(img, headline)
        img = self.draw_photo_zone(img, photo=photo, sector=sector)
        img = self.draw_cta_banner(img, cta_text)

        return img
