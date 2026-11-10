"""cues.json for VIDEO_007: hallway air + light hum, power-down on "out", wind + heartbeat in the dark."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from beats import B, DURATION as D, end, start  # noqa: E402

cues = [
    dict(t=0.0, sfx="room_tone", gain_db=2, bus="amb", dur=D, fade_in=0.05, note="hall air"),
    dict(t=0.0, sfx="lamp_buzz", gain_db=2, bus="amb", dur=B["out"] + 0.1, fade_in=0.05, fade_out=0.05, note="light hum"),
    dict(t=B["out"] + 0.2, sfx="wind", gain_db=-2, bus="amb", dur=D - B["out"], fade_in=0.4, note="house creaks in the wind"),
    dict(t=B["out"] - 0.05, sfx="power_down", gain_db=-6, note="lights die"),
    dict(t=end("T1") + 0.05, sfx="heartbeat", gain_db=-10, note="Kai's heart"),
    dict(t=end("T2") + 0.02, sfx="floor_creak", gain_db=-8, pan=-0.4, note="someone behind him"),
    dict(t=start("T3") - 0.1, sfx="breath_close", gain_db=-16, pan=-0.3, note="her breath"),
    dict(t=end("T3") + 0.05, sfx="impact_soft", gain_db=-10, note="sting"),
]
C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0), sfx_duck_db=-5.0, amb_duck_db=-4.0,
         ceiling_dbtp=-1.6, cues=cues)
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-4.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues")
