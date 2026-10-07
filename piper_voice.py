"""Synthesize one local page with Piper. The story is read from stdin, not argv."""

import base64
import io
import json
import sys
import wave
from pathlib import Path


VOICES = {
    "en-US": "en_US-amy-medium",
    "ru-RU": "ru_RU-irina-medium",
    "uk-UA": "uk_UA-ukrainian_tts-medium",
    "es-ES": "es_ES-sharvard-medium",
    "de-DE": "de_DE-thorsten-medium",
    "fr-FR": "fr_FR-siwis-medium",
}


def synthesize(data: dict, root: Path) -> str:
    from piper import PiperVoice

    locale = data.get("locale")
    text = data.get("text")
    if locale not in VOICES or not isinstance(text, str) or not 1 <= len(text) <= 1800:
        raise ValueError("Invalid narration request")
    model = root / (VOICES[locale] + ".onnx")
    if not model.is_file() or not model.with_suffix(".onnx.json").is_file():
        raise ValueError("Local voice for this language is not installed")
    voice = PiperVoice.load(str(model))
    audio = io.BytesIO()
    with wave.open(audio, "wb") as output:
        voice.synthesize_wav(text, output)
    return base64.b64encode(audio.getvalue()).decode("ascii")


if __name__ == "__main__":
    try:
        request = json.load(sys.stdin)
        print(synthesize(request, Path(sys.argv[1])), flush=True)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
