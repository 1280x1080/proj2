# VIDEO_007 — standards test (5 s): "lights out"

Narrator: "Then the lights go out." · KAI: "Mia? Where are you?" · MIA: "Right behind you."

Exercises every rule in `STUDIO/STANDARDS.md`: Qwen3-TTS voices (reused from VIDEO_006, no redesign), `flat.emote`
per line for speaker AND listener (Kai neutral → nervous when the lights die → scared while calling → terrified while
she answers; Mia teasing), `TIMING.lip` lip-sync, caption style v2 with speaker labels, `ZONES` face boxes + overlap
check (clean), no dead air (hall air, light hum → power-down → wind, heartbeat, floor creak, breath).

QA: 0 word mismatches (both Whisper models), qc_video all pass (5.0 s, −14.0 LUFS, −1.75 dBTP), dead_air pass
(voice ≥ 9.1 LU over the bed), overlap check clean.  Fixed after the first full-size review: faces were near-black after
the lights died (darkness now applies to the room only; characters keep moonlight).
