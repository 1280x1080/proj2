# VIDEO_003 — GOING DOWN, Part 1 (series pilot)

Vertical horror "decide the story" short, built on the formula of the "Line 9" reference
(hook → wrong normal → presence → guide + 3 survival rules → tests → cliffhanger → choice screen).
Series continuity lives in [`STUDIO/SERIES/GOING_DOWN/series_bible.md`](../../SERIES/GOING_DOWN/series_bible.md).

**Logline.** 3 AM. Your elevator presses button 13 by itself — in a building with no 13th floor. A woman in a red
raincoat wants a ride; Gus the janitor writes three rules on your palm. At the lobby the bell rings twice… and Gus
tells you to stay in.

## Files (project format)
| file | what |
|---|---|
| `script.json` | 30 VO lines, 191 words (narrator / gus / rider), delivery + emotion per line, `pause_after` |
| `beats.py` | every beat from word timing (`audio/timing.json`); falls back to word-count estimates before narration |
| `edit_video003.py` | **`SCENES`** (32 scenes: shot, key word + colour, visual, camera, SFX, HUD) → `SEGMENTS`, `OVERLAYS` (title card, HUD tag/clock/RIDERS, 3 SURVIVAL RULE cards, choice screen), `CAPTIONS` |
| `audio/build_cues.py` | SFX/ambience cues from the scene table (library names only) |
| `scene_sheet.py` → `SCENES.md` | the full per-scene sheet (timestamp, duration, VO, captions, key word/colour, visual, camera, SFX, HUD) |

| `audio/` | narration done: `lines/*.wav`, `narration_raw.wav`, `timing.json`, `narration_report.json`, `voice_qc.json` |

Production next steps: `anim2d.py` with the 17 shots named in SCENES (`panel_cu, car_wide, you_cu, mirror_pov, doors_13,
gus_reveal, gus_cu, palm_cu, indicator_cu, doors_9, rider_corner, thumb_cu, hand_slap, car_red, lobby_pov,
wet_hand_cu, choice_bg`), a `cue_video003()` in music_gen, then `python STUDIO/make_video.py 003 --from sfx`.

## Choice
**PART 2 — DO YOU STEP OUT?** `1 STEP OUT` · `2 STAY IN` · `COMMENT 1 OR 2 · TOP COMMENT DECIDES PART 2`
(the last VO line also says "Do you step out? The top comment decides.")

Why it's a real 50/50: rule 3 (Gus's own rule) says go, the bell rang twice and the lobby looks like home — but Gus,
who just saved you from rule 2, says stay. Each side has evidence:

| 1 — STEP OUT (Gus is lying) | 2 — STAY IN (the lobby is fake) |
|---|---|
| S05 (0:09) and S17 (0:39): the mirror shows Gus's corner **empty** | S26 (0:58): HUD clock jumps **back to 3:07**; lobby clock says 3:07 |
| S24 (0:54): Gus's sleeve is **wet** — so is the hand on your shoulder (1:04) | S26: **daylight** through the lobby doors at 3 AM |
| The bell rang twice: rule 3 is satisfied | A **faint third ding** under the two loud ones (−34 dB) |
| | RIDERS ticks to **4** when the hand lands — someone new is in the car |

**Pinned comment**
> Gus wrote rule 3 himself… so why is he breaking it now? 🤔 Count the dings at 0:58 before you vote. And watch the clock.
> 1 or 2 — the top comment decides Part 2.

Part 2 outlines for both options are in the series bible.

## Final check
| check | result |
|---|---|
| Hook within 3 s | S01 "Your elevator pressed a button by itself." ends at **2.2 s**, over the `GOING DOWN / PART 1` title card; button 13 clicks on frame 0 |
| Runtime 60–90 s | **71.6 s** from the recorded narration's word timing (VO 191 words) |
| Scenes | **32**; all 1.5–3.5 s except the deliberate freeze (0.95 s) and the choice screen (4.15 s) |
| Rules | #1 tested (S16–S18, floor 9 mirror), #2 tested twice incl. the Mom-voice manipulation (S19–S24), #3 set up as the Part 2 choice (S26–S29) |
| Real 50/50 | rule 3 + the bell vs Gus's warning; ≥ 2 planted clues per side (table above); RIDERS = 4 cuts both ways |
| Voice | Chatterbox, 2–6 takes per line: **0 word mismatches on all 30 lines** with Whisper small.en, and again with base.en in voice_qc; all lines 2.6–4.2 words/s |
| Captions | ≤ 5 words per chunk; the only 1-word chunks are the beats "ONE." "TWO." "THREE." "SWEETIE," "LOBBY." (same as the reference's "ONE.") |

Script fixes made during narration QC: S02 "riding" → "going" (heard as "writing" in 6/6 takes), S07/S17 split into short
sentences, S08 → "She starts to turn. The doors cut her off." ("doors close/shut/slam" kept being heard as "Doris closed" /
"door is shut"), S23 → "Your thumb finds the button.", slower delivery on S07/S23/S24/S30 (S24 "slaps" was heard as "slapped").
The TTS checker's number normaliser also had a bug ("13th" counted as a mismatch against "thirteenth"; "3 a.m." against "AM");
fixed in `PIPELINE/tts/textnorm.py` (QC code, not editing code) and every line re-scored.

## Caption gap (needs your OK — editing code untouched as asked)
The series spec is ALL-CAPS captions with one key word in RED (danger) or YELLOW (rules/objects). The current
`edl_engine.py` builds captions from the narration text and supports one emphasis colour, so today:
* captions render in the script's case (the script can't be ALL CAPS: Chatterbox read "IT" as "I.T." in a test), and
* only the RED key words are coloured; YELLOW key words render white.

`CAPTIONS` already carries the full spec (`upper=True`, `line_colors={line: {word: colour}}`); the engine ignores
unknown keys. Reading those two keys in `draw_captions` is a ~10-line change — say the word and I'll make it.

## Other production notes
* **Voices**: no reference clips yet, so narrator, Gus and the Rider use the same default Chatterbox voice. Add clips
  in `script.json` → `voices` (`gus`: old male, `rider`: your "Mom" voice) and re-run narrate (only those lines regenerate).
* **SFX**: cues use existing library sounds. Worth adding for this series: elevator door slide, elevator bell
  (two-tone), cable creak/drop, marker squeak, water drip.
* **Font**: captions use Inter Black (the engine's font). The reference uses a condensed display font; an OFL condensed
  font would also be an engine change.
