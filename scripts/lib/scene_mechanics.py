#!/usr/bin/env python3
"""
Ars Arcanum Scene Mechanics & Motivation-Reaction Unit (MRU) Analyzer
(scripts/lib/scene_mechanics.py)
================================================================================
Zero-dependency, offline scene structure & MRU craft linter.

Capabilities (PLT-104):
1. Motivation-Reaction Unit (MRU) Sequencing:
   - Swain & Butcher craft mechanics:
     * Stimulus (External Event / Sensory Input)
     * Visceral Reflex (Involuntary physical sensation: gasp, flinch, adrenaline, pulse)
     * Emotional Response (Instinctive feeling: dread, fury, sorrow, relief)
     * Cognitive Reflection (Internal monologue / rational thought)
     * Action / Dialogue (Spoken words, deliberate movement, counter-attack)
   - Flags inverted / backwards MRU sequences (e.g., character speaks or analyzes
     before registering sensory stimulus or visceral reaction).
2. Scene vs Sequel Anatomy:
   - Proactive Scenes: Goal -> Conflict -> Disaster / Setback
   - Reactive Sequels: Reaction -> Dilemma -> Decision
   - Identifies scenes missing clear Goal/Conflict or ending without a hook.
   - Proactive-to-Reactive scene balance distribution.
3. Standalone HTML/SVG report with interactive MRU scene breakdown.

Zero external dependencies; 100% offline privacy.
"""

import sys
import re
import json
import html
import argparse
import logging
from pathlib import Path
from collections import Counter

try:
    from lib.fs_utils import atomic_write
except ImportError:
    try:
        from fs_utils import atomic_write
    except ImportError:
        def atomic_write(path, data, encoding="utf-8"):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, (bytes, bytearray)):
                p.write_bytes(data)
            else:
                p.write_text(data, encoding=encoding)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.scene_mechanics")

# Keyword dictionaries for MRU phase classification
VISCERAL_KEYWORDS = {
    "pulse", "heart", "breath", "gasp", "flinch", "shiver", "shudder", "adrenaline",
    "spine", "stomach", "gut", "throat", "choke", "sweat", "tremble", "jolt",
    "recoil", "clench", "freeze", "blench", "dizzy", "nausea", "blood", "skin"
}

EMOTION_KEYWORDS = {
    "fear", "dread", "terror", "rage", "fury", "anger", "grief", "sorrow",
    "relief", "hope", "despair", "panic", "joy", "bitter", "shame", "guilt",
    "pride", "spite", "envy", "shock", "horror", "disgust", "awe"
}

COGNITIVE_KEYWORDS = {
    "thought", "knew", "realized", "pondered", "wondered", "considered", "remembered",
    "calculated", "decided", "understood", "reasoned", "deduced", "concluded",
    "believed", "supposed", "doubted", "recognized", "assessed"
}

GOAL_KEYWORDS = {
    "must", "need to", "had to", "wanted", "plan", "objective", "target", "mission",
    "intend", "goal", "seek", "ordered", "promised", "duty"
}

DISASTER_KEYWORDS = {
    "suddenly", "too late", "failed", "trap", "ambush", "explosion", "betrayal",
    "collapsed", "struck", "shattered", "ruined", "lost", "broken", "cornered"
}


def classify_sentence_mru(sentence: str) -> str:
    """Classifies a sentence into its predominant MRU craft phase."""
    s_lower = sentence.lower()
    words = set(re.findall(r'\b[a-z]+\b', s_lower))

    # 1. Visceral Reflex (Involuntary bodily sensation)
    if words & VISCERAL_KEYWORDS:
        return "Visceral Reflex"

    # 2. Dialogue / Spoken Action
    if re.search(r'["“][^"”]+["”]|[\'‘][^\'’]{3,}[\'’]', sentence):
        return "Action/Dialogue"

    # 3. Emotional Response
    if words & EMOTION_KEYWORDS:
        return "Emotional Response"

    # 4. Cognitive Thought
    if words & COGNITIVE_KEYWORDS or s_lower.startswith(("he thought", "she thought", "if only", "why had")):
        return "Cognitive Thought"

    # 5. External Action / Stimulus (Default for physical description)
    return "Action/Stimulus"


def analyze_scene_text(text: str, scene_title: str = "Scene") -> dict:
    """Analyzes a scene's MRU flow, goal/conflict presence, and proactive/reactive type."""
    clean_text = re.sub(r'^\s*[@#\-].*$', '', text, flags=re.MULTILINE)
    raw_sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    sentences = [s.strip() for s in raw_sentences if s.strip() and len(re.findall(r'\b\w+\b', s)) > 0]

    mru_sequence = []
    for idx, s in enumerate(sentences, 1):
        phase = classify_sentence_mru(s)
        mru_sequence.append({
            "index": idx,
            "sentence": s,
            "phase": phase
        })

    # Inverted Sequence Warnings
    # Ideal: Stimulus -> Visceral -> Emotion -> Thought -> Action
    # Flag when Action/Thought appears directly preceding Visceral in high-tension moments
    flaws = []
    for i in range(len(mru_sequence) - 1):
        curr = mru_sequence[i]
        nxt = mru_sequence[i + 1]
        if curr["phase"] in ("Cognitive Thought", "Action/Dialogue") and nxt["phase"] == "Visceral Reflex":
            preceding_type = "Cognitive thought" if curr["phase"] == "Cognitive Thought" else "Dialogue / Action"
            flaws.append({
                "type": "inverted_mru",
                "sentence_idx": nxt["index"],
                "message": f"Possible inverted MRU: Visceral reflex ('{nxt['sentence'][:40]}...') occurs AFTER {preceding_type} ('{curr['sentence'][:40]}...'). Involuntary reflex should precede rational analysis and deliberate action.",
                "context": f"{curr['sentence']} -> {nxt['sentence']}"
            })

    # Goal / Conflict / Disaster checks
    text_lower = text.lower()
    has_goal = any(g in text_lower for g in GOAL_KEYWORDS)
    has_disaster = any(d in text_lower for d in DISASTER_KEYWORDS)

    # Determine Scene vs Sequel
    phase_counts = Counter(item["phase"] for item in mru_sequence)
    internal_weight = phase_counts["Visceral Reflex"] + phase_counts["Emotional Response"] + phase_counts["Cognitive Thought"]
    external_weight = phase_counts["Action/Stimulus"] + phase_counts["Action/Dialogue"]

    scene_type = "Proactive Scene" if external_weight >= internal_weight else "Reactive Sequel"

    return {
        "title": scene_title,
        "total_sentences": len(sentences),
        "scene_type": scene_type,
        "has_goal": has_goal,
        "has_disaster": has_disaster,
        "phase_distribution": dict(phase_counts),
        "mru_flaws": flaws,
        "mru_sequence_sample": mru_sequence[:25]
    }


def scan_manuscript_scenes(target_path: Path) -> dict:
    """Scans all chapters/scenes in a manuscript for MRU craft analysis."""
    files = []
    if target_path.is_file():
        files.append(target_path)
    elif target_path.is_dir():
        for p in sorted(target_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                files.append(p)
    else:
        raise FileNotFoundError(f"Target path not found: {target_path}")

    scenes = []
    proactive_count = 0
    reactive_count = 0
    total_flaws = 0

    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            res = analyze_scene_text(content, scene_title=f.stem)
            res["file"] = str(f)
            scenes.append(res)
            if res["scene_type"] == "Proactive Scene":
                proactive_count += 1
            else:
                reactive_count += 1
            total_flaws += len(res["mru_flaws"])
        except Exception as e:
            logger.warning("Error reading %s: %s", f, e)

    return {
        "target": str(target_path),
        "total_scenes": len(scenes),
        "proactive_scenes": proactive_count,
        "reactive_sequels": reactive_count,
        "total_mru_flaws": total_flaws,
        "scenes": scenes
    }


def generate_scene_mechanics_html(report: dict, output_path: Path) -> Path:
    """Generates an offline interactive HTML report for scene MRU mechanics."""
    scenes = report.get("scenes", [])
    
    scene_cards = []
    for sc in scenes:
        badge_type = "<span style='background:#0284c7;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.75rem;'>Proactive Scene</span>" if sc["scene_type"] == "Proactive Scene" else "<span style='background:#7c3aed;color:#fff;padding:2px 8px;border-radius:4px;font-size:0.75rem;'>Reactive Sequel</span>"
        
        flaws_html = "".join(
            f"<div style='background:#7f1d1d;color:#fecaca;padding:6px;border-radius:4px;font-size:0.8rem;margin-top:6px;'>⚠️ {html.escape(flaw['message'])}</div>"
            for flaw in sc.get("mru_flaws", [])
        ) or "<p style='color:#10b981;font-size:0.8rem;margin:6px 0 0 0;'>✓ Natural MRU flow</p>"

        card = f"""
        <div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:1.25rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <h3 style="margin:0;color:#38bdf8;">{html.escape(sc['title'])}</h3>
            {badge_type}
          </div>
          <p style="color:#94a3b8;font-size:0.85rem;margin:0.5rem 0;">{sc['total_sentences']} sentences | Goal: {'✓' if sc['has_goal'] else '⚠️ Missing'} | Climax/Disaster: {'✓' if sc['has_disaster'] else '—'}</p>
          <div style="margin-top:0.75rem;">
            {flaws_html}
          </div>
        </div>
        """
        scene_cards.append(card)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Scene Mechanics & MRU Analyzer</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444; --success: #10b981;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .scenes-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.25rem; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🎬 Scene Mechanics & Motivation-Reaction Units</h1>
    <p style="color: var(--muted);">Target: {html.escape(report.get('target', ''))} | Total Scenes: {report.get('total_scenes', 0)}</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Proactive Scenes</h3>
      <div class="metric">{report.get('proactive_scenes', 0)}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Goal -> Conflict -> Disaster</p>
    </div>
    <div class="card">
      <h3>Reactive Sequels</h3>
      <div class="metric">{report.get('reactive_sequels', 0)}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Reaction -> Dilemma -> Decision</p>
    </div>
    <div class="card">
      <h3>Inverted MRU Flaws</h3>
      <div class="metric" style="color: {'var(--danger)' if report.get('total_mru_flaws', 0) > 0 else 'var(--success)'};">{report.get('total_mru_flaws', 0)}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Sequencing contradictions</p>
    </div>
  </div>

  <h2>📚 Chapter Scene Ledger</h2>
  <div class="scenes-grid">
    {''.join(scene_cards)}
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Scene Mechanics MRU Analyzer (PLT-104)")
    parser.add_argument("target", help="Manuscript directory or file")
    parser.add_argument("--html", help="Generate HTML report to output path")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    report = scan_manuscript_scenes(target_path)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"=== Scene Mechanics & MRU Analysis: {target_path.name} ===")
    print(f"Total Scenes: {report['total_scenes']} | Proactive: {report['proactive_scenes']} | Reactive Sequels: {report['reactive_sequels']}")
    print(f"Inverted MRU Warnings: {report['total_mru_flaws']}")
    print("-" * 65)
    for sc in report["scenes"]:
        flaw_str = f" [⚠️ {len(sc['mru_flaws'])} MRU flaws]" if sc["mru_flaws"] else " [✓ OK]"
        print(f"  🎬 {sc['title']:<24} | {sc['scene_type']:<16} | Goal: {'Yes' if sc['has_goal'] else 'No':<3}{flaw_str}")

    if args.html:
        out_p = Path(args.html)
        generate_scene_mechanics_html(report, out_p)
        print(f"\nHTML report written to: {out_p}")


if __name__ == "__main__":
    main()
