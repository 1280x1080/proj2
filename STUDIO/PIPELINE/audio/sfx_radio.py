"""Radio-station SFX (added for VIDEO_008, THE FREQUENCY THAT KNOWS TOMORROW)."""
import numpy as np

from dsp import bandpass, exp_decay, highpass, lowpass, normalize, pan, pink, saturate, secs, sine, t_axis, white
from sfx_lib import _loopable, _room, reg


@reg("radio_static", "Dead-air radio static: band-limited hiss with slow drift and crackles, 8 s loopable", "ambience", loop=True)
def radio_static():
    d = 9.0
    t = t_axis(d)
    hiss = bandpass(white(d, 11), 400, 6000) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.17 * t))
    r = np.random.default_rng(12)
    crack = np.zeros(secs(d))
    for _ in range(120):
        i = r.integers(0, len(crack) - 400)
        crack[i:i + 400] += white(400 / 48000, int(r.integers(0, 9999))) * np.exp(-np.arange(400) / 80) * r.uniform(0.2, 0.9)
    return _loopable(pan(hiss * 0.5 + bandpass(crack, 800, 5000), 0.0), -24)


@reg("speaker_on", "Studio speakers powering on: relay click, low thump, crackle", "radio")
def speaker_on():
    d = 0.9
    t = t_axis(d)
    click = bandpass(white(0.03, 21), 1500, 7000) * exp_decay(0.03, 0.004)
    thump = sine(55 * np.exp(-t * 6) + 30, d) * exp_decay(d, 0.09)
    crack = bandpass(white(d, 22), 900, 6000) * exp_decay(d, 0.12) * (np.random.default_rng(23).random(secs(d)) > 0.85)
    x = thump * 0.9 + crack * 0.6
    x[: len(click)] += click
    return normalize(_room(x, 0.15, 0.6), -3)


@reg("crackle_burst", "Loud speaker crackle burst, 0.7 s", "radio")
def crackle_burst():
    d = 0.7
    r = np.random.default_rng(31)
    gate = np.repeat(r.random(int(d * 80)) > 0.45, secs(d) // int(d * 80) + 1)[: secs(d)]
    x = bandpass(white(d, 32), 500, 7000) * gate * exp_decay(d, 0.35)
    return normalize(saturate(x, 2.0), -4)


@reg("desk_phone_ring", "Office desk phone: electronic double trill, one 1.4 s ring", "radio")
def desk_phone_ring():
    d = 1.4
    t = t_axis(d)
    trill = (np.sign(np.sin(2 * np.pi * 20 * t)) > 0).astype(float)
    tone = sine(1046, d) * trill + sine(1318, d) * (1 - trill)
    env = ((t < 0.45) | ((t > 0.6) & (t < 1.05))).astype(float)
    return normalize(_room(bandpass(tone * lowpass(env, 200), 600, 5000), 0.15, 0.6), -5)


@reg("computer_beep", "Computer alert: two short sine beeps", "radio")
def computer_beep():
    d = 0.5
    x = np.zeros(secs(d))
    for t0 in (0.0, 0.16):
        b = sine(1760, 0.09) * np.hanning(secs(0.09))
        x[secs(t0):secs(t0) + len(b)] += b
    return normalize(x, -10)


@reg("transmitter_hum", "Transmitter rack: transformer hum + fans, 8 s loopable", "ambience", loop=True)
def transmitter_hum():
    d = 9.0
    t = t_axis(d)
    hum = sine(50, d) * 0.4 + sine(100, d) * 0.3 + sine(150, d) * 0.1
    fan = bandpass(pink(d, 41), 200, 1500) * (0.8 + 0.2 * np.sin(2 * np.pi * 3.1 * t))
    return _loopable(pan(hum * 0.5 + fan * 0.4, -0.3), -26)
