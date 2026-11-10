# VIDEO_005 — OPEN 24/7, Part 1

Built from the user's scene sheet (33 scenes, ~185 words, HUD clock + CUSTOMERS, 3 survival rules, 4-way choice).
Series bible: [`SERIES/OPEN_24_7/series_bible.md`](../../SERIES/OPEN_24_7/series_bible.md) · publish kit: [`PUBLISH.md`](PUBLISH.md).

## Files
| file | what |
|---|---|
| `script.json` | 33 VO lines (186 words) placed at the sheet's scene times (`at`); narrator / janitor / woman / sister / whisper |
| `voices/` | pitched reference clips: janitor (−5 st, low & slow), woman (+2 st), sister (+5 st); narrator = default voice |
| `edit_video005.py` | SCENES = the sheet (captions per line via `line_text`, key words RED/YELLOW), HUD (clock turns red at 3:33, CUSTOMERS glitch 2→4), rule cards, no-VO beat 17, choice screen with 4 pinned options |
| `anim2d.py` | 25 shots (store exterior, counter set, monitor with 4 feeds, aisle, back room, janitor, card, wall phone, the woman, dark-store inserts, choice) |
| `audio/build_cues.py` | 119 cues; rain + store air + fluorescent buzz / CRT hum beds, story sounds in every pause |

## Deviations from the sheet (and why)
* Runtime **1:27** (sheet ~1:24): the janitor's lower, slower voice runs past some 2–2.5 s slots; lines are never allowed to
  overlap, so later scenes start up to ~2 s late. Scene 17 was given its full beat by starting the woman's entrance at 0:41.
* VO wording: S01 "You took... the night shift." (pause for pace), S08 "Someone **is** standing there" (the "'s" was
  swallowed), S20 extra pauses, S23 "The phone **starts to ring**" ("phone rings" was heard as "foam rings"). Captions keep the
  sheet's text.
* Scene 21 and 30 are split into two lines (narrator + janitor / narrator + whisper) so each voice is right.
* "Silence" (scenes 28, 32): the music cuts out but rain and the monitor's hum stay, per the no-dead-air rule.

## QA
| check | result |
|---|---|
| Export | 87.1 s, 2614 frames in 175 s (0.067 s/frame), 1080×1920 / 30 fps / H.264 / AAC |
| qc_video.py | pass except "frozen" 1.2 s at scene 28 = the sheet's hard cut to black (intended); −14.4 LUFS, −1.29 dBTP |
| dead_air.py | **pass**: quietest 400 ms −31.5 LUFS, all pauses filled (−30…−21 LUFS), voice ≥ 8 LU over the bed on every line |
| Voice | 0 word mismatches on all 33 lines (Whisper small.en + base.en), every line 1.5–4.2 words/s |

Pipeline changes made for this video: `edl_engine` captions take per-line caption text (`line_text`; "" hides a line);
`place_lines` never overlaps lines placed with `at`; `mix.py` per-video `ceiling_dbtp` (bells/rings overshoot after AAC);
voice checker understands clock digits ("333" = 3:33), apostrophes, aisle/isle, backroom/back room.
