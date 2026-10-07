"""Experimental family-voice narration. Runs only when a parent installed it.

Input (stdin JSON): {"sample": "<wav path>", "language": "ru", "pages": [...]}
Output: the same shape as voice_worker.synthesize_book.

Two optional local engines are supported, tried in this order:
  1. Chatterbox Multilingual (MIT licence)        pip install chatterbox-tts
  2. Coqui XTTS-v2 (non-commercial model licence) pip install coqui-tts
Neither engine is bundled, and neither was verified by the Storyworld test
suite: quality, speed and language coverage must be checked on the family's
own computer. No sample or text leaves the machine.
"""

import base64
import io
import json
import sys
import tempfile
import wave
from pathlib import Path

from voice_worker import synthesize_book

# Storyworld locale -> language code understood by the cloning engines.
LANGUAGE_CODES = {
    "en-US": "en", "es-ES": "es", "ru-RU": "ru", "de-DE": "de", "fr-FR": "fr",
    "it-IT": "it", "pt-BR": "pt", "pl-PL": "pl", "tr-TR": "tr", "ar-JO": "ar",
    "he-IL": "he", "hi-IN": "hi", "zh-CN": "zh", "ja-JP": "ja", "ko-KR": "ko",
}
XTTS_CODES = {"zh": "zh-cn"}
XTTS_LANGUAGES = {"en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "ar", "zh", "ja", "ko", "hi"}

_engine = {}


def available_engine() -> str | None:
    try:
        import chatterbox.mtl_tts  # noqa: F401
        return "chatterbox"
    except Exception:  # an optional dependency may fail in many ways
        pass
    try:
        import TTS.api  # noqa: F401
        return "xtts"
    except Exception:
        return None


def to_pcm16_wav(samples, rate: int) -> str:
    import numpy as np
    samples = np.asarray(samples, dtype=np.float32).reshape(-1)
    if samples.size == 0 or not np.isfinite(samples).all():
        raise ValueError("The family voice returned empty audio")
    peak = float(np.max(np.abs(samples)))
    if peak > 0.96:
        samples = samples * (0.96 / peak)
    sound = io.BytesIO()
    with wave.open(sound, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())
    return base64.b64encode(sound.getvalue()).decode("ascii")


def speak_chatterbox(text: str, sample: str, language: str) -> str:
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    if "model" not in _engine:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _engine["model"] = ChatterboxMultilingualTTS.from_pretrained(device=device)
    model = _engine["model"]
    audio = model.generate(text, language_id=language, audio_prompt_path=sample)
    return to_pcm16_wav(audio.detach().cpu().numpy(), int(model.sr))


def speak_xtts(text: str, sample: str, language: str) -> str:
    import torch
    from TTS.api import TTS
    if language not in XTTS_LANGUAGES:
        raise ValueError("This language is not supported by the installed family-voice engine")
    if "model" not in _engine:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _engine["model"] = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    with tempfile.TemporaryDirectory() as directory:
        target = str(Path(directory, "line.wav"))
        _engine["model"].tts_to_file(text=text, speaker_wav=sample,
                                     language=XTTS_CODES.get(language, language), file_path=target)
        with wave.open(target, "rb") as produced:
            import numpy as np
            frames = produced.readframes(produced.getnframes())
            samples = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768
            if produced.getnchannels() > 1:
                samples = samples.reshape(-1, produced.getnchannels()).mean(axis=1)
            return to_pcm16_wav(samples, produced.getframerate())


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("probe"):
        print(json.dumps({"engine": available_engine()}), flush=True)
        return
    engine = available_engine()
    if not engine:
        raise RuntimeError("No family-voice engine is installed")
    sample = data.get("sample")
    if not isinstance(sample, str) or not Path(sample).is_file():
        raise ValueError("The family voice sample is missing")
    language = LANGUAGE_CODES.get(data.get("locale"))
    if not language:
        raise ValueError("This language is not supported by the family-voice engine")
    speak = speak_chatterbox if engine == "chatterbox" else speak_xtts
    result = synthesize_book(data, Path("."), speak=lambda chunk: speak(chunk, sample, language))
    result["engine"] = engine
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
