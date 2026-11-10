# THE FREQUENCY THAT KNOWS TOMORROW — series bible

Read before writing each part; update after it ships and when the comments decide.

## Premise
You work the night shift alone at a small radio station (WKTM 98.7 FM). At 1:06 AM the station plays a recording of
**you dying** — made 90 seconds in the future (stamped 1:07:30). Different versions of you start sending warnings
through the speakers, the phone and the playout computer, and they contradict each other.

## Format (every part)
* 9:16, ~90–100 s, second-person present-tense narration; follow all of `STUDIO/STANDARDS.md` (emotion presets per line
  for YOU, lip-sync for any on-screen speaker, caption style v2 with speaker labels, overlap check, no dead air).
* Voices (Qwen3-TTS, designed once, reused every part — files in `VIDEOS/VIDEO_008/voices/`):
  narrator (low calm baritone) · **YOU** (young radio-host voice; heard as `radio` through the speakers and as `phone`
  through the handset, coloured per line by `place_lines.voice_fx`) · **UNKNOWN** (older man, too gentle, hoarse).
  Speaker labels: `YOU · RADIO`, `YOU · PHONE`, `UNKNOWN`.
* Recorded voices have no faces: speakers, VU meters and the phone's earpiece react to them instead.
* HUD: `NIGHT N · WKTM 98.7` tag; a clock that **ticks every real second** from 1:06:00 and turns red with a
  "1:07:30 — THE RECORDING" tag when the recording's time passes; a TRANSMISSIONS counter.
* Choice screen: question + lettered pills pinned to the objects (A on the transmitter, B on the phone) with the
  "What if…" doubt line under each; "COMMENT A OR B · YOUR CHOICE DECIDES PART 2".

## Characters
| who | notes after Part 1 |
|---|---|
| **YOU** (studio mascot, red cap backwards) | alone at the desk, has not touched the phone or the transmitter |
| **YOU · RADIO** (the recording) | warned: don't answer line three; don't let him know you're alone; you answered him last time and don't remember; destroy the transmitter |
| **UNKNOWN** (line three) | "Hello? Are you alone in there?" — through a phone whose cable is unplugged |
| **YOU · PHONE** | "Please. Don't destroy the transmitter." |
| **THE STATION** | sent "STOP LISTENING TO THE VERSION OF YOU THAT WANTS TO SURVIVE." from its own address |

## Objects
Line 3 (red button), the unplugged phone cable on the floor, studio speakers (turn on by themselves), the playout
computer (no file, no schedule), TX-1 transmitter with a red MAIN POWER switch, the wall clock.

## Clues planted in Part 1
* A — destroy the transmitter: the radio-you warned correctly about line three (it rang); the UNKNOWN voice came through
  a disconnected phone; the station itself is the sender of the strange message.
* B — answer the phone: the radio-you admits you "answered him last time" (and you're still alive?); the message says the
  version of you that wants to survive is the one lying; the phone-you only begs, it never threatens.

## HUD values
| part | clock | TRANSMISSIONS |
|---|---|---|
| 1 | 1:06:00 → ~1:07:39 (passes **1:07:30** on the choice screen) | 0 → 5 |

## Choices & winners
| part | question | A | B | winner |
|---|---|---|---|---|
| 1 (VIDEO_008) | WHAT DO YOU DO? | DESTROY THE TRANSMITTER | ANSWER THE PHONE | TBD |

## Part 2 outlines
**A — DESTROY THE TRANSMITTER.** You pull MAIN POWER. Everything dies — clock, lights, phone — except the speakers, which
keep playing: the recording now runs past 1:07:30. On it you hear yourself pull the switch… and something step out of
the control-room window. New rule from the dead radio: "Don't look at the window." Choice: hide in the booth / run.

**B — ANSWER THE PHONE.** You pick up line three. The phone-you is calm: "Good. Now listen — the one on the radio isn't
you anymore. It's been you since 1:07:30 last night." The clock jumps back to 1:06:00. The speakers start the hook again,
word for word. Choice: trust the phone / hang up and pull the plug.
