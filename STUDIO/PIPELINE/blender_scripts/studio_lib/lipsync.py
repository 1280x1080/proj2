"""Mouth-open curve from word timing (pure Python, also usable outside Blender)."""
import math


def _syl(w):
    w = "".join(c for c in w.lower() if c.isalpha())
    n, prev = 0, False
    for ch in w:
        v = ch in "aeiouy"
        if v and not prev:
            n += 1
        prev = v
    return max(1, n - (1 if w.endswith("e") and n > 1 else 0))


def mouth_curve(words, fps=30, step=2):
    """-> [(frame, amount 0..1)] keyed every `step` frames, closing between words."""
    if not words:
        return []
    f0 = int(words[0]["start"] * fps) - 2
    f1 = int(words[-1]["end"] * fps) + 3
    out = []
    for f in range(f0, f1 + 1, step):
        t = f / fps
        a = 0.0
        for w in words:
            if w["start"] - 0.04 <= t <= w["end"] + 0.04:
                d = max(0.08, w["end"] - w["start"])
                u = min(1, max(0, (t - w["start"]) / d))
                a = max(a, math.sin(math.pi * u) ** 0.5 * (0.55 + 0.45 * abs(math.sin(math.pi * _syl(w["w"]) * u))))
        out.append((f, round(a, 3)))
    return out
