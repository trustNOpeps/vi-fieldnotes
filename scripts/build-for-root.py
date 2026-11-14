"""Build VI Fieldnotes for root-path hosting (Cloudflare Pages, custom domain).
Set SITE_ORIGIN to exact public origin, e.g. https://project.pages.dev.
This does not modify the source website or its GitHub Pages deployment.
"""
from pathlib import Path
from urllib.parse import urlparse
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ORIGIN = os.getenv("SITE_ORIGIN", "").strip().rstrip("/")
OLD_ORIGIN = "https://trustnopeps.github.io/vi-fieldnotes/"

def main():
    parsed = urlparse(ORIGIN)
    if parsed.scheme != "https" or not parsed.hostname or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise SystemExit("SITE_ORIGIN must be an HTTPS origin without a path, e.g. https://my-site.pages.dev")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    folders = ("about", "faq", "guides", "launch-day", "partner", "platforms", "tools", "assets")
    root_files = ("index.html", "404.html", "style.css", "script.js", "robots.txt", "sitemap.xml", ".nojekyll")
    def write(src, dest):
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.name == ".nojekyll":
            dest.write_bytes(b"")
            return
        contents = src.read_text(encoding="utf-8")
        # Replace full old origin before the shorter path prefix.
        contents = contents.replace(OLD_ORIGIN, ORIGIN + "/")
        contents = contents.replace("/vi-fieldnotes/", "/")
        dest.write_text(contents, encoding="utf-8")
    for name in root_files:
        src = ROOT / name
        if not src.is_file():
            raise SystemExit(f"Missing required site file: {name}")
        write(src, DIST / name)
    for name in folders:
        folder = ROOT / name
        if not folder.is_dir():
            raise SystemExit(f"Missing site folder: {name}")
        for src in folder.rglob("*"):
            if src.is_file():
                write(src, DIST / src.relative_to(ROOT))
    # Source content unchanged. Dist intentionally excludes docs, tests and secrets.
    print(f"Built {sum(p.is_file() for p in DIST.rglob('*'))} site files for {ORIGIN}")
if __name__ == "__main__":
    main()
