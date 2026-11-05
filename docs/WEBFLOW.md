# Pushing /solutions/legal to Webflow

Files
- `fragment.html`  page body only (no nav, footer or closing CTA: those are the site's existing components)
- `../ap/ap.css`   shared primitives, every selector scoped under `.ap` and prefixed `ap-`
- `../bs/bs.css`   workbench, spec chips, use-case and related grids (`bs-*`)
- `lg.css`         legal-specific styles, every selector prefixed `lg-`
- `lg.js`          workbench, clause locator, amendment chain, tabs, GSAP + ScrollTrigger motion (needs GSAP)

Rebuild: `python3 lg_build.py` (writes `lg/fragment.html` and the standalone `legal.html`).

Content sources
- Fields, contract types, clause identification, amendment linking, FAQs, security, retention, pricing and trial: https://www.sensible.so/doc-types/contracts
- SDK usage (`sensibleapi`, `sensible-api`, `extract`, `wait_for`/`waitFor`): https://docs.sensible.so
- The MSA in the workbench mirrors Sensible's public contracts demo. The NDA, SaaS agreement, lease, the three clause-locator agreements and the amendment chain are illustrative.

Same constraints as `/solutions/accounts-payable` and `/doc-types/bank-statements`
- GSAP and ScrollTrigger are not on sensible.so pages; load them from jsDelivr or host them with the other site scripts.
- Add `<script>document.documentElement.classList.add('ap-js')</script>` to the page head to avoid a flash before GSAP runs.
- The fragment is ~110 KB, so it should not go in as a single Code Embed; insert it section by section.
- If GSAP fails to load or the visitor prefers reduced motion, `lg.js` removes the `ap-js` class and every section stays visible and interactive.
