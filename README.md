# PakExamPrep

Free notes and MCQs for Pakistani government job tests (FPSC, AJK PSC): Geography, GK, current affairs and geopolitics.

## How it's built

- `src/pages/` — one HTML file per page, starting with a `<!--meta {...} -->` block (title, description, path, breadcrumbs).
- `src/data/` — MCQ sets as JSON, placed in a page with `{{mcqs:<name>}}`.
- `src/layout.html` — shared header, footer and SEO tags.
- `src/static/` — CSS, JS and icons, copied as-is.
- `build.py` — run `python3 build.py` to regenerate `site/`.

Cloudflare serves the `site/` folder (see `wrangler.jsonc`). Run `python3 build.py` and commit `site/` before pushing; no build step runs on Cloudflare.
