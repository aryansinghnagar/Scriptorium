#!/usr/bin/env python3
"""
Ars Arcanum 6-Dimensional Sensory Palette & Prose Monotony Engine (scripts/lib/senses.py)
========================================================================================
Zero-dependency, offline stylistic analyzer that measures sensory immersion across
six sensory dimensions, flagging "White Room Syndrome" and perceptual monotony.

Sensory Dimensions:
1. Visual (Sight): Colors, lighting, shadows, clarity, radiance, forms.
2. Auditory (Hearing): Sounds, whispers, volume, acoustics, timbre, echoes, silence.
3. Olfactory (Smell): Scents, odors, stenches, aromas, musk, acridity, freshness.
4. Gustatory (Taste): Flavors, sweetness, bitterness, savoriness, salt, tang, metallic tastes.
5. Tactile / Thermal (Touch & Temperature): Textures, rough/smooth, cold, heat, pressure, pain.
6. Kinesthetic / Vestibular (Body & Balance): Vertigo, momentum, inertia, muscle strain, balance, pulse.

Diagnostic Codes:
- SNS-101: "White Room Syndrome" (Scene lacks tactile, auditory, or olfactory grounding).
- SNS-102: Sensory Monotony / Extreme Visual Skew (>90% visual anchors in scenes >300 words).

Zero external dependencies; 100% offline privacy.
"""

import sys
import os
import re
import json
import html
import argparse
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.senses")

SENSORY_LEXICON = {
    "visual": [
        "crimson", "azure", "emerald", "golden", "shadow", "shadows", "glare", "gloom",
        "gleaming", "flicker", "flickering", "radiant", "darkness", "brilliance", "pallor",
        "pale", "violet", "amber", "silhouette", "glimmer", "scintillating", "luminous",
        "shimmer", "blinding", "dazzling", "opaque", "translucent", "vivid", "murky",
        "scarlet", "indigo", "ebony", "ivory", "ochre", "cobalt", "gleam", "sparkle"
    ],
    "auditory": [
        "whisper", "whispered", "whispering", "roar", "roared", "roaring", "clang",
        "clattering", "crash", "silence", "silent", "echo", "echoed", "echoing",
        "deafening", "chime", "chimed", "hiss", "hissing", "murmur", "murmured",
        "rustle", "rustling", "rumble", "rumbling", "shriek", "shrieking", "thump",
        "humming", "screech", "buzz", "crack", "crackle", "groan", "rattle", "thud",
        "cacophony", "reverberate", "muffled", "shrill", "clamor", "hushed", "snarl"
    ],
    "olfactory": [
        "scent", "scented", "stench", "aroma", "musk", "musky", "acrid", "fragrant",
        "fragrance", "rancid", "perfume", "smoke", "smoky", "rotting", "foul", "pine",
        "ozone", "sulfur", "sulfuric", "pungent", "musty", "fetid", "incense", "odor",
        "sweet-smelling", "reek", "reeked", "reeking", "damp earth", "stale", "putrid"
    ],
    "gustatory": [
        "bitter", "sweet", "sweetness", "sour", "savory", "metallic", "salty", "saltiness",
        "umami", "spicy", "tangy", "tart", "ash", "honey", "copper", "succulent", "briny",
        "bland", "peppery", "acrid taste", "zesty", "astringent", "insipid", "cloying"
    ],
    "tactile_thermal": [
        "rough", "smooth", "freezing", "frozen", "searing", "scalding", "damp", "dampness",
        "humid", "sharp", "soft", "coarse", "friction", "icy", "blister", "burning",
        "chilly", "silk", "silky", "stone", "abrasive", "clammy", "slimy", "jagged",
        "prickle", "frost", "scorching", "gritty", "velvety", "numb", "sting", "stinging"
    ],
    "kinesthetic_vestibular": [
        "vertigo", "dizzy", "dizziness", "weightless", "weightlessness", "momentum",
        "inertia", "acceleration", "tremble", "trembling", "tremor", "nausea", "nauseous",
        "pulse", "pulsing", "exhaustion", "strain", "straining", "stagger", "staggered",
        "aching", "tension", "swaying", "off-balance", "lurch", "lurched", "flutter",
        "heaviness", "paralysis", "tingling", "spasm", "whirling", "spinning"
    ],
}

SENSORY_PATTERNS = {
    dim: [re.compile(r"\b" + re.escape(w) + r"\b", re.IGNORECASE) for w in words]
    for dim, words in SENSORY_LEXICON.items()
}


def analyze_text_senses(text: str) -> dict:
    """Computes sensory counts for a given text block."""
    counts = {dim: 0 for dim in SENSORY_LEXICON}
    matches = {dim: [] for dim in SENSORY_LEXICON}
    words = [w for w in re.findall(r"\b\w+\b", text) if not w.startswith("@")]
    total_words = len(words)

    for dim, patterns in SENSORY_PATTERNS.items():
        for pat in patterns:
            for m in pat.finditer(text):
                counts[dim] += 1
                if len(matches[dim]) < 5:
                    matches[dim].append(m.group(0).lower())

    total_sensory_anchors = sum(counts.values())
    percentages = {}
    for dim, cnt in counts.items():
        percentages[dim] = round((cnt / total_sensory_anchors * 100.0), 1) if total_sensory_anchors > 0 else 0.0

    return {
        "total_words": total_words,
        "total_sensory_anchors": total_sensory_anchors,
        "counts": counts,
        "percentages": percentages,
        "sample_anchors": matches,
    }


def audit_manuscript_senses(manuscript_dir: Path) -> dict:
    """Analyzes 6D sensory palette across all scenes in manuscript and catches White Room scenes."""
    scenes_data = {}
    findings = []
    overall_counts = {dim: 0 for dim in SENSORY_LEXICON}
    total_words_all = 0

    for md_file in sorted(manuscript_dir.rglob("*.md")):
        if md_file.name.startswith(".") or "Front_Matter" in md_file.parts or "Back_Matter" in md_file.parts:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            # Strip tag lines
            clean_lines = [l for l in content.splitlines() if not l.strip().startswith("@")]
            clean_text = "\n".join(clean_lines)

            stats = analyze_text_senses(clean_text)
            rel_path = str(md_file.relative_to(manuscript_dir))
            scenes_data[rel_path] = stats
            total_words_all += stats["total_words"]

            for dim, cnt in stats["counts"].items():
                overall_counts[dim] += cnt

            # Check for White Room Syndrome (SNS-101)
            # If scene has > 150 words but non-visual anchors < 2
            non_visual_count = sum(stats["counts"][d] for d in stats["counts"] if d != "visual")
            if stats["total_words"] > 150 and non_visual_count < 2:
                findings.append({
                    "id": "SNS-101",
                    "severity": "WARNING",
                    "scene": rel_path,
                    "words": stats["total_words"],
                    "non_visual_anchors": non_visual_count,
                    "message": f"White Room Syndrome: Scene has {stats['total_words']} words but only {non_visual_count} non-visual sensory anchors (lacks auditory, olfactory, or tactile grounding).",
                    "file": rel_path,
                })

            # Check for Extreme Visual Monotony (SNS-102)
            # If scene has > 300 words and visual percentage > 90%
            if stats["total_words"] > 300 and stats["total_sensory_anchors"] >= 5 and stats["percentages"]["visual"] >= 90.0:
                findings.append({
                    "id": "SNS-102",
                    "severity": "WARNING",
                    "scene": rel_path,
                    "visual_pct": stats["percentages"]["visual"],
                    "message": f"Sensory Monotony: Scene is {stats['percentages']['visual']}% visual anchors with negligible sensory variety.",
                    "file": rel_path,
                })
        except Exception as e:
            logger.warning("Failed to analyze senses for %s: %s", md_file, e)

    total_sensory_all = sum(overall_counts.values())
    overall_pct = {}
    for dim, cnt in overall_counts.items():
        overall_pct[dim] = round((cnt / max(1, total_sensory_all) * 100.0), 1)

    return {
        "manuscript": manuscript_dir.name,
        "total_words": total_words_all,
        "total_sensory_anchors": total_sensory_all,
        "overall_counts": overall_counts,
        "overall_percentages": overall_pct,
        "scenes": scenes_data,
        "findings": findings,
    }


def generate_senses_html_report(audit_data: dict, output_path: Path):
    """Generates standalone HTML report with 6D sensory radar and scene breakdown."""
    ms_name = audit_data.get("manuscript", "Manuscript")
    overall_pct = audit_data.get("overall_percentages", {})
    overall_cnt = audit_data.get("overall_counts", {})
    findings = audit_data.get("findings", [])
    scenes = audit_data.get("scenes", {})

    findings_cards = []
    for fd in findings:
        findings_cards.append(f"""
        <div class="card finding-card">
            <span class="badge badge-warning">{html.escape(fd.get('id', 'SNS-101'))}</span>
            <strong>{html.escape(fd.get('scene', ''))}</strong>: {html.escape(fd.get('message', ''))}
        </div>
        """)

    findings_html = "".join(findings_cards) if findings_cards else "<div style='color: #34d399;'>✓ All scenes exhibit balanced multi-sensory grounding.</div>"

    scene_rows = []
    for sc_name, sc_data in sorted(scenes.items()):
        p = sc_data["percentages"]
        scene_rows.append(f"""
        <tr>
            <td><strong>{html.escape(sc_name)}</strong> ({sc_data['total_words']} words)</td>
            <td style="color: #38bdf8;">{p.get('visual', 0)}%</td>
            <td style="color: #4ade80;">{p.get('auditory', 0)}%</td>
            <td style="color: #f59e0b;">{p.get('olfactory', 0)}%</td>
            <td style="color: #f43f5e;">{p.get('gustatory', 0)}%</td>
            <td style="color: #c084fc;">{p.get('tactile_thermal', 0)}%</td>
            <td style="color: #a3e635;">{p.get('kinesthetic_vestibular', 0)}%</td>
        </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — 6D Sensory Palette Report ({html.escape(ms_name)})</title>
<style>
  :root {{
    --bg: #0f172a;
    --card-bg: #1e293b;
    --border: #334155;
    --text: #f8fafc;
    --accent: #38bdf8;
    --warning: #fbbf24;
    --success: #34d399;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 2rem;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  h1, h2, h3 {{ color: var(--accent); }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .badge {{
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }}
  .badge-warning {{ background: #d97706; color: #fff; }}
  .finding-card {{ margin-bottom: 0.75rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ background: #0f172a; color: var(--accent); }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 1rem; text-align: center; }}
  .stat-box {{ background: #0f172a; padding: 1rem; border-radius: 6px; border: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="container">
  <h1>🎨 Ars Arcanum 6D Sensory Palette Analysis</h1>
  <p>Manuscript: <strong>{html.escape(ms_name)}</strong> | Total Words: <strong>{audit_data.get('total_words', 0):,}</strong></p>

  <div class="card">
    <h2>Manuscript Sensory Distribution</h2>
    <div class="stat-grid">
      <div class="stat-box"><strong style="color: #38bdf8;">Visual</strong><br/>{overall_pct.get('visual', 0)}%<br/><small>({overall_cnt.get('visual', 0)})</small></div>
      <div class="stat-box"><strong style="color: #4ade80;">Auditory</strong><br/>{overall_pct.get('auditory', 0)}%<br/><small>({overall_cnt.get('auditory', 0)})</small></div>
      <div class="stat-box"><strong style="color: #f59e0b;">Olfactory</strong><br/>{overall_pct.get('olfactory', 0)}%<br/><small>({overall_cnt.get('olfactory', 0)})</small></div>
      <div class="stat-box"><strong style="color: #f43f5e;">Gustatory</strong><br/>{overall_pct.get('gustatory', 0)}%<br/><small>({overall_cnt.get('gustatory', 0)})</small></div>
      <div class="stat-box"><strong style="color: #c084fc;">Tactile</strong><br/>{overall_pct.get('tactile_thermal', 0)}%<br/><small>({overall_cnt.get('tactile_thermal', 0)})</small></div>
      <div class="stat-box"><strong style="color: #a3e635;">Kinesthetic</strong><br/>{overall_pct.get('kinesthetic_vestibular', 0)}%<br/><small>({overall_cnt.get('kinesthetic_vestibular', 0)})</small></div>
    </div>
  </div>

  <div class="card">
    <h2>White Room & Sensory Monotony Diagnostics ({len(findings)})</h2>
    {findings_html}
  </div>

  <div class="card">
    <h2>Per-Scene Sensory Palette Breakdown</h2>
    <table>
      <thead>
        <tr>
          <th>Scene</th>
          <th>Visual</th>
          <th>Auditory</th>
          <th>Olfactory</th>
          <th>Gustatory</th>
          <th>Tactile</th>
          <th>Kinesthetic</th>
        </tr>
      </thead>
      <tbody>
        {"".join(scene_rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    output_path.write_text(html_content, encoding="utf-8")


def resolve_manuscript_dir(target_str: str = None) -> str:
    """Resolves manuscript input string (path or name) to absolute directory path."""
    if target_str:
        p = Path(target_str).expanduser().resolve()
        if p.is_dir():
            return str(p)
        home = Path.home()
        for m_dir in sorted((home / "Manuscripts").glob("*")):
            if m_dir.is_dir() and m_dir.name.lower() == target_str.lower():
                return str(m_dir)
        p_cwd = Path.cwd() / target_str
        if p_cwd.is_dir():
            return str(p_cwd)

    home = Path.home()
    manuscripts = sorted((home / "Manuscripts").glob("*"), key=lambda p: str(p))
    manuscripts = [p for p in manuscripts if p.is_dir()]
    if len(manuscripts) == 1:
        return str(manuscripts[0])
    elif len(manuscripts) > 1:
        print("Error: Multiple manuscripts discovered — specify one explicitly.", file=sys.stderr)
        sys.exit(2)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum 6-Dimensional Sensory Palette & White Room Engine")
    parser.add_argument("manuscript", nargs="?", help="Manuscript draft directory")
    parser.add_argument("-m", "--manuscript", dest="ms_flag", help="Manuscript draft directory")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--html", help="Path to export standalone HTML report")

    args = parser.parse_args()

    raw_ms = getattr(args, "ms_flag", None) or getattr(args, "manuscript", None)
    ms_dir_str = resolve_manuscript_dir(raw_ms)
    if not ms_dir_str or not Path(ms_dir_str).is_dir():
        print("Error: No valid Manuscript directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    ms_path = Path(ms_dir_str)
    audit_data = audit_manuscript_senses(ms_path)

    if args.json:
        print(json.dumps(audit_data, indent=2))
    else:
        print(f"\n\033[1;35m=== Ars Arcanum 6-Dimensional Sensory Palette ===\033[0m")
        print(f"Manuscript: \033[1m{ms_path.name}\033[0m | Words: {audit_data['total_words']:,} | Sensory Anchors: {audit_data['total_sensory_anchors']:,}\n")

        pct = audit_data["overall_percentages"]
        cnt = audit_data["overall_counts"]
        print("\033[1mSensory Distribution:\033[0m")
        print(f"  👁️  Visual       : \033[36m{pct.get('visual', 0):>5.1f}%\033[0m ({cnt.get('visual', 0)} occurrences)")
        print(f"  👂 Auditory     : \033[32m{pct.get('auditory', 0):>5.1f}%\033[0m ({cnt.get('auditory', 0)} occurrences)")
        print(f"  👃 Olfactory    : \033[33m{pct.get('olfactory', 0):>5.1f}%\033[0m ({cnt.get('olfactory', 0)} occurrences)")
        print(f"  👅 Gustatory    : \033[31m{pct.get('gustatory', 0):>5.1f}%\033[0m ({cnt.get('gustatory', 0)} occurrences)")
        print(f"  ✋ Tactile/Therm: \033[35m{pct.get('tactile_thermal', 0):>5.1f}%\033[0m ({cnt.get('tactile_thermal', 0)} occurrences)")
        print(f"  🤸 Kinesthetic  : \033[34m{pct.get('kinesthetic_vestibular', 0):>5.1f}%\033[0m ({cnt.get('kinesthetic_vestibular', 0)} occurrences)\n")

        findings = audit_data["findings"]
        if not findings:
            print("\033[32m[OK] Multi-sensory grounding is well-balanced across all scenes.\033[0m\n")
        else:
            print(f"\033[1;33mDiagnostic Findings ({len(findings)}):\033[0m")
            for fd in findings:
                print(f"  ⚠️  \033[33m[{fd['id']}]\033[0m {fd['message']}")
                print(f"     Location: {fd['file']}\n")

    if args.html:
        out_p = Path(args.html)
        generate_senses_html_report(audit_data, out_p)
        print(f"Interactive HTML report written to: {out_p}")

    sys.exit(1 if len(audit_data["findings"]) > 0 else 0)


if __name__ == "__main__":
    main()
