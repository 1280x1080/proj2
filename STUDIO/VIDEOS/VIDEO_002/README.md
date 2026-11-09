# VIDEO_002 — mascot test (5 s, 2D)

The new mascot (`CAST["mascot"]` = `CAST["teen"]` in `PIPELINE/twod/flat.py`): average-height teenager,
5'9" (~175 cm, `height=1.03` vs the 170 cm base puppet), slim build, grey sweater, jeans, white sneakers,
**red cap worn backwards**: brim sticks out behind the head (peeks out on the side away from the face when he turns),
snapback strap + opening over the forehead with hair showing through, bangs hanging below the band, short sides.
Same flat + cel-shadow style as the rest of the cast.

Beat: drops into frame on frame 0 and lands → "Yo! I'm the new mascot. Same studio, fresh cap." (wave, thumb to chest,
turn to show the brim, hand to the cap) → wink.

| | |
|---|---|
| Narration | Chatterbox default voice, 3 takes, chosen take 0 word mismatches |
| Picture | 150 frames, 8.7 s (0.057 s/frame, 4 workers) |
| Mix | −14.1 LUFS, −1.0 dBTP on the export |
| qc_video.py | 14/14 pass |

Fixed from test stills: teen too small → moved closer; drop-in started too high (cap cut off on frame 0);
hand stopped beside the head on the cap tap → elbow bend so the hand reaches the back of the cap;
bangs hid the eyebrows → cap band raised, bangs shortened, brows drawn over the hair.

Known weak spots: the cap-tap hand goes behind the head (reads as touching the back of the cap, not the brim);
the wink is drawn as an overlay in anim2d.py rather than a per-eye control in the puppet; same default TTS voice as VIDEO_001.
