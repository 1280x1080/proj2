"""dead_air.py - "no dead spaces" + "appropriate volume" check for a finished mix.

Uses the stems mix.py writes (audio/stems/mix_{narration,music,sfx,ambience}.wav) and audio/timing.json.

  1. DEAD AIR      : momentary loudness (400 ms windows, 100 ms hop) of the master never drops below
                     DEAD_LUFS for longer than 0.3 s.
  2. GAPS FILLED   : every pause between lines (and the lead-in / tail) has a background bed
                     (music + sfx + ambience) at least GAP_MIN_LUFS loud, and not louder than GAP_MAX_LUFS.
  3. SPEECH CLEAR  : while someone speaks, the bed stays >= SPEECH_MARGIN_LU below the voice.

    python dead_air.py STUDIO/VIDEOS/VIDEO_004 [--out qc]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pyloudnorm as pyln

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "audio"))
import dsp  # noqa: E402

DEAD_LUFS = -42.0
GAP_MIN_LUFS = -34.0
GAP_MAX_LUFS = -14.0
SPEECH_MARGIN_LU = 8.0
SR = dsp.SR
METER = pyln.Meter(SR, block_size=0.4)


def lufs(x):
    x = dsp.to_stereo(x)
    if len(x) < int(0.4 * SR):  # centre-pad short windows to one 400 ms block
        pad = int(0.4 * SR) - len(x)
        x = np.pad(x, ((pad // 2, pad - pad // 2), (0, 0)), mode="reflect" if len(x) > pad else "constant")
    if np.max(np.abs(x)) < 1e-7:
        return -120.0
    v = METER.integrated_loudness(x)
    return float(v) if np.isfinite(v) else -120.0


def momentary(x, hop=0.1, win=0.4):
    n, h = int(win * SR), int(hop * SR)
    out = []
    for i in range(0, max(1, len(x) - n), h):
        out.append((i / SR, lufs(x[i:i + n])))
    return out


def run(vdir, out=None):
    vdir = Path(vdir).resolve()
    a = vdir / "audio"
    st = {k: dsp.to_stereo(dsp.read_audio(a / "stems" / f"mix_{k}.wav")) for k in ("narration", "music", "sfx", "ambience")}
    n = min(len(v) for v in st.values())
    st = {k: v[:n] for k, v in st.items()}
    bed = st["music"] + st["sfx"] + st["ambience"]
    master = dsp.to_stereo(dsp.read_audio(a / "mix_master.wav"))[:n]
    timing = json.loads((a / "timing.json").read_text())
    dur = n / SR
    rep = {}

    # 1. dead air in the master
    mom = momentary(master)
    runs, cur = [], None
    for t, l in mom:
        if l < DEAD_LUFS:
            cur = [t, t + 0.4] if cur is None else [cur[0], t + 0.4]
        elif cur is not None:
            runs.append(cur)
            cur = None
    if cur is not None:
        runs.append(cur)
    dead = [dict(start=round(s, 2), end=round(e, 2)) for s, e in runs if e - s >= 0.3 + 0.4]
    rep["dead_air"] = dict(threshold_lufs=DEAD_LUFS, quietest_momentary=round(min(l for _, l in mom), 1), runs=dead,
                           ok=not dead)

    # 2. pauses filled with an appropriate bed
    lines = timing["lines"]
    gaps = [("lead-in", 0.0, lines[0]["start"])]
    gaps += [(f'{lines[i]["id"]}->{lines[i + 1]["id"]}', lines[i]["end"], lines[i + 1]["start"]) for i in range(len(lines) - 1)]
    gaps.append(("tail", lines[-1]["end"], dur))
    rows = []
    for name, s, e in gaps:
        if e - s < 0.2:
            continue
        seg = bed[int(s * SR):int(e * SR)]
        lv = lufs(seg)
        rows.append(dict(gap=name, start=round(s, 2), dur=round(e - s, 2), bed_lufs=round(lv, 1),
                         ok=GAP_MIN_LUFS <= lv <= GAP_MAX_LUFS))
    rep["gaps"] = dict(min_lufs=GAP_MIN_LUFS, max_lufs=GAP_MAX_LUFS, rows=rows, ok=all(r["ok"] for r in rows))

    # 3. bed under speech
    srows = []
    for ln in lines:
        s, e = int(ln["start"] * SR), int(ln["end"] * SR)
        v, b = lufs(st["narration"][s:e]), lufs(bed[s:e])
        srows.append(dict(line=ln["id"], voice_lufs=round(v, 1), bed_lufs=round(b, 1), margin_lu=round(v - b, 1),
                          ok=(v - b) >= SPEECH_MARGIN_LU))
    rep["speech"] = dict(min_margin_lu=SPEECH_MARGIN_LU, rows=srows, ok=all(r["ok"] for r in srows))
    rep["passed"] = rep["dead_air"]["ok"] and rep["gaps"]["ok"] and rep["speech"]["ok"]

    out = Path(out) if out else vdir / "qc"
    out.mkdir(parents=True, exist_ok=True)
    (out / "dead_air.json").write_text(json.dumps(rep, indent=2))
    print(f'[{"PASS" if rep["dead_air"]["ok"] else "FAIL"}] dead air: quietest 400 ms window '
          f'{rep["dead_air"]["quietest_momentary"]} LUFS (limit {DEAD_LUFS}); runs: {dead or "none"}')
    g = rep["gaps"]["rows"]
    if g:
        print(f'[{"PASS" if rep["gaps"]["ok"] else "FAIL"}] {len(g)} pauses filled: bed {min(r["bed_lufs"] for r in g)}..'
              f'{max(r["bed_lufs"] for r in g)} LUFS (want {GAP_MIN_LUFS}..{GAP_MAX_LUFS})')
    else:
        print("[PASS] no pause longer than 0.2 s to fill")
    for r in g:
        if not r["ok"]:
            print(f'      !! {r["gap"]} at {r["start"]}s ({r["dur"]}s): bed {r["bed_lufs"]} LUFS')
    m = [r["margin_lu"] for r in srows]
    print(f'[{"PASS" if rep["speech"]["ok"] else "FAIL"}] voice over bed: margin {min(m)}..{max(m)} LU (want >= {SPEECH_MARGIN_LU})')
    for r in srows:
        if not r["ok"]:
            print(f'      !! {r["line"]}: voice {r["voice_lufs"]} / bed {r["bed_lufs"]} LUFS')
    print("NO DEAD AIR, LEVELS OK" if rep["passed"] else "AUDIO FILL CHECK: FIX FLAGGED ITEMS")
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video_dir")
    ap.add_argument("--out")
    a = ap.parse_args()
    run(a.video_dir, a.out)
