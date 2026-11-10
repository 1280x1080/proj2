# OPEN 24/7 — series bible

Read before writing each part; update after it ships and when the winning comment is in.

## Premise
You took the night shift at a lone convenience store on an empty road (HWY 9 MART). 3 AM, rain. It pays triple and
nobody tells you why. A laminated card from an old janitor holds the survival rules.

## Format (every part)
* 9:16, ~1:24 (Part 1 shipped at 1:27), ~33 scenes, ~185 words of second-person present-tense VO; lines placed at the sheet's scene times.
* HUD: in-world clock (top left, under the `NIGHT N · HWY 9 MART` tag) + **CUSTOMERS** counter (top right).
  The clock turns red at 3:33; the counter glitches when something unseen is counted.
* Captions: the sheet's caption text per line (can differ from the VO), ALL CAPS, key words RED (danger) / YELLOW (rules,
  objects). Survival-rule cards pop on screen when a rule is spoken.
* A no-VO beat mid-video: "YOUR COMMENT COULD DECIDE PART 2" (rain only).
* **No dead air**: rain + store air + fluorescent buzz / CRT hum under everything, a story sound in every pause; the
  sheet's "silence" = music drops out, rain and the monitor hum stay. `quality_control/dead_air.py` must pass.
* Voices: narrator = default TTS voice; janitor (and the whisper behind you) = lower pitched reference clip; the woman =
  slightly higher; your sister = high (clips in `VIDEOS/VIDEO_005/voices/`, reuse them every part).
* Choice screen: `PART N+1 — WHAT DO YOU DO?`, numbered options **pinned to their spots in the scene** with leader lines,
  "TOP COMMENT CHOOSES WHAT HAPPENS NEXT" / "Comment your number + why". Pinned comment must say the top comment has
  to name a number to count.
* Publish kit in `VIDEOS/VIDEO_NNN/PUBLISH.md` (title, description, pinned comment — copyable boxes).

## Characters
| who | look | status after Part 1 |
|---|---|---|
| **YOU** — new night clerk | studio mascot (red cap backwards), green store vest, name tag ALEX | behind the counter in the dark, monitor glow on your face, a wet hand on your shoulder |
| **THE JANITOR** | old, white hair, navy coveralls, tired eyes, **name tag scratched off**, mop + yellow bucket | came out of the back room; gave the rules; blocked the woman with his mop; stopped you answering at 3:33. **Real or fake: unresolved** — his voice is now coming from the back room while a whisper behind you sounds like him |
| **THE BAREFOOT WOMAN** (threat) | soaking wet, long black hair over her face, smile slightly too wide, barefoot, grey dress | asked to come behind the counter; left — **the chime didn't ring**; leaves wet bare footprints |
| **THE MANAGER** | only via text | "Whatever happens, DON'T open the back room." |
| **YOUR LITTLE SISTER** | voice on the 3:33 call, caller ID HOME | "Please pick up. I'm scared." |

## Survival rules (laminated card)
| # | rule | tested in Part 1 |
|---|---|---|
| 1 | Never let anyone behind the counter. | yes — the woman asks; the janitor's mop blocks the gap |
| 2 | If the lights go out, don't look at the monitor. | set up — lights die, the monitor is the only light; a whisper repeats the rule |
| 3 | Never answer the phone at 3:33. | yes — sister's voice; janitor stops you. It rings again at 3:34 (loophole?) |
Manager's rule: don't open the back room.

## HUD values
| part | clock | CUSTOMERS |
|---|---|---|
| 1 | 2:58 → 3:00 → 3:12 → 3:20 → **3:33 (red)** → 3:34 | 0 → 1 (figure on camera) → 2 (janitor) → 3 (woman) → 2 (she leaves) → **glitch 2→4** (2 visible) |

## Clues planted in Part 1
1. **LOOK AT THE MONITOR** — scene 08/09: the monitor showed a figure in aisle 4 the room didn't; wet footprints were real.
2. **TRUST THE JANITOR** — scene 21: his mop saved you; scene 26: he stopped the 3:33 call.
3. **RUN TO THE BACK ROOM** — scene 31: the line of light under the back-room door is the only light left, and the
   janitor's voice is coming from there.
4. **ANSWER THE PHONE** — scene 27: the rule only says 3:33; it's 3:34 and ringing again.

## Open mysteries
* Why does it pay triple? Who were the clerks before you?
* Which janitor is real? Why is his name tag scratched off?
* What did CUSTOMERS 4 count? What's in the back room?

## Choices & winners
| part | question | options | winner |
|---|---|---|---|
| 1 (VIDEO_005) | WHAT DO YOU DO? | 1 look at the monitor / 2 trust the janitor / 3 run to the back room / 4 answer the phone | TBD |

## Part 2 outlines (one per option)
1. **LOOK AT THE MONITOR** — The feed shows you at the counter with the barefoot woman's hand on your shoulder, and the
   real janitor in the back room waving you over. You broke rule #2. CUSTOMERS jumps to 5. Next: what happens when you
   break a rule.
2. **TRUST THE JANITOR** — You close your eyes and wait. The lights come back; the janitor behind you is smiling too wide.
   The real janitor bursts out of the back room. Twist: there were always two janitors.
3. **RUN TO THE BACK ROOM** — You break the manager's warning. Inside: the real janitor, a stack of old "Night pay x3"
   sticky notes from past clerks, and a new rule written on the wall. Reveal: why it pays triple.
4. **ANSWER THE PHONE** — The loophole works. It's really your sister, at home: "Why is someone standing behind you on the
   store camera? It's on the news livestream." New mystery: who's watching the feed?
