"""Electric / household SFX (added for VIDEO_001)."""
import numpy as np

from dsp import ar, bandpass, exp_decay, highpass, lowpass, normalize, pan, pink, secs, sine, t_axis, white
from sfx_lib import _loopable, _room, reg


@reg("lamp_buzz", "Mains hum of an old lamp: 50/100 Hz hum + faint crackle, 6 s loopable", "ambience", loop=True)
def lamp_buzz():
    d = 7.0
    t = t_axis(d)
    hum = sine(100, d) * 0.5 + sine(200, d) * 0.25 + sine(300, d) * 0.1 + sine(50, d) * 0.2
    hum *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.31 * t)
    r = np.random.default_rng(5)
    crackle = np.zeros(secs(d))
    for _ in range(40):
        i = r.integers(0, len(crackle) - 400)
        crackle[i:i + 400] += highpass(white(400 / 48000, int(r.integers(0, 999))), 3000) * exp_decay(400 / 48000, 0.002) * r.uniform(0.1, 0.4)
    return _loopable(pan(hum * 0.4 + crackle, -0.2), -30)


@reg("flicker_zap", "Bulb flicker: electric crackle with a hum dropout (0.3 s)", "foley")
def flicker_zap():
    d = 0.32
    t = t_axis(d)
    gate = ((t < 0.07) | ((t > 0.12) & (t < 0.17))).astype(float)
    zap = bandpass(white(d, 61), 1500, 9000) * gate * (0.5 + 0.5 * np.random.default_rng(3).random(len(t)) ** 4)
    hum = (sine(100, d) + 0.5 * sine(200, d)) * (1 - gate) * 0.35
    thunk = sine(70, d) * exp_decay(d, 0.03) * 0.5
    return normalize(_room(zap * 0.8 + hum + thunk, 0.12, 0.5), -3)


@reg("door_knock", "Single knuckle knock on a wooden door, heard from inside", "foley")
def door_knock():
    d = 0.45
    modes = [(118, 0.07), (236, 0.045), (410, 0.03), (980, 0.012)]
    x = sum(sine(f, d) * exp_decay(d, tau) / (i + 1) ** 0.6 for i, (f, tau) in enumerate(modes))
    x += lowpass(white(d, 9), 2500) * exp_decay(d, 0.006) * 0.8
    return normalize(_room(x, 0.25, 0.8, 3500), -2)
