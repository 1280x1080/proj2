# GOING DOWN — series bible

Read this before writing every new part; update it after the part is final and again when the winning comment is in.

## Premise
Every night at 3 AM the elevator in Tower B stops at floor 13, a floor the 22-storey building doesn't have.
A tall woman in a red raincoat wants a ride. An old janitor who seems to live in the elevator knows the rules.
Each part ends on a choice; **the top comment decides the next part**.

## Format (every part)
* 9:16, 60–90 s, ~150–210 words of second-person, present-tense VO, 25–40 scenes, cut on (almost) every line.
* Formula: hook (0–3 s, title card `GOING DOWN / PART N`; Part 2+ opens on a 1-line recap of the winning choice
  as consequence) → wrong normal → presence (HUD counter bump) → guide gives 3 SURVIVAL RULES (cards) →
  tests (one emotional-manipulation test; lights die; colour shifts to red) → cliffhanger (guide's last warning
  contradicts the situation; threat closer; freeze on your face) → choice screen.
* Choice screen wording (fixed): `PART N+1` / `<QUESTION>?` / `COMMENT 1 OR 2 · TOP COMMENT DECIDES PART N+1`,
  pills `1 <OPTION>` (red) and `2 <OPTION>` (blue). The last VO line says "The top comment decides."
* Captions: 2–4 words, ALL CAPS, one key word: RED = danger / threat, YELLOW = rules / important objects.
  Dialogue in quotes. Kept off faces in close-ups.
* HUD: top-left tag `NIGHT N · TOWER B` + clock; top-right `RIDERS` counter (flashes red when it changes).
* Project files per part: `VIDEOS/VIDEO_NNN/script.json`, `beats.py`, `edit_videoNNN.py` (SCENES → SEGMENTS /
  OVERLAYS / CAPTIONS), `audio/build_cues.py`, `scene_sheet.py` → `SCENES.md`, `README.md`.

## Characters
| who | look | voice / behaviour | status after Part 1 |
|---|---|---|---|
| **YOU** | the studio mascot (`CAST["mascot"]`): teen, 5'9", red cap on backwards with bangs showing, grey hoodie, jeans, white sneakers | never speaks; we hear your thoughts through the narrator | in the lobby doorway, wet hand on your shoulder, rules written on your left palm in black marker |
| **GUS** | old janitor, grey coveralls, name tag GUS, grey stubble, wire glasses, sits on an upturned bucket in the back corner, mop beside him | slow, low, certain; never raises his voice | gave the 3 rules; slapped your hand off button 13; told you to **stay in** against his own rule 3. **Not visible in the mirror. Sleeve wet.** |
| **THE RIDER** | very tall woman in a red raincoat, hood up, always facing a wall/corner, long grey fingers, drips water | speaks in borrowed voices (so far: polite stranger, YOUR MOM) | boarded at 13 during Part 1; still in the front corner |
| **MOM** (voice only) | — | warm, tired — "Sweetie, it's Mom." | used by the Rider to tempt you to break rule 2 |
| **MR. REYES** | night doorman, navy uniform, friendly | waves you out of the elevator | seen only in the (possibly fake) lobby at the end of Part 1 |

## Places
* **Tower B**: 22 floors, no 13th (12 → 14). You live on 22.
* **The elevator car**: brushed-steel walls, mirror on the back wall, button panel right of the doors, floor
  indicator + brass bell above the doors, 6 ceiling light panels.
* **Floor 13**: long dark hallway, every apartment door open.
* **The lobby** (end of Part 1): warm light, wall clock reading 3:07, daylight through the glass street doors.

## Survival rules
| # | rule (written on your palm) | given | tested | result |
|---|---|---|---|---|
| 1 | Never look in the mirror with the doors open. | Part 1 | Part 1 (floor 9: someone behind you in the mirror) | kept |
| 2 | Never press a floor she asks for. | Part 1 | Part 1 (Rider asks; then Mom's voice) | kept (Gus slapped your hand away) |
| 3 | Only get out when the bell rings twice. | Part 1 | **Part 1 cliffhanger → Part 2** | bell rang twice… plus a very faint third ding |

## HUD values
| part | clock start → end | RIDERS start → end | notes |
|---|---|---|---|
| 1 | 3:07 → 3:16 → **jumps back to 3:07** in the lobby | 1 → 2 (Gus) → 3 (Rider inside) → **4** (wet hand, nobody new visible) | clock reset and the 4th rider are open mysteries |

## Clues planted (Part 1)
Supports **1 — STEP OUT** (Gus is lying / not human):
* S05 (0:09) + S17 (0:39): the mirror shows the back corner empty — Gus is sitting there.
* S24 (0:54): Gus's coverall sleeve is dripping wet; the hand on your shoulder (S30, 1:04) is wet.
* Rule 3 is Gus's own rule, and the bell did ring twice.

Supports **2 — STAY IN** (the lobby is fake):
* S26 (0:58): the HUD clock jumps back to 3:07 and the lobby wall clock says 3:07.
* S26: daylight through the lobby's street doors at 3 AM.
* S26: a barely audible third ding after the two loud ones (−34 dB in the mix) — rule 3 may not be met.
* RIDERS = 4 when the hand lands: someone besides you, Gus and the Rider is in the car.

## Open mysteries (keep consistent)
* Who/what is the 4th rider?
* Why isn't Gus in the mirror? How long has he been in the elevator?
* What does the Rider want from a floor-13 button press?
* Why does time loop back to 3:07?

## Choices & winners
| part | question | option 1 | option 2 | winner | top comment (paste) |
|---|---|---|---|---|---|
| 1 (VIDEO_003, 71.6 s) | DO YOU STEP OUT? | STEP OUT | STAY IN | _pending_ | |

## Next-part outlines (Part 2, ready either way)
**If 1 — STEP OUT wins.** Recap hook: "You stepped out. The doors were gone before you turned around."
The elevator is a blank wall. The lobby is perfect — too perfect: every clock says 3:07, it's daylight outside
but the street is empty and silent, Mr. Reyes keeps smiling and never blinks. Your palm rules are smeared by the
wet hand. Gus's voice crackles through the lobby intercom: "I told you. That's not your floor." A real doorman's
log book under the desk holds 3 new rules (e.g. "Don't answer the desk phone", "Don't let Mr. Reyes see your palm",
"Take the stairs, never the elevator"). The Rider's red raincoat is reflected in the lobby glass, closer every cut.
Tests → the desk phone rings in your mom's voice again. Cliffhanger: the stairwell door opens onto floor 13.
Choice: **PART 3 — DO YOU TAKE THE STAIRS? 1 TAKE THE STAIRS / 2 CALL THE ELEVATOR.**

**If 2 — STAY IN wins.** Recap hook: "You stayed in. The doorman's smile slid off his face."
The doors close on the lobby as Mr. Reyes's face drops like wet paper. The wet hand squeezes. Gus: "Don't turn around."
(new rule pressure). The car goes UP. Gus admits he has ridden this car every night since 1987 — "Every night she
asks. Every night I say no." (pays off the mirror clue: he's a ghost, but on your side… maybe). The 4th rider is
revealed as a reflection of YOU in the mirror with the doors open (rule 1 test). New rules: "When she says your
name, say Gus's", "Count the dings out loud", "If the light goes green, get down". Cliffhanger: doors open on 22 —
your apartment door is open and your mom calls your name from inside.
Choice: **PART 3 — DO YOU GO HOME? 1 GO HOME / 2 STAY WITH GUS.**

## Style notes
* Palette: cold fluorescent (FLUO) → dying panels (DIM) → deep red emergency (RED); lobby = warm amber.
  Natural colours otherwise, no over-saturated grade.
* Danger stays mostly off-screen or facing away (the Rider is never seen from the front in Part 1).
* Every part needs ≥ 2 clues per option and one emotional-manipulation test.

## Pitches (Part 0)
1. **GOING DOWN** *(chosen)* — 3 AM elevator, a floor that doesn't exist, a janitor with rules. HUD: clock + RIDERS.
2. **NIGHT SHIFT** — first overnight at a 24-hour gas station; a laminated rule sheet from a manager who never shows;
   a trucker parked at pump 4 every night is the guide; the threat comes in as customers. HUD: clock + CUSTOMERS.
3. **LOW BATTERY** — lost on a trail after dark; a park ranger on an emergency call talks you out; something on the
   trail starts answering in the ranger's voice. HUD: clock + BATTERY %.

Why 1: a confined space with built-in counters (floors, riders, dings) gives visual, testable rules (mirror, buttons,
bell) and a clean 50/50 (step out vs stay in) — the same engine as the reference without copying its train setting.
