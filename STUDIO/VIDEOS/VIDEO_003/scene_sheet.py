"""Writes SCENES.md - the per-scene sheet (time, duration, VO, captions, visual, camera, SFX, HUD)
straight from edit_video003.SCENES.  Re-run after narrate.py to replace the estimated times.
Caption chunks use the same split rule as edl_engine.build_captions (<= 5 words, break on punctuation)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edit_video003 as E  # noqa: E402

script = {l["id"]: l for l in json.loads((HERE / "script.json").read_text())["lines"]}
COL = {E.RED: "RED", E.YEL: "YELLOW"}


def chunks(text, maxw=5):
    out, cur = [], []
    for w in text.split():
        cur.append(w)
        if w[-1:] in ".,!?;:" or w.endswith(('."', '?"', ',"', '!"')) or len(cur) >= maxw:
            out.append(cur)
            cur = []
    if cur:
        if len(cur) == 1 and out and len(out[-1]) < maxw + 1:
            out[-1] += cur
        else:
            out.append(cur)
    return [" ".join(c).upper() for c in out]


def norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum() or ch == "'")


rows = []
seg = {s["scene"]: s for s in E.SEGMENTS}
for sc in E.SCENES:
    s = seg[sc["id"]]
    ln = script.get(sc["line"]) if sc.get("line") else None
    vo = f'{ln["who"].upper()}: {ln["text"]}' if ln else "-"
    if sc.get("at"):
        vo = f'(insert cut on "{sc["at"][1]}" during {sc["at"][0]})'
    caps = " / ".join(chunks(ln["text"])) if ln and not sc.get("at") else "-"
    key = f'{sc["key"][0].strip(".,?!\"").upper()} ({COL[sc["key"][1]]})' if sc.get("key") else "-"
    sfx = ", ".join(f"{n} {g:+d}dB" for n, g, _ in sc.get("sfx", []) if g is not None) or "-"
    hud = f'{sc["hud"][0]} · RIDERS {sc["hud"][1]}' if sc.get("hud") else "(choice screen)"
    note = f' **{sc["note"]}**' if sc.get("note") else ""
    rows.append(f'| {sc["id"]} | {s["t0"]:.1f} | {s["t1"] - s["t0"]:.1f} | {vo} | {caps} | {key} | {sc["visual"]}{note} '
                f'| {sc["cam"]} | {sfx} | {hud} |')

hdr = ("| # | t (s) | dur | Voiceover | Captions (ALL CAPS chunks) | Key word | Visual (shot, expression, light) | Camera | SFX | HUD |\n"
       "|---|---|---|---|---|---|---|---|---|---|")
est = " (ESTIMATED from word counts - re-run after narrate.py)" if E.ESTIMATED else " (from narration word timing)"
md = f"# VIDEO_003 scene sheet - GOING DOWN, Part 1\n\nRuntime {E.DURATION:.1f} s{est}, {len(E.SCENES)} scenes.\n\n" + hdr + "\n" + "\n".join(rows) + "\n"
(HERE / "SCENES.md").write_text(md)
print(md[:300], "...", f"\n{len(rows)} rows")
