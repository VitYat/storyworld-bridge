"""Local narration presets. A preset never falls back to a different language."""

from pathlib import Path

VOICE_PRESETS = [
    {"id": "kokoro-af_heart", "locale": "en-US", "label": "Heart · gentle female", "gender": "female", "engine": "Kokoro", "voice": "af_heart", "lang": "en-us"},
    {"id": "kokoro-af_bella", "locale": "en-US", "label": "Bella · warm female", "gender": "female", "engine": "Kokoro", "voice": "af_bella", "lang": "en-us"},
    {"id": "kokoro-am_michael", "locale": "en-US", "label": "Michael · warm male", "gender": "male", "engine": "Kokoro", "voice": "am_michael", "lang": "en-us"},
    {"id": "kokoro-am_fenrir", "locale": "en-US", "label": "Fenrir · calm male", "gender": "male", "engine": "Kokoro", "voice": "am_fenrir", "lang": "en-us"},
    {"id": "piper-en-amy", "locale": "en-US", "label": "Amy · local female", "gender": "female", "engine": "Piper", "model": "en_US-amy-medium"},
    {"id": "piper-ru-irina", "locale": "ru-RU", "label": "Irina · local female", "gender": "female", "engine": "Piper", "model": "ru_RU-irina-medium"},
    {"id": "piper-uk", "locale": "uk-UA", "label": "Ukrainian · local narrator", "gender": "unspecified", "engine": "Piper", "model": "uk_UA-ukrainian_tts-medium"},
    {"id": "piper-es", "locale": "es-ES", "label": "Spanish · local narrator", "gender": "unspecified", "engine": "Piper", "model": "es_ES-sharvard-medium"},
    {"id": "piper-de", "locale": "de-DE", "label": "Thorsten · local male", "gender": "male", "engine": "Piper", "model": "de_DE-thorsten-medium"},
    {"id": "piper-fr", "locale": "fr-FR", "label": "Siwis · local female", "gender": "female", "engine": "Piper", "model": "fr_FR-siwis-low"},
    # v23 language expansion.
    {"id": "piper-it", "locale": "it-IT", "label": "Paola · local female", "gender": "female", "engine": "Piper", "model": "it_IT-paola-medium"},
    {"id": "piper-pt", "locale": "pt-BR", "label": "Faber · local male", "gender": "male", "engine": "Piper", "model": "pt_BR-faber-medium"},
    {"id": "piper-pl", "locale": "pl-PL", "label": "Gosia · local female", "gender": "female", "engine": "Piper", "model": "pl_PL-gosia-medium"},
    {"id": "piper-tr", "locale": "tr-TR", "label": "Dfki · local narrator", "gender": "unspecified", "engine": "Piper", "model": "tr_TR-dfki-medium"},
    {"id": "piper-ar", "locale": "ar-JO", "label": "Kareem · local male", "gender": "male", "engine": "Piper", "model": "ar_JO-kareem-medium"},
    {"id": "piper-zh", "locale": "zh-CN", "label": "Huayan · local female", "gender": "female", "engine": "Piper", "model": "zh_CN-huayan-medium"},
    {"id": "piper-hi", "locale": "hi-IN", "label": "Priyamvada · local female", "gender": "female", "engine": "Piper", "model": "hi_IN-priyamvada-medium"},
    {"id": "kokoro-jf_alpha", "locale": "ja-JP", "label": "Alpha · gentle female", "gender": "female", "engine": "Kokoro", "voice": "jf_alpha", "lang": "ja"},
    {"id": "kokoro-ef_dora", "locale": "es-ES", "label": "Dora · gentle female", "gender": "female", "engine": "Kokoro", "voice": "ef_dora", "lang": "es"},
    {"id": "kokoro-if_sara", "locale": "it-IT", "label": "Sara · gentle female", "gender": "female", "engine": "Kokoro", "voice": "if_sara", "lang": "it"},
    {"id": "kokoro-pf_dora", "locale": "pt-BR", "label": "Dora · gentle female", "gender": "female", "engine": "Kokoro", "voice": "pf_dora", "lang": "pt-br"},
    {"id": "kokoro-hf_alpha", "locale": "hi-IN", "label": "Alpha · gentle female", "gender": "female", "engine": "Kokoro", "voice": "hf_alpha", "lang": "hi"},
    {"id": "kokoro-zf_xiaobei", "locale": "zh-CN", "label": "Xiaobei · gentle female", "gender": "female", "engine": "Kokoro", "voice": "zf_xiaobei", "lang": "cmn"},
    # Hebrew and Korean presets
    {"id": "edge-he-hila", "locale": "he-IL", "label": "Hila · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "he-IL-HilaNeural"},
    {"id": "edge-he-avri", "locale": "he-IL", "label": "Avri · calm male", "gender": "male", "engine": "EdgeTTS", "voice": "he-IL-AvriNeural"},
    {"id": "edge-ko-sunhi", "locale": "ko-KR", "label": "Sun-Hi · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "ko-KR-SunHiNeural"},
    {"id": "edge-ko-injoon", "locale": "ko-KR", "label": "In-Joon · calm male", "gender": "male", "engine": "EdgeTTS", "voice": "ko-KR-InJoonNeural"},
]

LOCALES_WITHOUT_VOICE = ()


def installed(root: Path | None, python: str) -> list[dict]:
    if root is None or not python or not Path(python).is_file():
        return []
    result = []
    for preset in VOICE_PRESETS:
        engine = preset.get("engine")
        if engine == "Kokoro":
            ready = (root / "kokoro-v1.0.onnx").is_file() and (root / "voices-v1.0.bin").is_file()
        elif engine == "EdgeTTS":
            ready = True
        else:
            model = root / (preset["model"] + ".onnx")
            ready = model.is_file() and model.with_suffix(".onnx.json").is_file()
        if ready:
            result.append({key: preset[key] for key in ("id", "locale", "label", "gender", "engine")})
    return result


def select(locale: str, voice_id: str | None) -> dict:
    matches = [p for p in VOICE_PRESETS if p["locale"] == locale and (not voice_id or p["id"] == voice_id)]
    if not matches:
        raise ValueError("The selected voice does not support this story language.")
    return matches[0]
