"""cues.json for VIDEO_002 from the beat times."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from beats import B, DURATION  # noqa: E402

cues = []


def cue(t, sfx, gain_db=0.0, bus="sfx", pan=0.0, note="", **kw):
    cues.append(dict(t=round(max(0.0, t), 3), sfx=sfx, gain_db=gain_db, bus=bus, pan=pan, note=note, **kw))


cue(0.0, "room_tone", 0, "amb", dur=DURATION, fade_in=0.02, note="room")
cue(0.0, "whoosh", -8, note="drops into frame")
cue(B["land"], "impact_soft", -3, note="lands")
cue(B["land"], "footstep_hard", -6, pan=-0.15, note="left shoe")
cue(B["land"] + 0.03, "footstep_hard", -7, pan=0.15, note="right shoe")
cue(B["land"] + 0.05, "pop", -12, note="NEW MASCOT chip")
cue(B["studio"] - 0.12, "whoosh_soft", -11, note="push-in")
cue(B["cap"] + 0.02, "thud_wood", -9, note="taps cap")
cue(B["cap"] + 0.05, "pop", -10, note="FRESH CAP stamp")
cue(B["wink"] + 0.05, "ding", -9, note="wink sparkle")

C = dict(duration=DURATION, loop=False, narration=dict(file="narration_raw.wav", offset=0.0),
         music=dict(file="music.wav", gain_db=-3.0, duck_db=-9.0), cues=sorted(cues, key=lambda c: c["t"]))
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues -> {HERE / 'cues.json'}")
