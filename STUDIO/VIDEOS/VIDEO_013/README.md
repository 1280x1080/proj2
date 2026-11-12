# VIDEO_013 — AFTER HOURS, Part 1

Series bible: [`SERIES/AFTER_HOURS/series_bible.md`](../../SERIES/AFTER_HOURS/series_bible.md) · publish kit: [`PUBLISH.md`](PUBLISH.md).

* **Hook:** the five of you in the dark hallway → a red pen grading the answer sheets by itself → "Rewind."
* **Cast:** YOU, KAI, BEN (boys) · MIA, ZOE (girls); each plays the group mood differently (`VARIANT` in `anim2d.py`).
* **Jumpscares (2):** the teacher's face at the door window; then at the board after the chalk writes "4 LEFT".
* **Top comment rule:** yellow banner on the choice screen + narrator reads it.
* **Voices (Qwen3-TTS, no new designs):** narrator (VIDEO_008) · MIA (VIDEO_009 "her") · INTERCOM (VIDEO_009 principal, `fx: intercom`).
* New SFX: `chalk_write`.

## QA
| check | result |
|---|---|
| Export | 72.1 s, 1080×1920 / 30 fps — `qc_video.py` ALL PASSED (−14.2 LUFS, −1.58 dBTP) |
| Overlap check | clean |
| Voice QC | 13/13 lines, 0 mismatches |
| Dead air | none; the two jumpscare gaps are loud on purpose |
| Frame review | 2–3 frames per cut; fixed: friends hidden below their webcam tiles, red ink overflowing the sheets, captions over legs, choice pills covering the board, a too-still choice screen, one sound peaking |
