"""qc_video.py - technical QA on a real export.

Checks: resolution / fps / codecs / pixel format / colour tags, duration, integrated loudness and
true peak, black segments, frozen segments, audio silence, plus a contact sheet (one tile every
--every seconds, timestamped) for the visual pass.

    python qc_video.py EXPORTS/video001.mp4 [--every 0.5] [--out VIDEOS/VIDEO_001/qc] [--expect-dur 10]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "audio"))
import dsp  # noqa: E402

FONT = Path(__file__).resolve().parents[2] / "ASSETS" / "fonts" / "Inter-Bold.otf"


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def ff_detect(path, vf=None, af=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path)]
    if vf:
        cmd += ["-vf", vf, "-an"]
    if af:
        cmd += ["-af", af, "-vn"]
    cmd += ["-f", "null", "-"]
    return subprocess.run(cmd, capture_output=True, text=True).stderr


def black_segments(path, min_d=0.1):
    log = ff_detect(path, vf=f"blackdetect=d={min_d}:pic_th=0.98:pix_th=0.06")
    return [dict(start=float(a), end=float(b), dur=float(c)) for a, b, c in
            re.findall(r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)", log)]


def frozen_segments(path, min_d=1.0):
    log = ff_detect(path, vf=f"freezedetect=n=0.0015:d={min_d}")
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", log)]
    segs = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else None
        segs.append(dict(start=s, end=e, dur=(e - s) if e else None))
    return segs


def silences(path, min_d=0.8, db=-50):
    log = ff_detect(path, af=f"silencedetect=n={db}dB:d={min_d}")
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return [dict(start=s, end=en[i] if i < len(en) else None) for i, s in enumerate(st)]


def audio_array(path):
    with tempfile.TemporaryDirectory() as d:
        wav = Path(d) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vn", "-ac", "2", "-ar", "48000", str(wav)],
                       check=True)
        return dsp.read_audio(wav)


def loudness(x):
    m = pyln.Meter(48000)
    return float(m.integrated_loudness(dsp.to_stereo(x))), float(dsp.true_peak(x))


def contact_sheet(path, out_png, every=0.5, cols=6, tile_w=180):
    pr = probe(path)
    dur = float(pr["format"]["duration"])
    times = np.arange(0, dur - 1e-3, every)
    tile_h = int(tile_w * 16 / 9)
    rows = int(np.ceil(len(times) / cols))
    sheet = Image.new("RGB", (cols * tile_w, rows * (tile_h + 22)), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(FONT), 16)
    except OSError:
        font = ImageFont.load_default()
    with tempfile.TemporaryDirectory() as d:
        # one ffmpeg pass: fps filter picks frames on the grid
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vf",
                        f"select='not(mod(n\\,{max(1, round(every * 30))}))',scale={tile_w}:{tile_h}", "-fps_mode", "vfr",
                        str(Path(d) / "t_%05d.png")], check=True)
        files = sorted(Path(d).glob("t_*.png"))
        for k, f in enumerate(files[: len(times)]):
            r, c = divmod(k, cols)
            sheet.paste(Image.open(f), (c * tile_w, r * (tile_h + 22) + 22))
            draw.text((c * tile_w + 4, r * (tile_h + 22) + 2), f"{k * every:5.1f}s", fill=(230, 230, 230), font=font)
    sheet.save(out_png)
    return out_png


def run(path, out_dir=None, every=0.5, expect_dur=None, loop=False):
    path = Path(path).resolve()
    out_dir = Path(out_dir) if out_dir else path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    pr = probe(path)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), None)
    num, den = map(int, v["r_frame_rate"].split("/"))
    fps = num / den
    dur = float(pr["format"]["duration"])
    checks = {}

    def chk(name, ok, val, want):
        checks[name] = dict(ok=bool(ok), value=val, want=want)

    chk("resolution", (v["width"], v["height"]) == (1080, 1920), f'{v["width"]}x{v["height"]}', "1080x1920")
    chk("fps", abs(fps - 30) < 0.01, round(fps, 3), 30)
    chk("video_codec", v["codec_name"] == "h264", v["codec_name"], "h264")
    chk("pix_fmt", v.get("pix_fmt") == "yuv420p", v.get("pix_fmt"), "yuv420p")
    chk("color", v.get("color_primaries") == "bt709" and v.get("color_space") == "bt709",
        f'{v.get("color_space")}/{v.get("color_primaries")}/{v.get("color_transfer")}', "bt709")
    chk("audio_codec", a is not None and a["codec_name"] == "aac", a and a["codec_name"], "aac")
    chk("audio_rate", a is not None and int(a["sample_rate"]) == 48000, a and a["sample_rate"], 48000)
    if expect_dur:
        chk("duration", abs(dur - expect_dur) < 0.1, round(dur, 3), expect_dur)
    else:
        chk("duration", 10 <= dur <= 90 or dur < 15, round(dur, 3), "30-90 s (tests may be shorter)")
    if a is not None:
        vdur = float(v.get("duration", dur))
        adur = float(a.get("duration", dur))
        chk("av_length_match", abs(vdur - adur) < 0.08, dict(video=vdur, audio=adur), "|diff| < 0.08 s")
        x = audio_array(path)
        L, tp = loudness(x)
        chk("loudness_lufs", abs(L - (-14)) <= 1.0, round(L, 2), "-14 ±1")
        chk("true_peak_dbtp", tp <= -1.0 + 0.05, round(tp, 2), "<= -1.0")
        sil = silences(path)
        chk("no_long_silence", not [s for s in sil if (s["end"] or dur) - s["start"] > 1.5], sil, "no silence > 1.5 s")
    blacks = black_segments(path)
    chk("no_black", not blacks, blacks, "no black segments >= 0.1 s (unless intended)")
    frz = frozen_segments(path)
    chk("no_frozen", not frz, frz, "no frozen picture >= 1 s (unless intended)")
    sheet = contact_sheet(path, out_dir / "contact_sheet.png", every)
    rep = dict(file=str(path), duration=dur, checks=checks, contact_sheet=str(sheet),
               passed=all(c["ok"] for c in checks.values()))
    (out_dir / "qc_report.json").write_text(json.dumps(rep, indent=2, default=str))
    for k, c in checks.items():
        print(f"  [{'PASS' if c['ok'] else 'FAIL'}] {k:18s} {c['value']}  (want {c['want']})")
    print(f"contact sheet: {sheet}\n{'ALL PASSED' if rep['passed'] else 'SOME CHECKS FAILED'}")
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out")
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--expect-dur", type=float)
    a = ap.parse_args()
    run(a.video, a.out, a.every, a.expect_dur)
