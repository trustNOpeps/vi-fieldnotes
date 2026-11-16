import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "studio"))
import pipeline

CONFIG = pipeline.load(ROOT / "studio/config.json")
STORIES = pipeline.load(ROOT / "studio/stories.json")["stories"]


class StudioTests(unittest.TestCase):
    def test_all_curated_stories_valid_as_of_launch_week(self):
        for story in STORIES:
            with self.subTest(story=story["id"]):
                self.assertEqual(pipeline.validate_story(story, CONFIG, date(2026, 11, 16)), [])

    def test_source_verification_expires(self):
        self.assertTrue(any("expired" in s.lower() for s in pipeline.validate_story(STORIES[0], CONFIG, date(2026, 11, 25))))

    def test_disallow_unapproved_sources_and_rights(self):
        item = json.loads(json.dumps(STORIES[0]))
        item["source_urls"] = ["https://random-host.invalid/rumor"]
        item["rights"]["visuals"] = "unknown"
        errors = pipeline.validate_story(item, CONFIG, date(2026, 11, 16))
        self.assertTrue(any("host" in s.lower() for s in errors))
        self.assertTrue(any("rights" in s.lower() for s in errors))

    def test_draft_bundle_and_no_publishing(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "draft"
            payload = pipeline.build(STORIES[0], out, CONFIG, date(2026, 11, 16))
            self.assertFalse(payload["publish_allowed"])
            self.assertFalse(payload["manual_editorial_approval"])
            self.assertTrue((out / "voice_script.txt").exists())
            self.assertTrue((out / "caption_en.txt").exists())
            self.assertTrue((out / "storyboard.html").exists())
            self.assertIn("00:00:00,000", (out / "subtitles.srt").read_text())
            self.assertIn("NEEDS_HUMAN_REVIEW", (out / "STATUS.md").read_text())

    def test_deterministic_schedule_never_repeats_unscheduled_content(self):
        with tempfile.TemporaryDirectory() as d:
            cmd = [sys.executable, str(ROOT / "studio/pipeline.py"), "build", "--date", "2026-11-23", "--output", d]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((Path(d) / "scheduled_status.json").read_text())["publication"], "DISABLED")
            self.assertFalse((Path(d) / "voice_script.txt").exists())

    def test_discovery_offline_never_makes_claim(self):
        with tempfile.TemporaryDirectory() as d:
            leads = pipeline.discover(CONFIG, Path(d), offline=True)
            self.assertEqual(len(leads), 3)
            self.assertTrue(all(x["claim_status"] == "UNVERIFIED_RESEARCH_LEAD" for x in leads))
            self.assertTrue(all(x["status"] == "SKIPPED_OFFLINE" for x in leads))

    def test_srt_time(self):
        self.assertEqual(pipeline.fmt_srt_time(65.125), "00:01:05,125")

    def test_preview_and_release_gate(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            pipeline.build(STORIES[0], out, CONFIG, date(2026, 11, 16))
            release = subprocess.run([sys.executable, str(ROOT / "studio/render.py"), "--input", str(out),
                                      "--mode", "release", "--width", "360", "--height", "640"],
                                     capture_output=True, text=True)
            self.assertNotEqual(release.returncode, 0)
            self.assertIn("Release requires", release.stderr)


if __name__ == "__main__":
    unittest.main()
