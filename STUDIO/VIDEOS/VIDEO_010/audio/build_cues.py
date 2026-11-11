"""cues.json for VIDEO_010 (FLIGHT 417 Part 1).  No dead air: cabin drone all the way (radar-room hum in the 10-years-ago
scenes), a hollow ghost drone from the moment the other plane appears, and a story sound in every pause."""
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


# beds
cue(0.0, "crt_hum", 2, "amb", dur=B["hook_ghost"], fade_in=0.02, note="radar room (hook)")
cue(B["hook_ghost"], "ghost_drone", 2, "amb", dur=B["story"] - B["hook_ghost"], fade_in=0.05, note="flash-forward: the other plane")
cue(B["story"], "cabin_drone", 0, "amb", dur=start("L02") - B["story"], fade_in=0.1, note="Flight 417, ten years ago")
cue(start("L02") - 0.1, "crt_hum", 4, "amb", dur=B["tonight"] - start("L02") + 0.1, fade_in=0.05, note="radar room")
cue(B["tonight"], "cabin_drone", 2, "amb", dur=D - B["tonight"], fade_in=0.1, note="your flight")
cue(B["plane"], "ghost_drone", 0, "amb", dur=D - B["plane"], fade_in=1.2, note="Flight 417 alongside")
# hook
for k in range(3):
    cue(0.15 + k * 0.7, "radar_ping", -8, note="radar")
cue(1.6, "power_down", -8, note="blip gone (hook)")
cue(B["hook_ghost"], "impact_cinematic", -8, note="ghost plane")
cue(B["story"] - 0.2, "whoosh_soft", -12)
# ten years ago
cue(B["story"] + 0.3, "whoosh", -14, note="take-off")
t = start("L02")
while t < B["vanish"] - 0.2:
    cue(t, "radar_ping", -8, note="radar")
    t += 0.8
cue(B["vanish"], "power_down", -6, note="it vanishes")
cue(end("L02") + 0.02, "tinnitus", -20, note="nothing")
# tonight
cue(B["tonight"] + 0.1, "cabin_ding", -8, note="seat-belt sign")
cue(start("L04") + 0.3, "tick", -8, note="his watch")
cue(start("L04") + 1.3, "tick", -8)
cue(end("L04") + 0.02, "tick", -8)
cue(end("L05") + 0.02, "breath_close", -14, pan=0.3, note="he sighs")
cue(B["flicker"], "flicker_zap", -4, note="lights flicker")
cue(B["flicker"] + 0.35, "flicker_zap", -6)
cue(B["black"], "power_down", -5, note="screens die")
cue(end("L06") + 0.02, "turbulence", -8, note="a shudder")
cue(start("L07") - 0.5, "cabin_ding", -8, note="PA")
cue(end("L07") + 0.02, "heartbeat", -10)
cue(B["plane"], "riser", -12, note="something outside")
cue(start("L09"), "impact_soft", -10)
cue(end("L09") - 0.9, "impact_cinematic", -7, note="417")
cue(start("L10") + 0.3, "heartbeat", -10)
cue(end("L10") + 0.02, "breath_close", -12, note="your breath")
cue(end("L11") + 0.02, "heartbeat", -10)
cue(B["point"], "whoosh_soft", -10, note="she points")
cue(start("L13") + 0.05, "whoosh", -10, note="you turn")
cue(end("L13") + 0.02, "turbulence", -10)
cue(start("L14") - 0.45, "cabin_ding", -8, note="PA again")
cue(start("L14") - 0.1, "crackle_burst", -12, note="wrong voice")
cue(end("L14") + 0.05, "heartbeat", -8)
cue(B["unbuckle"], "belt_click", -4, pan=0.3, note="he unbuckles")
cue(end("L16") + 0.02, "breath_close", -12)
cue(B["door"] + 0.5, "handle_turn", -3, pan=-0.4, note="the exit handle turns by itself")
cue(B["door"] + 2.0, "handle_turn", -3, pan=-0.4)
cue(B["freeze"], "impact_cinematic", -6, note="freeze")
cue(B["choice"], "riser", -12, note="choice")

C = dict(duration=D, loop=False, narration=dict(file="narration_raw.wav", offset=0.0), sfx_duck_db=-5.0, amb_duck_db=-5.0,
         ceiling_dbtp=-1.7, cues=sorted(cues, key=lambda c: c["t"]))
if (HERE / "music.wav").exists():
    C["music"] = dict(file="music.wav", gain_db=-4.0, duck_db=-10.0)
(HERE / "cues.json").write_text(json.dumps(C, indent=2))
print(f"{len(cues)} cues")
