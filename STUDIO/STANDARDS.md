# Studio standards (from the user's review notes) — follow on every video

## Before sending ANY video
1. Run the export: `edl_engine.py` prints `OVERLAP CHECK` (also `qc/overlaps.json`). It must say **clean**: no caption over
   an overlay (title, rule card, choice pill, chip) and no caption over a shot's keep-clear zones (faces, key props).
   Every shot with a character's face must register its face in `anim2d.ZONES[shot](t) -> [(name, l, t, r, b)]`.
2. **Visual pass at full size**, not only the thumbnail contact sheet: grab one full-res frame from every cut
   (`ffmpeg -ss T -i video.mp4 -frames:v 1`) and look for shapes overlapping wrongly — props poking out of hands, limbs
   crossing bodies, hands floating in front of chests, half-drawn objects, elements cut off oddly. If a prop doesn't
   read cleanly, remove it rather than ship it.
3. `qc_video.py` + `dead_air.py` + `voice_qc.py` pass (or every remaining flag is explained as intended).

## Lip-sync
* Every character who speaks must have their mouth driven by their own lines: `pose = TIMING.lip(pose, t, who)`.
  It sets `talk` (opens/closes on every syllable, closes between words) and `speaking=True`, which also animates
  "o" / "grin" mouth shapes (they used to stay frozen open).
* Custom-drawn characters (not `flat.Puppet`) need their own `talk` input (e.g. the smile opening).
* Shots get the **absolute video time** by default (segment `offset` defaults to the cut time) — never re-base a shot's
  clock, or poses / lip-sync / doors play at the wrong moment.

## Captions (style v2 — reference: the KAI label screenshot)
* **Fixed position** for the whole video (`CAPTIONS["y"]` = top of the first text line); no per-shot moves.
  Compose shots so faces sit above it (zoom close-ups about the real face centre).
* Fixed size; wraps to 2 lines; shrinks only if 3+ lines would be needed.
* One consistent entrance for every chunk: fade + 18 px rise in 0.16 s. No per-word pops. A chunk stays up until the
  next one when the gap is short (no blinking).
* ALL CAPS, key words RED (danger) / YELLOW (rules, objects).
* **Speaker label**: when a character (not the narrator) speaks, a small dark pill with their name in their colour sits
  centred just above the caption; their dialogue drops the quote marks.

## Emotion must match — face AND body
* Every line has one emotion, and the voice, the face and the body all show **that** emotion. Decide it per line in
  the scene table (e.g. `emotion="scared"`) next to the voice delivery / Qwen voice instruction.
* Use the presets: `pose = flat.emote(pose, "scared", t)` (then `TIMING.lip(pose, t, who)` for talking).
  12 presets: calm, happy, teasing, nervous, scared, terrified, shocked, suspicious, sad, angry, determined, neutral.
  Each sets brows, lids, eyes, mouth, head tilt, lean, crouch, arm positions, tremble and breathing rate together.
* Listeners react too: the character who isn't speaking still shows their emotion (a scared listener trembles,
  a suspicious one narrows their eyes) — no blank faces during someone else's line.
* Change emotion on story beats, with an eased blend (`emote(..., amount=span(t, beat, beat + 0.3))`), never a pop.
* Visual pass: for every cut, ask "would someone with the sound off read the same emotion?" If not, fix the pose.
* Preset sheet check: `emotions.png` (all presets on one character) must show no limbs crossing the body.
* Dark scenes: darken the ROOM, not the faces. Characters keep a readable key/moon light so their emotion still reads
  (VIDEO_007's first export failed this check: faces went near-black when the lights died).
