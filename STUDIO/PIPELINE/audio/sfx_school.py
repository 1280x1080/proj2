"""School SFX (added for VIDEO_009, THE LAST BELL)."""
import numpy as np

from dsp import bandpass, brown, exp_decay, highpass, lowpass, normalize, pan, pink, saturate, secs, sine, t_axis, white
from sfx_lib import _loopable, _room, reg


@reg("classroom_after", "Empty classroom after school: HVAC air, fluorescent hum, far-off kids outside, 10 s loopable",
     "ambience", loop=True)
def classroom_after():
    d = 11.0
    t = t_axis(d)
    air = lowpass(pink(d, 41), 900) * 0.6
    hum = (sine(120, d) * 0.5 + sine(240, d) * 0.2) * 0.04
    kids = bandpass(brown(d, 42), 300, 1800) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t) ** 2) * 0.5
    return _loopable(pan(air + hum + kids, 0.0), -26)


@reg("lockdown_alarm", "School lockdown alarm in the hallway: harsh two-tone whoop, 3 s", "school")
def lockdown_alarm():
    d = 3.0
    t = t_axis(d)
    f = np.where((t * 2.5) % 1 < 0.5, 880, 660)
    x = saturate(np.sign(np.sin(2 * np.pi * np.cumsum(f) / 48000)) * 0.5, 1.5)
    x = bandpass(x, 400, 4000) * np.minimum(1, t * 20) * np.minimum(1, (d - t) * 10)
    return normalize(_room(x, 0.35, 1.4, 3000), -5)


@reg("pa_chime", "Old school PA: click + two-note chime before an announcement", "school")
def pa_chime():
    d = 1.6
    x = np.zeros(secs(d))
    x[: secs(0.03)] += bandpass(white(0.03, 51), 1500, 6000) * exp_decay(0.03, 0.004)
    for t0, fq in ((0.15, 784), (0.65, 622)):
        n = secs(0.9)
        tone = (sine(fq, 0.9) + 0.3 * sine(fq * 2, 0.9)) * exp_decay(0.9, 0.35)
        x[secs(t0):secs(t0) + n] += tone[: len(x) - secs(t0)]
    return normalize(saturate(bandpass(x, 350, 3200), 1.4), -6)


@reg("lock_click", "Door lock thrown: metal clack", "school")
def lock_click():
    d = 0.35
    x = bandpass(white(d, 61), 1200, 7000) * exp_decay(d, 0.015)
    x[secs(0.06):] += (bandpass(white(d, 62), 600, 4000) * exp_decay(d, 0.03))[: len(x) - secs(0.06)] * 0.8
    return normalize(_room(x, 0.2, 0.5), -6)


@reg("handle_turn", "Metal lever handle slowly pressed down: squeak + latch strain", "school")
def handle_turn():
    d = 1.6
    t = t_axis(d)
    sq = sine(900 + 300 * t, d) * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * t)) * 0.15
    grind = bandpass(white(d, 71), 500, 3000) * (0.4 + 0.6 * np.random.default_rng(72).random(secs(d)) ** 4)
    x = (sq + grind * 0.5) * np.minimum(1, t * 6) * np.minimum(1, (d - t) * 6)
    x[-secs(0.2):] += (bandpass(white(0.2, 73), 800, 5000) * exp_decay(0.2, 0.02))
    return normalize(_room(x, 0.2, 0.6), -6)


@reg("pencil_scribble", "Pencil scribbling on paper, 1.2 s", "school")
def pencil_scribble():
    d = 1.2
    t = t_axis(d)
    x = bandpass(white(d, 81), 2000, 9000) * (0.3 + 0.7 * (np.sin(2 * np.pi * 6 * t) > 0))
    return normalize(x * np.minimum(1, (d - t) * 8), -16)


@reg("chair_scrape", "Chair legs scraping on a classroom floor", "school")
def chair_scrape():
    d = 0.8
    t = t_axis(d)
    x = bandpass(saturate(sine(180 + 60 * np.sin(t * 30), d) + white(d, 91) * 0.4, 2), 150, 2500) * np.sin(np.pi * t / d)
    return normalize(_room(x, 0.2, 0.6), -10)


@reg("light_buzz_out", "Fluorescent lights clunk off, emergency red light buzz starts", "school")
def light_buzz_out():
    d = 1.4
    x = np.zeros(secs(d))
    x[: secs(0.1)] += lowpass(white(0.1, 95), 600) * exp_decay(0.1, 0.03)
    tail = (sine(100, d - 0.2) + 0.4 * sine(300, d - 0.2)) * 0.2 * np.minimum(1, t_axis(d - 0.2) * 3)
    x[secs(0.2):secs(0.2) + len(tail)] += tail[: len(x) - secs(0.2)]
    return normalize(_room(x, 0.2, 0.6), -8)


@reg("chalk_write", "Chalk writing fast on a blackboard: scratchy strokes + taps, 1.6 s", "school")
def chalk_write():
    d = 1.6
    t = t_axis(d)
    r = np.random.default_rng(201)
    env = np.zeros(secs(d))
    for k in range(11):
        i = secs(0.05 + k * 0.14)
        n = secs(float(r.uniform(0.06, 0.12)))
        env[i:i + n] = np.hanning(n) * r.uniform(0.6, 1.0)
    x = bandpass(white(d, 202), 1800, 7000) * env * (0.7 + 0.3 * np.sin(2 * np.pi * 90 * t))
    return normalize(_room(x, 0.25, 0.7), -8)
