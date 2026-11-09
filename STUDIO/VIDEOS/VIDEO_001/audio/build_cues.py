"""Build cues.json for VIDEO_001 from the EDL beat times (re-run after any re-timing)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from beats import B, DURATION, FLICKS_ALL  # noqa: E402
import edit_video001 as E  # noqa: E402

cues = []


def cue(t, sfx, gain_db=0.0, bus="sfx", pan=0.0, note="", **kw):
    cues.append(dict(t=round(t, 3), sfx=sfx, gain_db=gain_db, bus=bus, pan=pan, note=note, **kw))


# ambience bed
cue(0.0, "room_tone", -2, "amb", dur=DURATION, fade_in=0.05, note="living room tone")
cue(0.0, "lamp_buzz", -6, "amb", pan=-0.3, dur=DURATION, fade_in=0.05, note="lamp mains hum")
t = 0.5
while t < DURATION - 0.3:  # wall clock
    cue(t, "tick", -20, pan=0.35, note="wall clock")
    t += 1.0

# picture-led cues
cue(0.15, "pop", -16, note="11:00 PM chip")
for i, ft in enumerate(FLICKS_ALL):
    on_lamp_cu = E.cut_lamp_in <= ft < E.cut_lamp_out
    cue(ft - 0.01, "flicker_zap", -3 if i == 3 else -7, pan=0.0 if on_lamp_cu else -0.45, note=f"flicker {i + 1}")
cue(E.cut_lamp_in - 0.12, "whoosh_soft", -14, note="cut to lamp")
cue(B["reveal"] + 0.02, "impact_soft", -6, note="4th flicker punch-in")
cue(B["reveal"] + 0.02, "whoosh_soft", -10, note="punch-in air")
cue(B["reveal"] + 0.12, "pop", -12, note="FOUR?! stamp")
cue(B["reveal"] + 0.45, "heartbeat", -8, note="tension")
cue(B["reveal"] + 1.35, "heartbeat", -10, note="tension")
cue(E.whip_t - 0.25, "whoosh", -9, note="whip to door")
for k, kt in enumerate(B["knocks"]):
    cue(kt, "door_knock", -1 - k * 0.5, pan=0.25, note=f"knock {k + 1}")

C = dict(duration=DURATION, loop=False,
         narration=dict(file="narration_raw.wav", offset=0.0),
         music=dict(file="music.wav", gain_db=-4.0, duck_db=-10.0),
         cues=sorted(cues, key=lambda c: c["t"]))
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues -> {HERE / 'cues.json'}")
