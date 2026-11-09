"""Text normalisation shared by narrate.py / voice_qc.py (digits vs words never count as errors)."""
from __future__ import annotations

import re

_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
        "seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def num_words(n: int) -> str:
    if n < 0:
        return "minus " + num_words(-n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000:
        return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + num_words(n % 100))
    for div, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand")):
        if n >= div:
            return num_words(n // div) + " " + name + ("" if n % div == 0 else " " + num_words(n % div))
    return str(n)


def _num_repl(m):
    s = m.group(0).replace(",", "")
    if "." in s:
        a, b = s.split(".", 1)
        return num_words(int(a or 0)) + " point " + " ".join(_ONES[int(d)] for d in b)
    return num_words(int(s))


def normalize_words(text: str) -> list[str]:
    t = text.lower()
    t = t.replace("%", " percent").replace("&", " and ").replace("$", " dollars ")
    t = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", t)
    t = re.sub(r"\d[\d,]*(\.\d+)?", _num_repl, t)
    t = t.replace("-", " ").replace("—", " ").replace("–", " ")
    t = re.sub(r"[^a-z' ]+", " ", t)
    words = [w.strip("'") for w in t.split()]
    # contractions both ways count as equal
    return [w for w in words if w]


def mismatches(ref: str, hyp: str) -> int:
    """Word-level edit distance after normalisation."""
    a, b = normalize_words(ref), normalize_words(hyp)
    d = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(b) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
            prev = cur
    return d[len(b)]
