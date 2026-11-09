"""cues.json for VIDEO_004 (THE ROOM THAT WASN'T THERE - Part 1).

No dead air: a bedroom-at-3-AM bed (fridge hum through the wall, distant traffic, wind) plays under the whole
video, a slow wall-clock tick keeps time, and every pause between lines carries a story sound (ring, buzz,
knocks, creaks, scratching, breathing).  SFX and ambience duck under the voice and swell back up in the
pauses (sfx_duck_db / amb_duck_db); the music bed ducks too.  Checked by quality_control/dead_air.py.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import edit_video004 as E  # noqa: E402
from beats import end, start  # noqa: E402

lib = json.loads((HERE.parents[2] / "AUDIO" / "sound_effects" / "LIBRARY.json").read_text())
cues = []


def cue(t, sfx, gain_db=0.0, bus="sfx", pan=0.0, note="", **kw):
    assert sfx in lib, f"unknown SFX {sfx}"
    cues.append(dict(t=round(max(0.0, t), 3), sfx=sfx, gain_db=gain_db, bus=bus, pan=pan, note=note, **kw))


B, D = E.B, E.DURATION
seg_t0 = {sg["scene"]: sg["t0"] for sg in E.SEGMENTS}
for sc in E.SCENES:
    for name, gain, off in sc.get("sfx", []):
        if gain is None:
            continue
        cue(seg_t0.get(sc["id"], 0.0) + off, name, gain, note=sc["id"])

# ---- beds (never silent) ----
cue(0.0, "night_room", 7, "amb", dur=D, fade_in=0.02, fade_out=0.4, note="3 AM bedroom bed")
cue(0.0, "room_tone", 2, "amb", dur=D, fade_in=0.02, note="room air")
cue(B["silence"], "tinnitus", 2, "amb", dur=start("R17") - B["silence"] + 1.0, fade_in=0.3, fade_out=0.8,
    note="the silence after the knocking rings")
t = 0.6
while t < B["choice"]:  # slow wall clock - keeps the pauses alive, stops dead on the choice
    cue(t, "tick", -22, pan=0.4, note="wall clock")
    t += 1.0

# ---- story sounds placed in the pauses ----
for k, kt in enumerate(B["knocks"]):  # the three slow knocks (pause after R07)
    cue(kt, "knock_slow", -2 - k, pan=-0.25, note=f"slow knock {k + 1}")
cue(B["text2"], "text_ping", -10, note="second text")
cue(B["text2"] - 0.1, "phone_vibrate", -12, note="second text buzz")
cue(B["own_voice"] - 0.9, "floor_creak", -9, pan=-0.3, note="someone shifts in the hallway")
cue(end("R16") + 0.15, "floor_creak", -11, pan=-0.3, note="hallway")
cue(end("R20") + 0.1, "breath_close", -16, pan=-0.3, note="breathing at the bedroom door")
cue(end("R25") + 0.1, "scratch_wood", -8, pan=0.3, note="scratching continues in the pause")
cue(end("R27") + 0.05, "heartbeat", -6, note="your heart before the freeze")
cue(B["choice"] + 0.8, "breath_close", -18, pan=0.3, note="small door breathes")
cue(B["choice"] + 2.5, "knock_slow", -14, pan=-0.4, note="one more knock (bedroom door)")
cue(end("R30") + 0.1, "scratch_wood", -14, pan=0.4, note="small door scratch")

C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0),
         sfx_duck_db=-5.0, amb_duck_db=-5.0, cues=sorted(cues, key=lambda c: c["t"]))
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-3.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues -> {HERE / 'cues.json'}  (estimated times: {E.ESTIMATED})")
