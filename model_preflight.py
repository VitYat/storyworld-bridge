"""Pick a responsive, already downloaded LM Studio model for children's stories.

Only localhost APIs are used. The probe contains no child data.
"""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


EXPERIMENTAL = ("uncensored", "heretic", "defiant", "abliterated")


def request(base: str, path: str, payload: dict | None = None, timeout: int = 15) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(base + path, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.load(response)


def model_score(model: dict) -> tuple[int, int]:
    label = f"{model.get('key', '')} {model.get('display_name', '')}".lower()
    size = model.get("size_bytes") or 0
    if model.get("type") != "llm" or any(word in label for word in EXPERIMENTAL):
        return (-1, 0)
    if size and size > 13_000_000_000:
        return (-1, 0)
    if "qwen3.5" in label and "9b" in label:
        return (50, -size)
    if "qwen" in label and any(term in label for term in ("instruct", "3b", "4b", "7b")):
        return (40, -size)
    if "instruct" in label and size and size < 9_000_000_000:
        return (20, -size)
    return (-1, 0)


def probe(base: str, instance_id: str, timeout: int = 90) -> bool:
    payload = {
        "model": instance_id,
        "input": "Write one gentle story page about a little bird finding a garden. Return JSON only.",
        "system_prompt": (
            'Return only JSON: {"heading":"...","body":"...","imagePrompt":"..."}. '
            "Write a complete body of at least 70 words and an English illustrated scene prompt. "
            "No thinking or explanations."
        ),
        "reasoning": "off", "max_output_tokens": 950, "store": False,
    }
    try:
        result = request(base, "/api/v1/chat", payload, timeout=timeout)
        output = result.get("output", [])
        content = "\n".join(item.get("content", "") for item in output
                            if isinstance(item, dict) and item.get("type") == "message")
        data = json.loads(content)
        return (all(isinstance(data.get(key), str) and data[key].strip()
                    for key in ("heading", "body", "imagePrompt"))
                and len(data["body"].split()) >= 70)
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError):
        return False


def select_model(base: str, current_id: str, *, forced: bool = False) -> dict:
    parsed = urlsplit(base)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost"):
        raise ValueError("LM Studio preflight only accepts a local HTTP server.")
    catalog = request(base, "/api/v1/models", timeout=15).get("models", [])
    models = [m for m in catalog if isinstance(m, dict) and m.get("type") == "llm"]
    current = next((m for m in models if any(i.get("id") == current_id
                                            for i in m.get("loaded_instances", []))), None)
    if current is None:
        raise RuntimeError("The selected text model is no longer loaded in LM Studio.")
    candidates = sorted((m for m in models if model_score(m)[0] >= 0),
                        key=model_score, reverse=True)
    experimental = any(word in f"{current.get('key', '')} {current.get('display_name', '')}".lower()
                       for word in EXPERIMENTAL)
    if forced or not experimental:
        if probe(base, current_id):
            return {"model": current_id, "switched": False}
    if forced:
        raise RuntimeError("The explicitly selected model failed a short local story probe.")
    alternatives = [m for m in candidates if m.get("key") != current.get("key")]
    if not alternatives:
        raise RuntimeError("The loaded model did not answer, and no ordinary instruct model is downloaded in LM Studio. Download a standard Qwen instruct model, then retry.")
    loaded_current = current.get("loaded_instances", [])
    for candidate in alternatives:
        key = candidate.get("key")
        if not isinstance(key, str) or not key:
            continue
        # Unload only the failed model's instances. Do not touch other LM Studio chats.
        for instance in loaded_current:
            if instance.get("id"):
                request(base, "/api/v1/models/unload", {"instance_id": instance["id"]}, timeout=30)
        loaded_current = []
        loaded = candidate.get("loaded_instances", [])
        if loaded:
            next_id = loaded[0]["id"]
        else:
            result = request(base, "/api/v1/models/load", {
                "model": key, "context_length": 4096, "flash_attention": True,
            }, timeout=180)
            next_id = result.get("instance_id")
        if next_id and probe(base, next_id):
            return {"model": next_id, "switched": True}
        if next_id:
            loaded_current = [{"id": next_id}]
    raise RuntimeError("Downloaded text models failed a short local story probe. LM Studio may be stalled; check its model runtime before launching Storyworld.")


if __name__ == "__main__":
    try:
        result = select_model(os.environ["STORYWORLD_LM_URL"].removesuffix("/v1"),
                              os.environ["STORYWORLD_MODEL_ID"],
                              forced=os.environ.get("STORYWORLD_FORCE_MODEL_ID") == "1")
        print(json.dumps(result))
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"Storyworld model preflight failed: {exc}", file=sys.stderr)
        sys.exit(1)
