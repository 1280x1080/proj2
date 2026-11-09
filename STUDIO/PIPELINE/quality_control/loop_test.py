"""loop_test.py - does the video loop seamlessly?

Builds the video played 3x back-to-back (stream copy concat) and checks the seam:
  * black or silence at the seam
  * click: sample jump across the seam vs typical sample-to-sample jumps
  * audio gap / A/V length mismatch (would drift over repeats)
  * picture change across the seam vs the normal frame-to-frame motion of the video

    python loop_test.py EXPORTS/video002.mp4 [--out VIDEOS/VIDEO_002/qc]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qc_video import audio_array, probe  # noqa: E402


def frames(path, n_first=0, n_last=0):
    """Decode all frames small (135x240 gray) -> array (N, h, w)."""
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", "scale=135:240,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(out, np.uint8).reshape(-1, 240, 135).astype(np.float32)
    return a


def run(path, out_dir=None):
    path = Path(path).resolve()
    out_dir = Path(out_dir) if out_dir else path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    pr = probe(path)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), None)
    vdur, adur = float(v["duration"]), float(a["duration"]) if a else 0.0
    res = {}

    # --- picture seam
    f = frames(path)
    diffs = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    seam = float(np.abs(f[0] - f[-1]).mean())
    med, p95 = float(np.median(diffs)), float(np.percentile(diffs, 95))
    res["picture_seam"] = dict(seam_diff=round(seam, 2), median_motion=round(med, 2), p95_motion=round(p95, 2),
                               ok=seam <= max(p95, 3.0) * 1.1)
    res["black_at_seam"] = dict(first=float(f[0].mean()), last=float(f[-1].mean()),
                                ok=f[0].mean() > 8 and f[-1].mean() > 8)

    # --- audio seam
    if a is not None:
        x = audio_array(path)
        head, tail = x[:2400], x[-2400:]
        rms = lambda y: float(np.sqrt(np.mean(y ** 2)) + 1e-12)  # noqa: E731
        jump = float(np.max(np.abs(x[0] - x[-1])))
        typical = float(np.percentile(np.abs(np.diff(x, axis=0)).max(1), 99.5))
        res["audio_click"] = dict(seam_jump=round(jump, 4), p99_5_step=round(typical, 4), ok=jump <= typical * 1.5)
        res["audio_silence_at_seam"] = dict(head_rms_db=round(20 * np.log10(rms(head)), 1),
                                            tail_rms_db=round(20 * np.log10(rms(tail)), 1),
                                            ok=rms(head) > 10 ** (-60 / 20) and rms(tail) > 10 ** (-60 / 20))
        res["av_length"] = dict(video=vdur, audio=adur, ok=abs(vdur - adur) < 1 / 30 + 0.025)

    # --- 3x concat for viewing
    with tempfile.TemporaryDirectory() as d:
        lst = Path(d) / "l.txt"
        lst.write_text("".join(f"file '{path}'\n" for _ in range(3)))
        x3 = out_dir / f"{path.stem}_loop3x.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                        str(x3)], check=True)
    p3 = probe(x3)
    res["loop3x_file"] = dict(path=str(x3), duration=float(p3["format"]["duration"]),
                              ok=abs(float(p3["format"]["duration"]) - 3 * vdur) < 0.2)
    res["passed"] = all(v["ok"] for k, v in res.items() if isinstance(v, dict) and "ok" in v)
    (out_dir / "loop_test.json").write_text(json.dumps(res, indent=2))
    for k, v in res.items():
        if isinstance(v, dict):
            print(f"  [{'PASS' if v['ok'] else 'FAIL'}] {k:22s} " + ", ".join(f"{a}={b}" for a, b in v.items() if a != "ok"))
    print("LOOP OK" if res["passed"] else "LOOP HAS ISSUES")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out")
    a = ap.parse_args()
    run(a.video, a.out)
