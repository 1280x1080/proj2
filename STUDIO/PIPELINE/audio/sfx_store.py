"""Night convenience-store SFX (added for VIDEO_005, OPEN 24/7)."""
import numpy as np

from dsp import (ar, bandpass, brown, exp_decay, fm_bell, highpass, lowpass, midi_hz, normalize, pan, pink, saturate,
                 secs, sine, t_axis, white)
from sfx_lib import _loopable, _room, reg


@reg("door_chime", "Shop door chime: two-tone ding-dong, slightly detuned / wrong", "store")
def door_chime():
    d = 2.4
    x = np.zeros(secs(d))
    for t0, m, det in ((0.0, 79, 0.0), (0.42, 75, -0.35)):
        b = fm_bell(midi_hz(m + det), d - t0, ratio=2.76, index=1.8, tau=0.45)
        b += 0.5 * fm_bell(midi_hz(m + det) * 1.013, d - t0, ratio=2.76, index=1.2, tau=0.4)  # beating = detuned
        x[secs(t0):] += b[: len(x) - secs(t0)]
    return normalize(_room(x, 0.25, 1.4), -6)


@reg("old_phone_ring", "Old wall phone: mechanical bell ringer burst, 1.6 s", "store")
def old_phone_ring():
    d = 1.6
    t = t_axis(d)
    clap = (np.sin(2 * np.pi * 20 * t) > 0).astype(float)  # 20 Hz hammer
    bell = (sine(1180, d) + 0.6 * sine(1420, d) + 0.35 * sine(2650, d)) * (0.6 + 0.4 * clap)
    bell += bandpass(white(d, 3), 2000, 7000) * clap * 0.15
    env = np.clip(t / 0.02, 0, 1) * np.clip((d - t) / 0.08, 0, 1)
    return normalize(_room(saturate(bell * env, 1.3), 0.2, 0.8), -4)


@reg("power_down", "Power cut: relay thunk, fluorescent hum dropping out, 1.8 s", "store")
def power_down():
    d = 1.8
    t = t_axis(d)
    thunk = sine(60 * np.exp(-t * 3) + 35, d) * exp_decay(d, 0.12) + lowpass(white(d, 9), 600) * exp_decay(d, 0.03)
    hum = (sine(120, d) * 0.4 + sine(240, d) * 0.2) * np.clip(1 - t / 0.5, 0, 1) ** 2
    pitch_drop = sine(np.geomspace(240, 40, len(t)), d) * np.clip(1 - t / 0.9, 0, 1) * 0.25
    return normalize(_room(thunk + hum + pitch_drop, 0.3, 1.2, 2500), -2)


@reg("crt_hum", "CRT security monitor: 15.7 kHz whine (soft) + 60 Hz hum + faint static, 6 s loopable", "ambience",
     loop=True)
def crt_hum():
    d = 7.0
    hum = sine(60, d) * 0.3 + sine(120, d) * 0.15
    whine = sine(9800, d) * 0.03
    static = bandpass(white(d, 21), 2000, 8000) * 0.05
    return _loopable(pan(hum + whine + static, 0.15), -28)


@reg("rain_outside", "Steady night rain on asphalt + store awning, 10 s loopable", "ambience", loop=True)
def rain_outside():
    d = 11.0
    bed = bandpass(pink(d, 31), 300, 7000)
    r = np.random.default_rng(32)
    taps = np.zeros(secs(d))
    for _ in range(2200):
        i = r.integers(0, len(taps) - 500)
        taps[i:i + 500] += highpass(white(500 / 48000, int(r.integers(0, 9999))), 1500) * exp_decay(500 / 48000, 0.002) * r.uniform(0.05, 0.3)
    low = lowpass(brown(d, 33), 200) * 0.4
    l = bed * 0.6 + taps + low
    rr = np.roll(bed, 7000) * 0.6 + np.roll(taps, 3000) + low
    return _loopable(np.stack([l, rr], 1), -18)


@reg("drip", "Single water drop on tile", "foley")
def drip():
    d = 0.5
    t = t_axis(d)
    x = sine(1400 * np.exp(-t * 18) + 900, d) * exp_decay(d, 0.05) + highpass(white(d, 41), 3000) * exp_decay(d, 0.003) * 0.3
    return normalize(_room(x, 0.3, 0.8), -10)


@reg("wet_steps", "Three slow barefoot steps on a wet tile floor", "foley")
def wet_steps():
    d = 2.2
    x = np.zeros(secs(d))
    for k, t0 in enumerate((0.0, 0.7, 1.4)):
        n = secs(0.35)
        slap = bandpass(white(0.35, 50 + k), 300, 4000) * ar(0.35, 0.004, 4) + sine(110, 0.35) * exp_decay(0.35, 0.03) * 0.5
        squelch = bandpass(white(0.35, 60 + k), 900, 3000) * ar(0.35, 0.05, 2) * 0.3
        x[secs(t0):secs(t0) + n] += (slap + squelch)[:n]
    return normalize(_room(x, 0.2, 0.7), -8)


@reg("card_slap", "Laminated card slapped flat on a counter", "foley")
def card_slap():
    d = 0.5
    x = bandpass(white(d, 71), 400, 6000) * exp_decay(d, 0.012) + sine(180, d) * exp_decay(d, 0.04) * 0.6
    return normalize(_room(x, 0.15, 0.5), -4)


@reg("mop_slam", "Wooden mop handle slammed across a counter", "foley")
def mop_slam():
    d = 0.9
    modes = [(240, 0.06), (520, 0.035), (1100, 0.02)]
    x = sum(sine(f, d) * exp_decay(d, tau) for f, tau in modes)
    x += bandpass(white(d, 81), 500, 5000) * exp_decay(d, 0.01)
    return normalize(_room(saturate(x, 1.6), 0.2, 0.6), -2)


@reg("glitch", "Short digital glitch / static burst (HUD, monitor)", "ui")
def glitch():
    d = 0.35
    r = np.random.default_rng(91)
    x = white(d, 92) * (r.random(secs(d)) > 0.7)
    x = bandpass(x, 800, 9000) * np.repeat(r.random(int(d * 60)) > 0.4, secs(d) // int(d * 60) + 1)[: secs(d)]
    return normalize(x + sine(1000, d) * 0.1 * (r.random(secs(d)) > 0.5), -10)
