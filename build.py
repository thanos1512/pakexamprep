#!/usr/bin/env python3
"""Builds the PakExamPrep static site.

Source pages live in src/pages/<path>.html. Each starts with a JSON meta
block inside an HTML comment:

    <!--meta {"title": "...", "description": "...", "path": "/geography/"} -->

MCQ sets live in src/data/<name>.json and are placed in a page with
{{mcqs:<name>}}. Output goes to site/, which Vercel serves as-is.

Run:  python3 build.py
"""
import html
import json
import re
import shutil
from pathlib import Path

BASE_URL = "https://pakexamprep.mujtabashafiq56.workers.dev"
SITE_NAME = "PakExamPrep"
ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "site"

NAV = [
    ("Geography", "/geography/"),
    ("General Knowledge", "/gk/"),
    ("Current Affairs", "/current-affairs/"),
    ("Geopolitics", "/geopolitics/"),
    ("Exam Guides", "/exams/"),
]

META_RE = re.compile(r"^<!--meta\s+(\{.*?\})\s*-->\s*", re.S)
MCQ_RE = re.compile(r"\{\{mcqs:([a-z0-9-]+)\}\}")
LETTERS = "ABCD"


def esc(s):
    return html.escape(s, quote=True)


def render_mcqs(name):
    data = json.loads((SRC / "data" / f"{name}.json").read_text(encoding="utf-8"))
    qs = data["questions"]
    items = []
    for i, q in enumerate(qs, 1):
        answer = q["answer"].lower()
        opts = []
        for j, opt in enumerate(q["options"]):
            letter = LETTERS[j]
            opts.append(
                f'<button class="opt" type="button" data-opt="{letter.lower()}">'
                f'<span class="bubble" aria-hidden="true">{letter}</span>'
                f'<span class="opt-t">{esc(opt)}</span></button>'
            )
        correct_text = q["options"][LETTERS.index(answer.upper())]
        items.append(
            f'<li class="mcq" id="q{i}" data-answer="{answer}">'
            f'<p class="mcq-q"><span class="mcq-n">{i}.</span> {esc(q["q"])}</p>'
            f'<div class="opts" role="group" aria-label="Options for question {i}">{"".join(opts)}</div>'
            f'<div class="explain"><p><strong>Answer: {answer.upper()}) {esc(correct_text)}.</strong> '
            f'{esc(q["why"])}</p></div></li>'
        )
    total = len(qs)
    return (
        f'<section class="mcq-set" aria-labelledby="mcq-h" data-total="{total}">'
        f'<div class="sheet-head"><h2 id="mcq-h">{esc(data["heading"])}</h2>'
        f'<p class="sheet-note">Tap a bubble to answer. You will see the right answer and why straight away.</p></div>'
        f'<div class="score-bar" role="status" aria-live="polite">'
        f'<span class="score">Score <b data-score>0</b> of {total}</span>'
        f'<span class="answered" data-answered>0 answered</span>'
        f'<span class="score-actions"><button type="button" class="btn-quiet" data-reveal>Show all answers</button>'
        f'<button type="button" class="btn-quiet" data-reset>Start again</button></span></div>'
        f'<ol class="mcqs">{"".join(items)}</ol></section>'
    )


def breadcrumb_html(crumbs):
    if not crumbs:
        return ""
    parts = []
    for name, path in crumbs[:-1]:
        parts.append(f'<li><a href="{path}">{esc(name)}</a></li>')
    parts.append(f'<li aria-current="page">{esc(crumbs[-1][0])}</li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(parts)}</ol></nav>'


def jsonld(meta, crumbs):
    blocks = []
    url = BASE_URL + meta["path"]
    if meta["path"] == "/":
        blocks.append({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": SITE_NAME,
            "url": BASE_URL + "/",
            "description": meta["description"],
            "inLanguage": "en-PK",
        })
    if crumbs:
        blocks.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": n, "item": BASE_URL + p}
                for i, (n, p) in enumerate(crumbs, 1)
            ],
        })
    if meta.get("type") == "article":
        blocks.append({
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": meta["h1"],
            "description": meta["description"],
            "dateModified": meta["updated"],
            "datePublished": meta.get("published", meta["updated"]),
            "author": {"@type": "Organization", "name": SITE_NAME, "url": BASE_URL + "/about/"},
            "publisher": {"@type": "Organization", "name": SITE_NAME, "url": BASE_URL + "/"},
            "mainEntityOfPage": url,
            "inLanguage": "en-PK",
        })
    return "".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>'
        for b in blocks
    )


def nav_html(path):
    links = []
    for name, href in NAV:
        cur = ' aria-current="page"' if path.startswith(href) else ""
        links.append(f'<li><a href="{href}"{cur}>{name}</a></li>')
    return "".join(links)


def page(meta, body):
    tpl = (SRC / "layout.html").read_text(encoding="utf-8")
    crumbs = [tuple(c) for c in meta.get("crumbs", [])]
    canonical = BASE_URL + meta["path"]
    title = meta["title"] if meta["path"] == "/" else f'{meta["title"]} | {SITE_NAME}'
    robots = '<meta name="robots" content="noindex">' if meta.get("noindex") else ""
    repl = {
        "{{title}}": esc(title),
        "{{description}}": esc(meta["description"]),
        "{{canonical}}": canonical,
        "{{robots}}": robots,
        "{{og_type}}": "article" if meta.get("type") == "article" else "website",
        "{{nav}}": nav_html(meta["path"]),
        "{{crumbs}}": breadcrumb_html(crumbs),
        "{{jsonld}}": jsonld(meta, crumbs),
        "{{body}}": body,
        "{{year}}": "2026",
        "{{page_class}}": meta.get("type", "page"),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)
    return tpl


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "static", OUT)
    sitemap = []
    for f in sorted((SRC / "pages").rglob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = META_RE.match(raw)
        if not m:
            raise SystemExit(f"Missing meta block in {f}")
        meta = json.loads(m.group(1))
        body = MCQ_RE.sub(lambda mm: render_mcqs(mm.group(1)), raw[m.end():])
        out_html = page(meta, body)
        if meta["path"] == "/404/":
            dest = OUT / "404.html"
        else:
            dest = OUT / meta["path"].strip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out_html, encoding="utf-8")
        if meta.get("sitemap", True) and not meta.get("noindex"):
            sitemap.append((meta["path"], meta.get("updated", "2026-11-05")))
    urls = "".join(
        f"<url><loc>{BASE_URL}{p}</loc><lastmod>{d}</lastmod></url>" for p, d in sitemap
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8"
    )
    print(f"Built {len(sitemap)} indexed pages into {OUT}")


if __name__ == "__main__":
    build()
