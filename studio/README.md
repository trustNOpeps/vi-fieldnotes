# VI Fieldnotes — Automated Editorial Studio (MVP v1)

**Status: working draft generation and internal preview; NEVER auto-publishes.**  Source code lives in the existing `trustNOpeps/vi-fieldnotes` repository, but does not change the static website or Cloudflare build output.

## Goal

Build an **original, source-backed, global-English, neon-coast gaming editorial workflow**. One daily idea is selected from a date-bound, manually curated queue. It creates a script, a five-scene storyboard, subtitles, social copy and an MP4 preview for human review. It is **not** an auto-reupload bot or a general-purpose unlimited viral-video generator.

## Fast start

Requires Python 3.12+, FFmpeg, FFprobe and Pillow. Install Pillow with `python -m pip install Pillow`.

```bash
python studio/pipeline.py check --date 2026-11-16
python -m unittest discover -s tests -p test_studio.py -v
python studio/pipeline.py discover --offline --output studio_output
python studio/pipeline.py build --story xbox-one-cloud-2026 --date 2026-11-16 --output studio_output
python studio/render.py --input studio_output --mode preview
```

Open `studio_output/storyboard.html` in a browser. Watch `studio_output/internal_DRAFT_preview.mp4`, read the draft script, SRT, caption, primary source URLs, QA JSON, and `STATUS.md`. Default renderer output is 1080 × 1920. Demo in the downloaded handover bundle uses a smaller resolution only for fast test.

To make a calendar draft rather than selecting a story manually, omit `--story` or use `--story auto`. `studio/stories.json` contains **seven different scheduled topics for November 16–22, 2026**. When no safely verified story is scheduled, the bot emits `scheduled_status.json` and deliberately produces **no repeated video**. Add new reviewed stories before future dates.

## Daily GitHub Actions

`editorial-studio.yml` runs at **08:17 WITA (00:17 UTC)** each day, subject to GitHub schedule delays. It first discovers **unverified leads** from publisher/platform pages, then builds and renders an internal preview for the curated date slot, and uploads a private-to-run (access-controlled) review artifact with 14-day retention. If a source is expired or the queue is empty, it does not fabricate or publish content. `workflow_dispatch` also supports running any curated story manually.

To manually run: **GitHub repository → Actions → VI Fieldnotes editorial studio (draft only) → Run workflow**. Download the run artifact when complete. The original live Cloudflare website is unaffected.

## Quality and anti-copy policies

- Research sources: first-party Rockstar / Xbox / PlayStation only, reviewed as of a specific date. `discover` hashes source pages but **does not verify factual claims**, extract footage, or elevate social rumors to facts. Claims are curated in `studio/stories.json` and marked with `reviewed_on`, `review_by`, and exact URLs.
- Viral topic ranking is **editorial priority**, not an invented measurement of views. No Twitch/YouTube copying or automated downloading of streamer material. Do not use game footage, trailers or streamer clips without rights evidence and substantive editorial value.
- Per video: five beats, 16–55 seconds, legible 9:16 visual, original self-created abstract palm/coast art, EN voice script, SRT, sourced caption, and explicit draft status.
- Preview renderer provides an **original synthesized ambient sound bed** but intentionally **no fake/robotic voice**. It watermarks `INTERNAL PREVIEW / VOICE-OVER REQUIRED`. Do not publish it as a finished video.
- For a public release, separately source or record a **high-quality licensed English narration**, add it as `--voice`, and create `editorial_approval.json` only after checking exact source facts, visuals, usage rights, and audio license. `render.py --mode release --voice voice.wav` refuses release without the approval JSON. **Manual review cannot be bypassed by an automated grade or arbitrary CLI flag.** Review and publishing remain the owner's responsibility.
- No automatic YouTube/Instagram/TikTok/X publishing is configured, no platform keys are stored, and no purchases/credits are consumed.

### Human approval format

Save as `studio_output/editorial_approval.json` **only after actually completing the checks**:

```json
{
  "reviewer": "Your reviewer identifier",
  "sources_rechecked": true,
  "rights_checked": true,
  "visual_checked": true,
  "voice_license_checked": true,
  "human_approved": true
}
```

Example final render: `python studio/render.py --input studio_output --mode release --voice /path/to/licensed-voice.wav`. The renderer combines the supplied narration with the original low-volume ambient bed and validates codecs and duration. Check voice timing, audio levels and subtitles manually. The approval JSON should be regenerated per video; no permanent global approval.

## Publishing, cost, and privacy

Default budget **USD 0/day**. GitHub Actions usage is subject to the repository/account quotas, which should be verified by the account owner. Cloudflare Pages deploys only the static website; studio files and temporary outputs are excluded from `scripts/build-for-root.py`.

Manual publication steps: download a reviewed video; use YouTube Studio, Instagram/TikTok native apps and X; verify account authorization, music and voice licensing, privacy settings and captions; paste the description with its source URLs; log real URLs, outcomes and costs in `operations/social-publishing-log.csv`. No view counts or earnings are invented. API publishing can be added only after platform approval, proper scopes, and explicit owner authorization.

`STATUS.md` describes what succeeded, failed, or needs human input. After each batch, measure real first-three-second retention, completion rate, click-throughs, and independent viewer feedback. The screenshot's 'blind A/B picks' are **future experiments**, not a feature falsely claimed as already implemented.

## Boundaries and next iteration

Working: source registry, date-safe editorial queue, lead fingerprints, scripting, subtitles, captions, 5-scene storyboard, preview MP4 with original synth, source/rights gate, test suite, GitHub scheduled draft job, review bundle, no-publish safety.

Not automated: real-time clip ranking or footage acquisition, high-quality neural voice generation (requires a legally usable source/service), independent human critic or verified blind A/B, rights clearance, platform posting APIs, real analytics collection. **Do not assume monetization approval.** After the 7-day test, add only features justified by retention and publishing results.

Primary links: https://www.rockstargames.com/VI, https://news.xbox.com/en-us/2026/11/10/grand-theft-auto-6-comes-to-xbox-cloud-gaming-november-19/, and YouTube reused-content monetization policy https://support.google.com/youtube/answer/1311392.
