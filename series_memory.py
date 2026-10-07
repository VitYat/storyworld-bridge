"""Bounded recall from an untruncated episode archive; no photos in memory."""

import re


def recall(memory: dict, theme: str) -> dict:
    episodes = memory.get("episodes", [])
    if not isinstance(episodes, list) or len(episodes) > 2000:
        raise ValueError("Invalid story series archive")
    episodes = [e for e in episodes if isinstance(e, dict)]
    terms = set(re.findall(r"\w{4,}", theme.lower()))
    ranked = sorted(episodes[:-3], key=lambda e: len(terms & set(re.findall(
        r"\w{4,}", f"{e.get('title', '')} {e.get('summary', '')} {e.get('facts', [])}".lower()))), reverse=True)
    selected = []
    for episode in episodes[:1] + episodes[-2:] + ranked[:2]:
        if episode not in selected:
            selected.append(episode)
    return {
        "episodeNumber": len(episodes) + 1,
        "worldBible": str(memory.get("bible", ""))[:1000],
        "recalledEpisodes": [{"number": e.get("number"), "title": str(e.get("title", ""))[:100],
                              "summary": str(e.get("summary", ""))[:300],
                              "nextThread": str(e.get("nextThread", ""))[:80],
                              "facts": [str(f)[:80] for f in (e.get("facts", []) if isinstance(e.get("facts", []), list) else [])[:2]]} for e in selected],
    }
