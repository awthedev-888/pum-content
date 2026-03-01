"""QuoteStoryTemplate - branded Instagram image for success stories and testimonials.

Generates 1080x1080 RGBA PNG images using the 3-zone layout:
- Top: solid color headline zone with short headline + KrabbelBabbel mark
- Middle: stock photo (or gradient+icon fallback) with white corner brackets
- Bottom: orange CTA banner with PermanentMarker text + PUM logo

Body text, attribution, and story details go in the caption only.

Usage:
    from templates.quote_story import QuoteStoryTemplate

    qt = QuoteStoryTemplate()
    img = qt.render({
        "headline_short": "Kisah Sukses\\nPetani Yogya",
        "headline": "Kisah Sukses PUM Indonesia",
        "body": "Bapak Sutrisno berhasil meningkatkan...",
        "attribution": "--- Bapak Sutrisno, Petani Yogyakarta",
        "sector": "agriculture",
        "cta_text": "READ THE WHOLE STORY",
    }, photo=pexels_image)
    qt.save(img, "output/quote_story.png")
"""

from templates.base import BaseTemplate


class QuoteStoryTemplate(BaseTemplate):
    """Template for success story and testimonial Instagram posts.

    Uses the 3-zone layout: headline / photo / CTA banner.
    Body text and attribution are rendered in the caption, not on the image.
    """

    def render(self, data, photo=None):
        """Render a Quote/Story template with the 3-zone layout.

        Args:
            data: Dictionary with keys:
                - headline_short (str | None): Very short headline for image (2-4 words/line).
                - headline (str): Full headline (fallback if headline_short missing).
                - body (str): Story text (caption only, not rendered on image).
                - attribution (str): Attribution line (caption only).
                - sector (str | None): Optional sector key for fallback icon.
                - cta_text (str | None): CTA banner text.
            photo: Optional PIL Image for the photo zone.

        Returns:
            PIL Image in RGBA mode, 1080x1080.
        """
        headline = data.get("headline_short") or data.get("headline", "")[:30]
        sector = data.get("sector")
        cta_text = data.get("cta_text", "READ THE WHOLE STORY")

        img = self.create_canvas()
        img, _ = self.draw_headline_zone(img, headline)
        img = self.draw_photo_zone(img, photo=photo, sector=sector)
        img = self.draw_cta_banner(img, cta_text)

        return img
