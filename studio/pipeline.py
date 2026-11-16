#!/usr/bin/env python3
"""VI Fieldnotes editorial studio. No paid APIs, no unattended publishing.

Treat fetched pages as research LEADS, not verified facts. Story facts are curated and
re-reviewed by a human. All outputs are draft until source, rights, and voice QA pass.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.json"
STORIES = HERE / "stories.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, payload: dict | list):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def today(value: str | None = None) -> dt.date:
    return dt.date.fromisoformat(value) if value else dt.datetime.now(dt.timezone.utc).date()


def validate_story(story: dict, config: dict, on: dt.date) -> list[str]:
    errors = []
    mandatory = ("id", "title", "hook", "claims", "source_urls", "beats", "rights", "reviewed_on", "review_by")
    missing = [k for k in mandatory if k not in story]
    if missing:
        return ["Missing story keys: " + ", ".join(missing)]
    try:
        reviewed, expiry = dt.date.fromisoformat(story["reviewed_on"]), dt.date.fromisoformat(story["review_by"])
        if reviewed > on:
            errors.append("Source review date is in the future")
        if expiry < on:
            errors.append("Source verification expired: re-review first-party pages and update review_by")
        if expiry < reviewed:
            errors.append("review_by precedes reviewed_on")
    except (ValueError, TypeError):
        errors.append("Invalid review dates")
    if not story["source_urls"] or not story["claims"]:
        errors.append("Primary URLs and substantive claims are mandatory")
    for url in story["source_urls"]:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in config["allowed_source_hosts"]:
            errors.append(f"Unapproved primary-source host: {url}")
    rights = story["rights"]
    if rights.get("visuals") != "self_created":
        errors.append("Visual rights missing (must be self-created or separately approved with evidence)")
    if rights.get("footage") not in ("none", "self_created"):
        errors.append("Third-party footage requires a separate cleared-rights workflow")
    if len(story["beats"]) != 5:
        errors.append("Portrait editorial format needs exactly five beats")
    for index, beat in enumerate(story["beats"], 1):
        for key in ("title", "subtitle", "voice", "seconds"):
            if not beat.get(key):
                errors.append(f"Beat {index} missing {key}")
        if len(beat.get("voice", "").split()) > config["quality"]["max_words_per_beat"]:
            errors.append(f"Beat {index} too dense")
        if not 3 <= beat.get("seconds", 0) <= 12:
            errors.append(f"Beat {index} invalid timing")
    duration = sum(b.get("seconds", 0) for b in story["beats"])
    if duration < config["quality"]["min_seconds"] or duration > config["quality"]["max_seconds"]:
        errors.append(f"Duration {duration}s outside limits")
    script = " ".join(b.get("voice", "") for b in story["beats"])
    if len(script.split()) > config["quality"]["max_narration_words"]:
        errors.append("Narration too long")
    if re.search(r"(?i)\b(leaked footage|confirmed playable now|secret early access|100% guaranteed)\b", script):
        errors.append("High-risk sensational claim in narration")
    return errors


def fmt_srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, rest = divmod(ms, 3600000)
    m, rest = divmod(rest, 60000)
    s, ms = divmod(rest, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_storyboard(story: dict, out: Path):
    cells = []
    t = 0
    for i, beat in enumerate(story["beats"], 1):
        cells.append(f'''<div class="scene"><div class="sun"></div><div class="city"></div><div class="copy">
          <small>VI / FIELDNOTES &nbsp; · &nbsp; 0{i} / 05</small>
          <h2>{html.escape(beat["title"])}</h2><p>{html.escape(beat["subtitle"])}</p>
          <div class="foot">FACTS BEFORE HYPE<br>vi-fieldnotes.pages.dev</div></div></div>''')
        t += beat["seconds"]
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>VI Fieldnotes — Draft storyboard</title><style>
body{margin:0;background:#0c1028;color:#f8f4ee;font:600 16px system-ui}header{padding:24px;text-align:center}main{display:flex;flex-wrap:wrap;gap:16px;justify-content:center;padding:20px}.scene{position:relative;width:242px;height:430px;overflow:hidden;border-radius:20px;background:linear-gradient(175deg,#10152e 4%,#46215e 38%,#e65b99 62%,#fb9175 82%,#142348 100%);box-shadow:0 14px 38px #0008}.sun{position:absolute;top:32%;left:12%;width:76%;aspect-ratio:1;border-radius:50%;background:linear-gradient(#ff67a3,#ff9c62);box-shadow:0 0 65px #f57ba6}.city{position:absolute;top:48%;width:100%;height:32%;background:repeating-linear-gradient(90deg,#101633 0 11px,#181439 11px 22px,#131932 22px 47px);clip-path:polygon(0 38%,10% 38%,10% 5%,18% 5%,18% 56%,26% 56%,26% 28%,39% 28%,39% 45%,46% 45%,46% 8%,57% 8%,57% 38%,65% 38%,65% 30%,78% 30%,78% 5%,87% 5%,87% 50%,100% 50%,100% 100%,0 100%)}.copy{position:absolute;inset:0;background:linear-gradient(0deg,#10152efa 1%,transparent 80%);padding:24px;display:flex;flex-direction:column;justify-content:flex-end}.copy small{font-size:10px;letter-spacing:2px;color:#38e8e1}.copy h2{font-size:29px;line-height:1.05;margin:15px 0 8px}.copy p{font-size:13px;color:#f8f4ee;margin:0 0 36px}.foot{color:#38e8e1;font-size:10px;letter-spacing:1px;line-height:1.8}footer{text-align:center;padding:22px;color:#a1a5b7;font-size:13px}</style></head><body><header><h1>VI Fieldnotes / Neon Coast Storyboard</h1><p>INTERNAL DRAFT · NOT APPROVED FOR PUBLICATION</p></header><main>''' + "\n".join(cells) + '''</main><footer>Original abstract visuals. Every claim must be rechecked before publication.</footer></body></html>'''
    (out / "storyboard.html").write_text(page, encoding="utf-8")


def build(story: dict, output: Path, config: dict, on: dt.date) -> dict:
    errs = validate_story(story, config, on)
    if errs:
        raise ValueError("Quality gate failed:\n- " + "\n- ".join(errs))
    output.mkdir(parents=True, exist_ok=True)
    total = sum(b["seconds"] for b in story["beats"])
    landing = config["site"].rstrip("/") + "/" + story["landing_path"].lstrip("/")
    landing += "?utm_source=organic&utm_medium=social&utm_campaign=studio_launch&utm_content=" + story["id"]
    script = "\n\n".join(f"SCENE {i:02d} · {b['seconds']}s · {b['title']}\n{b['voice']}" for i, b in enumerate(story["beats"], 1))
    (output / "voice_script.txt").write_text(script + "\n", encoding="utf-8")
    (output / "sources.txt").write_text("MANUALLY RECHECK BEFORE PUBLISHING\n" + "\n".join(story["source_urls"]) + "\n", encoding="utf-8")
    time = 0
    lines = []
    for i, b in enumerate(story["beats"], 1):
        lines.extend([str(i), f"{fmt_srt_time(time)} --> {fmt_srt_time(time + b['seconds'])}", b["voice"], ""])
        time += b["seconds"]
    (output / "subtitles.srt").write_text("\n".join(lines), encoding="utf-8")
    caption = (f"{story['hook']}\n\n" + " ".join(story["claims"]) + f"\n\nRead the source-linked guide: {landing}\n"
               + "Independent, unofficial GTA VI information. Not affiliated with Rockstar Games.\n#GTAVI #GamingNews #VIFIELDNOTES\n")
    (output / "caption_en.txt").write_text(caption, encoding="utf-8")
    write_storyboard(story, output)
    manifest = {"project": config["project"], "story_id": story["id"], "built_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "asof_date": on.isoformat(), "duration_seconds": total, "format": "1080x1920 9:16",
                "reviewed_on": story["reviewed_on"], "review_by": story["review_by"], "sources": story["source_urls"],
                "claims": story["claims"], "rights": story["rights"], "landing_url": landing, "story": story,
                "publish_allowed": False, "voice_status": "missing", "manual_editorial_approval": False,
                "status": "DRAFT_NEEDS_HUMAN_REVIEW", "spend_usd": 0}
    save(output / "manifest.json", manifest)
    save(output / "quality_report.json", {"pass": True, "errors": [], "warnings": [
        "Claims are from a manually curated source ledger, not live fact-checked by the script.",
        "No natural voice-over asset included. Rendered preview is not publication ready.",
        "External clips are never downloaded. Publishing is disabled.",
    ], "planned_critic_rounds": config["quality"]["critic_rounds"], "suggested_human_review": [
        "Open each primary source and re-check all time-sensitive claims.",
        "Watch entire video on a phone; inspect text within safe area and pacing.",
        "Listen with headphones and verify music/voice rights and no clipping.",
        "Ask an independent reviewer to pick the stronger of two hooks; record evidence.",
    ]})
    (output / "STATUS.md").write_text(f"# VI Fieldnotes Studio / {story['id']}\n\n"
         f"- Stage: DRAFT_NEEDS_HUMAN_REVIEW\n- Duration: {total}s\n- Claims reviewed: {story['reviewed_on']}\n"
         f"- Review expires: {story['review_by']}\n- Spend: $0 (pipeline only)\n- Publish: DISABLED\n"
         "- Voice: NOT ATTACHED (do not publish video preview)\n- Source rights: self-created visuals; no third-party footage\n"
         "- Next: add high-quality licensed voice, visually review, verify sources and approve manually\n", encoding="utf-8")
    return manifest


def discover(config: dict, output: Path, offline: bool):
    """Only discovery leads; NEVER turns page text into an asserted claim."""
    leads = []
    urls = ["https://www.rockstargames.com/VI", "https://www.rockstargames.com/newswire",
            "https://news.xbox.com/en-us/2026/11/10/grand-theft-auto-6-comes-to-xbox-cloud-gaming-november-19/"]
    for url in urls:
        record = {"url": url, "source_kind": "primary", "claim_status": "UNVERIFIED_RESEARCH_LEAD"}
        if offline:
            record["status"] = "SKIPPED_OFFLINE"
        else:
            try:
                req = Request(url, headers={"User-Agent": "VIFieldnotesEditorialStudio/1.0 (+independent editorial review)"})
                with urlopen(req, timeout=12) as response:
                    raw = response.read(180000)
                    record.update(status="FETCHED", http_status=response.status, page_sha256=hashlib.sha256(raw).hexdigest(),
                                  bytes_fetched=len(raw))
            except Exception as exc:
                record.update(status="FETCH_FAILED", error=f"{type(exc).__name__}: {str(exc)[:180]}")
        leads.append(record)
    save(output / "discovery_leads.json", {"disclaimer": "Lead discovery only: requires source check and rights review", "leads": leads})
    return leads


def main(argv=None):
    parser = argparse.ArgumentParser(description="VI Fieldnotes studio (no automatic publishing)")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("build", help="Build curated source-backed draft bundle")
    gen.add_argument("--story", default="auto")
    gen.add_argument("--date", help="Editorial as-of YYYY-MM-DD; defaults to UTC today")
    gen.add_argument("--output", default="studio_output")
    disc = sub.add_parser("discover", help="Fetch source fingerprints as unverified leads")
    disc.add_argument("--output", default="studio_output")
    disc.add_argument("--offline", action="store_true")
    check = sub.add_parser("check", help="Validate all source-backed stories without rendering")
    check.add_argument("--date")
    args = parser.parse_args(argv)
    config = load(CONFIG)
    stories = load(STORIES)["stories"]
    if config["publishing"]["enabled"]:
        parser.error("Safety gate: publishing.enabled must remain false in MVP")
    if args.command == "discover":
        leads = discover(config, Path(args.output), args.offline)
        print(f"Saved {len(leads)} discovery leads (none fact-verified)")
        return 0
    if args.command == "check":
        day = today(args.date)
        results = {s["id"]: validate_story(s, config, day) for s in stories}
        for name, errors in results.items():
            print(f"{name}: {'PASS' if not errors else 'NEEDS REVIEW: ' + '; '.join(errors)}")
        return 1 if any(results.values()) else 0
    day = today(args.date)
    available = [s for s in stories if not validate_story(s, config, day)]
    if args.story != "auto":
        matches = [s for s in stories if s["id"] == args.story]
        if not matches:
            parser.error("Unknown story id")
        chosen = matches[0]
    else:
        due = [s for s in available if s.get("scheduled_for") == day.isoformat()]
        if not due:
            output = Path(args.output)
            output.mkdir(parents=True, exist_ok=True)
            save(output / "scheduled_status.json", {"date": day.isoformat(), "status": "NO_SAFE_SCHEDULED_DRAFT", "publication": "DISABLED", "message": "Editorial calendar requires a new reviewed story. Nothing generated."})
            print(f"NO SAFE SCHEDULED STORY for {day}; nothing will be repeated or published")
            return 0
        chosen = max(due, key=lambda s: s.get("priority", 0))
    try:
        manifest = build(chosen, Path(args.output), config, day)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    print(f"DRAFT built: {manifest['story_id']} ({manifest['duration_seconds']}s). Publishing DISABLED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
