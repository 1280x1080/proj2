"""cues.json for VIDEO_009 (THE LAST BELL Part 1).  No dead air: empty-classroom bed (HVAC, fluorescent hum, kids far
outside) until the alarm; from the alarm the emergency light buzz + a distant looping hallway alarm under everything.
Every pause carries a story sound (scribble, chair, knocks, breath, phone, handle)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from beats import B, DURATION as D, end, start  # noqa: E402

lib = json.loads((HERE.parents[2] / "AUDIO" / "sound_effects" / "LIBRARY.json").read_text())
cues = []


def cue(t, sfx, gain_db=0.0, bus="sfx", pan=0.0, note="", **kw):
    assert sfx in lib, sfx
    cues.append(dict(t=round(max(0.0, t), 3), sfx=sfx, gain_db=gain_db, bus=bus, pan=pan, note=note, **kw))


A = B["alarm"]
# beds
cue(0.0, "classroom_after", 3, "amb", dur=D, fade_in=0.02, note="empty classroom after school")
cue(B["hook_red"], "lamp_buzz", -4, "amb", dur=B["story"] - B["hook_red"], fade_in=0.05, note="hook flash-forward: red light")
cue(A, "lamp_buzz", -4, "amb", dur=D - A, fade_in=0.3, note="emergency light buzz")
t = A + 3.0
while t < D:  # the hallway alarm keeps going, muffled, under the whole lockdown
    cue(t, "lockdown_alarm", -24, pan=0.5, note="distant alarm down the hall")
    t += 3.0
# hook
cue(B["hook_red"], "light_buzz_out", -6, note="lights go red")
cue(B["hook_door"] + 0.1, "knock_slow", -6, pan=0.3, note="knock (hook)")
cue(B["hook_door"] + 0.45, "knock_slow", -7, pan=0.3)
cue(B["story"] - 0.15, "whoosh_soft", -12, note="back to the afternoon")
# calm afternoon
cue(start("P02") + 0.5, "pencil_scribble", -8, note="working on the project")
cue(start("P03") + 0.6, "pencil_scribble", -15)
cue(start("P04") + 0.2, "chair_scrape", -16, pan=0.2, note="she scoots closer")
# lockdown
cue(A - 0.05, "lockdown_alarm", -2, pan=0.2, note="alarm starts screaming")
cue(A + 0.02, "impact_cinematic", -10)
cue(start("P06"), "light_buzz_out", -6, note="lights turn red")
cue(start("P07") - 0.9, "pa_chime", -8, pan=0.3, note="intercom")
cue(start("P09") + 0.2, "heartbeat", -14)
cue(start("P10") + 0.3, "chair_scrape", -10, pan=-0.2, note="moving away from the windows")
cue(start("P10") + 1.4, "footstep_soft", -14)
cue(end("P10") - 0.6, "tinnitus", -22, note="hallway goes silent")
for k, kt in enumerate(B["knocks"]):
    cue(kt, "knock_slow", -2, pan=0.35, note="three knocks" if k == 0 else "")
cue(start("P13") + 0.6, "breath_close", -16, pan=-0.2, note="her breath")
cue(B["knock2"] - 0.25, "door_knock", -5, pan=0.35, note="knocking again")
cue(B["knock2"] + 0.2, "door_knock", -6, pan=0.35)
cue(start("P17") + 0.2, "impact_soft", -16, note="she grabs your arm")
cue(start("P19"), "heartbeat", -10, note="blood runs cold")
cue(start("P21") + 0.3, "riser", -16)
cue(B["photo"] + 0.05, "phone_vibrate", -6, note="phone vibrates")
cue(B["photo"] + 1.0, "text_ping", -10)
cue(start("P24") + 0.05, "whoosh", -10, note="you spin around")
cue(start("P24") + 0.6, "floor_creak", -12, pan=-0.4, note="nobody there")
cue(start("P25") - 0.1, "text_ping", -8, note="another message")
cue(start("P26") + 0.4, "breath_close", -12, pan=-0.2, note="crying")
cue(B["handle"] + 0.1, "handle_turn", -3, pan=0.35, note="the handle turns")
cue(start("P29") + 0.2, "whoosh_soft", -14)
cue(B["freeze"], "impact_cinematic", -6, note="freeze")
cue(B["choice"], "riser", -12, note="choice")

C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0), sfx_duck_db=-5.0, amb_duck_db=-5.0,
         ceiling_dbtp=-1.7, cues=sorted(cues, key=lambda c: c["t"]))
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-4.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues")
