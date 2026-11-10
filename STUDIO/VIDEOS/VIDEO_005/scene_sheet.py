"""Writes SCENES.md - the per-scene sheet for VIDEO_005 from edit_video005.SCENES (re-run after any re-timing)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edit_video005 as E  # noqa: E402

script = {l["id"]: l for l in json.loads((HERE / "script.json").read_text())["lines"]}
seg = {s["scene"]: s for s in E.SEGMENTS}
COL = {E.RED: "RED", E.YEL: "YELLOW"}
rows, last = [], None
for sc in E.SCENES:
    s = seg.get(sc["id"])
    if s is not None:
        last = s
    ln = script.get(sc["line"]) if sc.get("line") else None
    vo = f'{ln["who"].upper()}: {ln["text"]}' if ln else "(no VO)"
    cap = sc.get("cap")
    cap = ln["text"].upper() if (cap is None and ln) else (cap if cap else "-")
    keys = ", ".join(f'{k.strip(".,?!\\"").upper()} ({COL[v]})' for k, v in sc.get("keys", {}).items()) or "-"
    sfx = ", ".join(f"{n} {g:+d}dB" for n, g, _ in sc.get("sfx", []) if g is not None) or "-"
    hud = f'{sc["clock"]} · CUSTOMERS {sc["cust"]}' if sc.get("clock") else "(choice screen)"
    t0 = s["t0"] if s else E.start(sc["line"]) - 0.1
    dur = (s["t1"] - s["t0"]) if s else (E.end(sc["line"]) - E.start(sc["line"]))
    note = f' **{sc["note"]}**' if sc.get("note") else ""
    rows.append(f'| {sc["id"]} | {t0:.1f} | {dur:.1f} | {vo} | {cap} | {keys} | {sc["visual"]}{note} | {sc["cam"] or "(cont.)"} | {sfx} | {hud} |')
md = (f"# VIDEO_005 scene sheet - OPEN 24/7, Part 1\n\nRuntime {E.DURATION:.1f} s (from narration word timing), "
      f"{len(E.SEGMENTS)} cuts.\n\n| # | t (s) | dur | Voiceover | Caption | Key words | Visual | Camera | SFX | HUD |\n"
      "|---|---|---|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n")
(HERE / "SCENES.md").write_text(md)
print(len(rows), "rows")
