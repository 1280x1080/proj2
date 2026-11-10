# VIDEO_008 — THE FREQUENCY THAT KNOWS TOMORROW, Part 1: "The Voice on the Radio"

The user's script, made to every rule in `STUDIO/STANDARDS.md`. Series bible:
[`SERIES/THE_FREQUENCY/series_bible.md`](../../SERIES/THE_FREQUENCY/series_bible.md) · publish kit: [`PUBLISH.md`](PUBLISH.md).

* **Voices (Qwen3-TTS, designed once):** narrator · YOU (young radio-host voice, heard through the speakers = `radio`
  colouring, and through the handset = `phone` colouring — `place_lines.voice_fx`) · UNKNOWN (older man, too gentle).
  Labels: `YOU · RADIO`, `YOU · PHONE`, `UNKNOWN`.
* **No faces for recordings:** speakers pump, VU needles swing and the handset's earpiece glows with whichever voice talks.
* **YOU on screen:** emotion per line from the scene table (calm → shocked → suspicious → nervous → scared → terrified →
  determined), blended on each line.
* **HUD:** clock ticks every second from 1:06:00; at 1:07:30 (the recording's timestamp — it passes during the choice
  screen) it turns red with a "1:07:30 — THE RECORDING" tag. TRANSMISSIONS counter 0 → 5.
* **Sound:** studio air + console hum + transmitter rack, radio static once the speakers are live, a tick every second,
  speaker pops / crackles, line-three rings, footsteps, heartbeat; 124 cues. 6 new SFX (`sfx_radio.py`).

## QA
| check | result |
|---|---|
| Export | 98.3 s, 2950 frames, 1080×1920 / 30 fps / H.264 / AAC |
| qc_video | all pass except **duration 98 s** (> 90 s guideline: the script is long and the designed narrator is unhurried; pauses already tightened from 102 s) |
| Overlap check | clean (faces, the MAIN POWER switch and the unplugged plug are registered keep-clear zones) |
| dead_air | pass — quietest 400 ms −32 LUFS, all pauses filled, voice ≥ 8.2 LU over the bed |
| Voice | 0 word mismatches on all 32 lines (both Whisper models), all lines within 1.5–4.2 words/s |
| Full-size pass | one frame per cut reviewed |

Fixed before sending (from the full-size pass and the overlap check): console faders under your chin in close-ups;
handset cut off; caption over the MAIN POWER switch and over the loose plug; the choice screen's camera moves slid the
transmitter's labels under the pills (now one gentle push, transmitter re-framed, doubt lines on dark backing and sized to
their half); caption text on top of the white fader knobs.
