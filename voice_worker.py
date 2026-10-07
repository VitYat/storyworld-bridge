"""Generate local WAV with a chosen narrator. No browser/system voice fallback."""

import base64
import io
import json
import re
import sys
import wave
from pathlib import Path

from narration_catalog import select

_voices = {}


def narration_chunks(text: str, limit: int = 1200) -> list[str]:
    """Keep each inference short while retaining every word in long pages."""
    words = text.split()
    chunks = []
    current = []
    for word in words:
        if len(word) > limit:
            raise ValueError("A narration word is too long")
        if current and len(' '.join(current)) + 1 + len(word) > limit:
            chunks.append(' '.join(current))
            current = []
        current.append(word)
    if current:
        chunks.append(' '.join(current))
    return chunks


def synthesize(data: dict, root: Path) -> str:
    text = data.get("text")
    if not isinstance(text, str) or not 1 <= len(text) <= 1800:
        raise ValueError("Invalid narration text")
    preset = select(data.get("locale"), data.get("voiceId"))
    sound = io.BytesIO()
    if preset["engine"] == "Kokoro":
        import numpy as np
        from kokoro_onnx import Kokoro
        key = (str(root), "Kokoro")
        if key not in _voices:
            _voices[key] = Kokoro(str(root / "kokoro-v1.0.onnx"), str(root / "voices-v1.0.bin"))
        voice = _voices[key]
        samples, rate = voice.create(text, voice=preset["voice"], speed=0.90, lang=preset["lang"])
        samples = np.asarray(samples, dtype=np.float32)
        if samples.size == 0 or not np.isfinite(samples).all():
            raise ValueError("The narrator returned empty audio")
        peak = float(np.max(np.abs(samples)))
        if peak > 0.96:
            samples *= 0.96 / peak
        pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes()
        with wave.open(sound, "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(rate)
            output.writeframes(pcm)
    elif preset["engine"] == "EdgeTTS":
        import asyncio
        import edge_tts
        import miniaudio
        async def _run_edge():
            comm = edge_tts.Communicate(text, preset["voice"], rate="-5%")
            mp3_bytes = bytearray()
            async for chunk in comm.stream():
                if chunk['type'] == 'audio':
                    mp3_bytes.extend(chunk['data'])
            return bytes(mp3_bytes)
        mp3 = asyncio.run(_run_edge())
        decoded = miniaudio.mp3_read_s16(mp3)
        samples = decoded.samples
        if decoded.nchannels == 2:
            samples = samples[::2]
        with wave.open(sound, "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(decoded.sample_rate)
            output.writeframes(samples.tobytes())
    else:
        from piper import PiperVoice, SynthesisConfig
        model = root / (preset["model"] + ".onnx")
        key = (str(root), preset["model"])
        if key not in _voices:
            _voices[key] = PiperVoice.load(str(model))
        voice = _voices[key]
        with wave.open(sound, "wb") as output:
            voice.synthesize_wav(text, output, syn_config=SynthesisConfig(length_scale=1.10))
    return base64.b64encode(sound.getvalue()).decode("ascii")


SENTENCE_END = re.compile(r"(?<=[.!?…。！？؟])\s+")


def narration_sentences(text: str, limit: int = 400) -> list[str]:
    """Split a page into sentence-sized pieces so the reader can follow the voice.

    Every word is kept, in order. A very long sentence is split on word boundaries.
    """
    pieces = []
    for sentence in SENTENCE_END.split(text.strip()):
        if not sentence.strip():
            continue
        pieces.extend(narration_chunks(sentence, limit))
    return pieces


def synthesize_book(data: dict, root: Path, speak=None) -> dict:
    """Join every sentence into one WAV and report where each page and sentence starts.

    `segments` lets the reader highlight words in time with the voice.
    """
    speak = speak or (lambda chunk: synthesize(
        {"locale": data.get("locale"), "voiceId": data.get("voiceId"), "text": chunk}, root))
    pages = data.get("pages")
    if not isinstance(pages, list) or not 1 <= len(pages) <= 80:
        raise ValueError("Invalid narration pages")
    sound = io.BytesIO()
    offsets = []
    segments = []
    total_frames = 0
    rate = 0
    with wave.open(sound, "wb") as output:
        for page_index, text in enumerate(pages):
            chunks = narration_sentences(text)
            if not chunks:
                raise ValueError("A narration page is empty")
            for chunk_index, chunk in enumerate(chunks):
                encoded = speak(chunk)
                with wave.open(io.BytesIO(base64.b64decode(encoded)), "rb") as page:
                    if not rate:
                        rate = page.getframerate()
                        output.setnchannels(page.getnchannels())
                        output.setsampwidth(page.getsampwidth())
                        output.setframerate(rate)
                    if rate != page.getframerate() or page.getnchannels() != 1 or page.getsampwidth() != 2:
                        raise ValueError("Incompatible narration audio format")
                    if chunk_index == 0:
                        offsets.append(total_frames / rate)
                    output.writeframes(page.readframes(page.getnframes()))
                    segments.append({"page": page_index, "start": round(total_frames / rate, 3),
                                     "end": round((total_frames + page.getnframes()) / rate, 3),
                                     "text": chunk})
                    pause_frames = round(rate * (.6 if chunk_index == len(chunks) - 1 else .25))
                    output.writeframes(b"\0" * pause_frames * 2)
                    total_frames += page.getnframes() + pause_frames
    return {"audioBase64": base64.b64encode(sound.getvalue()).decode("ascii"),
            "pageOffsets": offsets, "segments": segments, "durationSeconds": total_frames / rate}


if __name__ == "__main__":
    try:
        raw_input = sys.stdin.buffer.read().decode("utf-8-sig")
        data = json.loads(raw_input)
        result = synthesize_book(data, Path(sys.argv[1])) if "pages" in data else synthesize(data, Path(sys.argv[1]))
        print(json.dumps(result) if isinstance(result, dict) else result, flush=True)
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
