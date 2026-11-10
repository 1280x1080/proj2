"""mix.py - cues.json -> mix_master.wav (+ stems + mix_stats.json)

Chain
  narration : HPF 80 Hz -> presence EQ -> compressor -> loudness-normalise to -16 LUFS
  music     : gain -> side-chain ducked under narration (key = narration envelope)
  sfx / amb : per-cue gain + pan, ambiences looped to the requested length
  master    : sum -> loudness to -14 LUFS integrated -> true-peak limiter at -1 dBTP
Optional circular mix for looping videos: everything that rings past the end is folded onto t=0.

    python mix.py STUDIO/VIDEOS/VIDEO_001/audio/cues.json

cues.json
{
  "duration": 10.0, "loop": false,
  "narration": {"file": "narration_raw.wav", "offset": 0.0},
  "music": {"file": "music.wav", "gain_db": -3, "duck_db": -9},
  "cues": [{"t": 1.2, "sfx": "whoosh", "gain_db": -8, "bus": "sfx", "pan": 0.0, "note": "..."},
           {"t": 0.0, "sfx": "room_tone", "bus": "amb", "gain_db": -6, "dur": 10.0}]
}
Paths are relative to the cues.json folder; SFX names resolve to STUDIO/AUDIO/sound_effects/<name>.flac.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pyloudnorm as pyln

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dsp  # noqa: E402
from dsp import SR, secs  # noqa: E402

STUDIO = HERE.parents[1]
SFX_DIR = STUDIO / "AUDIO" / "sound_effects"
METER = pyln.Meter(SR)

NARR_LUFS = -16.0
MASTER_LUFS = -14.0
CEILING_DBTP = -1.3  # -1.0 dBTP spec with 0.3 dB headroom: AAC encoding adds ~0.25 dB of true peak


def lufs(x):
    x = dsp.to_stereo(x)
    if len(x) < secs(0.5) or np.max(np.abs(x)) < 1e-7:
        return -120.0
    return float(METER.integrated_loudness(x))


def gain_to_lufs(x, target):
    l = lufs(x)
    return x * dsp.undb(target - l) if l > -100 else x


def narration_chain(x):
    x = dsp.highpass(x, 80, 2)
    x = dsp.peaking(x, 3000, 2.0, 0.9)
    x = dsp.shelf(x, 9000, 1.0, high=True)
    x = dsp.compressor(x, threshold_db=-22, ratio=2.5, attack=0.004, release=0.15)
    return gain_to_lufs(dsp.to_stereo(x), NARR_LUFS)


def duck(music, key, depth_db=-9.0, attack=0.06, release=0.45, thresh_db=-40):
    """Side-chain duck: gain smoothly falls by depth_db while the key (narration) is active."""
    k = np.max(np.abs(key), 1) if key.ndim == 2 else np.abs(key)
    k = np.pad(k, (0, max(0, len(music) - len(k))))[: len(music)]
    env = dsp.envelope_follower(k, 0.01, 0.12)
    active = (dsp.db(env) > thresh_db).astype(float)
    # attack/release smoothing of the 0/1 activity, run at 1 kHz control rate then upsampled
    step = SR // 1000
    ctl = active[::step]
    ca, cr = np.exp(-1 / (1000 * attack)), np.exp(-1 / (1000 * release))
    sm = np.empty_like(ctl)
    cur = 0.0
    for i, v in enumerate(ctl):
        cur = v + (cur - v) * (ca if v > cur else cr)
        sm[i] = cur
    amount = np.interp(np.arange(len(music)), np.arange(len(ctl)) * step, sm)
    g = dsp.undb(depth_db * amount)
    return music * g[:, None], g


def _fit(x, n, loop=False):
    x = dsp.to_stereo(x)
    if loop and len(x) < n:
        reps = int(np.ceil(n / len(x)))
        x = np.concatenate([x] * reps)
    out = np.zeros((n, 2))
    m = min(n, len(x))
    out[:m] = x[:m]
    return out


def place(bus, x, t, gain_db, pan, circular, total_n):
    x = dsp.to_stereo(x)
    if pan:
        l = np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
        r = np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
        x = x * np.array([min(l, 1.0), min(r, 1.0)])
    g = dsp.undb(gain_db)
    i = secs(t)
    if circular:
        idx = (np.arange(len(x)) + i) % total_n
        np.add.at(bus, idx, x * g)
    else:
        dsp.mix_into(bus, x, t, g)


def run(cues_path):
    cues_path = Path(cues_path).resolve()
    base = cues_path.parent
    C = json.loads(cues_path.read_text())
    dur = float(C["duration"])
    loop = bool(C.get("loop", False))
    n = secs(dur)
    stems = {}

    # --- narration
    nc = C.get("narration")
    narr = np.zeros((n, 2))
    if nc:
        raw = dsp.read_audio(base / nc["file"])
        proc = narration_chain(raw)
        place(narr, proc, nc.get("offset", 0.0), 0.0, 0.0, loop, n)
    stems["narration"] = narr

    # --- music
    mc = C.get("music")
    mus = np.zeros((n, 2))
    if mc:
        m = _fit(dsp.read_audio(base / mc["file"]), n) * dsp.undb(mc.get("gain_db", 0.0))
        mus, _ = duck(m, narr, depth_db=mc.get("duck_db", -9.0))
    stems["music"] = mus

    # --- sfx + ambience
    sfx = np.zeros((n, 2))
    amb = np.zeros((n, 2))
    cache = {}
    for c in C.get("cues", []):
        name = c["sfx"]
        if name not in cache:
            f = Path(name) if name.endswith((".wav", ".flac")) else SFX_DIR / f"{name}.flac"
            if not f.is_absolute():
                f = (base / f) if (base / f).exists() else f
            cache[name] = dsp.read_audio(f)
        x = cache[name]
        bus = amb if c.get("bus", "sfx") == "amb" else sfx
        if "dur" in c:
            x = dsp.fade(_fit(x, secs(c["dur"]), loop=True), c.get("fade_in", 0.3), c.get("fade_out", 0.5))
        if c.get("rate"):
            x = dsp.pitch_shift_resample(x, 12 * np.log2(c["rate"]))
        place(bus, x, c["t"], c.get("gain_db", 0.0), c.get("pan", 0.0), loop, n)
    # optional: duck the SFX / ambience buses under the voice so the background swells in the pauses
    # (cues.json "sfx_duck_db" / "amb_duck_db", default 0 = off, so older mixes are unchanged)
    if C.get("sfx_duck_db"):
        sfx, _ = duck(sfx, narr, depth_db=float(C["sfx_duck_db"]), attack=0.04, release=0.35)
    if C.get("amb_duck_db"):
        amb, _ = duck(amb, narr, depth_db=float(C["amb_duck_db"]), attack=0.08, release=0.6)
    stems["sfx"] = sfx
    stems["ambience"] = amb

    # --- master (cues.json "ceiling_dbtp" lowers the limiter for very transient mixes; AAC adds overshoot)
    ceiling = float(C.get("ceiling_dbtp", CEILING_DBTP))
    mix = narr + mus + sfx + amb
    pre_l = lufs(mix)
    g = dsp.undb(MASTER_LUFS - pre_l) if pre_l > -100 else 1.0
    mix = mix * g
    stems = {k: v * g for k, v in stems.items()}
    out = dsp.limiter(mix, ceiling)
    # second pass: the limiter removes some loudness, so nudge and re-limit once
    l1 = lufs(out)
    if l1 > -100 and abs(l1 - MASTER_LUFS) > 0.3:
        out = dsp.limiter(mix * dsp.undb(MASTER_LUFS - l1), ceiling)
    if not loop:
        out = dsp.fade(out, 0.0, 0.02)

    stats = dict(duration=dur, loop=loop, master_lufs=round(lufs(out), 2),
                 master_true_peak_dbtp=round(float(dsp.true_peak(out)), 2),
                 narration_lufs_pre_master=round(NARR_LUFS, 1),
                 stems_lufs={k: round(lufs(v), 2) for k, v in stems.items()},
                 cue_count=len(C.get("cues", [])))
    dsp.write_audio(base / "mix_master.wav", out)
    (base / "stems").mkdir(exist_ok=True)
    for k, v in stems.items():
        dsp.write_audio(base / "stems" / f"mix_{k}.wav", v)
    (base / "mix_stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    return stats


if __name__ == "__main__":
    run(sys.argv[1])
