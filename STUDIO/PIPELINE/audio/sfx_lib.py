"""sfx_lib.py - procedural sound-effect library.

Every effect is a function decorated with @reg(name, description) that returns a mono or
stereo float array at dsp.SR.  `sfx_generate.py` renders all of them to
STUDIO/AUDIO/sound_effects/<name>.flac and writes LIBRARY.json.

Add per-video effects in new modules named sfx_<topic>.py that import `reg` from here;
sfx_generate.py imports every sfx_*.py automatically.
"""
from __future__ import annotations

import numpy as np

from dsp import (SR, adsr, ar, bandpass, brown, convolve, exp_decay, fade, fm_bell, highpass, karplus,
                 lowpass, midi_hz, normalize, pan, peaking, pink, reverb_ir, saturate, secs, sine,
                 sweep_filter, t_axis, white)

REGISTRY: dict[str, dict] = {}


def reg(name, description, category="misc", loop=False):
    def wrap(fn):
        REGISTRY[name] = dict(fn=fn, description=description, category=category, loop=loop)
        return fn
    return wrap


def _room(x, wet=0.18, dur=0.9, damp=5000):
    return convolve(x, reverb_ir(dur, damp=damp), wet=wet)


# ============================================================================ impacts
@reg("impact_soft", "Soft cushioned thud (body landing on sofa, bag dropped)", "impact")
def impact_soft():
    d = 0.6
    t = t_axis(d)
    body = sine(70 * np.exp(-t * 6) + 45, d) * exp_decay(d, 0.09)
    thump = lowpass(brown(d, 3), 400) * exp_decay(d, 0.05)
    return normalize(_room(body * 0.8 + thump * 0.6, 0.08), -3)


@reg("impact_hard", "Hard punchy hit with low boom and click", "impact")
def impact_hard():
    d = 1.4
    t = t_axis(d)
    boom = sine(110 * np.exp(-t * 9) + 38, d) * exp_decay(d, 0.28)
    click = highpass(white(d, 5), 2500) * exp_decay(d, 0.006)
    crunch = bandpass(white(d, 6), 300, 2500) * exp_decay(d, 0.04)
    x = saturate(boom * 1.0 + click * 0.5 + crunch * 0.45, 2.2)
    return normalize(_room(x, 0.15, 1.6), -1)


@reg("impact_cinematic", "Big trailer hit: sub drop, metallic layer and long tail", "impact")
def impact_cinematic():
    d = 3.5
    t = t_axis(d)
    sub = sine(60 * np.exp(-t * 2.5) + 28, d) * exp_decay(d, 0.9)
    metal = sum(fm_bell(f, d, ratio=1.41, index=6, tau=0.6) for f in (183, 257, 341)) / 3
    noise = lowpass(pink(d, 9), 3000) * exp_decay(d, 0.25)
    x = saturate(sub * 1.1 + metal * 0.25 + noise * 0.35, 1.6)
    return normalize(_room(x, 0.35, 3.0, 3500), -1)


@reg("thud_wood", "Knock / object set down on a wooden table", "impact")
def thud_wood():
    d = 0.35
    modes = [(190, 0.05), (410, 0.03), (760, 0.02), (1350, 0.012)]
    x = sum(sine(f, d) * exp_decay(d, tau) * (1 / (i + 1)) for i, (f, tau) in enumerate(modes))
    x = x + bandpass(white(d, 2), 500, 4000) * exp_decay(d, 0.004) * 0.6
    return normalize(_room(x, 0.12, 0.5), -3)


# ============================================================================ movement
@reg("whoosh", "Fast air whoosh (camera whip, object flying past), ~0.6 s", "movement")
def whoosh():
    d = 0.7
    t = t_axis(d)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2.5
    x = sweep_filter(pink(d, 11) * env, 300, 4000, "band", q=1.6)
    x2 = sweep_filter(pink(d, 12) * env, 260, 3400, "band", q=1.6)
    pn = np.linspace(-0.8, 0.8, len(x))
    st = np.stack([x * np.cos((pn + 1) * np.pi / 4) + x2 * 0.3, x * np.sin((pn + 1) * np.pi / 4) + x2 * 0.3], 1)
    return normalize(st, -2)


@reg("whoosh_soft", "Gentle swish for titles and transitions", "movement")
def whoosh_soft():
    d = 0.5
    t = t_axis(d)
    env = np.sin(np.pi * t / d) ** 2
    x = bandpass(pink(d, 21), 500, 3500) * env
    return normalize(pan(x, 0) * 0.7, -6)


@reg("riser", "Tension riser: noise + rising tone, 2.5 s, ends abruptly", "movement")
def riser():
    d = 2.5
    t = t_axis(d)
    env = (t / d) ** 2
    tone = sine(np.geomspace(180, 900, len(t)), d) * 0.3
    nz = sweep_filter(white(d, 4), 400, 9000, "band", q=0.9)
    x = (tone + nz) * env
    return normalize(_room(x, 0.25, 1.2), -2)


@reg("footstep_hard", "Single shoe step on hard floor", "foley")
def footstep_hard():
    d = 0.25
    heel = bandpass(white(d, 31), 150, 1800) * exp_decay(d, 0.012)
    sole = bandpass(white(d, 32), 800, 5000) * np.concatenate([np.zeros(secs(0.035)), exp_decay(d - 0.035, 0.01)])
    low = sine(95, d) * exp_decay(d, 0.02) * 0.6
    return normalize(_room(heel + sole * 0.4 + low, 0.1, 0.5), -6)


@reg("footstep_soft", "Soft step on carpet", "foley")
def footstep_soft():
    d = 0.22
    x = lowpass(white(d, 41), 900) * ar(d, 0.015, 3) + sine(80, d) * exp_decay(d, 0.03) * 0.4
    return normalize(x, -9)


# ============================================================================ objects
@reg("door_open", "Door handle click + creaky swing", "foley")
def door_open():
    d = 1.4
    click = bandpass(white(0.05, 51), 1500, 6000) * exp_decay(0.05, 0.006)
    t = t_axis(1.2)
    f = 420 + 160 * np.sin(2 * np.pi * 1.6 * t) + 60 * np.sin(2 * np.pi * 7 * t)
    pulses = (np.sin(2 * np.pi * np.cumsum(f / 18) / SR) > 0.6).astype(float)
    creak = bandpass(pulses * white(1.2, 52), 600, 2400) * np.sin(np.pi * t / 1.2) ** 0.7
    x = np.zeros(secs(d))
    x[: len(click)] += click
    x[secs(0.15): secs(0.15) + len(creak)] += creak * 0.6
    return normalize(_room(x, 0.2, 0.9), -4)


@reg("door_close", "Door shutting with latch", "foley")
def door_close():
    d = 0.8
    t = t_axis(d)
    body = sine(85 * np.exp(-t * 4) + 55, d) * exp_decay(d, 0.08)
    slap = bandpass(white(d, 61), 200, 3000) * exp_decay(d, 0.015)
    latch = np.zeros(secs(d))
    lt = bandpass(white(0.04, 62), 2000, 7000) * exp_decay(0.04, 0.004)
    latch[secs(0.05): secs(0.05) + len(lt)] = lt
    return normalize(_room(body + slap * 0.7 + latch * 0.5, 0.22, 0.9), -3)


@reg("click_ui", "Crisp UI click", "ui")
def click_ui():
    d = 0.06
    x = sine(2200, d) * exp_decay(d, 0.006) + highpass(white(d, 71), 3000) * exp_decay(d, 0.002) * 0.4
    return normalize(x, -8)


@reg("pop", "Cartoon pop for text/stickers appearing", "ui")
def pop():
    d = 0.18
    t = t_axis(d)
    x = sine(np.geomspace(300, 1100, len(t)), d) * ar(d, 0.003, 3)
    return normalize(x, -6)


@reg("ding", "Bright notification ding (FM bell)", "ui")
def ding():
    d = 1.2
    x = fm_bell(midi_hz(88), d, ratio=2.0, index=2.5, tau=0.35) + 0.4 * fm_bell(midi_hz(95), d, 3.0, 1.5, 0.25)
    return normalize(_room(x, 0.2, 1.0), -6)


@reg("tick", "Clock tick", "ui")
def tick():
    d = 0.05
    x = bandpass(white(d, 81), 2500, 8000) * exp_decay(d, 0.003)
    return normalize(x, -10)


@reg("pluck_note", "Single plucked string note (C5)", "ui")
def pluck_note():
    return normalize(_room(karplus(midi_hz(72), 1.2, 0.995, 0.6, 3), 0.15, 0.8), -8)


@reg("glass_clink", "Two glasses clinking", "foley")
def glass_clink():
    d = 1.0
    modes = [2630, 3410, 5120, 6890]
    x = sum(sine(f, d) * exp_decay(d, 0.25 / (i + 1)) for i, f in enumerate(modes)) / 3
    return normalize(_room(x * ar(d, 0.001, 1), 0.2, 1.0), -8)


@reg("heartbeat", "Lub-dub heartbeat, one beat (~0.8 s)", "body")
def heartbeat():
    d = 0.8
    x = np.zeros(secs(d))
    for at, f, g in ((0.0, 55, 1.0), (0.22, 48, 0.7)):
        b = sine(f, 0.18) * ar(0.18, 0.01, 2.5) * g
        x[secs(at): secs(at) + len(b)] += b
    return normalize(lowpass(x, 200), -3)


# ============================================================================ ambiences (loopable)
@reg("room_tone", "Quiet interior room tone, 8 s loopable", "ambience", loop=True)
def room_tone():
    d = 8.0
    x = lowpass(brown(d, 91), 400) * 0.6 + lowpass(pink(d, 92), 2500) * 0.08
    x += sine(60, d) * 0.01 + sine(120, d) * 0.006
    return _loopable(pan(x, 0) + pan(lowpass(pink(d, 93), 1500) * 0.05, 0.6), -26)


@reg("rain_window", "Rain on a window, 8 s loopable", "ambience", loop=True)
def rain_window():
    d = 8.0
    bed = bandpass(pink(d, 101), 400, 6000) * 0.5
    r = np.random.default_rng(102)
    drops = np.zeros(secs(d))
    for _ in range(900):
        i = r.integers(0, len(drops) - 2000)
        drops[i: i + 600] += sine(r.uniform(1800, 5000), 600 / SR) * exp_decay(600 / SR, 0.002) * r.uniform(0.1, 0.5)
    st = np.stack([bed + drops * 0.6, bandpass(pink(d, 103), 400, 6000) * 0.5 + np.roll(drops, 7000) * 0.6], 1)
    return _loopable(st, -22)


@reg("wind", "Outdoor wind gusts, 10 s loopable", "ambience", loop=True)
def wind():
    d = 10.0
    t = t_axis(d)
    gust = 0.55 + 0.45 * np.sin(2 * np.pi * t / d * 2 + 1) * np.sin(2 * np.pi * t / d * 3)
    l = sweep_filter(pink(d, 111), 300, 300, "band", q=1.2)
    x = lowpass(pink(d, 112), 900) * gust
    return _loopable(np.stack([x + l * 0.2 * gust, np.roll(x, 3000) + l * 0.2 * gust], 1), -22)


def _loopable(x, peak_db):
    """Crossfade the last 1 s into the start so the file loops seamlessly."""
    n = secs(1.0)
    x = np.array(x, dtype=float)
    head, tail = x[:n].copy(), x[-n:].copy()
    w = np.linspace(0, 1, n)[:, None] if x.ndim == 2 else np.linspace(0, 1, n)
    x = x[:-n]
    x[:n] = head * w + tail * (1 - w)
    return normalize(x, peak_db)
