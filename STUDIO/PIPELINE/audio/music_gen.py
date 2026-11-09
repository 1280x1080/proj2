"""music_gen.py - procedural score per video.

A Score has buses (pad / bass / lead / perc / fx).  Instruments are plain functions that
return mono audio; Score.note() places them (with pan + gain) on a bus.  gate() writes a
gain automation (e.g. silence the music for a punchline).  One cue_videoNNN() per video
builds the score from story beats imported from that video's EDL.

    python music_gen.py 001          # -> VIDEOS/VIDEO_001/audio/music.wav (+ stems)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dsp  # noqa: E402
from dsp import SR, adsr, ar, bandpass, exp_decay, fm_bell, highpass, karplus, lowpass, midi_hz, pink, \
    saw, secs, sine, square, t_axis, white  # noqa: E402

STUDIO = HERE.parents[1]
BUSES = ("pad", "bass", "lead", "perc", "fx")

# ----------------------------------------------------------------------------- instruments (mono)

def inst_pad(f, dur, bright=0.35, detune=0.12):
    x = sum(saw(f * 2 ** (d / 1200), dur, harmonics=14) for d in (-detune * 100, 0, detune * 100)) / 3
    x = lowpass(x, 400 + bright * 3000, 2)
    return x * adsr(dur, min(0.8, dur * 0.3), 0.3, 0.8, min(1.0, dur * 0.3))


def inst_strings(f, dur, bright=0.5):
    t = t_axis(dur)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t / 0.6, 0, 1)
    x = sum(dsp.sine(f * k * vib, dur) / k ** 1.2 for k in range(1, 9))
    x = lowpass(x, 1200 + bright * 3500)
    return x * adsr(dur, min(0.35, dur * 0.3), 0.2, 0.85, min(0.6, dur * 0.3))


def inst_pluck(f, dur, bright=0.6):
    return karplus(f, dur, decay=0.994, bright=bright) * ar(dur, 0.002, 1.5)


def inst_bell(f, dur, bright=0.5):
    return fm_bell(f, dur, ratio=3.5, index=1.5 + bright * 3, tau=dur / 3)


def inst_bass(f, dur, bright=0.3):
    x = sine(f, dur) + 0.35 * sine(2 * f, dur) + 0.15 * lowpass(saw(f, dur, 8), 300 + bright * 900)
    return x * adsr(dur, 0.008, 0.12, 0.75, min(0.12, dur * 0.3))


def inst_stab(f, dur, bright=0.6):
    x = sum(square(f * r, dur, 10) for r in (1, 1.5, 2)) / 3
    return lowpass(x, 900 + bright * 4000) * ar(dur, 0.004, 3)


def inst_tremolo(f, dur, rate=8.0, bright=0.5):
    t = t_axis(dur)
    return inst_strings(f, dur, bright) * (0.55 + 0.45 * np.sin(2 * np.pi * rate * t))


def drum_kick(dur=0.45):
    t = t_axis(dur)
    return np.tanh(2 * sine(48 + 110 * np.exp(-t * 28), dur) * exp_decay(dur, 0.16))


def drum_snare(dur=0.3):
    return (bandpass(white(dur, 5), 900, 8000) * exp_decay(dur, 0.06) * 0.8
            + sine(190, dur) * exp_decay(dur, 0.04) * 0.6)


def drum_hat(dur=0.08, open_=False):
    d = 0.35 if open_ else dur
    return highpass(white(d, 9), 7000) * exp_decay(d, 0.12 if open_ else 0.015) * 0.6


def drum_tom(f=110, dur=0.5):
    t = t_axis(dur)
    return sine(f * (1 + 0.6 * np.exp(-t * 20)), dur) * exp_decay(dur, 0.18)


INSTRUMENTS = dict(pad=inst_pad, strings=inst_strings, pluck=inst_pluck, bell=inst_bell, bass=inst_bass,
                   stab=inst_stab, tremolo=inst_tremolo)

# ----------------------------------------------------------------------------- chords
NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}


def chord(name, octave=3):
    """'Am', 'F', 'C', 'G7', 'Dm7', 'Esus4' -> list of midi notes."""
    root = name[:2] if len(name) > 1 and name[1] == "#" else name[:1]
    q = name[len(root):]
    r = 12 * (octave + 1) + NOTE[root]
    iv = {"": [0, 4, 7], "m": [0, 3, 7], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11],
          "sus4": [0, 5, 7], "sus2": [0, 2, 7], "dim": [0, 3, 6], "add9": [0, 4, 7, 14]}[q]
    return [r + i for i in iv]


# ----------------------------------------------------------------------------- score

class Score:
    def __init__(self, duration, bpm=90.0, seed=0):
        self.duration = float(duration)
        self.bpm = bpm
        self.n = secs(duration + 4.0)  # room for tails
        self.bus = {b: np.zeros((self.n, 2)) for b in BUSES}
        self.gates: list[tuple[float, float, float, float]] = []  # (t0, t1, gain, fade)
        self.rng = np.random.default_rng(seed)

    @property
    def beat(self):
        return 60.0 / self.bpm

    def add(self, bus, x, at, gain=1.0, pan=0.0):
        if at >= self.duration + 4.0:
            return
        x = np.asarray(x, dtype=float)
        st = dsp.pan(x, pan) if x.ndim == 1 else x
        dsp.mix_into(self.bus[bus], st, at, gain)

    def note(self, bus, inst, midi, at, dur, gain=0.3, pan=0.0, **kw):
        fn = INSTRUMENTS[inst] if isinstance(inst, str) else inst
        self.add(bus, fn(midi_hz(midi), dur, **kw), at, gain, pan)

    def chord(self, bus, inst, name, at, dur, gain=0.2, octave=3, spread=0.5, **kw):
        notes = chord(name, octave)
        for i, m in enumerate(notes):
            p = (i / max(1, len(notes) - 1) * 2 - 1) * spread
            self.note(bus, inst, m, at, dur, gain / np.sqrt(len(notes)), p, **kw)

    def hit(self, bus, x, at, gain=0.5, pan=0.0):
        self.add(bus, x, at, gain, pan)

    def gate(self, t0, t1, gain=0.0, fade=0.08):
        """Automate the whole music mix to `gain` between t0 and t1 (with fades)."""
        self.gates.append((t0, t1, gain, fade))

    def _gate_curve(self, n):
        g = np.ones(n)
        t = np.arange(n) / SR
        for t0, t1, gain, fd in self.gates:
            ramp_in = np.clip((t - (t0 - fd)) / max(fd, 1e-4), 0, 1)
            ramp_out = np.clip(((t1 + fd) - t) / max(fd, 1e-4), 0, 1)
            w = np.minimum(ramp_in, ramp_out)
            g *= 1 - w * (1 - gain)
        return g

    def render(self, loop=False, reverb=0.22):
        """-> (mix, stems) both trimmed to duration.  loop=True folds tails past the end onto the start."""
        ir = dsp.reverb_ir(2.2, damp=5000)
        stems = {}
        nd = secs(self.duration)
        for b, x in self.bus.items():
            wet = {"pad": reverb, "lead": reverb, "fx": reverb * 1.3, "perc": reverb * 0.4, "bass": 0.0}[b]
            y = dsp.convolve(x, ir, wet=wet)[: self.n] if wet > 0 else x.copy()
            if b == "bass":
                y = dsp.lowpass(y, 400)
            if loop:
                tail = y[nd:]
                y = y[:nd].copy()
                k = min(len(tail), nd)
                y[:k] += tail[:k]
            else:
                y = dsp.fade(y[:nd], 0.0, 0.5)
            stems[b] = y
        g = self._gate_curve(nd)[:, None]
        stems = {b: y * g for b, y in stems.items()}
        mix = sum(stems.values())
        pk = np.max(np.abs(mix)) + 1e-9
        if pk > dsp.undb(-3):
            s = dsp.undb(-3) / pk
            mix *= s
            stems = {b: y * s for b, y in stems.items()}
        return mix, stems


# ----------------------------------------------------------------------------- per-video cues

def _load_edl(num):
    p = STUDIO / "VIDEOS" / f"VIDEO_{num}" / f"edit_video{num}.py"
    spec = importlib.util.spec_from_file_location(f"edit_video{num}", p)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(p.parent))
    spec.loader.exec_module(m)
    return m


def cue_video001():
    """10 s test.  Cosy-but-uneasy pad until the 4th flicker; a hard music drop on the reveal;
    then a low drone + tremolo cluster that swells into the knocks."""
    edl = _load_edl("001")
    B = edl.BEATS
    s = Score(edl.DURATION, bpm=80, seed=1)
    bar = s.beat * 4
    rv = B["reveal"]
    prog = ["Am", "Fmaj7", "C", "G"]
    t, i = 0.0, 0
    while t < rv:
        d = min(bar + 0.3, rv - t + 0.05)
        name = prog[i % 4]
        s.chord("pad", "pad", name, t, d, gain=0.20, octave=3, bright=0.25)
        s.note("bass", "bass", chord(name, 2)[0], t, min(bar * 0.95, d), gain=0.22)
        t += bar
        i += 1
    # sparse music-box motif on the narrator's line, one note per flicker
    for k, ft in enumerate(B["flicks"]):
        s.note("lead", "bell", [76, 79, 81][k], ft, 1.6, gain=0.07, pan=-0.3, bright=0.3)
    # reveal: silence punch, then tension
    s.gate(rv - 0.02, rv + 0.35, gain=0.0, fade=0.03)
    end = edl.DURATION
    s.note("bass", "bass", 33, rv + 0.3, end - rv, gain=0.32)                       # A1 drone
    for m, p in ((57, -0.4), (58, 0.4), (64, 0.0)):                                  # A3/Bb3/E4 cluster
        s.note("pad", "tremolo", m, rv + 0.4, end - rv, gain=0.07, pan=p, rate=9.0)
    sw = max(0.5, B["knocks"][0] - rv - 0.4)
    nz = dsp.sweep_filter(pink(sw, 3) * np.linspace(0, 1, secs(sw)) ** 2, 200, 3000, "band", q=0.9)
    s.hit("fx", nz, rv + 0.4, 0.10)
    s.gate(B["knocks"][0] - 0.05, B["knocks"][2] + 0.25, gain=0.35, fade=0.04)
    s.hit("perc", drum_tom(55, 1.2), B["knocks"][2] + 0.45, 0.35)
    s.note("pad", "stab", 45, B["knocks"][2] + 0.45, 1.4, gain=0.10, bright=0.2)
    return s, dict(loop=False)


def cue_video002():
    """5 s mascot test: bright, bouncy C-G-Am-F at 112 bpm; downbeat hit on the landing; button on the wink."""
    edl = _load_edl("002")
    B = edl.BEATS
    s = Score(edl.DURATION, bpm=112, seed=2)
    bar = s.beat * 4
    prog = ["C", "G", "Am", "F"]
    t0 = B["land"]
    s.hit("perc", drum_kick(), t0, 0.5)
    s.hit("fx", inst_stab(midi_hz(60), 0.5), t0, 0.12)
    t, i = t0, 0
    while t < s.duration:
        name = prog[i % 4]
        s.chord("pad", "pad", name, t, bar + 0.2, gain=0.14, octave=4, bright=0.45)
        s.note("bass", "bass", chord(name, 2)[0], t, s.beat * 1.6, gain=0.26)
        s.note("bass", "bass", chord(name, 2)[0], t + s.beat * 2, s.beat * 1.6, gain=0.22)
        for k in range(8):
            nt = chord(name, 5)[[0, 1, 2, 1, 0, 2, 1, 2][k]]
            s.note("lead", "pluck", nt, t + k * s.beat / 2, 0.5, gain=0.06, pan=(-0.35 if k % 2 else 0.35))
        for k in range(4):
            s.hit("perc", drum_kick(), t + k * s.beat, 0.28 if k % 2 == 0 else 0.0)
            s.hit("perc", drum_snare(), t + k * s.beat, 0.16 if k % 2 == 1 else 0.0)
            s.hit("perc", drum_hat(), t + k * s.beat + s.beat / 2, 0.07)
        t += bar
        i += 1
    s.gate(B["wink"] - 0.05, B["wink"] + 0.25, gain=0.3, fade=0.04)
    s.hit("fx", inst_bell(midi_hz(84), 1.5), B["wink"] + 0.05, 0.1)
    return s, dict(loop=False)


def cue_video003():
    """GOING DOWN Part 1 - elevator horror.  Low drone + music-box bell motif; heartbeat bass under the
    tests; tremolo cluster rising into the drop; silence punch on the drop and on "Stay in"; low hit on
    the freeze; the choice screen sits on a quiet drone."""
    edl = _load_edl("003")
    B = edl.BEATS
    D = edl.DURATION
    s = Score(D, bpm=70, seed=3)
    # drone (A1 + E2) under everything
    s.note("bass", "bass", 33, 0.0, D, gain=0.22)
    s.note("pad", "pad", 40, 0.0, B["drop"], gain=0.10, bright=0.15)
    # music-box motif: hook, the glowing 13, the doors on 13, each rule card
    motif = [76, 72, 75, 71]
    for k, tt in enumerate([0.05, B["thirteen_glow"], B["doors13"]] + list(B["rules"])):
        s.note("lead", "bell", motif[k % 4], tt, 2.4, gain=0.06, pan=(-0.3 if k % 2 else 0.3), bright=0.25)
    # unease pad after the presence
    for t0, name in ((B["doors13"], "Am"), (B["gus"], "Fmaj7"), (B["rules"][0], "Dm7"), (B["mirror_test"], "Esus4")):
        s.chord("pad", "strings", name, t0, 8.0, gain=0.07, octave=3, bright=0.2)
    # heartbeat bass pulse under the tests
    t = B["mirror_test"]
    while t < B["drop"]:
        s.hit("perc", drum_kick(0.4), t, 0.22)
        s.hit("perc", drum_kick(0.3), t + 0.28, 0.14)
        t += 60 / 72 if t < B["mom"] else 60 / 96
    # tremolo cluster rising from the mom test into the drop
    for m, p in ((57, -0.4), (58, 0.4), (64, 0.0)):
        s.note("pad", "tremolo", m, B["inside"], B["drop"] - B["inside"] + 0.2, gain=0.06, pan=p, rate=10.0)
    s.gate(B["drop"] - 0.02, B["drop"] + 0.45, gain=0.0, fade=0.03)
    s.hit("perc", drum_tom(48, 1.6), B["drop"] + 0.45, 0.45)
    # red section: low red pad, drops out for "Stay in"
    s.chord("pad", "pad", "Am", B["drop"] + 0.4, B["freeze"] - B["drop"], gain=0.12, octave=2, bright=0.1)
    s.gate(B["stay"] - 0.05, B["stay"] + 1.3, gain=0.15, fade=0.05)
    s.hit("perc", drum_tom(44, 2.0), B["freeze"], 0.5)
    s.note("pad", "stab", 45, B["freeze"], 1.6, gain=0.10, bright=0.15)
    s.note("lead", "bell", 69, B["choice"] + 0.2, 3.0, gain=0.06, bright=0.2)
    return s, dict(loop=False)


def main():
    num = sys.argv[1].zfill(3)
    s, opts = globals()[f"cue_video{num}"]()
    mix, stems = s.render(loop=opts.get("loop", False))
    out = STUDIO / "VIDEOS" / f"VIDEO_{num}" / "audio"
    (out / "stems").mkdir(parents=True, exist_ok=True)
    dsp.write_audio(out / "music.wav", mix)
    for b, y in stems.items():
        dsp.write_audio(out / "stems" / f"music_{b}.wav", y)
    (out / "music_info.json").write_text(json.dumps(dict(duration=s.duration, bpm=s.bpm, gates=s.gates,
                                                         loop=opts.get("loop", False)), indent=2))
    print(f"music.wav {len(mix) / SR:.2f}s -> {out}")


if __name__ == "__main__":
    main()
