"""voice_qc.py - independent check of the assembled narration.

Re-transcribes narration_raw.wav per line window (with a different Whisper model than narrate.py
by default), reports mismatched words, speaking rate, clipping, gaps and loudness.

    ~/.venvs/tts/bin/python voice_qc.py STUDIO/VIDEOS/VIDEO_001/script.json [--whisper base.en]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "audio"))
import dsp  # noqa: E402
from textnorm import mismatches, normalize_words  # noqa: E402


def run(script_path, whisper_model="base.en"):
    from faster_whisper import WhisperModel
    script_path = Path(script_path).resolve()
    out = script_path.parent / "audio"
    timing = json.loads((out / "timing.json").read_text())
    x = dsp.read_audio(out / "narration_raw.wav")
    if x.ndim == 2:
        x = x.mean(1)
    m = WhisperModel(whisper_model, device="cpu", compute_type="int8")
    rows = []
    for ln in timing["lines"]:
        a, b = dsp.secs(max(0, ln["start"] - 0.05)), dsp.secs(ln["end"] + 0.1)
        seg = x[a:b]
        from scipy.signal import resample_poly
        seg16 = resample_poly(seg, 1, 3).astype(np.float32)
        segs, _ = m.transcribe(seg16, language="en", beam_size=5, condition_on_previous_text=False)
        hyp = " ".join(s.text.strip() for s in segs)
        dur = ln["end"] - ln["start"]
        nw = len(normalize_words(ln["text"]))
        rows.append(dict(id=ln["id"], text=ln["text"], heard=hyp, mismatches=mismatches(ln["text"], hyp),
                         duration=round(dur, 2), words_per_sec=round(nw / max(dur, 0.1), 2),
                         clipped=bool(np.max(np.abs(seg)) >= 0.999)))
    gaps = [round(timing["lines"][i + 1]["start"] - timing["lines"][i]["end"], 2) for i in range(len(timing["lines"]) - 1)]
    rep = dict(model=whisper_model, lines=rows, gaps=gaps, total=timing["duration"],
               peak_db=round(float(dsp.db(np.max(np.abs(x)))), 2),
               passed=all(r["mismatches"] == 0 and not r["clipped"] and 1.5 <= r["words_per_sec"] <= 4.2 for r in rows))
    (out / "voice_qc.json").write_text(json.dumps(rep, indent=2))
    for r in rows:
        flag = "OK " if r["mismatches"] == 0 else "!! "
        print(f"{flag}{r['id']:5s} {r['mismatches']} mm  {r['words_per_sec']:.2f} w/s  heard: {r['heard']}")
    print(f"gaps: {gaps}\n{'VOICE QC PASSED' if rep['passed'] else 'VOICE QC: CHECK FLAGGED LINES'}")
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--whisper", default="base.en")
    a = ap.parse_args()
    run(a.script, a.whisper)
