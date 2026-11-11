# VIDEO_012 — ORDER #000, Part 1

Series bible: [`SERIES/ORDER_000/series_bible.md`](../../SERIES/ORDER_000/series_bible.md) · publish kit: [`PUBLISH.md`](PUBLISH.md).

* **Hook:** "It's two AM. You order food. The app says your driver is one minute away... but the restaurant is forty
  minutes from your house." (app map → flash of him on the door camera).
* **Twists:** driver at the door before the phone is down → the app says the real driver is still at the restaurant →
  the bag is already on your bed → the mukbang girl stops eating and warns you → the bag moves.
* **Jumpscares (2):** his face slams into the door camera; something looks out of the bag.
* **Top comment rule:** yellow "TOP COMMENT DECIDES PART 2" banner on the choice screen + narrator reads it.
* **Voices (Qwen3-TTS):** narrator (VIDEO_008) · DELIVERY GUY (new, `fx: door`) · MUKBANG GIRL (VIDEO_009 "her", `fx: phone`).
* **Apps on screen:** generic originals (QuickBite, a vertical-video feed).
* 5 new SFX (`sfx_food.py`): slurp, paper_rustle, order_chime, cam_static, run_steps.

## QA
| check | result |
|---|---|
| Export | 66.8 s, 1080×1920 / 30 fps — `qc_video.py` ALL PASSED (−14.2 LUFS, −1.5 dBTP) |
| Overlap check | clean |
| Voice QC | 13/13 lines, 0 mismatches |
| Dead air | none; the two jumpscare gaps are loud on purpose (−13.7 / −12.7 LUFS) |
| Frame review | 2–3 frames per cut; fixed: mukbang girl hidden behind the table, her "happy eating" face read as scared, he stayed on camera after the scare, banner wrapped onto two lines, bag under the banner |
