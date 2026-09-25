#!/usr/bin/env python3
"""
Speculative Naming & Phoneme Collision Plugin for Ars Arcanum
=============================================================
Audits character and location names for phoneme collisions, edit distance
confusion, and unpronounceable consonant clustering.
"""

import difflib
import re
from typing import Any

# Common fantasy prefix/suffix clichés or collision checks
VOWELS = set("aeiouyAEIOUY")


def consonant_skeleton(name: str) -> str:
    """Extracts uppercase consonant skeleton of a name."""
    clean = re.sub(r"[^a-zA-Z]", "", name).lower()
    return "".join(c for c in clean if c not in VOWELS)


def hook_validate_entity(entity: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostics = []
    name = entity.get("name", "").strip()
    if not name:
        return diagnostics

    # 1. Consonant cluster check (e.g., 4+ consonants in a row without apostrophe)
    if re.search(r"[bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ]{5,}", name):
        diagnostics.append({
            "severity": "warning",
            "message": f"Entity name '{name}' contains a dense consonant cluster (5+ consonants) which may impede reader pronunciation.",
            "target": name,
        })

    # 2. Excessive apostrophe punctuation (trope detector)
    if name.count("'") > 1 or name.count("`") > 1:
        diagnostics.append({
            "severity": "info",
            "message": f"Entity name '{name}' uses multiple apostrophes/glottal stops.",
            "target": name,
        })

    # 3. Collision check against other known entities in context
    known_names = context.get("known_names", [])
    if isinstance(known_names, list):
        for other in known_names:
            if other and other != name:
                # Direct Levenshtein ratio
                ratio = difflib.SequenceMatcher(None, name.lower(), other.lower()).ratio()
                if ratio >= 0.85 and abs(len(name) - len(other)) <= 2:
                    diagnostics.append({
                        "severity": "warning",
                        "message": f"Name '{name}' is phonetically/orthographically very close to '{other}' ({int(ratio*100)}% match). Potential reader confusion.",
                        "target": name,
                        "details": {"similar_to": other, "similarity": ratio},
                    })
                elif consonant_skeleton(name) == consonant_skeleton(other) and len(name) > 3:
                    diagnostics.append({
                        "severity": "info",
                        "message": f"Name '{name}' shares identical consonant skeleton ('{consonant_skeleton(name)}') with '{other}'.",
                        "target": name,
                    })

    return diagnostics


def hook_custom_metric(text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Computes phonotactic diversity metric."""
    words = re.findall(r"\b[A-Z][a-z]+\b", text)
    unique_capitalized = set(words)
    return {
        "named_entity_count": len(words),
        "unique_proper_nouns": len(unique_capitalized),
        "proper_noun_density_pct": round(len(words) / max(1, len(text.split())) * 100, 2),
    }
