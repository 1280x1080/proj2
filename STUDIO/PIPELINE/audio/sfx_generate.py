"""Render every registered SFX to STUDIO/AUDIO/sound_effects/*.flac and write LIBRARY.json.

    python sfx_generate.py            # all (skips files that exist unless --force)
    python sfx_generate.py whoosh pop --force
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dsp  # noqa: E402
from sfx_lib import REGISTRY  # noqa: E402

OUT = HERE.parents[1] / "AUDIO" / "sound_effects"


def load_all_modules():
    for p in sorted(HERE.glob("sfx_*.py")):
        if p.stem not in ("sfx_lib", "sfx_generate"):
            importlib.import_module(p.stem)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    load_all_modules()
    OUT.mkdir(parents=True, exist_ok=True)
    lib_path = OUT / "LIBRARY.json"
    lib = json.loads(lib_path.read_text()) if lib_path.exists() else {}
    for name, info in REGISTRY.items():
        if a.names and name not in a.names:
            continue
        f = OUT / f"{name}.flac"
        if f.exists() and not a.force and name in lib:
            continue
        x = np.asarray(info["fn"](), dtype=float)
        x = dsp.to_stereo(x)
        if not info["loop"]:  # trim reverb tail below -70 dBFS
            loud = np.where(np.max(np.abs(x), 1) > dsp.undb(-70))[0]
            x = x[: (loud[-1] + 1 if len(loud) else len(x))]
        x = dsp.fade(x, 0.0005, 0.003 if not info["loop"] else 0.0)
        dsp.write_audio(f, x)
        lib[name] = dict(file=f.name, description=info["description"], category=info["category"],
                         loop=info["loop"], duration=round(len(x) / dsp.SR, 3),
                         peak_db=round(float(dsp.db(np.max(np.abs(x)))), 2))
        print(f"  {name:20s} {lib[name]['duration']:6.2f}s  {info['description']}")
    lib = {k: lib[k] for k in sorted(lib)}
    lib_path.write_text(json.dumps(lib, indent=2))
    print(f"{len(lib)} effects in {lib_path}")


if __name__ == "__main__":
    main()
