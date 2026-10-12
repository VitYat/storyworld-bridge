"""Local and cloud narration presets. A preset never falls back to a different language."""

from pathlib import Path

VOICE_PRESETS = [
    # Kokoro presets (highest quality, preferred wherever installed/supported)
    {"id": "kokoro-af_heart", "locale": "en-US", "label": "Heart · gentle female", "gender": "female", "engine": "Kokoro", "voice": "af_heart", "lang": "en-us"},
    {"id": "kokoro-af_bella", "locale": "en-US", "label": "Bella · warm female", "gender": "female", "engine": "Kokoro", "voice": "af_bella", "lang": "en-us"},
    {"id": "kokoro-af_nicole", "locale": "en-US", "label": "Nicole · cheerful female", "gender": "female", "engine": "Kokoro", "voice": "af_nicole", "lang": "en-us"},
    {"id": "kokoro-am_michael", "locale": "en-US", "label": "Michael · calm male", "gender": "male", "engine": "Kokoro", "voice": "am_michael", "lang": "en-us"},
    {"id": "kokoro-am_adam", "locale": "en-US", "label": "Adam · expressive male", "gender": "male", "engine": "Kokoro", "voice": "am_adam", "lang": "en-us"},
    {"id": "kokoro-ef_dora", "locale": "es-ES", "label": "Dora · gentle female", "gender": "female", "engine": "Kokoro", "voice": "ef_dora", "lang": "es"},
    {"id": "kokoro-em_alex", "locale": "es-ES", "label": "Alex · calm male", "gender": "male", "engine": "Kokoro", "voice": "em_alex", "lang": "es"},
    {"id": "kokoro-ff_siwis", "locale": "fr-FR", "label": "Siwis · gentle female", "gender": "female", "engine": "Kokoro", "voice": "ff_siwis", "lang": "fr-fr"},
    {"id": "kokoro-if_sara", "locale": "it-IT", "label": "Sara · gentle female", "gender": "female", "engine": "Kokoro", "voice": "if_sara", "lang": "it"},
    {"id": "kokoro-im_nicola", "locale": "it-IT", "label": "Nicola · calm male", "gender": "male", "engine": "Kokoro", "voice": "im_nicola", "lang": "it"},
    {"id": "kokoro-pt_dora", "locale": "pt-BR", "label": "Dora · gentle female", "gender": "female", "engine": "Kokoro", "voice": "pf_dora", "lang": "pt-br"},
    {"id": "kokoro-pm_alex", "locale": "pt-BR", "label": "Alex · calm male", "gender": "male", "engine": "Kokoro", "voice": "pm_alex", "lang": "pt-br"},
    {"id": "kokoro-jf_alpha", "locale": "ja-JP", "label": "Alpha · gentle female", "gender": "female", "engine": "Kokoro", "voice": "jf_alpha", "lang": "ja"},
    {"id": "kokoro-zf_xiaobei", "locale": "zh-CN", "label": "Xiaobei · gentle female", "gender": "female", "engine": "Kokoro", "voice": "zf_xiaobei", "lang": "zh"},
    {"id": "kokoro-hf_alpha", "locale": "hi-IN", "label": "Alpha · gentle female", "gender": "female", "engine": "Kokoro", "voice": "hf_alpha", "lang": "hi"},

    # EdgeTTS presets for all 16 languages (work everywhere in cloud and locally)
    {"id": "edge-en-jenny", "locale": "en-US", "label": "Jenny · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "en-US-JennyNeural"},
    {"id": "edge-en-guy", "locale": "en-US", "label": "Guy · calm male", "gender": "male", "engine": "EdgeTTS", "voice": "en-US-GuyNeural"},
    {"id": "edge-ru-svetlana", "locale": "ru-RU", "label": "Svetlana · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "ru-RU-SvetlanaNeural"},
    {"id": "edge-ru-dmitry", "locale": "ru-RU", "label": "Dmitry · calm male", "gender": "male", "engine": "EdgeTTS", "voice": "ru-RU-DmitryNeural"},
    {"id": "edge-uk-polina", "locale": "uk-UA", "label": "Polina · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "uk-UA-PolinaNeural"},
    {"id": "edge-uk-ostap", "locale": "uk-UA", "label": "Ostap · calm male", "gender": "male", "engine": "EdgeTTS", "voice": "uk-UA-OstapNeural"},
    {"id": "edge-es-elvira", "locale": "es-ES", "label": "Elvira · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "es-ES-ElviraNeural"},
    {"id": "edge-de-katja", "locale": "de-DE", "label": "Katja · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "de-DE-KatjaNeural"},
    {"id": "edge-fr-denise", "locale": "fr-FR", "label": "Denise · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "fr-FR-DeniseNeural"},
    {"id": "edge-it-elsa", "locale": "it-IT", "label": "Elsa · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "it-IT-ElsaNeural"},
    {"id": "edge-pt-francisca", "locale": "pt-BR", "label": "Francisca · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "pt-BR-FranciscaNeural"},
    {"id": "edge-pl-zofia", "locale": "pl-PL", "label": "Zofia · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "pl-PL-ZofiaNeural"},
    {"id": "edge-tr-emel", "locale": "tr-TR", "label": "Emel · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "tr-TR-EmelNeural"},
    {"id": "edge-ar-zariyah", "locale": "ar-JO", "label": "Zariyah · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "ar-SA-ZariyahNeural"},
    {"id": "edge-zh-xiaoxiao", "locale": "zh-CN", "label": "Xiaoxiao · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "zh-CN-XiaoxiaoNeural"},
    {"id": "edge-hi-swara", "locale": "hi-IN", "label": "Swara · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "hi-IN-SwaraNeural"},
    {"id": "edge-ja-nanami", "locale": "ja-JP", "label": "Nanami · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "ja-JP-NanamiNeural"},
    {"id": "edge-he-hila", "locale": "he-IL", "label": "Hila · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "he-IL-HilaNeural"},
    {"id": "edge-he-avri", "locale": "he-IL", "label": "Avri · calm male", "gender": "male", "engine": "EdgeTTS", "voice": "he-IL-AvriNeural"},
    {"id": "edge-ko-sunhi", "locale": "ko-KR", "label": "Sun-Hi · gentle female", "gender": "female", "engine": "EdgeTTS", "voice": "ko-KR-SunHiNeural"},
    {"id": "edge-ko-injoon", "locale": "ko-KR", "label": "In-Joon · calm male", "gender": "male", "engine": "EdgeTTS", "voice": "ko-KR-InJoonNeural"},

    # Local Piper presets (fallback when downloaded locally)
    {"id": "piper-en-amy", "locale": "en-US", "label": "Amy · local female", "gender": "female", "engine": "Piper", "model": "en_US-amy-medium"},
    {"id": "piper-ru-irina", "locale": "ru-RU", "label": "Irina · local female", "gender": "female", "engine": "Piper", "model": "ru_RU-irina-medium"},
    {"id": "piper-uk", "locale": "uk-UA", "label": "Ukrainian · local narrator", "gender": "unspecified", "engine": "Piper", "model": "uk_UA-ukrainian_tts-medium"},
    {"id": "piper-es", "locale": "es-ES", "label": "Spanish · local narrator", "gender": "unspecified", "engine": "Piper", "model": "es_ES-sharvard-medium"},
    {"id": "piper-de", "locale": "de-DE", "label": "Thorsten · local male", "gender": "male", "engine": "Piper", "model": "de_DE-thorsten-medium"},
    {"id": "piper-fr", "locale": "fr-FR", "label": "Siwis · local female", "gender": "female", "engine": "Piper", "model": "fr_FR-siwis-low"},
]

LOCALES_WITHOUT_VOICE = ()


def installed(root: Path | None = None, python: str | None = None) -> list[dict]:
    result = []
    has_local = root is not None and python and Path(python).is_file()
    for preset in VOICE_PRESETS:
        engine = preset.get("engine")
        if engine == "EdgeTTS":
            ready = True
        elif engine == "Kokoro" and has_local:
            ready = (root / "kokoro-v1.0.onnx").is_file() and (root / "voices-v1.0.bin").is_file()
        elif has_local:
            model = root / (preset["model"] + ".onnx")
            ready = model.is_file() and model.with_suffix(".onnx.json").is_file()
        else:
            ready = False
        if ready:
            result.append({key: preset[key] for key in ("id", "locale", "label", "gender", "engine")})
    # Guarantee Kokoro voices are at the very top of the catalog
    result.sort(key=lambda x: 0 if x.get("engine") == "Kokoro" else (1 if x.get("engine") == "EdgeTTS" else 2))
    return result


def select(locale: str, voice_id: str | None) -> dict:
    if voice_id:
        for p in VOICE_PRESETS:
            if p["id"] == voice_id and p["locale"] != locale:
                raise ValueError("The selected voice does not support this story language.")
    matches = [p for p in VOICE_PRESETS if p["locale"] == locale and (not voice_id or p["id"] == voice_id)]
    if not matches:
        matches = [p for p in VOICE_PRESETS if p["locale"] == locale]
    if not matches:
        raise ValueError("The selected voice does not support this story language.")
    # Always prioritize Kokoro over EdgeTTS and Piper
    matches.sort(key=lambda p: 0 if p.get("engine") == "Kokoro" else (1 if p.get("engine") == "EdgeTTS" else 2))
    return matches[0]
