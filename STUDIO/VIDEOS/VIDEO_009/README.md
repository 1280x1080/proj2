# VIDEO_009 — THE LAST BELL, Part 1: "The Lockdown"

Psychological horror / romance. Series bible: [`SERIES/THE_LAST_BELL/series_bible.md`](../../SERIES/THE_LAST_BELL/series_bible.md)
· publish kit: [`PUBLISH.md`](PUBLISH.md). Made to every rule in `STUDIO/STANDARDS.md`.

* **Hook (0–3 s):** laughing together → lights go red → cut to the door + knock; then "THE PROBLEM? SHE'S ALREADY
  SITTING NEXT TO YOU." and back to the calm afternoon.
* **Voices (Qwen3-TTS, designed once):** narrator (young woman, hushed) · HER (teen girl, soft) · OUTSIDE = HER's voice
  through the door (`fx: door`) · INTERCOM (principal, `fx: intercom`). Labels: `HER`, `OUTSIDE · HER VOICE?`, `INTERCOM`.
* **Acting:** emotion preset per line for HER and YOU (happy/teasing → shocked → scared → determined → terrified → sad),
  lip-sync on HER lines, blush in the intro, head shake on "slowly shakes her head", tears from P26. Talking mouths for
  frown/flat emotions are now tense shapes (corners down), never a D-smile (pipeline fix in `flat.py`).
* **The thing outside:** silhouette behind frosted glass, hand on the glass while it begs, tilts on "you know I like
  you", shadow under the door, the handle turns.
* **Sound:** empty-classroom bed → emergency buzz + distant looping alarm; PA chime, three knocks, knocking again, phone
  vibrate + pings, floor creak, handle turn, heartbeat; love theme (lo-fi pluck) → drone + heartbeat pulse → her theme
  as a detuned music box. 8 new SFX (`sfx_school.py`).

Build: `narrate.py --engine qwen` → `place_lines.py` → `voice_qc.py` → `music_gen.py 9` → `audio/build_cues.py` →
`mix.py` → `dead_air.py` → `edl_engine.py` → `qc_video.py`.
