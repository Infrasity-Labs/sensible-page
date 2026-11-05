# Prompt for the agent that makes this page live

Copy everything below the line into the agent.

---

You are deploying a finished static landing page to production. The code is complete; your job is to get it into a new empty Git repository, host it, and prove it works live. Do not redesign, rewrite copy, or "improve" the page.

## What you have

A project folder (unzipped) with this layout:

- `site/` is the deployable directory: `index.html` (redirects to `legal.html`), `legal.html` (CSS and JS inlined, generated), `assets/fonts/` (3 woff2), `assets/logos/` (11 images).
- `build/` is the generator: `python3 build/lg_build.py` (Python 3.9+, stdlib only) regenerates `site/legal.html` and `build/out/fragment.html`.
- `README.md` explains the layout. Read it first.

The page is Sensible's "Contract data extraction for legal teams" solutions page. It loads Google Fonts, GSAP 3.12.5 + ScrollTrigger from jsDelivr, and the Sensible logo from cdn.prod.website-files.com. All other links go to live sensible.so / docs.sensible.so / app.sensible.so URLs.

## Rules

1. `site/legal.html` is generated. Never hand-edit it. Any change goes in `build/lg_build.py` (copy, markup, head tags), `build/css/lg.css`, or `build/js/lg.js`, followed by `python3 build/lg_build.py`. Commit the regenerated output.
2. Do not change page copy, numbers, or claims. Do not remove the "illustrative sample" labels.
3. Do not add a build step to the hosting config. The built `site/` folder is committed; the host just serves it (no build command, publish directory `site`).
4. Never print or commit secrets or tokens.

## Steps

### 1. Verify the project before touching anything
- Run `shasum -a 256 site/legal.html`; it must print `53008bf0a92e84420e44fe591d06a99d404a6aba9e0bd9e68d546ef61b14954d`. Then run `python3 build/lg_build.py` and run the checksum again; it must be unchanged. If either differs, stop and report.
- Serve `site/` locally (`cd site && python3 -m http.server 8000`) and open `http://localhost:8000/legal.html` in a real browser. Confirm: no console errors, no broken images, the three MatterSQ fonts load (Network tab 200), the hero animation plays and reaches "Complete".

### 2. Create the repository
- Ask the user for the GitHub owner/org and repo name if not given. Default name: `sensible-legal-page`. Private unless told otherwise.
- `git init -b main`, commit everything (the folder already has a `.gitignore`), create the remote with the `gh` CLI (`gh repo create <owner>/<name> --private --source . --push`) or the user's preferred tooling.

### 3. Choose the host (ask once if the user has not said)
Pick the first option the user already has access to. All three work with zero build config:
- **Cloudflare Pages**: connect the repo, framework preset None, build command empty, output directory `site`.
- **Vercel**: Root Directory `.`, Framework Other, Build Command empty, Output Directory `site`.
- **Netlify**: Build command empty, Publish directory `site`.
GitHub Pages is acceptable only if you publish the contents of `site/` (for example via a GitHub Actions workflow that uploads `site/` as the Pages artifact); do not move files out of `site/`.

### 4. Clean URL (do this unless the user says no)
The intended production path is `/solutions/legal`. Keep the file at `site/legal.html` (asset paths are relative to the site root) and add a host rewrite, not a copy:
- Netlify / Cloudflare Pages: create `site/_redirects` containing `/solutions/legal  /legal.html  200`
- Vercel: create `vercel.json` at the repo root containing `{ "outputDirectory": "site", "cleanUrls": true, "rewrites": [{ "source": "/solutions/legal", "destination": "/legal.html" }] }`
Verify both `/legal` (or `/legal.html`) and `/solutions/legal` return the page with working fonts and logos. If a rewrite makes relative assets break, switch to root-relative asset URLs by changing the `assets/` prefixes in `build/lg_art.py` / `build/lg_build.py` to `/assets/`, rebuild, and re-verify.

### 5. Production hygiene (needs two answers from the user; ask, do not guess)
- Final public URL/domain. Then add to the `<head>` template in `build/lg_build.py` (inside the `page = f'''...` string): `<link rel="canonical" href="https://<domain>/solutions/legal">`, Open Graph tags (`og:title`, `og:description`, `og:url`, `og:type=website`) reusing the existing `<title>` and meta description text, then rebuild.
- Should the page be indexable yet? If it is not being served from Sensible's own domain, or has not been approved, add `<meta name="robots" content="noindex">` to the same head template and tell the user to remove it at go-live.

### 6. Optional hardening (only if the user asks)
Add Subresource Integrity to the two GSAP `<script>` tags (compute the hashes from the pinned 3.12.5 files; do not change the version) and `crossorigin="anonymous"`.

## Acceptance checks on the LIVE URL (do all, report each)

1. `curl -sI <url>` returns 200 for the page, all 3 fonts, and all 11 logo files (list: compscience.svg, founder-shield.svg, inclined.png, insurance-quantified.svg, ledgebrook.svg, lettuce.svg, limit.png, neptune-flood.svg, obie.svg, sterlingrisk.png, vouch.svg under `/assets/logos/`).
2. In a real browser at 1440x900: zero console errors; zero failed network requests; the stats bar (75M+ / SOC 2 + HIPAA / 95%+ / 14 days) has its bottom edge at the bottom of the viewport on first load; the hero panel shows a contract on the left and "Extracted fields" on the right, fills in field by field, and ends at "Complete".
3. Click the NDA, SaaS agreement and Commercial lease tabs: each replays; the lease ends with an amber "0.62 · REVIEW" row.
4. Scroll: the clause locator cycles through five clause chips and highlights a section in three agreements; the amendment chain shows three records; the fields explorer tabs switch; the FAQ accordions open one at a time.
5. At 390px width: no horizontal scrolling, hero stacks, fields explorer text is not clipped.
6. Every outbound link (nav, footer, CTA buttons, "Related document types") resolves with a non-error status.
7. Confirm the final URL, the commit SHA deployed, and the hosting project name.

## Report back

Give the user: repo URL, live URL (and the `/solutions/legal` URL), host and project name, the commit SHA live, anything you added (rewrite file, canonical/OG/noindex), and any check that failed with the exact error. If a check fails, fix it in the build sources, rebuild, redeploy, and re-run the checks; do not paper over it in `site/legal.html`.
