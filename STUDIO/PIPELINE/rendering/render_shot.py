"""render_shot.py - one Blender render job (run inside Blender).

    blender -b -P render_shot.py -- --scene videos/video002.py --job wide --out VIDEOS/VIDEO_002/renders/wide \
            [--frames 0,1,2,10-20] [--timing VIDEOS/VIDEO_002/audio/timing.json] [--threads 2] [--full-res]

Frames are SOURCE frames of the job (source time t -> frame round(t*30)); file f_{frame+1:04d}.png,
which is what edl_engine's kind="frames" source reads.  Existing files are skipped (resumable).
Default: 540x960 (50 %), 1 EEVEE sample + OpenImageDenoise, ray tracing off.
"""
import argparse
import importlib.util
import sys
import time
from pathlib import Path

import bpy

PIPE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPE / "blender_scripts"))


def parse_frames(spec, n):
    if not spec:
        return list(range(n))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return sorted(set(out))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames")
    ap.add_argument("--frame-file")
    ap.add_argument("--timing")
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--full-res", action="store_true")
    a = ap.parse_args(argv)
    sp = Path(a.scene)
    if not sp.is_absolute():
        sp = PIPE / "blender_scripts" / sp
    spec = importlib.util.spec_from_file_location("shotmod", sp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    t0 = time.time()
    sc = mod.build(a.timing)
    job = mod.JOBS[a.job]
    sc.camera = bpy.data.objects[job["camera"]]
    if a.full_res:
        sc.render.resolution_percentage = 100
    if a.threads:
        sc.render.threads_mode = "FIXED"
        sc.render.threads = a.threads
    n = job["end"] - job["start"] + 1
    spec_frames = Path(a.frame_file).read_text().strip() if a.frame_file else a.frames
    frames = parse_frames(spec_frames, n)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    print(f"[render_shot] scene built in {time.time() - t0:.1f}s; {len(frames)} frames of job {a.job}")
    done = 0
    for fr in frames:
        f = out / f"f_{fr + 1:04d}.png"
        if f.exists():
            continue
        sc.frame_set(job["start"] + fr)
        sc.render.filepath = str(f)
        t = time.time()
        bpy.ops.render.render(write_still=True)
        done += 1
        print(f"[render_shot] {a.job} frame {fr} -> {f.name}  {time.time() - t:.2f}s", flush=True)
    print(f"[render_shot] done {done} frames in {time.time() - t0:.1f}s")


main()
