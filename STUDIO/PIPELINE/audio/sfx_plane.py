"""Airliner SFX (added for VIDEO_010, FLIGHT 417)."""
import numpy as np

from dsp import bandpass, brown, exp_decay, highpass, lowpass, normalize, pan, pink, saturate, secs, sine, t_axis, white
from sfx_lib import _loopable, _room, reg


@reg("cabin_drone", "Airliner cabin at cruise: engine drone, air-conditioning hiss, slow beating, 10 s loopable", "ambience", loop=True)
def cabin_drone():
    d = 11.0
    t = t_axis(d)
    eng = (sine(92, d) + 0.6 * sine(93.1, d) + 0.35 * sine(184.5, d)) * 0.25 * (0.85 + 0.15 * np.sin(2 * np.pi * 0.21 * t))
    rumble = lowpass(brown(d, 101), 160) * 0.9
    air = bandpass(pink(d, 102), 700, 5000) * 0.22
    return _loopable(pan(eng + rumble + air, 0.0), -22)


@reg("cabin_ding", "Cabin chime: single soft two-partial 'bing' before an announcement / seat-belt sign", "plane")
def cabin_ding():
    d = 1.6
    x = (sine(587, d) + 0.5 * sine(1174, d) + 0.2 * sine(1761, d)) * exp_decay(d, 0.4)
    return normalize(_room(x, 0.2, 0.8), -8)


@reg("radar_ping", "Radar sweep ping: short high sine blip with a tail", "plane")
def radar_ping():
    d = 0.9
    x = sine(1320, d) * exp_decay(d, 0.16)
    return normalize(_room(x, 0.3, 1.0), -10)


@reg("ghost_drone", "Something huge and wrong flying beside you: detuned sub drone + hollow wind choir, 8 s loopable", "ambience", loop=True)
def ghost_drone():
    d = 9.0
    t = t_axis(d)
    sub = (sine(55, d) + sine(58.3, d) + 0.5 * sine(82.4, d)) * 0.3
    choir = sum(bandpass(pink(d, 110 + k), f, f * 1.06) * (0.6 + 0.4 * np.sin(2 * np.pi * (0.13 + 0.05 * k) * t))
                for k, f in enumerate((311, 370, 466))) * 2.5
    return _loopable(pan(sub + choir, 0.0), -20)


@reg("turbulence", "Cabin shudder: low rumble burst with rattling plastic, 1.5 s", "plane")
def turbulence():
    d = 1.5
    t = t_axis(d)
    env = np.sin(np.pi * t / d) ** 0.7
    rum = lowpass(brown(d, 121), 120) * 2.0
    rattle = bandpass(white(d, 122), 1500, 5000) * (np.random.default_rng(123).random(secs(d)) > 0.93) * 0.8
    return normalize(_room((rum + lowpass(rattle, 4000)) * env, 0.2, 0.6), -6)


@reg("belt_click", "Seat-belt buckle released: metal clack + strap slide", "plane")
def belt_click():
    d = 0.5
    x = bandpass(white(d, 131), 1500, 8000) * exp_decay(d, 0.012)
    x[secs(0.08):] += (bandpass(white(d, 132), 400, 2500) * exp_decay(d, 0.09))[: len(x) - secs(0.08)] * 0.4
    return normalize(_room(x, 0.15, 0.4), -6)
