#!/usr/bin/env python3
"""Original neon-coast video renderer; previews are watermarked and never publish-ready.
Requires Pillow and ffmpeg. A final release requires a licensed, human-approved voice file.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import wave
from array import array
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

THEME = {
    "night": (16, 21, 46), "cyan": (56, 232, 225), "pink": (244, 81, 165),
    "cream": (248, 244, 238), "coral": (255, 141, 122), "ink": (12, 17, 42)
}


def font(px: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, px)
    return ImageFont.load_default()


def fit(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, bold=True):
    size = start
    while size > 15 and draw.textbbox((0, 0), text, font=font(size, bold))[2] > max_width:
        size -= 2
    return font(size, bold)


def gradient(w: int, h: int, variant: int) -> Image.Image:
    im = Image.new("RGB", (w, h))
    pix = im.load()
    anchors = [(0.0, (13, 17, 43)), (0.28, (36 + variant * 2, 22, 75)),
               (0.51, (146, 42 + variant * 2, 117)), (0.67, (242, 99, 124)),
               (0.78, (44, 43, 91)), (1.0, (10, 18, 39))]
    for y in range(h):
        yy = y / max(h - 1, 1)
        for i in range(1, len(anchors)):
            if yy <= anchors[i][0]:
                left, c1 = anchors[i - 1]
                right, c2 = anchors[i]
                f = (yy - left) / (right - left)
                color = tuple(int(c1[k] * (1 - f) + c2[k] * f) for k in range(3))
                break
        for x in range(w):
            pix[x, y] = color
    return im


def city(draw: ImageDraw.ImageDraw, w: int, h: int, scene: int):
    water = int(h * .69)
    sun_y = int(h * (.53 + scene % 2 * .012))
    r = int(w * .31)
    cx = int(w * (.55 if scene % 2 else .43))
    for k in range(16, 0, -1):
        rr = r + k * max(1, w // 90)
        draw.ellipse((cx - rr, sun_y - rr, cx + rr, sun_y + rr), outline=(165 + k * 3, 57, 110), width=1)
    draw.ellipse((cx - r, sun_y - r, cx + r, sun_y + r), fill=(252, 95, 151))
    # Atmospheric city skyline, deliberately original and abstract.
    for i in range(22):
        x0 = int(i * w / 21.0)
        ww = int(w * (.035 + (i * 13 % 6) / 200))
        hh = int(h * (.09 + ((i * 17 + scene * 7) % 11) / 105))
        y0 = water - hh
        shade = (18 + i % 4 * 4, 20, 52 + i % 5 * 3)
        draw.rectangle((x0, y0, min(w, x0 + ww), water), fill=shade)
        for y in range(y0 + 9, water - 5, max(10, int(w*.026))):
            for x in range(x0 + 5, min(w, x0 + ww - 4), max(10, int(w*.022))):
                if ((x + y + scene * 7) // 13) % 3 != 0:
                    draw.rectangle((x, y, x+2, y+5), fill=(38, 193, 211) if i % 2 else (255, 112, 177))
    draw.rectangle((0, water, w, h), fill=(11, 22, 54))
    for j in range(22):
        y = water + int(j*j / 20 * (h - water) / 30)
        if y >= h: break
        a = int(w * (0.1 + (j * 17 % 30) / 100))
        length = int(w * (.3 + ((j * 7) % 10) / 35))
        color = (42, 122, 173) if j % 3 else (193, 58, 132)
        draw.line((a, y, min(w, a + length), y), fill=color, width=max(2, int(w*.003)))
    # Palm tree silhouette framing; no third-party GTA assets.
    for side in (0, 1):
        base_x = int(w * (.07 if side == 0 else .94))
        base_y = int(h * .79)
        tip_x = base_x + int(w * (.07 if side == 0 else -.08))
        tip_y = int(h * (.23 + scene % 3 * .02))
        draw.line((base_x, base_y, tip_x, tip_y), fill=(11, 14, 32), width=max(6, int(w*.022)))
        for k in range(9):
            angle = (k / 8) * math.pi * 1.7 - math.pi*.85
            reach = int(w * (.25 + (k%3) * .03))
            end_x = tip_x + int(math.sin(angle) * reach)
            end_y = tip_y + int(math.cos(angle) * reach * .36)
            draw.line((tip_x, tip_y, end_x, end_y), fill=(10, 13, 30), width=max(3, int(w*.008)))
            draw.line((end_x, end_y, end_x + int((end_x - tip_x)*.16), end_y + int(h*.04)), fill=(10,13,30), width=max(2,int(w*.005)))


def frame(beat: dict, index: int, output: Path, w: int, h: int, preview: bool):
    im = gradient(w, h, index)
    draw = ImageDraw.Draw(im, "RGB")
    city(draw, w, h, index)
    # Solid dark editorial panel for legibility, never the actual game's art.
    margin = int(w*.07)
    top = int(h*.13)
    draw.rounded_rectangle((margin, top, w-margin, int(h*.39)), radius=int(w*.04), fill=(15,19,48), outline=THEME["cyan"], width=max(2,int(w*.003)))
    draw.rectangle((margin + int(w*.045), top + int(h*.04), margin+int(w*.12), top + int(h*.044)), fill=THEME["pink"])
    sm = font(int(w*.026), True)
    draw.text((margin+int(w*.045), top+int(h*.065)), f"VI / FIELDNOTES     {index+1:02}/05", fill=THEME["cyan"], font=sm)
    size = int(w*.079)
    text = beat["title"]
    words = text.split()
    lines = []
    line = ""
    for word in words:
        proposal = f"{line} {word}".strip()
        if draw.textbbox((0,0), proposal, font=font(size,True))[2] > w - 2*margin - int(w*.08) and line:
            lines.append(line);line=word
        else: line=proposal
    if line: lines.append(line)
    while len(lines) > 3 and size > int(w*.055):
        size -= 2
        lines=[];line=""
        for word in words:
            trial=f"{line} {word}".strip()
            if draw.textbbox((0,0),trial,font=font(size,True))[2] > w-2*margin-int(w*.08) and line:
                lines.append(line);line=word
            else:line=trial
        if line:lines.append(line)
    line_height=int(size*1.22)
    for k, txt in enumerate(lines[:3]):
        draw.text((margin+int(w*.045), top+int(h*.115)+k*line_height), txt, font=font(size,True), fill=THEME["cream"])
    subfont=fit(draw,beat["subtitle"],w-2*margin-int(w*.08),int(w*.033),False)
    draw.text((margin+int(w*.045),int(h*.34)),beat["subtitle"],font=subfont,fill=THEME["cyan"])
    draw.rectangle((0,int(h*.826),w,h),fill=(12,17,42))
    draw.line((margin,int(h*.85),w-margin,int(h*.85)),fill=THEME["cyan"],width=max(2,int(w*.002)))
    draw.text((margin,int(h*.872)),"FACTS BEFORE HYPE",font=font(int(w*.035),True),fill=THEME["cream"])
    draw.text((margin,int(h*.905)),"vi-fieldnotes.pages.dev",font=font(int(w*.031)),fill=THEME["cyan"])
    if preview:
        draw.rounded_rectangle((margin,int(h*.958),w-margin,int(h*.982)),radius=6,fill=(11,18,38))
        draw.text((margin+8,int(h*.96)),"INTERNAL PREVIEW / VOICE-OVER REQUIRED",fill=(255,172,152),font=font(int(w*.019),True))
    im.save(output, optimize=True)


def ambient_wav(dest: Path, duration: int, sample_rate=22050):
    """Deterministic original ambient synth; no borrowed melody or samples."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(dest), "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sample_rate)
        # Simple layered chordal pad, around -31 dBFS to leave narration headroom.
        for second in range(duration + 1):
            chunk = array("h")
            for i in range(sample_rate):
                t = second + i/sample_rate
                fade = min(1.0, t / 2, max(0.0, duration - t) / 2)
                pulse = 0.7 + 0.3 * math.sin(2*math.pi*.09*t)
                chord = (math.sin(2*math.pi*110*t) + .55*math.sin(2*math.pi*164.81*t) +
                         .35*math.sin(2*math.pi*220.0*t) + .22*math.sin(2*math.pi*329.63*t))
                chunk.append(int(max(-32767,min(32767, chord * 550 * fade * pulse))))
            wf.writeframes(chunk.tobytes())


def ffprobe(video: Path) -> dict:
    out = subprocess.check_output(["ffprobe","-v","error","-show_entries","stream=codec_type,width,height","-show_entries","format=duration","-of","json",str(video)])
    return json.loads(out)


def main():
    p = argparse.ArgumentParser(description="Render neon coast storyboard (preview is never publish-ready)")
    p.add_argument("--input", required=True, help="Folder created by pipeline build")
    p.add_argument("--mode", choices=["preview", "release"], default="preview")
    p.add_argument("--voice", help="Licensed human/quality-approved voice WAV or MP3 (required for release)")
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    args = p.parse_args()
    folder=Path(args.input).resolve()
    manifest=json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        p.error("ffmpeg/ffprobe not installed")
    if args.width < 180 or args.height < 320 or args.height/args.width < 1.5:
        p.error("Portrait dimensions invalid")
    if args.mode == "release":
        approval=folder/"editorial_approval.json"
        if not args.voice or not Path(args.voice).is_file() or not approval.is_file():
            p.error("Release requires licensed voice, manual source check, and editorial_approval.json")
        decision=json.loads(approval.read_text(encoding="utf-8"))
        required=["sources_rechecked","rights_checked","visual_checked","voice_license_checked","human_approved"]
        if any(decision.get(k) is not True for k in required) or not decision.get("reviewer"):
            p.error("Release blocked: incomplete independent human approval")
        from datetime import datetime
        from zoneinfo import ZoneInfo
        if manifest["review_by"] < datetime.now(ZoneInfo("Asia/Makassar")).date().isoformat():
            p.error("Release blocked: the source review expired")
        voice_meta = ffprobe(Path(args.voice))
        voice_seconds = float(voice_meta["format"]["duration"])
        if abs(voice_seconds - manifest["duration_seconds"]) > 3.0:
            p.error(f"Release blocked: licensed narration is {voice_seconds:.1f}s; storyboard is {manifest['duration_seconds']}s. Retiming needed")
    tmp=folder/"render_assets";tmp.mkdir(exist_ok=True)
    beats=manifest["story"]["beats"]
    for i,beat in enumerate(beats):
        frame(beat,i,tmp/f"scene_{i:02}.png",args.width,args.height,args.mode=="preview")
    music=tmp/"original_ambient.wav"
    ambient_wav(music,int(manifest["duration_seconds"]))
    # Duration is pinned to source beats; transitions are direct cuts (no source footage).
    inputs=[]
    for i,beat in enumerate(beats):
        inputs += ["-loop","1","-framerate","24","-t",str(beat["seconds"]),"-i",str(tmp/f"scene_{i:02}.png")]
    inputs += ["-i",str(music)]
    if args.voice: inputs += ["-i",args.voice]
    concat="".join(f"[{i}:v]" for i in range(len(beats)))+f"concat=n={len(beats)}:v=1:a=0[v]"
    out=folder/("editorial_RELEASE.mp4" if args.mode=="release" else "internal_DRAFT_preview.mp4")
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",*inputs,"-filter_complex",concat,"-map","[v]"]
    if args.voice:
        # Loudness-correct narration and tuck original pad under it; cut to video duration.
        cmd += ["-filter_complex",concat+f";[{len(beats)}:a]volume=0.55[bed];[{len(beats)+1}:a]loudnorm=I=-18:TP=-2:LRA=11[vo];[vo][bed]amix=inputs=2:duration=first:normalize=0[a]","-map","[a]"]
    else: cmd += ["-map",f"{len(beats)}:a"]
    cmd += ["-t",str(manifest["duration_seconds"]),"-r","24","-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-movflags","+faststart",str(out)]
    # Remove the first filter_complex when narration needs a combined graph.
    if args.voice:
        first=cmd.index("-filter_complex")
        del cmd[first:first+2]
    subprocess.run(cmd,check=True)
    meta=ffprobe(out)
    streams=meta["streams"]
    assert any(s.get("codec_type")=="video" and s.get("width")==args.width and s.get("height")==args.height for s in streams)
    assert any(s.get("codec_type")=="audio" for s in streams)
    assert abs(float(meta["format"]["duration"])-manifest["duration_seconds"])<1.5
    print(f"{args.mode.upper()} VIDEO: {out} ({manifest['duration_seconds']} s, {args.width}x{args.height}); audio={'voice+original synth' if args.voice else 'original synth only'}")


if __name__ == "__main__":
    main()
