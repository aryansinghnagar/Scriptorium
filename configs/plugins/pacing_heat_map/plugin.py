#!/usr/bin/env python3
"""
Scene Pacing & Sensory Heat Map Plugin for Ars Arcanum
======================================================
Analyzes dialogue ratios, exposition stretches, and multi-sensory grounding.
"""

import re
from typing import Any

SENSORY_LEXICON = {
    "visual": {"shadow", "gleam", "crimson", "pale", "dark", "shimmer", "silhouette", "glow", "azure", "gold", "haze"},
    "auditory": {"whisper", "echo", "roar", "clash", "murmur", "thrum", "screech", "clang", "silence", "rattle", "hum"},
    "olfactory": {"scent", "stench", "aroma", "smoke", "perfume", "decay", "musty", "pungent", "fragrance", "incense"},
    "tactile": {"cold", "rough", "frost", "burning", "slick", "damp", "searing", "numb", "velvet", "grit", "prickle"},
    "gustatory": {"bitter", "sweet", "metallic", "sour", "coppery", "tangy", "ash", "salted", "acrid", "honeyed"},
}


def hook_validate_manuscript(manuscript: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostics = []
    chapters = manuscript.get("chapters", [])

    for ch in chapters:
        title = ch.get("title", "")
        content = ch.get("content", "")
        words = content.split()
        total_w = len(words)
        if total_w < 50:
            continue

        # 1. Dialogue Ratio Calculation
        dialogue_matches = re.findall(r'["“][^"”]+["”]', content)
        dialogue_words = sum(len(m.split()) for m in dialogue_matches)
        dialogue_ratio = dialogue_words / total_w if total_w > 0 else 0.0

        if dialogue_ratio > 0.85:
            diagnostics.append({
                "severity": "warning",
                "message": f"Chapter '{title}' has very high dialogue density ({int(dialogue_ratio*100)}%). Potential 'talking heads' syndrome without physical stage business.",
                "target": title,
                "details": {"dialogue_ratio": dialogue_ratio},
            })
        elif dialogue_ratio < 0.05 and total_w > 500:
            diagnostics.append({
                "severity": "info",
                "message": f"Chapter '{title}' is almost entirely exposition ({int((1-dialogue_ratio)*100)}% non-dialogue). Check pacing for sustained monologues.",
                "target": title,
                "details": {"dialogue_ratio": dialogue_ratio},
            })

        # 2. Sensory Grounding Check
        lower_content = content.lower()
        active_senses = sum(1 for category, keywords in SENSORY_LEXICON.items() if any(k in lower_content for k in keywords))
        if active_senses < 2 and total_w > 300:
            diagnostics.append({
                "severity": "info",
                "message": f"Chapter '{title}' engages only {active_senses}/5 sensory modalities. Consider adding olfactory, tactile, or ambient auditory grounding.",
                "target": title,
                "details": {"active_senses": active_senses},
            })

    return diagnostics


def hook_custom_metric(text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Calculates comprehensive scene pacing metrics."""
    words = text.split()
    total_w = len(words)
    dialogue_matches = re.findall(r'["“][^"”]+["”]', text)
    dialogue_words = sum(len(m.split()) for m in dialogue_matches)
    
    return {
        "word_count": total_w,
        "dialogue_word_count": dialogue_words,
        "dialogue_pct": round(dialogue_words / max(1, total_w) * 100, 1),
        "exposition_pct": round((total_w - dialogue_words) / max(1, total_w) * 100, 1),
    }
