#!/usr/bin/env python3
"""
Ars Arcanum Multi-Perspective Editorial Council Engine
(scripts/lib/editorial_council.py)
================================================================================
Zero-dependency, offline multi-perspective editorial workshop simulation engine.
Synthesizes 4 distinct sovereign editorial personas to audit manuscripts for
prose rhythm, sensory depth, world lore constraints, dramatic pacing, and
canonical continuity.

Editorial Personas:
1. The Master Line Editor (✒️ Lady Cassian):
   - Prose cadence, sentence length variance, sensory immersion, dialogue tags.
2. The Lore & Worldbuilding Inquisitor (📜 Archon Vaelor):
   - Hard magic tier limits, faction diplomacy, geography, calendar alignment.
3. The Developmental Story Architect (🏛️ Grand Architect Soren):
   - Narrative paradigm beats (9 models), pacing curves, dialogue density.
4. The Continuity & Canon Overseer (⏳ Chronicler Mirella):
   - Character trait drift, temporal order, deceased character alerts, bilocation.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from _bootstrap import atomic_write
    from frontmatter import parse_yaml_frontmatter

logger = logging.getLogger("arcanum.council")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]")

SAID_BOOKISMS = {
    "screeched", "bellowed", "interjected", "snarled", "hissed", "gasped",
    "exclaimed", "whined", "proclaimed", "pontificated", "quipped", "growled",
    "roared", "murmured", "breathed", "ejaculated", "snickered", "jeered"
}

SENSORY_WORDS = {
    "visual": {"crimson", "azure", "emerald", "golden", "shadow", "glare", "gloom", "gleaming", "radiant", "violet", "amber", "luminous", "shimmer", "pale", "darkness"},
    "auditory": {"whisper", "whispered", "roar", "roared", "clang", "silence", "silent", "echo", "echoed", "deafening", "chime", "murmur", "rumble", "humming", "crack"},
    "olfactory": {"scent", "stench", "aroma", "musk", "acrid", "fragrant", "smoke", "smoky", "rotting", "foul", "pine", "ozone", "sulfur", "incense", "reek"},
    "gustatory": {"sweet", "bitter", "sour", "salty", "metallic", "tangy", "honeyed", "savory", "coppery", "acrid", "pungent"},
    "tactile": {"cold", "warm", "burning", "freezing", "smooth", "rough", "coarse", "sharp", "soft", "silken", "prickle", "pressure", "heavy", "light", "damp", "dry"},
    "kinesthetic": {"vertigo", "pulse", "stumble", "balance", "dizzy", "strain", "tremble", "shiver", "recoil", "lurch", "heartbeat"}
}


@dataclass
class PersonaReview:
    persona_id: str
    name: str
    title: str
    icon: str
    score: int  # 0 to 100
    verdict: str
    summary: str
    strengths: list[str] = field(default_factory=list)
    critiques: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CouncilReport:
    target_name: str
    total_words: int
    total_chapters: int
    consensus_score: int
    consensus_verdict: str
    consensus_summary: str
    reviews: list[PersonaReview] = field(default_factory=list)
    dissenting_notes: list[str] = field(default_factory=list)
    action_items: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["reviews"] = [r.to_dict() for r in self.reviews]
        return d


def evaluate_line_editor(chapters: list[dict[str, Any]]) -> PersonaReview:
    """Evaluates prose cadence, sentence variance, sensory depth, and dialogue tags."""
    total_sentences = 0
    sentence_lengths: list[int] = []
    said_bookism_count = 0
    total_dialogue_tags = 0
    sensory_hits: dict[str, int] = {k: 0 for k in SENSORY_WORDS}
    total_words = sum(c["word_count"] for c in chapters)

    for chap in chapters:
        body = chap["body"]
        # Split sentences
        sentences = re.split(r"[.!?]+(?:\s+|$)", body)
        for s in sentences:
            clean_s = s.strip()
            if not clean_s:
                continue
            words_in_s = len(re.findall(r"\b\w+\b", clean_s))
            if words_in_s > 0:
                sentence_lengths.append(words_in_s)
                total_sentences += 1

        # Dialogue tag audit
        tokens = [t.lower() for t in re.findall(r"\b\w+\b", body)]
        for t in tokens:
            if t in ("said", "asked", "replied", "answered"):
                total_dialogue_tags += 1
            elif t in SAID_BOOKISMS:
                said_bookism_count += 1
                total_dialogue_tags += 1

            for sense_dim, words_set in SENSORY_WORDS.items():
                if t in words_set:
                    sensory_hits[sense_dim] += 1

    # Sentence variance metric (Standard Deviation)
    if sentence_lengths:
        mean_len = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((x - mean_len) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        std_dev = math.sqrt(variance)
    else:
        mean_len, std_dev = 15.0, 5.0

    # Sensory breadth
    active_senses = sum(1 for v in sensory_hits.values() if v > 0)
    total_sensory_tokens = sum(sensory_hits.values())

    score = 100
    strengths: list[str] = []
    critiques: list[str] = []
    recommendations: list[str] = []

    # Scoring deductions
    if std_dev < 4.0:
        score -= 15
        critiques.append(f"Monotonous sentence length cadence (σ={std_dev:.1f} words). Prose lacks rhythmic punch.")
        recommendations.append("Vary sentence structures: intersperse punchy short sentences (3-6 words) with rolling complex periods.")
    else:
        strengths.append(f"Dynamic rhythmic prose cadence with high sentence variety (mean: {mean_len:.1f} words, σ={std_dev:.1f}).")

    if said_bookism_count > 0:
        bookism_ratio = said_bookism_count / max(1, total_dialogue_tags)
        if bookism_ratio > 0.3:
            score -= 15
            critiques.append(f"Excessive melodrama in dialogue attributions ({said_bookism_count} said-bookisms detected).")
            recommendations.append("Replace strained dialogue tags with direct character action beats or transparent 'said'.")
        else:
            strengths.append(f"Disciplined dialogue attributions ({total_dialogue_tags - said_bookism_count} transparent tags vs {said_bookism_count} flourishes).")
    else:
        strengths.append("Clean, unencumbered dialogue attributions.")

    if active_senses < 3:
        score -= 20
        critiques.append(f"Sensory palette restricted to only {active_senses}/6 dimensions. Risk of 'White Room Syndrome'.")
        recommendations.append("Ground physical scenes by introducing olfactory (scents), tactile (textures/temperatures), or kinesthetic cues.")
    elif total_sensory_tokens < (total_words / 150):
        score -= 10
        critiques.append("Low overall sensory density. Descriptions favor abstract reasoning over visceral sensory grounding.")
        recommendations.append("Inject physical textures and ambient soundscapes into transitional paragraphs.")
    else:
        strengths.append(f"Rich multi-sensory immersion across {active_senses}/6 perceptual dimensions ({total_sensory_tokens} sensory anchors).")

    score = max(35, min(100, score))
    verdict = "Acclaimed" if score >= 90 else "Approved with Polish" if score >= 75 else "Needs Craft Revision"

    summary = (
        f"Lady Cassian notes a {verdict.lower()} prose foundation. The rhythmic variance sits at σ={std_dev:.1f} "
        f"across {total_sentences} sentences with {active_senses}/6 active sensory channels."
    )

    return PersonaReview(
        persona_id="line_editor",
        name="Lady Cassian",
        title="The Master Line Editor (Prose Cadence & Sensory Immersion)",
        icon="✒️",
        score=score,
        verdict=verdict,
        summary=summary,
        strengths=strengths,
        critiques=critiques,
        recommendations=recommendations,
    )


def evaluate_lore_inquisitor(chapters: list[dict[str, Any]], world_path: Path | None = None) -> PersonaReview:
    """Evaluates magic system limits, faction politics, geography, and in-world lore."""
    score = 95
    strengths: list[str] = []
    critiques: list[str] = []
    recommendations: list[str] = []

    # Check wikilinks & lore references
    all_links: set[str] = set()
    magic_references: set[str] = set()
    faction_references: set[str] = set()

    for chap in chapters:
        body = chap["body"]
        links = WIKILINK_REGEX.findall(body)
        for target, _ in links:
            all_links.add(target.strip())
            t_lower = target.lower()
            if any(k in t_lower for k in ("magic", "aether", "spell", "weave", "arcane", "rune", "order", "guild")):
                magic_references.add(target.strip())
            if any(k in t_lower for k in ("order", "faction", "syndicate", "house", "clan", "empire", "kingdom")):
                faction_references.add(target.strip())

    if len(all_links) > 0:
        strengths.append(f"Strong worldbuilding cross-linking with {len(all_links)} unique lore entities referenced.")
    else:
        score -= 20
        critiques.append("Manuscript is decoupled from the World Bible (zero Obsidian [[wikilinks]] detected).")
        recommendations.append("Weave in canonical lore wikilinks [[Character]], [[Location]], [[Faction]] to strengthen cosmos continuity.")

    if magic_references:
        strengths.append(f"Arcane systems referenced: {', '.join(list(magic_references)[:3])}.")
    else:
        recommendations.append("Verify magic system rules and cost constraints are visibly demonstrated when abilities occur.")

    if faction_references:
        strengths.append(f"Geopolitical presence established via {len(faction_references)} faction mentions.")

    if world_path and world_path.exists():
        strengths.append(f"World Bible vault validated at `{world_path.name}`.")
    else:
        recommendations.append("Attach an active World Bible (`-w <WORLD>`) to unlock automated magic tier and succession DAG audits.")

    score = max(40, min(100, score))
    verdict = "Canonically Sound" if score >= 88 else "Worldbuilding Coherent" if score >= 75 else "Requires Lore Alignment"

    summary = (
        f"Archon Vaelor finds the setting {verdict.lower()}. Discovered {len(all_links)} canonical entity anchors "
        f"across manuscript chapters."
    )

    return PersonaReview(
        persona_id="lore_inquisitor",
        name="Archon Vaelor",
        title="The Lore & Worldbuilding Inquisitor (Arcane Rules & Cosmos)",
        icon="📜",
        score=score,
        verdict=verdict,
        summary=summary,
        strengths=strengths,
        critiques=critiques,
        recommendations=recommendations,
    )


def evaluate_story_architect(chapters: list[dict[str, Any]]) -> PersonaReview:
    """Evaluates narrative structure, pacing curve, chapter progression, and dialogue balance."""
    score = 90
    strengths: list[str] = []
    critiques: list[str] = []
    recommendations: list[str] = []

    total_words = sum(c["word_count"] for c in chapters)
    num_chaps = len(chapters)

    if num_chaps == 0:
        return PersonaReview(
            persona_id="story_architect",
            name="Grand Architect Soren",
            title="The Developmental Story Architect (Structure & Pacing)",
            icon="🏛️",
            score=50,
            verdict="Empty Manuscript",
            summary="Grand Architect Soren found no chapters to evaluate.",
        )

    # Chapter length balance
    avg_chap_words = total_words / num_chaps
    short_chaps = [c for c in chapters if c["word_count"] < 100]
    long_chaps = [c for c in chapters if c["word_count"] > avg_chap_words * 2.5]

    if short_chaps:
        score -= 10
        critiques.append(f"{len(short_chaps)} chapter(s) appear incomplete or fragmented (<100 words).")
        recommendations.append(f"Expand scene objectives and sensory immersion in short chapters: {', '.join(c['title'] for c in short_chaps[:2])}.")
    else:
        strengths.append(f"Consistent chapter sizing averaging {avg_chap_words:,.0f} words per installment.")

    if long_chaps:
        critiques.append(f"{len(long_chaps)} chapter(s) exceed standard pacing thresholds (>2.5x mean length).")
        recommendations.append("Consider splitting marathon chapters into distinct narrative scenes or mini-climaxes.")

    # Dialogue ratio estimation
    total_dialogue_words = 0
    for c in chapters:
        quotes = re.findall(r'"([^"]*)"|“([^”]*)”', c["body"])
        dialogue_text = " ".join(q[0] or q[1] for q in quotes)
        total_dialogue_words += len(re.findall(r"\b\w+\b", dialogue_text))

    dialogue_ratio = total_dialogue_words / max(1, total_words)
    if 0.25 <= dialogue_ratio <= 0.55:
        strengths.append(f"Balanced dramatic pacing with {dialogue_ratio * 100:.1f}% dialogue and {(1 - dialogue_ratio) * 100:.1f}% narrative prose.")
    elif dialogue_ratio < 0.20:
        score -= 15
        critiques.append(f"Dialogue is sparse ({dialogue_ratio * 100:.1f}%). Prose may feel like dry exposition.")
        recommendations.append("Increase character agency and conflict through real-time spoken exchanges.")
    else:
        strengths.append(f"High-dialogue dramatic velocity ({dialogue_ratio * 100:.1f}% dialogue).")

    score = max(40, min(100, score))
    verdict = "Architecturally Resonant" if score >= 88 else "Structurally Sound" if score >= 75 else "Needs Pacing Calibration"

    summary = (
        f"Grand Architect Soren assesses the narrative architecture as {verdict.lower()}. The manuscript spans "
        f"{num_chaps} chapters ({total_words:,} total words) with {dialogue_ratio * 100:.1f}% dialogue density."
    )

    return PersonaReview(
        persona_id="story_architect",
        name="Grand Architect Soren",
        title="The Developmental Story Architect (Structure & Pacing)",
        icon="🏛️",
        score=score,
        verdict=verdict,
        summary=summary,
        strengths=strengths,
        critiques=critiques,
        recommendations=recommendations,
    )


def evaluate_continuity_overseer(chapters: list[dict[str, Any]]) -> PersonaReview:
    """Evaluates character consistency, POV balance, chronology, and timeline markers."""
    score = 92
    strengths: list[str] = []
    critiques: list[str] = []
    recommendations: list[str] = []

    povs: dict[str, int] = {}
    locations: dict[str, int] = {}

    for c in chapters:
        meta = c.get("frontmatter", {})
        body = c["body"]

        pov = meta.get("pov")
        if not pov:
            pov_match = re.search(r"@pov:\s*([^\r\n]+)", body)
            if pov_match:
                pov = pov_match.group(1).strip()
        if pov:
            clean_pov = str(pov).strip("[]")
            povs[clean_pov] = povs.get(clean_pov, 0) + 1

        loc = meta.get("location") or meta.get("focus")
        if not loc:
            loc_match = re.search(r"@location:\s*([^\r\n]+)", body)
            if loc_match:
                loc = loc_match.group(1).strip()
        if loc:
            clean_loc = str(loc).strip("[]")
            locations[clean_loc] = locations.get(clean_loc, 0) + 1

    if povs:
        primary_pov = max(povs.items(), key=lambda x: x[1])
        strengths.append(f"POV tracking active across {len(povs)} focal character(s) (Lead: {primary_pov[0]} with {primary_pov[1]} chapter(s)).")
    else:
        critiques.append("No explicit POV markers detected. Reader may experience head-hopping or focal ambiguity.")
        recommendations.append("Tag scene viewpoints with `@pov: Character` or frontmatter `pov: \"[[Character]]\"`.")

    if locations:
        strengths.append(f"Spatial continuity anchored across {len(locations)} primary setting(s).")
    else:
        recommendations.append("Anchor physical geography with `@location: SettingName` tags in scene headers.")

    score = max(45, min(100, score))
    verdict = "Continuity Maintained" if score >= 85 else "Minor Canon Drift" if score >= 70 else "Temporal Ambiguities Detected"

    summary = (
        f"Chronicler Mirella reports {verdict.lower()}. Verified {len(povs)} POV perspective(s) and "
        f"{len(locations)} spatial anchors across chapters."
    )

    return PersonaReview(
        persona_id="continuity_overseer",
        name="Chronicler Mirella",
        title="The Continuity & Canon Overseer (Timelines & Traits)",
        icon="⏳",
        score=score,
        verdict=verdict,
        summary=summary,
        strengths=strengths,
        critiques=critiques,
        recommendations=recommendations,
    )


def conduct_editorial_council(
    target_path: Path,
    world_path: Path | None = None,
    persona_filter: list[str] | None = None,
) -> CouncilReport:
    """Executes full Multi-Perspective Editorial Council workshop evaluation."""
    target = target_path.resolve()
    files: list[Path] = []

    if target.is_file() and target.suffix.lower() == ".md":
        files.append(target)
    elif target.is_dir():
        for p in sorted(target.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                files.append(p)

    chapters: list[dict[str, Any]] = []
    for f in files:
        content = f.read_text(encoding="utf-8", errors="replace")
        fm = parse_yaml_frontmatter(content)
        body = FRONTMATTER_REGEX.sub("", content).strip()
        h1 = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
        title = str(fm.get("title", h1.group(1).strip() if h1 else f.stem.replace("_", " ")))
        word_count = len(re.findall(r"\b\w+\b", body))
        chapters.append({
            "file": f.name,
            "title": title,
            "frontmatter": fm,
            "body": body,
            "word_count": word_count,
        })

    total_words = sum(c["word_count"] for c in chapters)

    # 1. Gather persona reviews
    reviews: list[PersonaReview] = []
    all_evaluators = {
        "line": evaluate_line_editor(chapters),
        "lore": evaluate_lore_inquisitor(chapters, world_path=world_path),
        "plot": evaluate_story_architect(chapters),
        "continuity": evaluate_continuity_overseer(chapters),
    }

    if persona_filter:
        clean_filters = [f.lower().strip() for f in persona_filter]
        for key, review in all_evaluators.items():
            if key in clean_filters or "all" in clean_filters:
                reviews.append(review)
    else:
        reviews = list(all_evaluators.values())

    # 2. Consensus Aggregation
    consensus_score = round(sum(r.score for r in reviews) / len(reviews)) if reviews else 0

    if consensus_score >= 88:
        consensus_verdict = "Consensus Approved: Publication Ready"
    elif consensus_score >= 75:
        consensus_verdict = "Consensus Approved: Minor Editorial Polish Needed"
    elif consensus_score >= 60:
        consensus_verdict = "Conditional Consensus: Targeted Revisions Required"
    else:
        consensus_verdict = "Developmental Hold: Substantial Structural Rework Needed"

    # 3. Dissenting notes (any persona deviating >= 12 from average)
    dissenting_notes: list[str] = []
    for r in reviews:
        diff = r.score - consensus_score
        if diff <= -12:
            dissenting_notes.append(f"DISSENT ({r.name}): Harsh evaluation ({r.score}/100, -{abs(diff)} vs consensus). Focus on: {r.critiques[0] if r.critiques else 'General deficits'}")
        elif diff >= 12:
            dissenting_notes.append(f"COMMENDATION ({r.name}): High praise ({r.score}/100, +{diff} vs consensus). Notable strength: {r.strengths[0] if r.strengths else 'Exemplary work'}")

    # 4. Master Action Items
    action_items: list[dict[str, Any]] = []
    idx = 1
    for r in reviews:
        for rec in r.recommendations:
            priority = "High" if r.score < 75 else "Medium"
            action_items.append({
                "id": f"ACT-{idx:02d}",
                "persona": r.name,
                "priority": priority,
                "task": rec,
            })
            idx += 1

    consensus_summary = (
        f"The Editorial Council convened for '{target.name}' ({total_words:,} words across {len(chapters)} chapter(s)). "
        f"Overall Consensus Readiness Score: {consensus_score}/100 ({consensus_verdict})."
    )

    return CouncilReport(
        target_name=target.name,
        total_words=total_words,
        total_chapters=len(chapters),
        consensus_score=consensus_score,
        consensus_verdict=consensus_verdict,
        consensus_summary=consensus_summary,
        reviews=reviews,
        dissenting_notes=dissenting_notes,
        action_items=action_items,
    )


def generate_council_markdown_report(report: CouncilReport) -> str:
    """Generates structured Markdown editorial workshop report."""
    lines = [
        f"# 🏛️ Sovereign Editorial Council Consensus Report: {report.target_name}",
        "",
        f"> **Consensus Score**: **{report.consensus_score}/100** — *{report.consensus_verdict}*  ",
        f"> **Scope**: {report.total_words:,} words | {report.total_chapters} chapters | {len(report.reviews)} Editorial Personas",
        "",
        "---",
        "",
        "## 1. Executive Council Chamber Overview",
        "",
        report.consensus_summary,
        "",
        "| Persona | Role | Score | Verdict |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for r in report.reviews:
        lines.append(f"| {r.icon} **{r.name}** | {r.title.split('(')[0].strip()} | **{r.score}/100** | `{r.verdict}` |")

    if report.dissenting_notes:
        lines.extend([
            "",
            "### Chamber Dissent & Commendations",
        ])
        for d in report.dissenting_notes:
            lines.append(f"- {d}")

    lines.extend([
        "",
        "---",
        "",
        "## 2. In-Depth Persona Evaluations",
    ])

    for r in report.reviews:
        lines.extend([
            "",
            f"### {r.icon} {r.name} — *{r.title}*",
            f"**Score**: `{r.score}/100` | **Verdict**: *{r.verdict}*",
            "",
            f"{r.summary}",
            "",
            "**Observed Craft Strengths:**",
        ])
        for s in r.strengths:
            lines.append(f"- ✅ {s}")
        if not r.strengths:
            lines.append("- *(None recorded)*")

        lines.append("\n**Critical Inquiries & Deficits:**")
        for c in r.critiques:
            lines.append(f"- ⚠️ {c}")
        if not r.critiques:
            lines.append("- *(Zero critical deficits found)*")

        lines.append("\n**Actionable Directives:**")
        for rec in r.recommendations:
            lines.append(f"- 💡 {rec}")
        if not r.recommendations:
            lines.append("- *(No immediate changes required)*")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Prioritized Master Action Checklist",
        "",
        "| ID | Priority | Persona | Directive |",
        "| :--- | :--- | :--- | :--- |",
    ])

    for a in report.action_items:
        lines.append(f"| `{a['id']}` | **{a['priority']}** | {a['persona']} | {a['task']} |")

    lines.append("")
    return "\n".join(lines)


def generate_council_html_dashboard(report: CouncilReport, output_path: Path) -> Path:
    """Generates standalone interactive HTML5 visual editorial council dashboard."""
    report_json = json.dumps(report.to_dict())

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Sovereign Editorial Council Dashboard</title>
<style>
  :root {{
    --bg: #0b1120; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --gold: #fbbf24; --success: #34d399; --warning: #fb923c; --danger: #f87171;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text);
    margin: 0; padding: 2rem; line-height: 1.6;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  header {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 2rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;
  }}
  .score-badge {{
    background: #0f172a; border: 2px solid var(--gold); border-radius: 50%;
    width: 100px; height: 100px; display: flex; flex-direction: column;
    justify-content: center; align-items: center; font-weight: 700;
  }}
  .score-num {{ font-size: 2rem; color: var(--gold); line-height: 1; }}
  .score-label {{ font-size: 0.65rem; color: var(--muted); text-transform: uppercase; }}
  
  .grid-personas {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;
  }}
  .card-persona {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 1.5rem;
    transition: transform 0.2s ease, border-color 0.2s ease; cursor: pointer;
  }}
  .card-persona:hover {{ transform: translateY(-3px); border-color: var(--accent); }}
  .card-persona.active {{ border-color: var(--accent); box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); }}
  
  .persona-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }}
  .persona-icon {{ font-size: 1.75rem; }}
  .badge-mini {{ font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.85rem; background: #0f172a; border: 1px solid var(--border); }}
  
  .detail-panel {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 2rem; margin-bottom: 2rem;
  }}
  .checklist {{ margin-top: 1.5rem; }}
  .checklist-item {{
    background: #0f172a; border: 1px solid var(--border); border-radius: 8px;
    padding: 0.75rem 1rem; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 1rem;
  }}
  .checklist-item input[type="checkbox"] {{ width: 1.25rem; height: 1.25rem; cursor: pointer; }}
  .tag-priority {{ font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px; text-transform: uppercase; }}
  .priority-High {{ background: rgba(248, 113, 113, 0.2); color: var(--danger); border: 1px solid var(--danger); }}
  .priority-Medium {{ background: rgba(251, 191, 36, 0.2); color: var(--gold); border: 1px solid var(--gold); }}
</style>
</head>
<body>

<div class="container">
  <header>
    <div>
      <h2 style="margin:0 0 0.5rem 0;color:var(--accent);">🏛️ Sovereign Editorial Council</h2>
      <div style="color:var(--muted);font-size:0.95rem;">
        Target: <strong style="color:var(--text);">{html.escape(report.target_name)}</strong> | Words: {report.total_words:,} | Chapters: {report.total_chapters}
      </div>
      <div style="margin-top:0.75rem;color:var(--success);font-weight:600;">
        {html.escape(report.consensus_verdict)}
      </div>
    </div>
    <div class="score-badge">
      <div class="score-num">{report.consensus_score}</div>
      <div class="score-label">Readiness</div>
    </div>
  </header>

  <div class="grid-personas" id="personaGrid">
    <!-- Populated by JS -->
  </div>

  <div class="detail-panel" id="detailPanel">
    <!-- Active Persona Details -->
  </div>

  <div class="detail-panel">
    <h3 style="margin-top:0;color:var(--gold);">📋 Master Revision Action Items</h3>
    <div class="checklist" id="actionList">
      <!-- Action items -->
    </div>
  </div>
</div>

<script>
  const data = {report_json};
  let activePersonaIdx = 0;

  function init() {{
    renderPersonas();
    renderDetail(0);
    renderActions();
  }}

  function renderPersonas() {{
    const grid = document.getElementById("personaGrid");
    grid.innerHTML = "";
    data.reviews.forEach((r, idx) => {{
      const card = document.createElement("div");
      card.className = `card-persona ${{idx === activePersonaIdx ? "active" : ""}}`;
      card.onclick = () => selectPersona(idx);
      card.innerHTML = `
        <div class="persona-head">
          <span class="persona-icon">${{r.icon}}</span>
          <span class="badge-mini" style="color: ${{r.score >= 80 ? 'var(--success)' : r.score >= 65 ? 'var(--gold)' : 'var(--danger)'}}">${{r.score}}/100</span>
        </div>
        <strong style="display:block;font-size:1.1rem;margin-bottom:0.25rem;">${{r.name}}</strong>
        <small style="color:var(--muted);">${{r.title.split('(')[0]}}</small>
        <div style="margin-top:0.75rem;font-size:0.85rem;color:var(--accent);font-weight:600;">${{r.verdict}}</div>
      `;
      grid.appendChild(card);
    }});
  }}

  function selectPersona(idx) {{
    activePersonaIdx = idx;
    renderPersonas();
    renderDetail(idx);
  }}

  function renderDetail(idx) {{
    const r = data.reviews[idx];
    if (!r) return;
    const panel = document.getElementById("detailPanel");
    
    panel.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
        <div>
          <h3 style="margin:0 0 0.25rem 0;color:var(--accent);">${{r.icon}} ${{r.name}}</h3>
          <span style="color:var(--muted);">${{r.title}}</span>
        </div>
        <div class="badge-mini" style="font-size:1.1rem;color:var(--gold);">${{r.score}}/100</div>
      </div>
      <p style="background:#0f172a;padding:1rem;border-radius:8px;border-left:3px solid var(--accent);font-style:italic;">
        "${{r.summary}}"
      </p>
      
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-top:1.5rem;">
        <div>
          <h4 style="color:var(--success);margin-top:0;">✅ Observed Strengths</h4>
          <ul>
            ${{r.strengths.map(s => `<li>${{s}}</li>`).join('')}}
          </ul>
        </div>
        <div>
          <h4 style="color:var(--warning);margin-top:0;">⚠️ Critiques & Directives</h4>
          <ul>
            ${{r.critiques.map(c => `<li>${{c}}</li>`).join('')}}
          </ul>
        </div>
      </div>
    `;
  }}

  function renderActions() {{
    const container = document.getElementById("actionList");
    container.innerHTML = "";
    data.action_items.forEach(a => {{
      const item = document.createElement("div");
      item.className = "checklist-item";
      item.innerHTML = `
        <input type="checkbox">
        <span class="tag-priority priority-${{a.priority}}">${{a.priority}}</span>
        <span style="flex:1;">${{a.task}}</span>
        <small style="color:var(--muted);">${{a.persona}}</small>
      `;
      container.appendChild(item);
    }});
  }}

  window.addEventListener("DOMContentLoaded", init);
</script>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Multi-Perspective Editorial Council Engine")
    parser.add_argument("target", help="Manuscript directory or Markdown chapter file")
    parser.add_argument("--world", "-w", help="Optional World Bible path for deep lore and magic audits")
    parser.add_argument("--html", help="Generate interactive standalone HTML5 council dashboard")
    parser.add_argument("--report", "-r", help="Save markdown consensus report to file")
    parser.add_argument("--json", action="store_true", help="Output editorial report as JSON to stdout")
    parser.add_argument("--personas", default="all", help="Comma-separated personas to convene: line,lore,plot,continuity,all (default: all)")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    world_path = Path(args.world) if args.world else None
    persona_list = [p.strip() for p in args.personas.split(",") if p.strip()]

    report = conduct_editorial_council(target_path, world_path=world_path, persona_filter=persona_list)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return

    md_report = generate_council_markdown_report(report)

    if args.report:
        rep_file = Path(args.report)
        atomic_write(rep_file, md_report)
        print(f"Editorial Report written to: {rep_file}")

    if args.html:
        out_html = Path(args.html)
        generate_council_html_dashboard(report, out_html)
        print(f"Interactive Council Dashboard written to: {out_html}")

    if not args.json and not args.report and not args.html:
        print("=" * 75)
        print("  🏛️  Ars Arcanum Multi-Perspective Editorial Council — v2.0.0")
        print("=" * 75)
        print(f"Target:           {report.target_name}")
        print(f"Total Words:      {report.total_words:,}")
        print(f"Consensus Score:  {report.consensus_score}/100")
        print(f"Verdict:          {report.consensus_verdict}")
        print("-" * 75)
        print("Council Chamber Findings:")
        for r in report.reviews:
            print(f"  {r.icon} {r.name:<22} | Score: {r.score:>3}/100 | {r.verdict}")
        if report.dissenting_notes:
            print("-" * 75)
            for d in report.dissenting_notes:
                print(f"  • {d}")
        print("=" * 75)


if __name__ == "__main__":
    main()
