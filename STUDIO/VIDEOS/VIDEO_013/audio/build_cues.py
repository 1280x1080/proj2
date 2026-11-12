"""cues.json for VIDEO_013 (AFTER HOURS Part 1).  No dead air: empty-school night bed all the way (game-night PC bed in
the rewind), a story sound in every pause.  Two jumpscare stings."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import edit_video013 as E  # noqa: E402
from beats import B, DURATION as D, end, start, word  # noqa: E402

lib = json.loads((HERE.parents[2] / "AUDIO" / "sound_effects" / "LIBRARY.json").read_text())
cues = []


def cue(t, sfx, gain_db=0.0, bus="sfx", pan=0.0, note="", **kw):
    assert sfx in lib, sfx
    cues.append(dict(t=round(max(0.0, t), 3), sfx=sfx, gain_db=gain_db, bus=bus, pan=pan, note=note, **kw))


M = B["midnight"]
cue(0.0, "night_room", 6, "amb", dur=B["story"], fade_in=0.02, note="school at night (hook)")
cue(0.0, "lamp_buzz", -8, "amb", dur=B["story"], fade_in=0.02)
cue(B["story"], "pc_room", 6, "amb", dur=start("L03") - B["story"], fade_in=0.05, note="game night")
cue(start("L03") - 0.1, "classroom_after", 4, "amb", dur=M - start("L03") + 0.1, fade_in=0.05, note="exam day")
cue(M, "night_room", 6, "amb", dur=D - M, fade_in=0.1, note="inside the school at midnight")
cue(M, "lamp_buzz", -8, "amb", dur=D - M, fade_in=0.1, note="EXIT sign buzz")
# hook
cue(0.2, "footstep_soft", -8)
cue(0.8, "footstep_soft", -9)
cue(1.5, "floor_creak", -10)
cue(B["hook_cut"], "impact_soft", -8)
cue(B["hook_cut"] + 0.3, "pencil_scribble", -3, note="the red pen, by itself")
cue(B["hook_cut"] + 1.5, "pencil_scribble", -3)
cue(B["story"] - 0.25, "whoosh", -8, note="rewind")
# game night
cue(B["story"] + 0.2, "keys_mouse", -6)
cue(B["story"] + 1.5, "game_shots", -10)
cue(B["story"] + 3.2, "keys_mouse", -8)
cue(start("L02") - 0.2, "game_shots", -12)
cue(end("L02") - 0.05, "keys_mouse", -5)
# exam
cue(start("L03") + 0.1, "pencil_scribble", -10)
cue(B["fail"] - 0.1, "impact_hard", -6, note="F stamp")
cue(end("L03") + 0.02, "ding", -12)
for w_ in ("So", "The", "locked", "Tonight,", "fix"):
    cue(word("L04", w_) + 0.15, "text_ping", -10, note="group chat")
cue(end("L04") + 0.02, "whoosh_soft", -10)
# inside
cue(M + 0.2, "door_creak_long", -8, note="gym window")
cue(M + 1.6, "footstep_soft", -8)
cue(M + 2.3, "footstep_soft", -9)
cue(end("L05") + 0.02, "floor_creak", -8)
cue(start("L06") + 0.1, "door_open", -8, note="Room 12")
cue(B["graded"], "impact_soft", -8)
cue(end("L06") + 0.02, "heartbeat", -8)
cue(end("L07") + 0.02, "crackle_burst", -8, note="intercom wakes up")
cue(end("L08") + 0.02, "tinnitus", -12)
cue(B["scare1"], "jumpscare_sting", -6, note="JUMPSCARE 1: face at the door window")
cue(B["slam"] - 0.05, "impact_hard", -3, note="door slams")
cue(B["slam"] + 0.5, "thud_wood", -8, note="Kai's flashlight hits the floor")
for k, w_ in enumerate(("One.", "Two.", "Three.", "Four.")):
    cue(word("L09", w_) + 0.25, "tick", -8)
cue(end("L09") + 0.02, "heartbeat", -6)
cue(end("L10") + 0.02, "breath_close", -8)
cue(B["chalk"] - 0.1, "chalk_write", -3, note="chalk, by itself")
cue(word("L11", "Four") - 0.1, "chalk_write", -3)
cue(B["chalk_end"] + 0.05, "tinnitus", -12)
cue(B["scare2"], "jumpscare_sting", -5, note="JUMPSCARE 2: she is at the board")
cue(B["choice"], "impact_cinematic", -8)
cue(B["choice"] + 1.2, "ding", -8, note="TOP COMMENT banner")

C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0), sfx_duck_db=-5.0, amb_duck_db=-5.0,
         ceiling_dbtp=-1.7, cues=sorted(cues, key=lambda c: c["t"]))
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-4.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues")
