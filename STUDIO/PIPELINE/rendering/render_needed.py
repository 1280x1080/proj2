"""render_needed.py - render only the Blender frames the edit actually shows.

Walks the EDL through the compositor's frame plan, collects every (job, source frame) used by
kind="frames" sources, drops frames already on disk, and renders the rest in parallel lanes
(one Blender process per lane).  Safe to kill and re-run: finished frames are skipped.

    python render_needed.py VIDEOS/VIDEO_002/edit_video002.py [--lanes 2] [--threads 2] [--dry-run]

EDL source spec for Blender jobs:
    SOURCES = {"wide": dict(kind="frames", dir="renders/wide", scene="videos/video002.py", job="wide")}
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

PIPE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPE / "editing"))
from edl_engine import FPS, Edit  # noqa: E402

BLENDER = "blender"


def needed(edit: Edit):
    need = {}
    for _, uses in edit.plan():
        for src, st in uses:
            spec = edit.sources.get(src, {})
            if spec.get("kind") != "frames":
                continue
            fr = max(0, int(round(st * spec.get("fps", FPS))))
            need.setdefault(src, set()).add(fr)
    return need


def run(edl, lanes=2, threads=2, dry=False):
    edit = Edit(edl)
    need = needed(edit)
    timing = edit.dir / "audio" / "timing.json"
    tasks = []
    for src, frames in need.items():
        spec = edit.sources[src]
        out = edit.dir / spec["dir"]
        todo = sorted(f for f in frames if not (out / f"f_{f + 1:04d}.png").exists())
        print(f"{src}: {len(frames)} frames used by the edit, {len(todo)} still to render")
        for i in range(lanes):
            chunk = todo[i::lanes]
            if chunk:
                tasks.append((spec, out, chunk))
    if dry or not tasks:
        return need
    procs = []
    t0 = time.time()
    for k, (spec, out, chunk) in enumerate(tasks):
        out.mkdir(parents=True, exist_ok=True)
        ff = out / f".lane{k}.frames"
        ff.write_text(",".join(map(str, chunk)))
        cmd = [BLENDER, "-b", "--factory-startup", "-P", str(PIPE / "rendering" / "render_shot.py"), "--",
               "--scene", spec["scene"], "--job", spec["job"], "--out", str(out), "--frame-file", str(ff),
               "--threads", str(threads)]
        if timing.exists():
            cmd += ["--timing", str(timing)]
        log = open(out / f".lane{k}.log", "w")
        procs.append((subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT), log, len(chunk)))
        if len(procs) >= lanes:  # keep at most `lanes` Blender processes running
            p, lg, _ = procs.pop(0)
            p.wait()
            lg.close()
    for p, lg, _ in procs:
        p.wait()
        lg.close()
    dt = time.time() - t0
    total = sum(len(c) for _, _, c in tasks)
    rep = dict(frames=total, seconds=round(dt, 1), sec_per_frame=round(dt / max(1, total), 2), lanes=lanes)
    (edit.dir / "qc").mkdir(exist_ok=True)
    (edit.dir / "qc" / "render_stats.json").write_text(json.dumps(rep, indent=2))
    print(rep)
    return need


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("edl")
    ap.add_argument("--lanes", type=int, default=2)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    run(a.edl, a.lanes, a.threads, a.dry_run)
