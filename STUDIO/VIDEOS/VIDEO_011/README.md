# VIDEO_011 — LAST ONE IN THE CALL, Part 1

Series bible: [`SERIES/LAST_ONE_IN_THE_CALL/series_bible.md`](../../SERIES/LAST_ONE_IN_THE_CALL/series_bible.md) · publish kit: [`PUBLISH.md`](PUBLISH.md).

* **Hook:** "It's one AM. Your whole squad just left the voice chat. So who is still breathing in your headset?" on the call UI.
* **Jumpscares (2):** SC1 after Jay's last whisper (mic scream + his tile becomes the grinning face); SC2 after "Look behind
  you" (the face over your shoulder). Music gates to near silence before each; slam zoom + shake + flash + `jumpscare_sting`.
* **Voices (Qwen3-TTS):** narrator (VIDEO_008 design) · JAY (new, `fx: phone`). Label `JAY · VOICE CHAT`.
* **Game screen:** generic original HUD — no real game's art.
* **Sound:** PC-fan bedroom bed, game audio, leave tones, knocks through Jay's mic, breathing on the open mic, door creak,
  knocks on your window; 7 new SFX (`sfx_gaming.py`).

## QA
| check | result |
|---|---|
| Export | 63.7 s, 1080×1920 / 30 fps — `qc_video.py` ALL PASSED (−14.2 LUFS, −1.65 dBTP) |
| Overlap check | clean |
| Voice QC | 14/14 lines correct ("Dee" heard as "D" — same sound; homophone added to `textnorm.py`) |
| Dead air | none. One pause is flagged loud on purpose: jumpscare 1 (−8.9 LUFS) |
| Frame review | 2–3 frames per cut; fixed: captions over the body in close-ups, title wrap, ending timing, A pin over a pill |
