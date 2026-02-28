# Phase 1: Foundation & Brand Setup - Context

**Gathered:** 2026-02-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Project has clean structure, all dependencies defined, brand config loaded, and PUM assets (logo, fonts, colors, icons) ready to use in code. No template rendering or content generation — just the foundation that all downstream phases build on.

</domain>

<decisions>
## Implementation Decisions

### Brand color palette
- Primary colors: `#D2E8D7` (mint green), `#0E5555` (dark green/donkergroen), `#FF6900` (orange)
- Secondary colors: `#659BD1` (blue), `#D69A5F` (warm brown), `#E9C779` (soft gold), `#F8E3B3` (light beige)
- Colors extracted from PUM's Canva Premium brand kit (authoritative source)
- Background-to-accent color combinations per template type: Claude's discretion

### Typography
- Headings: Noto Sans Bold (Google Font, free TTF)
- Body text: Noto Sans Regular
- Call-to-action / decorative: Permanent Marker (Google Font, hand-drawn style matching PUM's KrabbelBabbel illustrations)
- Standard Latin character support is sufficient for Bahasa Indonesia
- Font TTF files to be downloaded and stored in `assets/fonts/`

### Logo & icon assets
- Default watermark: dark green `PUM.` logo (`PUM_logo-donkergroen-rgb.png`)
- White logo with slogan available as secondary variant (`PUM_logo-slogan-alternatief-wit-rgb_1.png`)
- All sector icons included (20+ circular dark green icons with mint fill)
- Priority sectors for Indonesia content: Agriculture & Horticulture, Food & Hospitality, Manufacturing & Energy, Services & Education
- All sectors from pum.nl/sectors are valid content topics
- KrabbelBabbel scribble illustrations (orange + green variants) available for decoration
- 5 SVG social media frame templates at 1080x1350 available as reference

### Brand config scope
- `brand_config.yaml` contains: color palettes, font paths, logo path, slogan ("Together we grow" — English only), sector icon paths, asset directory paths
- No social media handles or hashtags in config (AI generates per-post)
- No content pillars in brand config (Claude decides appropriate location)
- No tone/voice guidelines in brand config

### Claude's Discretion
- Which background-accent color combos work best per template type
- Whether KrabbelBabbel scribbles enhance specific templates
- Where to define content pillars (brand config vs separate content config)
- Project directory structure and file organization
- Python dependency choices
- Test script design for asset verification

</decisions>

<specifics>
## Specific Ideas

- All brand assets originate from PUM's Canva Premium brand kit — source of truth for colors and visual identity
- Physical asset files are located at `/Users/anitawulandari/Downloads/PUM Brand Kit/` (to be copied into project `assets/` directory)
- PUM's website (pum.nl) uses NotoSans and PermanentMarker fonts — confirmed match with brand kit typography
- Slogan is "Together we grow" — visible on the white logo variant with orange scribble underline
- Sector icons are simple circular designs: dark green (#0E5555) background with mint (#D2E8D7) symbol inside

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation-brand-setup*
*Context gathered: 2026-02-28*
