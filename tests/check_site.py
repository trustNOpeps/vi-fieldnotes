"""Standard-library static site QA for GitHub Pages. Run: python3 tests/check_site.py."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "/vi-fieldnotes/"
SITE = "https://trustnopeps.github.io"
errors = []

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.assets = []
        self.canonical = []
        self.tags = []
        self.ids = set()
        self.guide_cards = 0
        self.in_title = False
        self.title = ""
        self.in_h1 = False
        self.h1 = ""
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if tag == "title": self.in_title = True
        if tag == "h1": self.in_h1 = True
        if "id" in a: self.ids.add(a["id"])
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag in ("script", "img") and a.get("src"): self.assets.append(a["src"])
        if tag == "link" and a.get("href"):
            if a.get("rel") == "canonical": self.canonical.append(a["href"])
            if a.get("rel") in ("stylesheet", "icon"): self.assets.append(a["href"])
        if tag == "a" and "guidecard" in a.get("class", "").split(): self.guide_cards += 1
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag == "h1": self.in_h1 = False
    def handle_data(self, data):
        if self.in_title: self.title += data
        if self.in_h1: self.h1 += data

def check(msg, ok):
    if not ok: errors.append(msg)

def target_for(url):
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        if parsed.netloc != "trustnopeps.github.io": return None
        path = parsed.path
    else:
        path = parsed.path
    if not path.startswith(PREFIX): return None
    rel = unquote(path[len(PREFIX):])
    return ROOT / (rel + "index.html" if not rel or rel.endswith("/") else rel)

pages = sorted(ROOT.rglob("*.html"))
paths = set()
for page in pages:
    rel = page.relative_to(ROOT).as_posix()
    if rel == "404.html": continue
    path = ("/" + rel[:-len("index.html")]) if rel.endswith("index.html") else "/" + rel
    paths.add(SITE + PREFIX[:-1] + path)

for page in pages:
    rel = page.relative_to(ROOT).as_posix()
    s = page.read_text(encoding="utf-8")
    p = PageParser()
    p.feed(s)
    check(f"{rel}: missing title/H1", bool(p.title.strip() and p.h1.strip()))
    check(f"{rel}: missing HTML lang", bool(re.search(r'<html[^>]+lang="en"', s)))
    check(f"{rel}: missing viewport", 'name="viewport"' in s)
    if rel != "404.html":
        check(f"{rel}: invalid canonical", len(p.canonical) == 1 and p.canonical[0] in paths)
    if re.match(r"^guides/[^/]+/index.html$", rel):
        check(f"{rel}: sources missing", "Primary sources" in s and ('rockstargames.com' in s or 'playstation.com' in s))
        check(f"{rel}: review date missing", "14 Nov 2026" in s)
    if rel == "guides/index.html":
        check("guides index: expected 15 cards", p.guide_cards == 15)
    for url in p.links + p.assets:
        parsed = urlparse(url)
        if url.startswith("#"):
            if url[1:] and url[1:] not in p.ids: errors.append(f"{rel}: broken fragment {url}")
            continue
        if url.lower().startswith("javascript:"): errors.append(f"{rel}: unsafe javascript href")
        destination = target_for(url)
        if destination is not None:
            check(f"{rel}: broken internal link {url}", destination.is_file())

check("expected exactly 15 article pages", len(list((ROOT/"guides").glob("*/index.html"))) == 15)
sitemap = ROOT/"sitemap.xml"
try:
    urls = {el.text for el in ET.parse(sitemap).iter() if el.tag.endswith("loc") and el.text}
    check("sitemap routes mismatch", urls == paths)
except (ET.ParseError, OSError) as e:
    errors.append(f"sitemap invalid: {e}")
script = (ROOT/"script.js").read_text(encoding="utf-8")
check("GA4 measurement ID missing", "G-R2X4W14SCX" in script)
check("consent-first analytics absent", "vi-consent" in script and "enableAnalytics()" in script and "analytics-consent" in script)
check("storage calculator not wired", "vi-storage-check" in script and "vi-storage-result" in script)
check("source archive missing", (ROOT/"docs"/"launch-playbook.md").is_file())

if errors:
    print("\n".join("FAIL: " + x for x in errors))
    print(f"FAIL: {len(errors)} problems")
    sys.exit(1)
print(f"PASS: {len(pages)} HTML documents, {len(paths)} sitemap routes, 15 article pages, internal links and assets, metadata, source notes, privacy, GA4 and utility wiring.")
