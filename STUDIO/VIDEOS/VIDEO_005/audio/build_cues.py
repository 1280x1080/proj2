"""cues.json for VIDEO_005 (OPEN 24/7 - Part 1).

No dead air: rain outside + room tone under everything, fluorescent buzz until the power dies, CRT hum
whenever the monitor matters (and after the lights die - it's the only thing still on), a wall clock tick,
and a story sound in every pause.  The sheet's "silence" moments (after the power-down, after the drip)
drop the music, but the rain and the monitor hum stay.  SFX/ambience duck under the voice.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import edit_video005 as E  # noqa: E402
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
        if gain is not None:
            cue(seg_t0.get(sc["id"], start(sc["line"]) - 0.1 if sc.get("line") else 0.0) + off, name, gain, note=sc["id"])

# ---- beds ----
cue(0.0, "rain_outside", 6, "amb", dur=start("S02") - 0.1, fade_in=0.02, fade_out=0.3, note="outside: full rain")
cue(start("S02") - 0.3, "rain_outside", 0, "amb", dur=D - start("S02") + 0.3, fade_in=0.3, note="rain on the glass, from inside")
cue(0.0, "room_tone", 2, "amb", dur=D, fade_in=0.02, note="store air")
cue(0.0, "lamp_buzz", 4, "amb", dur=B["lights_die"], fade_in=0.02, fade_out=0.05, note="fluorescent buzz (dies with the power)")
cue(start("S07") - 0.1, "crt_hum", 2, "amb", dur=start("S10") - start("S07"), fade_in=0.1, fade_out=0.3, note="monitor")
cue(B["lights_die"] + 1.0, "crt_hum", 4, "amb", dur=D - B["lights_die"] - 1.0, fade_in=0.6, note="the monitor: last thing on")
cue(B["s17"], "rain_outside", 4, "amb", dur=start("S18") - B["s17"], fade_in=0.3, fade_out=0.3, note="scene 17: rain only")
t = 0.6
while t < B["lights_die"]:  # wall clock behind the counter
    cue(t, "tick", -22, pan=0.35, note="clock")
    t += 1.0

# ---- story sounds in the pauses ----
cue(end("S05") + 0.1, "door_chime", -16, pan=0.4, note="the chime again, nobody there")
cue(end("S09") + 0.05, "drip", -12, note="wet footprints")
cue(end("S12") + 0.1, "footstep_soft", -14, note="janitor steps up")
cue(end("S19") + 0.05, "drip", -12, note="her dripping")
cue(end("S22") + 0.1, "drip", -14, note="water left behind")
cue(B["ring_stop"] - 0.3, "impact_soft", -14, note="ringing cut off")
cue(end("S29") + 0.05, "breath_close", -14, pan=-0.2, note="someone behind you")
cue(end("S31") + 0.05, "floor_creak", -12, pan=-0.4, note="back room")
cue(B["choice"] + 0.2, "old_phone_ring", -22, pan=0.4, note="phone still ringing, faint")
cue(B["choice"] + 1.8, "old_phone_ring", -23, pan=0.4)
cue(B["choice"] + 3.4, "old_phone_ring", -24, pan=0.4)
cue(B["choice"] + 2.6, "drip", -16)

C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0),
         sfx_duck_db=-5.0, amb_duck_db=-5.0, ceiling_dbtp=-1.8, cues=sorted(cues, key=lambda c: c["t"]))
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-3.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues -> {HERE / 'cues.json'}  (estimated times: {E.ESTIMATED})")
