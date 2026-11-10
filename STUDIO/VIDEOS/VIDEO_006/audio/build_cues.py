"""cues.json for VIDEO_006 - night porch: wind + crickets-ish air under everything, a floor creak in the pause."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from beats import DURATION as D, end, start  # noqa: E402

cues = [
    dict(t=0.0, sfx="wind", gain_db=2, bus="amb", dur=D, fade_in=0.05, fade_out=0.3, note="night wind"),
    dict(t=0.0, sfx="room_tone", gain_db=0, bus="amb", dur=D, fade_in=0.05, note="air"),
    dict(t=0.05, sfx="floor_creak", gain_db=-12, pan=-0.2, note="porch boards"),
    dict(t=end("D1") + 0.02, sfx="floor_creak", gain_db=-10, pan=0.3, note="Kai shifts his weight"),
    dict(t=end("D3") + 0.05, sfx="door_creak_long", gain_db=-10, pan=0.0, note="the door creaks open by itself"),
]
C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0), sfx_duck_db=-5.0, amb_duck_db=-4.0,
         ceiling_dbtp=-1.6, cues=cues)
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-4.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues")
