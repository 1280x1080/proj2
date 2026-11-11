"""Gaming / voice-chat SFX + jumpscare stings (added for VIDEO_011, LAST ONE IN THE CALL)."""
import numpy as np

from dsp import bandpass, exp_decay, highpass, lowpass, normalize, pan, pink, saturate, secs, sine, t_axis, white
from sfx_lib import _loopable, _room, reg


@reg("vc_leave", "Voice chat: someone left the call - two soft descending tones", "gaming")
def vc_leave():
    d = 0.5
    x = np.zeros(secs(d))
    for t0, f in ((0.0, 660), (0.16, 440)):
        n = secs(0.22)
        x[secs(t0):secs(t0) + n] += sine(f, 0.22) * np.hanning(n)
    return normalize(x, -10)


@reg("vc_join", "Voice chat: someone joined - two soft rising tones", "gaming")
def vc_join():
    d = 0.5
    x = np.zeros(secs(d))
    for t0, f in ((0.0, 440), (0.16, 660)):
        n = secs(0.22)
        x[secs(t0):secs(t0) + n] += sine(f, 0.22) * np.hanning(n)
    return normalize(x, -10)


@reg("pc_room", "Bedroom at night with a gaming PC: fan whirr, faint coil whine, 10 s loopable", "ambience", loop=True)
def pc_room():
    d = 11.0
    fan = bandpass(pink(d, 141), 180, 1400) * 0.7
    whine = sine(7400, d) * 0.004
    low = lowpass(pink(d, 142), 120) * 0.5
    return _loopable(pan(fan + whine + low, 0.0), -27)


@reg("keys_mouse", "Fast keyboard taps and mouse clicks, 1.6 s", "gaming")
def keys_mouse():
    d = 1.6
    x = np.zeros(secs(d))
    r = np.random.default_rng(143)
    for _ in range(16):
        i = int(r.integers(0, len(x) - 2000))
        n = 1400
        x[i:i + n] += bandpass(white(n / 48000, int(r.integers(0, 9999))), 1200, 6000)[:n] * np.exp(-np.arange(n) / 160) * r.uniform(0.4, 1.0)
    return normalize(_room(x, 0.1, 0.3), -14)


@reg("game_shots", "Cartoony game gunfire through headphones: five quick laser-pop shots + a win jingle note", "gaming")
def game_shots():
    d = 1.4
    x = np.zeros(secs(d))
    for k in range(5):
        n = secs(0.12)
        t = np.arange(n) / 48000
        shot = np.sin(2 * np.pi * (900 * np.exp(-t * 30) + 180) * t) * np.exp(-t * 28)
        x[secs(0.05 + k * 0.13):secs(0.05 + k * 0.13) + n] += shot
    for j, f in enumerate((784, 988, 1175)):
        n = secs(0.3)
        x[secs(0.8 + j * 0.1):secs(0.8 + j * 0.1) + n] += sine(f, 0.3) * exp_decay(0.3, 0.12) * 0.6
    return normalize(bandpass(x, 300, 5000), -10)


@reg("mic_scream", "A scream through a cheap headset mic: clipped, peaking, cut off dead", "scare")
def mic_scream():
    d = 0.75
    t = t_axis(d)
    f = 620 + 380 * np.minimum(1, t * 6) + 40 * np.sin(2 * np.pi * 11 * t)
    ph = 2 * np.pi * np.cumsum(f) / 48000
    voice = np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.4 * np.sin(3 * ph) + 0.5 * bandpass(white(d, 151), 1500, 5000)
    x = saturate(bandpass(voice, 500, 3800), 6.0) * np.minimum(1, t * 30)
    x[-secs(0.01):] *= np.linspace(1, 0, secs(0.01))  # the mic cuts
    return normalize(x, -3)


@reg("jumpscare_sting", "Jumpscare: slammed dissonant string cluster + sub hit + noise burst, 1.3 s", "scare")
def jumpscare_sting():
    d = 1.3
    t = t_axis(d)
    cluster = sum(np.sign(np.sin(2 * np.pi * f * t + k)) * 0.5 + np.sin(2 * np.pi * f * 1.01 * t) for k, f in
                  enumerate((466, 493, 622, 659, 932, 987)))
    cluster = bandpass(cluster, 300, 6000) * np.exp(-t * 2.2)
    sub = sine(48 * np.exp(-t * 3) + 34, d) * exp_decay(d, 0.35) * 3.0
    burst = highpass(white(d, 161), 2000) * np.exp(-t * 14) * 2.0
    return normalize(_room(saturate(cluster * 0.5 + sub + burst, 2.0), 0.25, 1.2), -1.5)
