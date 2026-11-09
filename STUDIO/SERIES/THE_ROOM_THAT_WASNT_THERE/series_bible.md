# THE ROOM THAT WASN'T THERE — series bible

Psychological / interactive horror, multi-part Shorts / TikTok. Read before writing each part; update after it ships
and again when the winning comment is in.

## Premise
You wake in your apartment at exactly 3:17 AM. There's a door you've never seen. Behind it is another version of
your apartment — and someone already lives there who looks exactly like you.

## Planned arc
| part | title | beat |
|---|---|---|
| 1 | DON'T OPEN THE DOOR | two mysterious doors appear; you hear a voice identical to yours |
| 2 | THE DOOR YOU CHOSE | continues from the winning choice |
| 3 | SOMEONE IS MISSING | you discover someone has been impersonating you |
| 4 | THE OTHER APARTMENT | where the second door leads |
| 5 | THE REAL YOU | a revelation changes everything |

## Storytelling rules (from the brief)
1. Immediate hook. 2. No unnecessary intro. 3. Escalate gradually. 4. Reveal slowly. 5. New mysteries before old ones
resolve. 6. Powerful cliffhanger. 7. Every cliffhanger gives choices (A, B, …). 8. Choices genuinely change the next part.
9. Dialogue short, natural, unsettling. 10. Never show the monster early — shadows, sounds, voices only.

## Format (every part)
* 9:16, ~60–90 s, second person / present tense, one line = one cut (+ inserts), ALL-CAPS captions with one key word
  (RED danger / YELLOW object), HUD: `NIGHT N · APT 317` tag, a clock stuck on **3:17 AM**, a **DOORS** counter.
* **No dead air** (from Part 1 on): a scene-appropriate bed under the whole video (bedroom-at-3-AM ambience, wall clock,
  music drone) plus a story sound in every pause; SFX/ambience duck under the voice and swell in the pauses.
  `quality_control/dead_air.py` must pass: no 400 ms window below −42 LUFS, every pause's bed between −34 and −14 LUFS,
  voice ≥ 8 LU over the bed on every line.
* **Every voice is the same TTS voice on purpose** — the caller, the texts, the hallway voice and the thing behind the
  small door all "sound exactly like yours". Keep it that way.
* Choice screen: `PART N+1` / question / `COMMENT A OR B · TOP COMMENT DECIDES PART N+1`, lettered option pills placed
  on the door/object they refer to. Last VO line: "The top comment decides."
* Publish kit in `VIDEOS/VIDEO_NNN/PUBLISH.md`: title, description (3–5 emojis), creator's pinned comment
  (follow / reply / comment for PART N+1) — each in a copyable code block.

## Characters & voices
| who | seen as | notes |
|---|---|---|
| **YOU** | studio mascot (teen, red cap backwards) in bed, phone glow on your face | never speaks |
| **THE CALLER** | phone call from UNKNOWN; whisper | "Whatever you do, don't open your bedroom door." |
| **THE TEXTER** | texts from UNKNOWN, **+1 (555) 013-0317** | "I'm outside. Let me in." / "Don't listen to the thing pretending to be me." / "There's a second door behind your wardrobe. Get inside. NOW." |
| **THE HALLWAY VOICE** | never seen: knocks, shadows under the door (4 feet), handle turning | your own voice: "Hey. It's okay. I'm coming inside." |
| **THE THING BEHIND THE SMALL DOOR** | never seen: scratches, breath at the keyhole | "Finally. You found me." |

## Places
* **Apartment 317**, your bedroom: door on the left (lever handle, **no lock** — there never was one), wardrobe on the
  right wall (now an inch off the wall), window with blinds, nightstand with a red digital clock.
* **The small wooden door** behind the wardrobe: old planks, iron straps, ring handle, keyhole; fresh scratches from
  the other side.

## Clues planted in Part 1
Supports **A — hide in the small door** (the hallway thing is the danger):
* R15: under the bedroom door there are **four** feet, not two.
* R20: the door creaks in a way it never has — whatever is outside isn't using it normally.
* The caller warned you not to open the bedroom door, and the hallway voice is trying to come in.

Supports **B — stay and confront** (the small door is the trap):
* R09: the texts come from a number ending in **0317** — the stuck clock and your apartment number.
* R24: the dust in front of the small door is **scraped in an arc** — it has been opened from the inside.
* R27: the voice behind the small door says "Finally. You found me." — it has been waiting for you.

## HUD values
| part | clock | DOORS |
|---|---|---|
| 1 | 3:17 AM the whole time (never moves) | 1 → 2 (small door found) |

## Open mysteries
* Why is time stuck at 3:17? Why does everything (number, clock, apartment) say 317?
* Who called — the same one who texts? Which of the voices is the real you?
* What are the four feet in the hallway?

## Choices & winners
| part | question | A | B | winner |
|---|---|---|---|---|
| 1 (VIDEO_004) | WHICH DOOR DO YOU TRUST? | HIDE IN THE SMALL DOOR | CONFRONT WHAT'S OUTSIDE | _pending_ |

## Part 2 outlines (ready either way)
**If A — HIDE IN THE SMALL DOOR wins.** Recap hook: "You crawled through the small door. It locked behind you."
A cramped crawlspace opens into a hallway that is your hallway, mirrored left-to-right; family photos on the wall have
your face scratched out. The phone gets one bar: a new text — "Good. Now don't let it see you." Footsteps in the
mirrored apartment; your own voice humming in the kitchen. Rules from the texter arrive one by one (don't look at
mirrors, don't answer to your name, stay below the windows). Cliffhanger: the humming stops and someone says from the
next room, "I know you're here. I've been you for a while now." Choice: **A — hide in the closet / B — go and look.**

**If B — CONFRONT WHAT'S OUTSIDE wins.** Recap hook: "You stayed. You put your hand on the handle."
The scratching behind the wardrobe stops instantly, as if listening. The hallway goes quiet; then the bedroom door opens
on its own — the hallway is empty, but the hall carpet shows four wet footprints that stop at your door. Your phone
rings: it's your own number calling. The voice says "You chose wrong. It's in the room with you now." Something under
the bed shifts. Cliffhanger: the wardrobe slowly slides back over the small door by itself. Choice: **A — look under the
bed / B — run into the hallway.**
