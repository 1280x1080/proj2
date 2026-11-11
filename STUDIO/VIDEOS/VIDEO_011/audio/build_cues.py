"""cues.json for VIDEO_011 (LAST ONE IN THE CALL Part 1).  No dead air: PC-fan bedroom bed all the way, game audio in
the fun part, an open-mic breathing bed after the scream, a story sound in every pause.  Two jumpscare stings."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from beats import B, DURATION as D, end, start, word  # noqa: E402

lib = json.loads((HERE.parents[2] / "AUDIO" / "sound_effects" / "LIBRARY.json").read_text())
cues = []


def cue(t, sfx, gain_db=0.0, bus="sfx", pan=0.0, note="", **kw):
    assert sfx in lib, sfx
    cues.append(dict(t=round(max(0.0, t), 3), sfx=sfx, gain_db=gain_db, bus=bus, pan=pan, note=note, **kw))


cue(0.0, "pc_room", 6, "amb", dur=D, fade_in=0.02, note="bedroom + PC fans")
cue(0.0, "night_room", 0, "amb", dur=D, fade_in=0.02)
# hook: an open mic, breathing
for k in range(3):
    cue(0.3 + k * 1.9, "breath_close", -8, note="breathing in your headset (hook)")
cue(word("H1", "So") - 0.1, "impact_soft", -8)
cue(B["story"] - 0.2, "whoosh_soft", -12)
# the fun part
cue(B["story"] + 0.2, "keys_mouse", -6, note="gaming")
cue(B["story"] + 1.6, "game_shots", -10, note="game audio")
cue(B["story"] + 3.2, "keys_mouse", -8)
cue(start("L02") - 0.1, "game_shots", -12)
cue(end("L02") + 0.02, "keys_mouse", -6)
# they leave
cue(B["leave1"], "vc_leave", -3, note="Marcus left")
cue(B["leave2"], "vc_leave", -3, note="Dee left")
cue(end("L03") + 0.02, "keys_mouse", -10)
cue(end("L04") + 0.02, "tick", -10)
cue(B["knock_jay"], "knock_slow", -12, pan=0.4, note="knocking, through Jay's mic")
cue(B["knock_jay"] + 0.5, "knock_slow", -13, pan=0.4)
cue(end("L05") + 0.02, "knock_slow", -11, pan=0.4)
cue(end("L06") + 0.02, "heartbeat", -8)
# JUMPSCARE 1
cue(end("L07") + 0.05, "breath_close", -10, note="Jay holds his breath")
cue(B["scare1"], "mic_scream", -2, note="JUMPSCARE 1: Jay screams")
cue(B["scare1"], "jumpscare_sting", -1)
cue(B["scare1_end"] - 0.05, "power_down", -8, note="mic goes quiet")
for k in range(8):  # ...but the mic is still open
    t = B["scare1_end"] + 0.8 + k * 2.6
    if t < B["scare2"] - 0.5:
        cue(t, "breath_close", -12, pan=0.2, note="breathing on Jay's mic")
cue(start("L09") + 0.05, "phone_vibrate", -6, note="text")
cue(B["text"], "text_ping", -8)
cue(word("L09", "That's"), "text_ping", -8)
cue(end("L09") + 0.02, "heartbeat", -8)
# JUMPSCARE 2
cue(end("L10") + 0.02, "tinnitus", -12, note="beat of silence")
cue(B["scare2"], "jumpscare_sting", 0, note="JUMPSCARE 2: behind you")
cue(B["scare2"] + 0.05, "impact_cinematic", -4)
cue(B["scare2_end"], "power_down", -8, note="monitor goes dark")
cue(B["door"] - 0.7, "door_creak_long", -8, pan=0.4, note="your door")
cue(end("L11") + 0.02, "floor_creak", -8, pan=0.4)
cue(start("L12") + 0.1, "heartbeat", -8)
for kt in B["knocks"]:
    cue(kt, "knock_slow", -1, pan=-0.4, note="on YOUR window")
cue(B["freeze"], "impact_cinematic", -6, note="freeze")
cue(B["choice"], "riser", -12)

C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0), sfx_duck_db=-5.0, amb_duck_db=-5.0,
         ceiling_dbtp=-1.7, cues=sorted(cues, key=lambda c: c["t"]))
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-4.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues")
