"""cues.json for VIDEO_012 (ORDER #000 Part 1).  No dead air: quiet night bedroom all the way, mukbang audio from the
phone, camera static on the door-cam shots, a story sound in every pause.  Two jumpscare stings."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import edit_video012 as E  # noqa: E402
from beats import B, DURATION as D, end, start, word  # noqa: E402

lib = json.loads((HERE.parents[2] / "AUDIO" / "sound_effects" / "LIBRARY.json").read_text())
cues = []


def cue(t, sfx, gain_db=0.0, bus="sfx", pan=0.0, note="", **kw):
    assert sfx in lib, sfx
    cues.append(dict(t=round(max(0.0, t), 3), sfx=sfx, gain_db=gain_db, bus=bus, pan=pan, note=note, **kw))


cue(0.0, "night_room", 6, "amb", dur=D, fade_in=0.02, note="bedroom at 2 AM")
cue(0.0, "room_tone", 2, "amb", dur=D, fade_in=0.02)
for sg in E.SEGMENTS:  # camera hiss whenever we look through the door camera
    if sg["src"] in ("doorcam", "scare_cam"):
        cue(sg["t0"], "cam_static", 4, "amb", dur=sg["t1"] - sg["t0"], fade_in=0.03, note="door camera feed")
# hook
cue(0.2, "text_ping", -8, note="app notification")
cue(E._t0("HB", None), "impact_cinematic", -8, note="him")
cue(B["story"] - 0.2, "whoosh_soft", -12)
# scrolling + mukbang
cue(B["story"] + 0.3, "whoosh_soft", -12, note="scroll")
t = E._t0("L01b", None)
while t < start("L02") - 0.3:
    cue(t, "slurp", -6, note="mukbang")
    t += 1.15
cue(start("L02") + 0.4, "heartbeat", -18, note="stomach")
cue(B["order"] - 0.1, "click_ui", -8, note="tap")
cue(B["order"] + 0.1, "order_chime", -6, note="order placed")
cue(end("L02") + 0.02, "text_ping", -8, note="driver arriving?!")
for kt in B["knocks"]:
    cue(kt, "door_knock", -2, pan=0.4, note="three knocks")
cue(start("L04") + 0.05, "click_ui", -10, note="open door camera")
cue(end("L04") + 0.02, "heartbeat", -8)
cue(end("L05") + 0.02, "breath_close", -10, note="your breath")
cue(start("L06") + 0.05, "phone_vibrate", -6)
cue(start("L06") + 0.9, "text_ping", -8)
cue(end("L06") + 0.02, "tinnitus", -12, note="beat of silence")
cue(B["scare1"], "jumpscare_sting", -6, note="JUMPSCARE 1: face in the lens")
cue(B["scare1"] + 0.03, "glitch", -8)
cue(B["scare1_end"], "power_down", -8, note="feed drops")
cue(word("L07", "run") - 0.1, "run_steps", -6, note="you run")
cue(word("L07", "lock"), "lock_click", -4, note="lock the door")
cue(end("L07") + 0.02, "breath_close", -8)
cue(start("L08") + 0.1, "impact_soft", -8)
cue(end("L08") + 0.02, "heartbeat", -6)
t = start("L09")
while t < B["stare"] - 0.6:
    cue(t, "slurp", -9, note="mukbang still playing")
    t += 1.2
cue(B["stare"], "power_down", -12, note="she stops")
cue(end("L09") + 0.02, "tinnitus", -14)
cue(end("L10") + 0.02, "heartbeat", -6)
cue(B["move"] - 0.2, "paper_rustle", -3, note="the bag moves")
cue(B["move"] + 0.9, "paper_rustle", -2)
cue(B["scare2"], "jumpscare_sting", -5, note="JUMPSCARE 2: out of the bag")
cue(B["scare2"] + 0.02, "paper_rustle", -4)
cue(B["choice"], "impact_cinematic", -8, note="choice")
cue(B["choice"] + 1.2, "ding", -8, note="TOP COMMENT banner")

C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0), sfx_duck_db=-5.0, amb_duck_db=-5.0,
         ceiling_dbtp=-1.7, cues=sorted(cues, key=lambda c: c["t"]))
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-4.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues")
