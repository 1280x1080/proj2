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
