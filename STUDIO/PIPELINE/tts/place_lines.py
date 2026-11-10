"""place_lines.py - assemble per-line wavs into narration_raw.wav + timing.json (no regeneration).

Lines play back-to-back (lead_in, then each line + its pause_after) unless a line has "at": <seconds>,
which pins it to a fixed story time (later lines continue after it).  Re-run after editing pauses/at:

    python place_lines.py STUDIO/VIDEOS/VIDEO_001/script.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "audio"))
import dsp  # noqa: E402


def assemble(script_path):
    script_path = Path(script_path).resolve()
    vdir = script_path.parent
    S = json.loads(script_path.read_text())
    out = vdir / "audio"
    rep = json.loads((out / "narration_report.json").read_text())
    t = float(S.get("lead_in", 0.25))
    placed = []
    for line in S["lines"]:
        lid = line["id"]
        if lid not in rep:
            raise SystemExit(f"line {lid} has no take yet - run narrate.py")
        x = dsp.read_audio(out / "lines" / f"{lid}.wav")
        if x.ndim == 2:
            x = x.mean(1)
        if line.get("at") is not None:
            if line["at"] < t - 1e-3:  # never overlap: a long previous line pushes this one later
                print(f"  ! {lid}: at={line['at']} would overlap the previous line - placed at {t:.2f}")
            t = max(t, float(line["at"]))
        d = len(x) / dsp.SR
        placed.append((line, x, t, d))
        t += d + float(line.get("pause_after", 0.3))
    total = t - float(placed[-1][0].get("pause_after", 0.3)) + float(S.get("tail", 0.6)) if placed else 1.0
    if S.get("duration"):
        total = max(total, float(S["duration"]))
    mix = np.zeros(dsp.secs(total) + 1)
    lines = []
    for line, x, t0, d in placed:
        dsp.mix_into(mix, x, t0)
        words = [dict(w=w["w"], start=round(t0 + w["start"], 3), end=round(t0 + w["end"], 3))
                 for w in rep[line["id"]]["words"]]
        lines.append(dict(id=line["id"], who=line.get("who", "narrator"), text=line["text"], start=round(t0, 3),
                          end=round(t0 + d, 3), words=words))
    dsp.write_audio(out / "narration_raw.wav", mix)
    timing = dict(duration=round(total, 3), lines=lines)
    (out / "timing.json").write_text(json.dumps(timing, indent=2))
    return timing


if __name__ == "__main__":
    tm = assemble(sys.argv[1])
    for ln in tm["lines"]:
        print(f"{ln['id']:6s} {ln['start']:6.2f}-{ln['end']:6.2f}  {ln['text']}")
    print(f"total {tm['duration']:.2f}s")
