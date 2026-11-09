"""Bedroom-at-night / phone / door SFX (added for VIDEO_004, THE ROOM THAT WASN'T THERE)."""
import numpy as np

from dsp import (adsr, ar, bandpass, brown, exp_decay, fm_bell, highpass, lowpass, midi_hz, normalize, pan, pink,
                 saturate, secs, sine, sweep_filter, t_axis, white)
from sfx_lib import _loopable, _room, reg


def _speaker(x):
    """Small phone speaker colour."""
    return saturate(bandpass(x, 500, 5000), 1.6)


@reg("phone_ring", "Phone ringtone through a small speaker, one 2.2 s ring cycle", "phone")
def phone_ring():
    d = 2.2
    t = t_axis(d)
    x = np.zeros(len(t))
    for k in range(8):  # 8 alternating marimba-ish beeps, then a gap
        t0 = k * 0.13
        n = secs(0.12)
        f = 1046 if k % 2 == 0 else 1318
        b = (sine(f, 0.12) + 0.4 * sine(2 * f, 0.12)) * ar(0.12, 0.004, 2.5)
        x[secs(t0): secs(t0) + n] += b[:n]
    return normalize(_room(_speaker(x), 0.12, 0.6), -4)


@reg("phone_vibrate", "Phone vibrating on a wooden nightstand, 1.2 s", "phone")
def phone_vibrate():
    d = 1.2
    t = t_axis(d)
    gate = ((t % 0.6) < 0.42).astype(float)
    gate = lowpass(gate, 60)
    buzz = sine(158, d) * 0.6 + sine(316, d) * 0.25
    rattle = bandpass(white(d, 31), 150, 1800) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 158 * t)))
    return normalize(_room((buzz + rattle * 0.5) * gate, 0.1, 0.4), -6)


@reg("text_ping", "Soft incoming-text chime (phone speaker)", "phone")
def text_ping():
    d = 0.9
    x = fm_bell(midi_hz(84), d, 2.0, 1.2, 0.18)
    x[secs(0.11):] += fm_bell(midi_hz(91), d - 0.11, 2.0, 1.0, 0.2)[: len(x) - secs(0.11)]
    return normalize(_speaker(x) * 0.8 + x * 0.2, -8)


@reg("knock_slow", "One heavy, slow knuckle knock on a bedroom door (from inside the room)", "foley")
def knock_slow():
    d = 0.7
    modes = [(92, 0.09), (184, 0.06), (330, 0.035), (720, 0.015)]
    x = sum(sine(f, d) * exp_decay(d, tau) / (i + 1) ** 0.5 for i, (f, tau) in enumerate(modes))
    x += lowpass(white(d, 13), 1800) * exp_decay(d, 0.008) * 0.9
    return normalize(_room(saturate(x, 1.4), 0.3, 1.0, 3000), -2)


@reg("handle_creak", "Door lever handle slowly turning: metal squeak + latch friction, 1.8 s", "foley")
def handle_creak():
    d = 1.8
    t = t_axis(d)
    f = 820 + 380 * (t / d) + 40 * np.sin(2 * np.pi * 9 * t)
    squeak = np.sin(2 * np.pi * np.cumsum(f) / 48000) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t) ** 2)
    squeak = bandpass(squeak, 600, 4000) * np.sin(np.pi * t / d) ** 0.6
    friction = bandpass(white(d, 41), 1500, 6000) * 0.25 * np.sin(np.pi * t / d)
    latch = np.zeros(len(t))
    lt = bandpass(white(0.04, 42), 1500, 6000) * exp_decay(0.04, 0.005)
    latch[secs(d - 0.2): secs(d - 0.2) + len(lt)] = lt
    return normalize(_room(squeak * 0.6 + friction + latch, 0.2, 0.8), -6)


@reg("door_creak_long", "Wooden door creaking open a crack, low and wrong, 2.4 s", "foley")
def door_creak_long():
    d = 2.4
    t = t_axis(d)
    f = 210 + 90 * np.sin(2 * np.pi * 0.7 * t) + 30 * np.sin(2 * np.pi * 5 * t)
    pulses = (np.sin(2 * np.pi * np.cumsum(f / 12) / 48000) > 0.55).astype(float)
    x = bandpass(pulses * white(d, 51), 250, 1800) * np.sin(np.pi * t / d) ** 0.5
    x += sweep_filter(white(d, 52) * 0.15, 300, 900, "band", q=4)
    return normalize(_room(x, 0.3, 1.2, 2500), -5)


@reg("scratch_wood", "Nails slowly scratching wood from the other side, 1.6 s", "foley")
def scratch_wood():
    d = 1.6
    t = t_axis(d)
    strokes = np.zeros(len(t))
    for k, (t0, ln) in enumerate(((0.0, 0.45), (0.55, 0.4), (1.05, 0.5))):
        a, b = secs(t0), secs(t0 + ln)
        u = np.linspace(0, 1, b - a)
        strokes[a:b] = np.sin(np.pi * u) ** 0.7
    grit = bandpass(white(d, 61), 1800, 7000) * (0.4 + 0.6 * (np.random.default_rng(6).random(len(t)) > 0.6))
    x = grit * strokes * (0.7 + 0.3 * np.sin(2 * np.pi * 37 * t))
    x += lowpass(brown(d, 62), 300) * strokes * 0.4  # through the wood
    return normalize(_room(lowpass(x, 5000), 0.25, 0.9, 3000), -6)


@reg("breath_close", "Slow breathing very close to a door, 3 s", "body")
def breath_close():
    d = 3.0
    t = t_axis(d)
    env = np.clip(np.sin(2 * np.pi * t / 1.5), 0, None) ** 1.5 * 0.8 + np.clip(-np.sin(2 * np.pi * t / 1.5), 0, None) ** 2 * 0.5
    x = bandpass(pink(d, 71), 300, 2600) * env
    return normalize(_room(x, 0.12, 0.5), -10)


@reg("floor_creak", "Single floorboard creak in the hallway, 0.9 s", "foley")
def floor_creak():
    d = 0.9
    t = t_axis(d)
    f = 140 + 60 * np.sin(2 * np.pi * 1.1 * t)
    pulses = (np.sin(2 * np.pi * np.cumsum(f / 6) / 48000) > 0.6).astype(float)
    x = bandpass(pulses * white(d, 81), 180, 1200) * np.sin(np.pi * t / d)
    return normalize(_room(x, 0.35, 1.0, 2000), -8)


@reg("tinnitus", "Silence-ringing: faint high tone over still air, 6 s loopable", "ambience", loop=True)
def tinnitus():
    d = 7.0
    t = t_axis(d)
    ring = sine(6400, d) * 0.12 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.2 * t)) + sine(3200, d) * 0.03
    air = lowpass(pink(d, 91), 600) * 0.15
    return _loopable(pan(ring + air, 0.0), -30)


@reg("night_room", "Bedroom at 3 AM: fridge hum through the wall, distant traffic, soft wind, 10 s loopable", "ambience",
     loop=True)
def night_room():
    d = 11.0
    t = t_axis(d)
    hum = (sine(60, d) * 0.5 + sine(120, d) * 0.3 + sine(180, d) * 0.08) * (0.9 + 0.1 * np.sin(2 * np.pi * 0.13 * t))
    traffic = lowpass(brown(d, 101), 220) * (0.6 + 0.4 * np.sin(2 * np.pi * t / d * 2) ** 2)
    wind = bandpass(pink(d, 102), 200, 1200) * (0.4 + 0.3 * np.sin(2 * np.pi * t / d * 3 + 1))
    l = hum * 0.25 + traffic * 0.8 + wind * 0.35
    r = hum * 0.22 + np.roll(traffic, 9000) * 0.8 + np.roll(wind, 4000) * 0.35
    return _loopable(np.stack([l, r], 1), -22)
