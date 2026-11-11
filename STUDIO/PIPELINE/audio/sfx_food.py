"""Food / delivery SFX (added for VIDEO_012, ORDER #000)."""
import numpy as np

from dsp import bandpass, exp_decay, highpass, lowpass, normalize, pan, pink, saturate, secs, sine, t_axis, white
from sfx_lib import _room, reg


@reg("slurp", "Noodle slurp + a chew, through a phone speaker, 1.1 s", "food")
def slurp():
    d = 1.1
    t = t_axis(d)
    sl = bandpass(white(d, 171), 900 + 2200 * t / d, 3200 + 2600 * t / d) if False else bandpass(white(d, 171), 1200, 5200)
    sl = sl * np.clip(t / 0.5, 0, 1) * (t < 0.55) * (0.6 + 0.4 * np.sin(2 * np.pi * 38 * t))
    chew = np.zeros(secs(d))
    for t0 in (0.68, 0.86):
        n = secs(0.1)
        chew[secs(t0):secs(t0) + n] += lowpass(white(0.1, int(t0 * 100)), 900)[:n] * np.hanning(n)
    return normalize(bandpass(sl + chew * 1.5, 400, 3800), -12)


@reg("paper_rustle", "Paper bag rustling / crinkling by itself, 1.2 s", "food")
def paper_rustle():
    d = 1.2
    r = np.random.default_rng(181)
    x = np.zeros(secs(d))
    for _ in range(46):
        i = int(r.integers(0, len(x) - 1500))
        n = int(r.integers(300, 1400))
        x[i:i + n] += highpass(white(n / 48000, int(r.integers(0, 9999))), 2500)[:n] * np.exp(-np.arange(n) / (n / 4)) * r.uniform(0.3, 1.0)
    return normalize(_room(x, 0.12, 0.4), -8)


@reg("order_chime", "Food app: order placed - bright three-note chime", "food")
def order_chime():
    d = 0.9
    x = np.zeros(secs(d))
    for j, f in enumerate((784, 988, 1319)):
        n = secs(0.5)
        seg = (sine(f, 0.5) + 0.3 * sine(f * 2, 0.5)) * exp_decay(0.5, 0.16)
        i = secs(j * 0.11)
        x[i:i + n] += seg[: len(x) - i]
    return normalize(x, -10)


@reg("cam_static", "Door camera feed: hiss + 50 Hz buzz + dropouts, 6 s loopable", "ambience", loop=True)
def cam_static():
    from sfx_lib import _loopable
    d = 7.0
    t = t_axis(d)
    x = bandpass(white(d, 191), 1500, 6000) * 0.4 + sine(100, d) * 0.08 + sine(50, d) * 0.1
    x = x * (0.8 + 0.2 * np.sign(np.sin(2 * np.pi * 0.7 * t)))
    return _loopable(pan(x, 0.0), -26)


@reg("run_steps", "Four fast barefoot steps on a wooden floor", "food")
def run_steps():
    d = 1.0
    x = np.zeros(secs(d))
    for k in range(4):
        n = secs(0.14)
        i = secs(0.05 + k * 0.21)
        x[i:i + n] += (lowpass(white(0.14, 200 + k), 500)[:n] * np.exp(-np.arange(n) / 900)) * (1.0 - 0.1 * k)
    return normalize(_room(x, 0.2, 0.5), -8)
