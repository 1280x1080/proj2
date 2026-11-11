# VIDEO_010 — FLIGHT 417, Part 1: "The Same Route"

Series bible: [`SERIES/FLIGHT_417/series_bible.md`](../../SERIES/FLIGHT_417/series_bible.md) · publish kit: [`PUBLISH.md`](PUBLISH.md).

* **Hook:** "Imagine boarding a plane that flies the same route as the plane that vanished ten years ago." over a radar
  blip dying → flash-forward of the ghost plane in your window.
* **Voices (Qwen3-TTS):** narrator + OLD MAN reuse the VIDEO_008 designs; CAPTAIN is new (PA colouring `fx: intercom`).
* **Acting:** emotion preset per line for YOU and the OLD MAN. New in `flat.py` (all videos): pinpoint pupils and sweat
  for fear, tears that follow the face, age lines (`Style.old`). He cries when he sees his wife, then smiles through it.
* **Sound:** cabin drone, radar pings, chimes, flicker, shudder, a hollow ghost drone once Flight 417 is alongside,
  belt click, the exit handle turning; 6 new SFX (`sfx_plane.py`).

## QA
| check | result |
|---|---|
| Export | 80.9 s, 2427 frames, 1080×1920 / 30 fps / H.264 / AAC — `qc_video.py` ALL PASSED |
| Overlap check | clean (first export flagged the CTA under the last caption → CTA now starts after the line) |
| Voice QC | 19/19 lines, 0 mismatches |
| Dead air | none; pauses −31.4…−16.6 LUFS; voice ≥ 11 LU over bed |
| Frame review | 3 frames per cut at full size; fixed: seated poses, watch hand, captions over bodies (captions now sit on the seat backs), stray belt straps, window sliver in the close-up |
