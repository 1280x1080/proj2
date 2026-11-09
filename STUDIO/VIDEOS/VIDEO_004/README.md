# VIDEO_004 — THE ROOM THAT WASN'T THERE, Part 1: "Don't Open the Door"

Your script, made in the studio format. Series bible: [`SERIES/THE_ROOM_THAT_WASNT_THERE/series_bible.md`](../../SERIES/THE_ROOM_THAT_WASNT_THERE/series_bible.md).
Publish kit (title, description, pinned comment): [`PUBLISH.md`](PUBLISH.md). Scene sheet: `SCENES.md`.

## Files
| file | what |
|---|---|
| `script.json` | 31 lines, 216 words; narrator / caller / texter / double / thing — all the same voice on purpose ("sounds exactly like yours") |
| `beats.py` | beats from word timing (ring, answer, the 3 knocks, texts, "Silence", handle, creak, small door, freeze, choice) |
| `edit_video004.py` | SCENES → 35 cuts, HUD (`NIGHT 1 · APT 317`, clock stuck on 3:17, DOORS 1→2), title card, choice screen (A/B on each door), ALL-CAPS captions with red/yellow key words |
| `anim2d.py` | 11 shots: clock, phone (incoming / call / lock screen / chat), you in bed, bedroom door (wide / close / under / handle), room wide, wardrobe, small door, two-door choice screen |
| `audio/build_cues.py` | 118 cues: 3 AM bedroom bed + room air + wall clock all the way, tinnitus after "Silence", story sounds in every pause |

## No dead air (new for this series)
* Beds under the whole video: `night_room` (fridge hum through the wall, distant traffic, wind), room air, a slow wall-clock tick,
  a music drone that never switches off; after "Silence." the music thins to a high cluster + tinnitus ring (still, not empty).
* A story sound sits in every pause: ringtone + buzz, the 3 slow knocks in the pause after "Three slow knocks.", text pings,
  hallway floor creaks, handle squeak, the long door creak, breathing at the door, scratching, heartbeat before the freeze.
* `mix.py` now ducks the SFX and ambience buses under the voice (opt-in `sfx_duck_db` / `amb_duck_db`), so the background
  swells in the pauses and steps back for speech.
* `quality_control/dead_air.py` (new) measures it: **PASS** — quietest 400 ms window −30 LUFS (limit −42), all 31 pauses filled
  at −31.5…−16 LUFS, voice ≥ 10.3 LU above the bed on every line.

## QA
| check | result |
|---|---|
| Export | 82.65 s, 2480 frames in 161 s (0.065 s/frame), 1080×1920 / 30 fps / H.264 / AAC |
| qc_video.py | **all pass**: −14.1 LUFS, −1.16 dBTP, no black, no frozen picture, no silence |
| Voice | 0 word mismatches on all 31 lines (Whisper small.en + base.en), every line 1.5–4.2 words/s |
| Hook | "You wake up at three-seventeen AM." ends at 2.1 s over the title card; clock flips to 3:17 on frame 9 |

Fixed along the way: walls/door far too bright for 3 AM; floating finger shapes on the phone; phone at the shoulder instead of the ear;
choice screen half black; feet under the door invisible (gap now lit cold); A/B pills too small; two 1 s still frames (added slow pushes);
5 lines read too fast (slow delivery + written pauses; take picker now prefers a take within the pace limit); the voice checker's false
alarms for "3.17am", "Nox", "towards", "Creek" (normaliser fixes, every line re-scored).

## Known weak spots
* The hallway threat is only shadows, sounds and a handle — by design (rule 10), but the middle section is door-heavy.
* "You" is the studio mascot with the red cap, in bed — brand over realism.
* All voices are the same default TTS voice (intended here, but a reference clip for the narrator would raise quality).
