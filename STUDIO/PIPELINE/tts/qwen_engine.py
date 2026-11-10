"""qwen_engine.py - Qwen3-TTS (Apache-2.0, open weights) as a narrate.py engine.  CPU, float32.

Run narrate.py with the Qwen virtualenv:
    ~/.venvs/qwentts/bin/python PIPELINE/tts/narrate.py VIDEOS/VIDEO_NNN/script.json --engine qwen

Voices (script.json "voices", per speaker; "voice_ref" for the narrator):
    "voices": {
      "narrator": {"design": "Male narrator, late 30s, low calm baritone, quiet late-night storytelling voice."},
      "mia":      {"design": "Female, 17, bright and quick, nervous laugh in her voice.",
                   "ref_text": "optional sentence the designed reference clip says"},
      "gus":      "voices/gus.wav"            # a real clip -> cloned (put its transcript in voices/gus.txt)
    }
A "design" voice is created ONCE with Qwen3-TTS-VoiceDesign (from the text description), saved to
voices/<who>_qwen.wav + .txt, and from then on every line is spoken by Qwen3-TTS-Base cloning that clip, so the
character sounds the same in every line and every part ("Voice Design then Clone" from the model card).
Delivery / emotion come from the text itself (punctuation, wording); the line's "delivery" maps to sampling
temperature (calm = steadier, excited = livelier).
"""
from __future__ import annotations

import gc
import os
from pathlib import Path

import numpy as np

DESIGN_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
CLONE_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
DEFAULT_NARRATOR = ("Neutral narrator, adult, clear mid-range voice, calm and measured storytelling pace, "
                    "close to the microphone.")
DEFAULT_REF_TEXT = "It was late, and the street outside was quiet. Somewhere a door closed, and I waited."
TEMPERATURE = {"calm": 0.6, "slow": 0.6, "whisper": 0.6, "neutral": 0.7, "warm": 0.7, "dramatic": 0.8,
               "excited": 0.85, "fast": 0.8}


class QwenEngine:
    name = "qwen"

    def __init__(self):
        import torch
        self.torch = torch
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        self._clone = None
        self._prompts = {}
        self.sr = 24000

    # ---------------------------------------------------------------- voices
    def prepare_voices(self, script, vdir):
        """Create any designed reference clips that don't exist yet.  Returns {who: path}."""
        import soundfile as sf
        vdir = Path(vdir)
        specs = dict(script.get("voices", {}))
        specs.setdefault("narrator", script.get("voice_ref") or {"design": DEFAULT_NARRATOR})
        out, todo = {}, []
        for who, spec in specs.items():
            if spec is None:
                spec = {"design": DEFAULT_NARRATOR}
            if isinstance(spec, dict):
                p = vdir / "voices" / f"{who}_qwen.wav"
                if not p.exists() or (p.with_suffix(".design").exists() and p.with_suffix(".design").read_text() != spec["design"]):
                    todo.append((who, spec, p))
                out[who] = p
            else:
                out[who] = vdir / spec
        if todo:
            from qwen_tts import Qwen3TTSModel
            model = Qwen3TTSModel.from_pretrained(DESIGN_MODEL, device_map="cpu", dtype=self.torch.float32)
            for who, spec, p in todo:
                p.parent.mkdir(parents=True, exist_ok=True)
                ref_text = spec.get("ref_text", DEFAULT_REF_TEXT)
                self.torch.manual_seed(1234)
                w, sr = model.generate_voice_design(text=ref_text, language="English", instruct=spec["design"])
                sf.write(str(p), np.asarray(w[0], dtype=np.float32), sr)
                p.with_suffix(".txt").write_text(ref_text)
                p.with_suffix(".design").write_text(spec["design"])
                print(f"designed voice '{who}' -> {p.name}  ({spec['design'][:70]}...)")
            del model
            gc.collect()
        return out

    # ---------------------------------------------------------------- synthesis
    def _model(self):
        if self._clone is None:
            from qwen_tts import Qwen3TTSModel
            self._clone = Qwen3TTSModel.from_pretrained(CLONE_MODEL, device_map="cpu", dtype=self.torch.float32)
        return self._clone

    def _prompt(self, voice_ref):
        key = str(voice_ref)
        if key not in self._prompts:
            import soundfile as sf
            x, sr = sf.read(str(voice_ref))
            if x.ndim == 2:
                x = x.mean(1)
            txt_p = Path(voice_ref).with_suffix(".txt")
            ref_text = txt_p.read_text().strip() if txt_p.exists() else None
            self._prompts[key] = self._model().create_voice_clone_prompt(
                ref_audio=(x.astype(np.float32), sr), ref_text=ref_text, x_vector_only_mode=ref_text is None)
        return self._prompts[key]

    def synth(self, text, voice_ref, seed, exaggeration=0.5, cfg_weight=0.5, temperature=0.75, delivery=None):
        if voice_ref is None:
            raise ValueError("qwen engine needs a voice (run prepare_voices first)")
        self.torch.manual_seed(seed)
        temp = TEMPERATURE.get(delivery or "", temperature)
        w, sr = self._model().generate_voice_clone(text=text.replace('"', ""), language="English",
                                                   voice_clone_prompt=self._prompt(voice_ref), temperature=temp)
        self.sr = sr
        return np.asarray(w[0], dtype=np.float64), sr
