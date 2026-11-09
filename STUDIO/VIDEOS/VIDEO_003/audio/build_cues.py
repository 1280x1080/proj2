"""cues.json for VIDEO_003 (GOING DOWN - Part 1), built from the SCENES table in the EDL.

Scene SFX are (name, gain_db, offset_from_scene_start); gain None = ambience handled below.
Only names that exist in AUDIO/sound_effects/LIBRARY.json are used.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import edit_video003 as E  # noqa: E402

lib = json.loads((HERE.parents[2] / "AUDIO" / "sound_effects" / "LIBRARY.json").read_text())
cues = []


def cue(t, sfx, gain_db=0.0, bus="sfx", pan=0.0, note="", **kw):
    assert sfx in lib, f"unknown SFX {sfx}"
    cues.append(dict(t=round(max(0.0, t), 3), sfx=sfx, gain_db=gain_db, bus=bus, pan=pan, note=note, **kw))


seg_t0 = {sg["scene"]: sg["t0"] for sg in E.SEGMENTS}
for sc in E.SCENES:
    for name, gain, off in sc.get("sfx", []):
        if gain is None:
            continue
        cue(seg_t0[sc["id"]] + off, name, gain, note=sc["id"])

B, D = E.B, E.DURATION
# ambience: elevator room tone all along; fluorescent hum until the drop; shaft wind after it
cue(0.0, "room_tone", 0, "amb", dur=D, fade_in=0.02, note="elevator car tone")
cue(0.0, "lamp_buzz", -4, "amb", dur=B["drop"], fade_in=0.02, fade_out=0.05, note="fluorescent hum (dies at the drop)")
cue(B["drop"], "wind", -10, "amb", dur=D - B["drop"], fade_in=0.4, note="shaft air after the drop")

C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0), cues=sorted(cues, key=lambda c: c["t"]))
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-4.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues -> {HERE / 'cues.json'}  (estimated times: {E.ESTIMATED})")
