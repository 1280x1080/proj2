# VIDEO_001 — "The fourth flicker" (10 s pipeline test, 2D mode)

**Story.** 11 PM. Narrator: *"Every night at eleven, Mia's lamp flickered exactly three times."* The lamp insert flickers
on "three", "times" and just after. Back on Mia, it flickers a **fourth** time: punch-in, shake, stamp "FOUR?!".
Mia: *"Wait… that was four."* Then three knocks at the door; whip to the door. (Not designed to loop.)

Export: `STUDIO/EXPORTS/video001.mp4` · rebuild: `python STUDIO/make_video.py 001`

## Files
| file | what |
|---|---|
| `script.json` | 2 lines (narrator, Mia) |
| `beats.py` | every story time computed from word timing (flickers, reveal, knocks, DURATION) |
| `anim2d.py` | shots `room` (one-point perspective living room, Mia puppet, floor lamp) and `lamp` (insert) |
| `edit_video001.py` | 3 segments, 4 overlays (chip, HUD counter, stamp, text), captions with speaker label |
| `audio/build_cues.py` | 27 SFX/ambience cues; new SFX added for this video: `lamp_buzz`, `flicker_zap`, `door_knock` |
| `PIPELINE/audio/music_gen.py: cue_video001` | uneasy pad → silence punch on the reveal → drone + tremolo cluster → knock gates |

## Render / QA report
| | |
|---|---|
| Narration | Chatterbox, default voice, 2 takes per line, **0 word mismatches** on both lines (Whisper small.en); independent re-check with base.en: 0 mismatches, 2.65 and 3.01 words/s |
| Picture | 300 frames, 2D, **20.3 s total (0.067 s/frame, 4 workers)**. Expected ~0.05–0.1 s/frame; on target. |
| Mix | −14.36 LUFS integrated, −1.0 dBTP (QC on the exported AAC) |
| qc_video.py | **14/14 checks pass**: 1080×1920, 30 fps, h264/yuv420p/BT.709, AAC 48 kHz, 10.0 s, A/V lengths match, no black, no freeze, no long silence |

### Fixed after the first stills / first export
* Mia was too small in the wide shot → moved closer to camera (she's now ~55 % of frame height).
* Stamp overlapped the HUD → moved down; then it was unreadable on the darkened frame → stamp now has a light card behind it.
* Emphasised caption word ("four.") ate the space before it → extra padding for emphasised words.
* Speaker label was tiny and overlapped the caption → larger label on a dark pill.
* Close-ups cropped the top of the head → punch-in reduced from 1.75× to 1.55×.
* QC contact sheet sampled frames slightly off its labels → now selects exact frame numbers.

### Known weak spots
* Narrator and Mia use the same default TTS voice (no reference clips supplied yet).
* The "Wait…" pause is short: the chosen take reads it as "Wait, that was four."
* The lamp insert is simple flat shapes; the room has no ambient-occlusion or contact shadows apart from the floor shadow.
* Mia's body barely moves (idle breathing, head turns, startle dip). Hands don't gesture while she talks.
