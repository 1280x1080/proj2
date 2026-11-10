"""cues.json for VIDEO_008.  No dead air: studio room tone + console/computer hum + transmitter hum all the way,
radio static whenever the speakers are live, a wall-clock tick every second (it's a countdown to 1:07:30),
and a story sound in every pause.  "Silence" = the music drops; hum, tick and static stay."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from beats import B, CLOCK0, DEATH, DURATION as D, end, start  # noqa: E402

lib = json.loads((HERE.parents[2] / "AUDIO" / "sound_effects" / "LIBRARY.json").read_text())
cues = []


def cue(t, sfx, gain_db=0.0, bus="sfx", pan=0.0, note="", **kw):
    assert sfx in lib, sfx
    cues.append(dict(t=round(max(0.0, t), 3), sfx=sfx, gain_db=gain_db, bus=bus, pan=pan, note=note, **kw))


# beds
cue(0.0, "room_tone", 3, "amb", dur=D, fade_in=0.02, note="studio air")
cue(0.0, "crt_hum", 2, "amb", dur=D, fade_in=0.02, note="console / computer hum")
cue(0.0, "transmitter_hum", 3, "amb", pan=0.4, dur=D, fade_in=0.02, note="transmitter rack")
cue(B["speakers_on"], "radio_static", 0, "amb", dur=D - B["speakers_on"], fade_in=0.1, note="speakers live: dead-air static")
t = 0.5
while t < D:
    cue(t, "tick", -20, pan=-0.4, note="wall clock (counting down to 1:07:30)")
    t += 1.0
# story sounds
cue(0.0, "crackle_burst", -6, note="the recording cuts in (hook)")
cue(B["speakers_on"], "speaker_on", -3, note="speakers turn on by themselves")
cue(start("F08") + 0.2, "click_ui", -12, note="search")
cue(start("F08") + 1.0, "computer_beep", -8, note="no file")
for k in range(4):
    cue(B["ring"] + k * 1.6, "desk_phone_ring", -10 if k == 0 else -13, pan=0.35, note="line three")
cue(start("F13") - 0.2, "crackle_burst", -8, note="recording again")
cue(B["ring_stop"] + 0.05, "impact_soft", -16, note="ringing cuts")
cue(end("F17") + 0.05, "breath_close", -14, pan=0.3, note="breathing on the line")
cue(start("F19") + 0.2, "footstep_soft", -12, note="you step back")
cue(start("F19") + 0.9, "footstep_soft", -13)
cue(B["crackle"], "crackle_burst", -3, note="speakers crackle")
cue(end("F22") + 0.05, "heartbeat", -8, note="frozen")
cue(B["computer"] - 0.05, "computer_beep", -6, note="transmission received")
for k in range(3):
    cue(B["ring2"] + k * 1.6, "desk_phone_ring", -12, pan=0.35, note="phone again")
cue(B["freeze"], "impact_cinematic", -8, note="freeze")
death_t = DEATH - CLOCK0
if death_t < D:
    cue(death_t, "glitch", -6, note="1:07:30 passes")
    cue(death_t + 0.05, "crackle_burst", -8)

C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0), sfx_duck_db=-5.0, amb_duck_db=-5.0,
         ceiling_dbtp=-1.7, cues=sorted(cues, key=lambda c: c["t"]))
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-4.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues")
