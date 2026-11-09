"""One command for the whole pipeline of one video (every step is re-runnable / cached).

    python STUDIO/make_video.py 001                 # all steps
    python STUDIO/make_video.py 001 --from mix      # start at a step
    python STUDIO/make_video.py 001 --only export qc
    python STUDIO/make_video.py 001 --stills 0 2.5 5  # test stills of the edit (no export)

Steps: narrate -> sfx -> cues -> music -> mix -> render3d (only if the EDL has Blender sources)
       -> export -> qc (+ loop test if the EDL sets LOOP = True)
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

STUDIO = Path(__file__).resolve().parent
PIPE = STUDIO / "PIPELINE"
TTS_PY = Path.home() / ".venvs" / "tts" / "bin" / "python"
PY = sys.executable
STEPS = ["narrate", "sfx", "cues", "music", "mix", "render3d", "export", "qc"]


def sh(cmd, **kw):
    print("$", " ".join(map(str, cmd)), flush=True)
    t = time.time()
    subprocess.run(list(map(str, cmd)), check=True, **kw)
    return time.time() - t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("num")
    ap.add_argument("--from", dest="start", choices=STEPS)
    ap.add_argument("--only", nargs="*", choices=STEPS)
    ap.add_argument("--stills", type=float, nargs="*")
    ap.add_argument("--takes", type=int, default=3)
    a = ap.parse_args()
    num = a.num.zfill(3)
    vd = STUDIO / "VIDEOS" / f"VIDEO_{num}"
    edl = vd / f"edit_video{num}.py"
    if a.stills:
        sh([PY, PIPE / "editing" / "edl_engine.py", edl, "--still", *a.stills])
        return
    steps = a.only or STEPS[STEPS.index(a.start):] if (a.only or a.start) else STEPS
    times = {}
    for st in steps:
        if st == "narrate":
            times[st] = sh([TTS_PY, PIPE / "tts" / "narrate.py", vd / "script.json", "--takes", a.takes])
        elif st == "sfx":
            times[st] = sh([PY, PIPE / "audio" / "sfx_generate.py"])
        elif st == "cues":
            times[st] = sh([PY, vd / "audio" / "build_cues.py"])
        elif st == "music":
            times[st] = sh([PY, PIPE / "audio" / "music_gen.py", num])
        elif st == "mix":
            times[st] = sh([PY, PIPE / "audio" / "mix.py", vd / "audio" / "cues.json"])
        elif st == "render3d":
            src = edl.read_text()
            if '"frames"' in src or "'frames'" in src:
                times[st] = sh([PY, PIPE / "rendering" / "render_needed.py", edl])
        elif st == "export":
            times[st] = sh([PY, PIPE / "editing" / "edl_engine.py", edl])
        elif st == "qc":
            mp4 = STUDIO / "EXPORTS" / f"video{num}.mp4"
            times[st] = sh([PY, PIPE / "quality_control" / "qc_video.py", mp4, "--out", vd / "qc"])
            if "LOOP = True" in edl.read_text():
                sh([PY, PIPE / "quality_control" / "loop_test.py", mp4, "--out", vd / "qc"])
    print("step times (s):", {k: round(v, 1) for k, v in times.items()})


if __name__ == "__main__":
    main()
