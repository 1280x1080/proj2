"""narrate.py - script.json -> per-line wavs + narration_raw.wav + word-level timing.json

For every line: generate N takes with a local TTS (Chatterbox, CPU), transcribe each take with
faster-whisper, keep the take with the fewest word mismatches (digits vs words don't count),
trim silence, then assemble (place_lines.assemble) and write word timing.

Run with the TTS virtualenv:
    ~/.venvs/tts/bin/python narrate.py STUDIO/VIDEOS/VIDEO_001/script.json [--takes 3] [--only L2] [--force]

script.json
{
  "voice_ref": null,                 # default reference clip for the narrator (null = model's built-in voice)
  "voices": {"mia": "voices/mia.wav"},
  "lead_in": 0.25, "tail": 0.6,
  "lines": [
    {"id": "L1", "who": "narrator", "text": "...", "delivery": "warm", "emotion": 0.5,
     "pause_after": 0.35, "voice_ref": null, "at": null}
  ]
}
Takes are cached by a hash of (text, voice, params, seed); edit one line and only that line regenerates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "audio"))
import dsp  # noqa: E402
from place_lines import assemble  # noqa: E402
from textnorm import mismatches, normalize_words  # noqa: E402

# delivery presets -> chatterbox knobs (exaggeration is overridden by the line's "emotion" if given)
DELIVERY = {
    "neutral": dict(exaggeration=0.5, cfg_weight=0.5, temperature=0.75),
    "warm": dict(exaggeration=0.55, cfg_weight=0.45, temperature=0.75),
    "calm": dict(exaggeration=0.4, cfg_weight=0.4, temperature=0.7),
    "excited": dict(exaggeration=0.8, cfg_weight=0.35, temperature=0.8),
    "dramatic": dict(exaggeration=0.7, cfg_weight=0.3, temperature=0.8),
    "whisper": dict(exaggeration=0.3, cfg_weight=0.5, temperature=0.7),
    "fast": dict(exaggeration=0.6, cfg_weight=0.6, temperature=0.8),
    "slow": dict(exaggeration=0.45, cfg_weight=0.25, temperature=0.7),
}


# ============================================================================ engines

class ChatterboxEngine:
    name = "chatterbox"

    def __init__(self):
        import torch
        from chatterbox.tts import ChatterboxTTS
        torch.set_num_threads(max(1, __import__("os").cpu_count() or 1))
        self.torch = torch
        t = time.time()
        self.model = ChatterboxTTS.from_pretrained(device="cpu")
        self.sr = self.model.sr
        print(f"chatterbox loaded in {time.time() - t:.1f}s (sr={self.sr})")

    def synth(self, text, voice_ref, seed, exaggeration, cfg_weight, temperature):
        self.torch.manual_seed(seed)
        kw = dict(exaggeration=exaggeration, cfg_weight=cfg_weight, temperature=temperature)
        if voice_ref:
            kw["audio_prompt_path"] = str(voice_ref)
        wav = self.model.generate(text, **kw)
        return wav.squeeze().cpu().numpy().astype(np.float64), self.sr


class EspeakEngine:
    """Robotic fallback ONLY for pipeline smoke tests (never for a real video)."""
    name = "espeak"

    def __init__(self):
        import shutil
        self.bin = shutil.which("espeak-ng") or shutil.which("espeak")
        if not self.bin:
            raise RuntimeError("espeak-ng not installed")
        self.sr = 22050

    def synth(self, text, voice_ref, seed, exaggeration, cfg_weight, temperature):
        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            subprocess.run([self.bin, "-s", "165", "-w", f.name, text], check=True)
            x = dsp.read_audio(f.name, sr=self.sr)
        return x, self.sr


# ============================================================================ whisper

class Checker:
    def __init__(self, model="small.en"):
        from faster_whisper import WhisperModel
        t = time.time()
        self.m = WhisperModel(model, device="cpu", compute_type="int8")
        print(f"whisper {model} loaded in {time.time() - t:.1f}s")

    def transcribe(self, wav_path, prompt=None):
        segs, _ = self.m.transcribe(load16k(wav_path), language="en", word_timestamps=True, beam_size=5,
                                    vad_filter=False, condition_on_previous_text=False, initial_prompt=prompt)
        words, text = [], []
        for s in segs:
            text.append(s.text)
            for w in s.words or []:
                words.append(dict(w=w.word.strip(), start=float(w.start), end=float(w.end), p=float(w.probability)))
        return " ".join(t.strip() for t in text), words


# ============================================================================ helpers

def load16k(path):
    """Whisper wants 16 kHz mono float32 (passing arrays avoids PyAV version issues)."""
    x = dsp.read_audio(path, sr=16000)
    if x.ndim == 2:
        x = x.mean(1)
    return x.astype(np.float32)


def trim_silence(x, sr, thresh_db=-42, pad=0.04):
    if len(x) == 0:
        return x, 0.0
    win = max(1, int(0.01 * sr))
    n = len(x) // win
    e = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, 1) + 1e-12)
    ref = np.max(e)
    on = np.where(20 * np.log10(e / ref) > thresh_db)[0]
    if len(on) == 0:
        return x, 0.0
    a = max(0, on[0] * win - int(pad * sr))
    b = min(len(x), (on[-1] + 1) * win + int(pad * 1.5 * sr))
    y = x[a:b].copy()
    f = int(0.006 * sr)
    y[:f] *= np.linspace(0, 1, f)
    y[-f:] *= np.linspace(1, 0, f)
    return y, a / sr


def align_words(script_text, wwords, dur):
    """Map whisper word times onto the script's own tokens (keeps script spelling for captions)."""
    from difflib import SequenceMatcher
    toks = script_text.split()
    flat_s = []
    for i, tk in enumerate(toks):
        for w in normalize_words(tk) or [""]:
            flat_s.append((w, i))
    flat_h = []
    for ww in wwords:
        ns = normalize_words(ww["w"]) or [""]
        span = (ww["end"] - ww["start"]) / len(ns)
        for k, w in enumerate(ns):
            flat_h.append((w, ww["start"] + k * span, ww["start"] + (k + 1) * span))
    sm = SequenceMatcher(a=[w for w, _ in flat_s], b=[w for w, _, _ in flat_h], autojunk=False)
    t0 = [None] * len(toks)
    t1 = [None] * len(toks)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            _, ti = flat_s[blk.a + k]
            _, s, e = flat_h[blk.b + k]
            t0[ti] = s if t0[ti] is None else min(t0[ti], s)
            t1[ti] = e if t1[ti] is None else max(t1[ti], e)
    # interpolate unmatched tokens by character length between known neighbours
    known = [i for i in range(len(toks)) if t0[i] is not None]
    if not known:
        lens = np.array([len(t) + 1 for t in toks], float)
        edges = np.concatenate([[0], np.cumsum(lens)]) / lens.sum() * dur
        return [dict(w=tk, start=float(edges[i]), end=float(edges[i + 1])) for i, tk in enumerate(toks)]
    i = 0
    while i < len(toks):
        if t0[i] is None:
            j = i
            while j < len(toks) and t0[j] is None:
                j += 1
            a = t1[i - 1] if i > 0 else 0.0
            b = t0[j] if j < len(toks) else dur
            lens = np.array([len(toks[k]) + 1 for k in range(i, j)], float)
            edges = a + np.concatenate([[0], np.cumsum(lens)]) / lens.sum() * max(0.05, b - a)
            for k in range(i, j):
                t0[k], t1[k] = float(edges[k - i]), float(edges[k - i + 1])
            i = j
        else:
            i += 1
    out = []
    for i, tk in enumerate(toks):
        s, e = t0[i], t1[i]
        if out and s < out[-1]["end"]:
            s = out[-1]["end"]
        out.append(dict(w=tk, start=round(float(s), 3), end=round(float(max(e, s + 0.04)), 3)))
    return out


def take_key(line, voice, params, seed, engine):
    h = hashlib.sha1(json.dumps([line["text"], str(voice), params, seed, engine], sort_keys=True).encode())
    return h.hexdigest()[:12]


# ============================================================================ main

def run(script_path, takes=3, only=None, force=False, engine_name="chatterbox", whisper_model="small.en",
        max_rounds=2):
    script_path = Path(script_path).resolve()
    vdir = script_path.parent
    S = json.loads(script_path.read_text())
    out = vdir / "audio"
    (out / "takes").mkdir(parents=True, exist_ok=True)
    (out / "lines").mkdir(parents=True, exist_ok=True)
    report_path = out / "narration_report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    engine = None
    checker = None

    for line in S["lines"]:
        lid = line["id"]
        if only and lid not in only:
            continue
        if engine_name == "qwen":  # designed / cloned voices per speaker (see qwen_engine.py)
            if engine is None:
                from qwen_engine import QwenEngine
                engine = QwenEngine()
                qwen_voices = engine.prepare_voices(S, vdir)
                checker = Checker(whisper_model)
            who = S.get("voice_alias", {}).get(line.get("who", "narrator"), line.get("who", "narrator"))
            voice = (vdir / line["voice_ref"]) if line.get("voice_ref") else qwen_voices.get(who, qwen_voices["narrator"])
        else:
            voice = line.get("voice_ref") or S.get("voices", {}).get(line.get("who", "narrator")) or S.get("voice_ref")
            voice = (vdir / voice) if voice else None
        params = dict(DELIVERY.get(line.get("delivery", "neutral"), DELIVERY["neutral"]))
        if line.get("emotion") is not None:
            params["exaggeration"] = float(line["emotion"])
        cached = report.get(lid)
        key0 = take_key(line, voice, params, 0, engine_name)
        if cached and cached.get("key") == key0 and not force and (out / "lines" / f"{lid}.wav").exists():
            print(f"[{lid}] cached (mismatches={cached['mismatches']})")
            continue
        if engine is None:
            engine = ChatterboxEngine() if engine_name == "chatterbox" else EspeakEngine()
            checker = Checker(whisper_model)
        cands = []
        for rnd in range(max_rounds):
            for k in range(takes):
                seed = 1000 * rnd + k
                t = time.time()
                if engine_name == "qwen":
                    x, sr = engine.synth(line["text"], voice, seed, delivery=line.get("delivery"), **params)
                else:
                    x, sr = engine.synth(line["text"], voice, seed, **params)
                x = dsp.normalize(x, -3) if np.max(np.abs(x)) > 0 else x
                x, _ = trim_silence(x, sr)
                p = out / "takes" / f"{lid}_r{rnd}_t{k}.wav"
                x48 = _resample(x, sr)
                dsp.write_audio(p, x48)
                gen_s = time.time() - t
                hyp, ww = checker.transcribe(p, prompt=None)
                mm = mismatches(line["text"], hyp)
                dur = len(x48) / dsp.SR
                cands.append(dict(path=str(p), hyp=hyp, words=ww, mismatches=mm, dur=dur, seed=seed,
                                  gen_seconds=round(gen_s, 1), mean_p=float(np.mean([w["p"] for w in ww]) if ww else 0)))
                print(f"[{lid}] take r{rnd}t{k}: {mm} mismatches, {dur:.2f}s audio, {gen_s:.1f}s gen  | {hyp!r}")
                if mm == 0 and k >= 1:
                    break
            if min(c["mismatches"] for c in cands) == 0:
                break
        nwords = len(normalize_words(line["text"]))
        too_fast = lambda c: nwords / max(c["dur"], 0.1) > 4.0  # noqa: E731  (prefer a take within the pace limit)
        best = min(cands, key=lambda c: (c["mismatches"], too_fast(c), -c["mean_p"], abs(c["dur"] - _expected_dur(line["text"]))))
        x = dsp.read_audio(best["path"])
        dsp.write_audio(out / "lines" / f"{lid}.wav", x)
        words = align_words(line["text"], best["words"], best["dur"])
        report[lid] = dict(key=key0, text=line["text"], chosen=Path(best["path"]).name, mismatches=best["mismatches"],
                           heard=best["hyp"], duration=round(best["dur"], 3), words=words, engine=engine_name,
                           takes=[dict(file=Path(c["path"]).name, mismatches=c["mismatches"], heard=c["hyp"],
                                       gen_seconds=c["gen_seconds"]) for c in cands])
        if best["mismatches"] > 0:
            print(f"  !! [{lid}] best take still has {best['mismatches']} mismatches - consider rewriting the line "
                  f"(short lines hallucinate).")
        report_path.write_text(json.dumps(report, indent=2))

    report_path.write_text(json.dumps(report, indent=2))
    timing = assemble(script_path)
    bad = {k: v["mismatches"] for k, v in report.items() if v["mismatches"]}
    print(f"narration: {timing['duration']:.2f}s, {len(timing['lines'])} lines; lines with mismatches: {bad or 'none'}")
    return timing


def _resample(x, sr):
    from math import gcd

    from scipy import signal
    g = gcd(sr, dsp.SR)
    return signal.resample_poly(x, dsp.SR // g, sr // g)


def _expected_dur(text):
    return len(normalize_words(text)) / 2.6  # ~156 wpm


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--takes", type=int, default=3)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--engine", default="chatterbox", choices=["chatterbox", "qwen", "espeak"])
    ap.add_argument("--whisper", default="small.en")
    a = ap.parse_args()
    run(a.script, a.takes, a.only, a.force, a.engine, a.whisper)
