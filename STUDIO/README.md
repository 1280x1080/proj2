# STUDIO — code-driven vertical-short pipeline

Story idea → finished 1080×1920 / 30 fps / H.264 + AAC MP4 with no manual editing.
CPU only, free/open-source tools only, all music and SFX synthesised by code, OFL fonts (Inter).

```
python STUDIO/make_video.py 001            # narrate → sfx → cues → music → mix → (render3d) → export → qc
python STUDIO/make_video.py 001 --from mix # resume from a step
python STUDIO/make_video.py 001 --stills 0 2.5 5   # test stills of the edit
```

## Install (what this container needed)
| tool | how | notes |
|---|---|---|
| Python libs | `pip install skia-python pyloudnorm faster-whisper soundfile scipy numpy pillow` | skia needs `apt-get install libegl1 libgl1` |
| TTS venv | `python3 -m venv ~/.venvs/tts`; CPU torch from `download.pytorch.org/whl/cpu`; Chatterbox deps; `pip install --no-deps chatterbox-tts` | Chatterbox pins torch 2.6 from PyPI (pulls ~2.5 GB of CUDA). Installing it `--no-deps` on CPU torch works. |
| Blender | 4.2.3 LTS tarball from download.blender.org → `/usr/local/bin/blender` | CPU EEVEE Next |
| ffmpeg | system package | |

## Layout
```
PIPELINE/
  tts/            narrate.py (N takes/line → Whisper → best take → word timing), place_lines.py, voice_qc.py, textnorm.py
  audio/          dsp.py, sfx_lib.py + sfx_*.py (@reg effects) → sfx_generate.py → AUDIO/sound_effects/*.flac + LIBRARY.json
                  music_gen.py (Score: buses, instruments, gate(), cue_videoNNN()), mix.py (cues.json → mix_master.wav)
  twod/           flat.py (vector cut-out puppets, cel shading, glows, vignettes), kit.py (keys/easing, blink, lip-sync, text, 1-point camera)
  blender_scripts/studio_lib/  scene, sets, characters (rig generator + crowd), lights, cameras, toon, lipsync
  blender_scripts/videos/      videoNNN.py: build(timing) + JOBS   (test3d.py = smoke test)
  rendering/      render_shot.py (one Blender job), render_needed.py (only frames the edit shows, parallel, resumable)
  editing/        edl_engine.py (EDL → mp4: segments, fx, overlays, captions, encode)
  quality_control/ qc_video.py, loop_test.py
VIDEOS/VIDEO_NNN/ script.json, beats.py, edit_videoNNN.py, anim2d.py, audio/build_cues.py, qc/, README.md
EXPORTS/          final mp4s
ASSETS/fonts/     Inter (OFL)
```

## How a video is wired
1. `script.json` → `narrate.py` → `audio/lines/*.wav`, `narration_raw.wav`, `timing.json` (word start/end).
2. `beats.py` turns words into story times (`B["reveal"] = ...`). The EDL, animation, SFX cues and music cue all
   import these, so a re-recorded line re-times everything.
3. `anim2d.py` (2D) draws each shot natively at 1080×1920; or `blender_scripts/videos/videoNNN.py` (3D) + `render_needed.py`.
4. `edit_videoNNN.py` = `SEGMENTS`, `OVERLAYS`, `CAPTIONS`, `AUDIO`, `DURATION`. All effects are 2D (zoom/punch-in, shake,
   flash, whip + motion blur, tint, VHS, pixelate, split, vignette, black, fade); overlays go through `paste()` which keeps
   them ≥ 36 px inside the frame and shrinks to fit.
5. `build_cues.py` → `cues.json` → `mix.py`: narration chain to −16 LUFS, music side-chain ducked, SFX/ambience buses,
   master −14 LUFS integrated, ≤ −1 dBTP (optional circular mix for loops).
6. Export (x264 slow, CRF 18, yuv420p, BT.709 tags, AAC 48 kHz, +faststart) → **show the video** → `qc_video.py` → fix → re-export.

## Measured speeds (this container: 4 CPU cores, 15 GB RAM)
| step | speed |
|---|---|
| Chatterbox TTS (CPU) | ~5 s of compute per 1 s of speech (first model load ~30 s plus a one-time ~3 GB weight download) |
| 2D compositor (puppet room + overlays + captions) | 0.067 s/frame with 4 workers → 10 s video in 20 s |
| Blender EEVEE 540×960, 1 sample + OIDN | ~0.9 s/frame after a ~15 s first-frame shader compile (test3d scene) |
| SFX library (24 effects) | 2 s |

## Known limits (honest)
* The 3D character generator is primitive-based (spheres/cylinders on a bone rig). Fine for blocking and simple shorts,
  far from production characters. Only test stills of the 3D path have been rendered; no full 3D video has been made yet.
* Chatterbox has no built-in way to pick a voice without a reference clip: with `voice_ref: null` every line uses the
  model's default voice (narrator and characters sound the same). Add per-character reference clips in `script.json`.
* The 2D side-view run cycle is rough; front-view puppets are the tested path.
