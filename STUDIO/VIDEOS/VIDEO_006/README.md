# VIDEO_006 — Qwen3-TTS demo (5 s): narrator + two-person exchange

Narrator: "Midnight. One dare." · MIA: "You go first." · KAI: "No way. You go!"  (porch of an old house, flashlight)

All three voices are **Qwen3-TTS** (Apache-2.0, open weights), designed from text and then cloned:
| speaker | design prompt | reference clip |
|---|---|---|
| narrator | Male narrator, late 30s, low calm baritone, quiet late-night storytelling voice, slight rasp, unhurried. | `voices/narrator_qwen.wav` |
| mia | Teenage girl, 16, bright clear voice, teasing but a little nervous, slightly breathy, quick. | `voices/mia_qwen.wav` |
| kai | Teenage boy, 17, tenor, playful but obviously scared, voice cracks slightly when nervous. | `voices/kai_qwen.wav` |

QA: 0 word mismatches (small.en + base.en), −14.0 LUFS, −2.4 dBTP, no dead air (wind + porch creaks under everything,
the door creaks open at the end), voice ≥ 14 LU over the bed, qc_video all pass. 150 frames in 10.9 s.
