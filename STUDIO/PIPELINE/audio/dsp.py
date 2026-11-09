"""dsp.py - small procedural-audio toolkit (numpy/scipy only).

Every function works on float32/float64 mono arrays at SR (48 kHz) unless noted.
Stereo signals are shape (n, 2).
"""
from __future__ import annotations

import numpy as np
from scipy import signal

SR = 48000
_rng = np.random.default_rng(1234)


def rng(seed=None):
    return np.random.default_rng(seed) if seed is not None else _rng


def secs(n):
    return int(round(n * SR))


def t_axis(dur):
    return np.arange(secs(dur)) / SR


# ----------------------------------------------------------------------------- noise colours
def white(dur, seed=None):
    return rng(seed).standard_normal(secs(dur))


def _shaped(dur, exponent, seed=None):
    n = secs(dur)
    if n == 0:
        return np.zeros(0)
    spec = np.fft.rfft(rng(seed).standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1] if len(f) > 1 else 1.0
    spec *= f ** (-exponent / 2.0)
    x = np.fft.irfft(spec, n)
    return x / (np.max(np.abs(x)) + 1e-12)


def pink(dur, seed=None):
    return _shaped(dur, 1.0, seed)


def brown(dur, seed=None):
    return _shaped(dur, 2.0, seed)


def blue(dur, seed=None):
    return _shaped(dur, -1.0, seed)


# ----------------------------------------------------------------------------- filters
def _sos(kind, f, order=2):
    nyq = SR / 2
    if isinstance(f, (tuple, list)):
        wn = [max(1.0, min(nyq * 0.999, x)) / nyq for x in f]
    else:
        wn = max(1.0, min(nyq * 0.999, f)) / nyq
    return signal.butter(order, wn, btype=kind, output="sos")


def lowpass(x, f, order=2):
    return signal.sosfilt(_sos("low", f, order), x, axis=0)


def highpass(x, f, order=2):
    return signal.sosfilt(_sos("high", f, order), x, axis=0)


def bandpass(x, lo, hi, order=2):
    return signal.sosfilt(_sos("band", (lo, hi), order), x, axis=0)


def peaking(x, f, gain_db, q=1.0):
    """RBJ peaking EQ."""
    a = 10 ** (gain_db / 40)
    w = 2 * np.pi * f / SR
    al = np.sin(w) / (2 * q)
    b = [1 + al * a, -2 * np.cos(w), 1 - al * a]
    aa = [1 + al / a, -2 * np.cos(w), 1 - al / a]
    return signal.lfilter(np.array(b) / aa[0], np.array(aa) / aa[0], x, axis=0)


def shelf(x, f, gain_db, high=True):
    """RBJ shelving EQ (S=1)."""
    a = 10 ** (gain_db / 40)
    w = 2 * np.pi * f / SR
    cs, al = np.cos(w), np.sin(w) / 2 * np.sqrt(2)
    s = 1 if high else -1
    b0 = a * ((a + 1) + s * (a - 1) * cs + 2 * np.sqrt(a) * al)
    b1 = -2 * s * a * ((a - 1) + s * (a + 1) * cs)
    b2 = a * ((a + 1) + s * (a - 1) * cs - 2 * np.sqrt(a) * al)
    a0 = (a + 1) - s * (a - 1) * cs + 2 * np.sqrt(a) * al
    a1 = 2 * s * ((a - 1) - s * (a + 1) * cs)
    a2 = (a + 1) - s * (a - 1) * cs - 2 * np.sqrt(a) * al
    return signal.lfilter([b0 / a0, b1 / a0, b2 / a0], [1, a1 / a0, a2 / a0], x, axis=0)


def sweep_filter(x, f0, f1, kind="low", q=0.8, block=256):
    """Time-varying 2-pole state-variable filter, cutoff moves exponentially f0 -> f1."""
    n = len(x)
    out = np.zeros(n)
    lp = bp = 0.0
    fc = np.geomspace(max(f0, 1), max(f1, 1), n)
    g = 2 * np.sin(np.pi * np.minimum(fc, SR / 6) / SR)
    damp = 1.0 / q
    for i in range(n):  # simple loop: fine for short SFX
        hp = x[i] - lp - damp * bp
        bp += g[i] * hp
        lp += g[i] * bp
        out[i] = lp if kind == "low" else (bp if kind == "band" else hp)
    return out


# ----------------------------------------------------------------------------- envelopes
def adsr(dur, a=0.01, d=0.1, s=0.7, r=0.2):
    n = secs(dur)
    env = np.zeros(n)
    na, nd, nr = secs(a), secs(d), secs(r)
    ns = max(0, n - na - nd - nr)
    parts = [np.linspace(0, 1, na, endpoint=False), np.linspace(1, s, nd, endpoint=False),
             np.full(ns, s), np.linspace(s, 0, nr)]
    cat = np.concatenate(parts)[:n]
    env[: len(cat)] = cat
    return env


def exp_decay(dur, tau):
    return np.exp(-t_axis(dur) / max(tau, 1e-5))


def ar(dur, attack=0.005, curve=4.0):
    """Attack then exponential-ish decay to 0 over dur."""
    t = t_axis(dur)
    a = np.clip(t / max(attack, 1e-5), 0, 1)
    d = (1 - np.clip((t - attack) / max(dur - attack, 1e-5), 0, 1)) ** curve
    return a * d


def fade(x, fin=0.005, fout=0.01):
    x = np.array(x, dtype=float, copy=True)
    a, b = secs(fin), secs(fout)
    if a:
        x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim == 2 else np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)[:, None] if x.ndim == 2 else np.linspace(1, 0, b)
    return x


# ----------------------------------------------------------------------------- oscillators / instruments
def sine(freq, dur, phase=0.0):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (secs(dur),))
    return np.sin(2 * np.pi * np.cumsum(f) / SR + phase)


def saw(freq, dur, harmonics=None):
    """Band-limited-ish saw by additive synthesis (freq scalar)."""
    t = t_axis(dur)
    nh = harmonics or max(1, int((SR / 2 * 0.9) // max(freq, 1)))
    nh = min(nh, 60)
    x = np.zeros_like(t)
    for k in range(1, nh + 1):
        x += np.sin(2 * np.pi * k * freq * t) / k
    return x * (2 / np.pi)


def square(freq, dur, harmonics=None):
    t = t_axis(dur)
    nh = min(harmonics or max(1, int((SR / 2 * 0.9) // max(freq, 1))), 60)
    x = np.zeros_like(t)
    for k in range(1, nh + 1, 2):
        x += np.sin(2 * np.pi * k * freq * t) / k
    return x * (4 / np.pi)


def fm_bell(freq, dur, ratio=3.5, index=4.0, tau=None):
    """2-operator FM bell; modulation index decays faster than the amplitude."""
    t = t_axis(dur)
    tau = tau or dur / 4
    idx = index * np.exp(-t / (tau * 0.5))
    mod = np.sin(2 * np.pi * freq * ratio * t)
    return np.sin(2 * np.pi * freq * t + idx * mod) * np.exp(-t / tau)


def karplus(freq, dur, decay=0.996, bright=0.5, seed=None):
    """Karplus-Strong plucked string."""
    n = secs(dur)
    p = max(2, int(SR / freq))
    buf = rng(seed).uniform(-1, 1, p)
    buf = lowpass(buf, 800 + bright * 9000) if p > 12 else buf
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ----------------------------------------------------------------------------- reverb
def reverb_ir(dur=1.8, predelay=0.012, damp=6000, stereo=True, seed=7, decay_db=60):
    n = secs(dur)
    t = np.arange(n) / SR
    env = 10 ** (-decay_db / 20 * t / dur)
    chans = []
    for c in range(2 if stereo else 1):
        x = rng(seed + c).standard_normal(n) * env
        x = lowpass(x, damp, 1)
        x = np.concatenate([np.zeros(secs(predelay)), x])
        chans.append(x / np.sqrt(np.sum(x ** 2) + 1e-12))
    return np.stack(chans, 1) if stereo else chans[0]


def convolve(x, ir, wet=0.25, dry=1.0):
    """Mono or stereo x with mono/stereo IR -> stereo out the length of x + ir tail."""
    x2 = to_stereo(x)
    ir2 = to_stereo(ir)
    w = np.stack([signal.fftconvolve(x2[:, c], ir2[:, c]) for c in range(2)], 1)
    out = np.zeros_like(w)
    out[: len(x2)] += x2 * dry
    out += w * wet
    return out


# ----------------------------------------------------------------------------- dynamics / colour
def saturate(x, drive=2.0):
    return np.tanh(x * drive) / np.tanh(drive)


def db(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-12))


def undb(d):
    return 10 ** (d / 20)


def envelope_follower(x, attack=0.005, release=0.1):
    """Peak follower on |x| (mono, or max across channels)."""
    a = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    # fast vectorised approximation: smooth with asymmetric one-pole via scipy for release,
    # and max with an attack-smoothed version
    ga = np.exp(-1 / (SR * attack))
    gr = np.exp(-1 / (SR * release))
    rel = signal.lfilter([1 - gr], [1, -gr], a)
    rel = np.maximum(rel, signal.lfilter([1 - ga], [1, -ga], a))
    return rel


def compressor(x, threshold_db=-18, ratio=3.0, attack=0.005, release=0.12, makeup_db=0.0, key=None):
    env = envelope_follower(key if key is not None else x, attack, release)
    lvl = db(env)
    over = np.maximum(lvl - threshold_db, 0)
    gain_db = -over * (1 - 1 / ratio) + makeup_db
    g = undb(gain_db)
    return x * (g[:, None] if x.ndim == 2 else g)


def true_peak(x, oversample=4):
    """dBTP estimate via polyphase oversampling."""
    y = signal.resample_poly(x, oversample, 1, axis=0)
    return db(np.max(np.abs(y)))


def limiter(x, ceiling_db=-1.0, lookahead=0.005, release=0.08, oversample=4):
    """Look-ahead brickwall limiter targeting a true-peak ceiling (approximate, then verified)."""
    ceil = undb(ceiling_db - 0.15)
    st = x.ndim == 2
    # detect on oversampled peaks folded back to sample grid
    y = signal.resample_poly(x, oversample, 1, axis=0)
    pk = np.abs(y).max(axis=1) if st else np.abs(y)
    pk = pk[: len(pk) // oversample * oversample].reshape(-1, oversample).max(1)
    pk = np.pad(pk, (0, len(x) - len(pk)), mode="edge") if len(pk) < len(x) else pk[: len(x)]
    need = np.minimum(1.0, ceil / np.maximum(pk, 1e-12))
    la = max(1, secs(lookahead))
    # look-ahead: minimum gain over the next la samples
    from scipy.ndimage import minimum_filter1d
    need = minimum_filter1d(need, size=2 * la + 1, mode="nearest")
    # smooth release (one-pole on gain going up only)
    gr = np.exp(-1 / (SR * release))
    g = np.empty_like(need)
    cur = 1.0
    for i in range(len(need)):  # numba-free loop, ~0.3 s per minute of audio
        v = need[i]
        cur = v if v < cur else v + (cur - v) * gr
        g[i] = cur
    out = x * (g[:, None] if st else g)
    # safety: final static trim if still over
    tp = true_peak(out, oversample)
    if tp > ceiling_db:
        out *= undb(ceiling_db - tp - 0.05)
    return out


# ----------------------------------------------------------------------------- utilities
def to_stereo(x):
    x = np.asarray(x, dtype=float)
    return np.stack([x, x], 1) if x.ndim == 1 else x


def pan(x, p=0.0):
    """Equal-power pan of mono x, p in [-1, 1]."""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)


def normalize(x, peak_db=-1.0):
    m = np.max(np.abs(x)) + 1e-12
    return x * undb(peak_db) / m


def mix_into(dst, src, at_s, gain=1.0):
    """Add src into dst starting at time at_s (grows nothing; clips to dst)."""
    i = secs(at_s)
    if i >= len(dst) or i + len(src) <= 0:
        return dst
    s0 = max(0, -i)
    i = max(0, i)
    n = min(len(src) - s0, len(dst) - i)
    if dst.ndim == 2 and src.ndim == 1:
        src = to_stereo(src)
    dst[i: i + n] += src[s0: s0 + n] * gain
    return dst


def pitch_shift_resample(x, semitones):
    r = 2 ** (semitones / 12)
    n = max(1, int(len(x) / r))
    return signal.resample(x, n, axis=0)


def read_audio(path, sr=SR):
    import soundfile as sf
    x, s = sf.read(str(path), always_2d=False)
    if s != sr:
        from math import gcd
        g = gcd(s, sr)
        x = signal.resample_poly(x, sr // g, s // g, axis=0)
    return x.astype(np.float64)


def write_audio(path, x, sr=SR, subtype=None):
    import soundfile as sf
    path = str(path)
    if subtype is None:
        subtype = "PCM_24" if path.endswith((".wav", ".flac")) else None
    sf.write(path, np.asarray(x, dtype=np.float32), sr, subtype=subtype)
