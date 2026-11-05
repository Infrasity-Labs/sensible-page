# Sensible: Contract data extraction for legal teams

A single static landing page (`/solutions/legal`) in the Sensible design system:
IBM Plex type, magenta accent, GSAP motion. No framework, no bundler, no runtime
dependencies beyond three CDNs (see "External dependencies").

## Layout

```
site/                     <- the deployable folder (publish this directory as-is)
  index.html              redirects to legal.html
  legal.html              the page: CSS and JS are inlined, GENERATED, do not hand-edit
  assets/fonts/           MatterSQ woff2 (3 files, referenced by the inlined CSS)
  assets/logos/           customer logos for the marquee (11 files)

build/                    <- source + generator
  lg_build.py             builds site/legal.html and build/out/fragment.html
  lg_art.py, bs_art.py    inline SVG illustrations and icons
  template/index.html     existing Sensible page, used ONLY as the source of the site nav, footer and base CSS
  css/ap.css, bs.css      shared Sensible page primitives (ap-*, bs-*)
  css/lg.css              legal-page styles (lg-*)
  js/lg.js                interactions + GSAP motion
  out/fragment.html       page body only, scoped under .ap (for the Webflow push)

docs/WEBFLOW.md           notes for pushing the fragment into Webflow instead
```

## Rebuild

```bash
python3 build/lg_build.py     # Python 3.9+, standard library only
```

It rewrites `site/legal.html` and `build/out/fragment.html`. All copy lives in
`build/lg_build.py`; styles in `build/css/lg.css`; behaviour in `build/js/lg.js`.
Edit those, then rebuild. Never edit `site/legal.html` directly.

## Preview locally

```bash
cd site && python3 -m http.server 8000     # http://localhost:8000/legal.html
```

## External dependencies (loaded by the page at runtime)

| What | From |
|---|---|
| IBM Plex Sans / Serif / Mono | fonts.googleapis.com |
| GSAP 3.12.5 + ScrollTrigger | cdn.jsdelivr.net |
| Sensible logo (nav) and footer images | cdn.prod.website-files.com |

If GSAP fails to load, or the visitor prefers reduced motion, the page degrades
to a fully visible, still-interactive version.

## Content provenance

Product facts (fields, contract types, clause identification, amendment linking,
FAQs, security, retention, pricing, trial) come from Sensible's public pages and docs:
https://www.sensible.so/doc-types/contracts and https://docs.sensible.so.
The MSA in the hero mirrors Sensible's public contracts demo. The NDA, SaaS
agreement, commercial lease, the three clause-locator agreements, the amendment
chain and the "example checks" are illustrative and labelled as such on the page.

## Design behaviours worth preserving

- On desktop, hero + stats bar fill exactly one viewport (the bar's bottom edge is the fold).
- The hero extraction animation builds up once, then cycles; hovering a field or a highlighted phrase takes over.
- Short desktop viewports compact the hero (under 820px tall), hide the source strip (under 770px) and the signature block (under 740px).
