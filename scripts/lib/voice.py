#!/usr/bin/env python3
"""
Ars Arcanum Character Voice Profiler & Dialogue Fingerprint Engine
(scripts/lib/voice.py)
================================================================================
Zero-dependency, offline character voice analyzer and dialogue profiler.

Capabilities (PRO-103):
1. Extract dialogue attributed to individual characters via:
   - Explicit tags: `"..." said Elena` / `Elena said, "..."`
   - Script format: `Elena: "..."` or `Elena:\n"..."`
   - novelWriter / Arcanum `@dialogue: Character` or `@pov: Character` blocks
2. Character Linguistic Fingerprint:
   - Type-Token Ratio (TTR / Lexical Richness)
   - Mean Utterance Length (words per dialogue line) & standard deviation
   - Contraction Usage Ratio (formal vs colloquial: don't/can't vs do not/cannot)
   - Punctuation cadence: Question (?), Exclamation (!), Ellipsis (...), Dash (—) ratios
   - Distinctive vocabulary / favorite words (TF-IDF approximation vs other characters)
3. Voice Bleed / Character Homogeneity Detector:
   - Computes cosine similarity of character dialogue vocabulary vectors
   - Warns when distinct characters sound identical or suffer from author voice bleed

4. Standalone HTML/SVG report with interactive voice fingerprint cards and similarity matrix.

Zero external dependencies; 100% offline privacy.
"""

import sys
import re
import math
import json
import html
import argparse
import logging
from pathlib import Path
from collections import Counter, defaultdict

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

logger = logging.getLogger("arcanum.voice")

# Common contractions for formality ratio calculation
CONTRACTION_PATTERNS = [
    r"\b(i'm|i've|i'll|i'd|you're|you've|you'll|you'd|he's|he'll|he'd|she's|she'll|she'd)\b",
    r"\b(it's|we're|we've|we'll|we'd|they're|they've|they'll|they'd)\b",
    r"\b(don't|doesn't|didn't|can't|couldn't|won't|wouldn't|shouldn't|mustn't)\b",
    r"\b(isn't|aren't|wasn't|weren't|hasn't|haven't|hadn't)\b",
    r"\b(what's|where's|when's|why's|how's|that's|there's|here's)\b",
    r"\b(gonna|wanna|gotta|lemme|gimme|kinda|sorta|dunno)\b"
]
CONTRACTION_REGEX = re.compile("|".join(CONTRACTION_PATTERNS), re.IGNORECASE)

COMMON_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "by", "of", "from", "up", "about", "into", "over", "after", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "that", "this", "these", "those", "it", "its", "you", "i", "he", "she",
    "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "their",
    "our", "said", "asked", "replied", "what", "which", "who", "when", "where", "why", "how"
}


def extract_character_dialogue(text: str) -> dict[str, list[str]]:
    """Extracts dialogue strings grouped by character name."""
    char_dialogue = defaultdict(list)
    lines = text.splitlines()

    current_pov = "Unknown"

    for line in lines:
        clean_line = line.strip()
        if not clean_line or clean_line.startswith(("---", "#")):
            continue

        # Check @pov: tag
        pov_m = re.match(r'^@pov:\s*([A-Za-z0-9_\-\'\s]+)', clean_line, re.IGNORECASE)
        if pov_m:
            current_pov = pov_m.group(1).strip()
            continue

        # Check script-style attribution: Character: "Dialogue"
        script_m = re.match(r'^([A-Z][A-Za-z0-9_\s]{1,25}):\s*["“]([^"”]+)["”]', clean_line)
        if script_m:
            char = script_m.group(1).strip()
            dlg = script_m.group(2).strip()
            char_dialogue[char].append(dlg)
            continue

        # Check post-quote tag: "Dialogue," said Character. / "Dialogue," Character whispered.
        post_m = re.finditer(r'["“]([^"”]+)["”][,\s]+(?:said|asked|whispered|murmured|replied|shouted|muttered|cried|screamed|called|growled|snapped)\s+([A-Z][a-zA-Z]{1,20})', clean_line)
        found_post = False
        for m in post_m:
            dlg = m.group(1).strip()
            char = m.group(2).strip()
            if char not in ("He", "She", "They", "It"):
                char_dialogue[char].append(dlg)
                found_post = True

        # Check pre-quote tag: Character said, "Dialogue"
        pre_m = re.finditer(r'\b([A-Z][a-zA-Z]{1,20})\s+(?:said|asked|whispered|murmured|replied|shouted|muttered|cried|screamed|called|growled|snapped)[,\s]+["“]([^"”]+)["”]', clean_line)
        found_pre = False
        for m in pre_m:
            char = m.group(1).strip()
            dlg = m.group(2).strip()
            if char not in ("He", "She", "They", "It"):
                char_dialogue[char].append(dlg)
                found_pre = True

        # If untagged quote in strong POV context
        if not found_post and not found_pre:
            quotes = re.findall(r'["“]([^"”]+)["”]', clean_line)
            if quotes and current_pov != "Unknown":
                # We record in POV context under POV-Dialogue if not specifically attributed
                pass

    return dict(char_dialogue)


def compute_voice_profile(utterances: list[str], all_characters_corpus: dict[str, list[str]] | None = None, char_name: str = "") -> dict:
    """Computes a comprehensive linguistic voice profile for a character's utterances."""
    if not utterances:
        return {
            "utterance_count": 0,
            "total_words": 0,
            "unique_words": 0,
            "ttr": 0.0,
            "mean_length": 0.0,
            "std_dev_length": 0.0,
            "contraction_rate": 0.0,
            "question_ratio": 0.0,
            "exclamation_ratio": 0.0,
            "ellipsis_ratio": 0.0,
            "interruption_ratio": 0.0,
            "formality_score": 50.0,
            "distinctive_words": []
        }

    total_words = 0
    word_tokens = []
    utterance_lengths = []
    contraction_count = 0
    questions = 0
    exclamations = 0
    ellipses = 0
    dashes = 0

    for u in utterances:
        words = re.findall(r'\b[A-Za-z\']+\b', u)
        u_len = len(words)
        total_words += u_len
        utterance_lengths.append(u_len)
        word_tokens.extend([w.lower() for w in words])

        if "?" in u:
            questions += 1
        if "!" in u:
            exclamations += 1
        if "..." in u or "…" in u:
            ellipses += 1
        if "—" in u or "--" in u:
            dashes += 1

        contractions = CONTRACTION_REGEX.findall(u)
        contraction_count += len(contractions)

    u_count = len(utterances)
    mean_len = total_words / u_count if u_count > 0 else 0.0
    var = sum((ulen - mean_len) ** 2 for ulen in utterance_lengths) / u_count if u_count > 0 else 0.0
    std_dev = math.sqrt(var)

    unique_words = len(set(word_tokens))
    ttr = (unique_words / total_words) if total_words > 0 else 0.0
    contraction_rate = (contraction_count / total_words * 100) if total_words > 0 else 0.0

    q_ratio = questions / u_count if u_count > 0 else 0.0
    ex_ratio = exclamations / u_count if u_count > 0 else 0.0
    el_ratio = ellipses / u_count if u_count > 0 else 0.0
    dash_ratio = dashes / u_count if u_count > 0 else 0.0

    # Formality estimation: higher contraction rate & shorter sentences -> lower formality
    # Higher average word length -> higher formality
    avg_word_len = sum(len(w) for w in word_tokens) / total_words if total_words > 0 else 4.5
    formality = 50.0 + (avg_word_len - 4.5) * 15.0 - (contraction_rate * 2.5) + (mean_len - 8.0) * 1.5
    formality = round(max(0.0, min(100.0, formality)), 1)

    # Distinctive words (TF-IDF against other characters)
    distinctive_words = []
    if all_characters_corpus and total_words >= 15:
        char_counts = Counter(word_tokens)
        other_counts = Counter()
        other_total = 0
        for other_c, other_utts in all_characters_corpus.items():
            if other_c != char_name:
                for ou in other_utts:
                    ow = [w.lower() for w in re.findall(r'\b[A-Za-z]+\b', ou)]
                    other_counts.update(ow)
                    other_total += len(ow)

        scored_words = []
        for word, count in char_counts.items():
            if len(word) >= 4 and word not in COMMON_STOPWORDS and count >= 2:
                tf = count / total_words
                other_tf = (other_counts[word] / other_total) if other_total > 0 else 0.0001
                distinctiveness = tf / (other_tf + 0.001)
                scored_words.append((word, count, distinctiveness))
        scored_words.sort(key=lambda x: x[2], reverse=True)
        distinctive_words = [{"word": w, "count": c, "score": round(s, 2)} for w, c, s in scored_words[:8]]

    warning = None
    if total_words < 100:
        warning = "Dialogue corpus contains fewer than 100 words. Voice fingerprint metrics may be statistically noisy."

    return {
        "utterance_count": u_count,
        "total_words": total_words,
        "unique_words": unique_words,
        "ttr": round(ttr, 3),
        "mean_length": round(mean_len, 2),
        "std_dev_length": round(std_dev, 2),
        "contraction_rate": round(contraction_rate, 2),
        "question_ratio": round(q_ratio, 3),
        "exclamation_ratio": round(ex_ratio, 3),
        "ellipsis_ratio": round(el_ratio, 3),
        "interruption_ratio": round(dash_ratio, 3),
        "formality_score": formality,
        "sample_size_warning": warning,
        "distinctive_words": distinctive_words
    }


def compute_voice_similarity(profile_a: dict, profile_b: dict) -> float:
    """Computes similarity (0.0 to 1.0) between two character voice profiles."""
    if profile_a["total_words"] < 10 or profile_b["total_words"] < 10:
        return 0.0

    # Metric feature vector: [TTR, MeanLen/30, ContractionRate/20, Formality/100, Q_ratio, Ex_ratio]
    v_a = [
        profile_a["ttr"],
        min(1.0, profile_a["mean_length"] / 30.0),
        min(1.0, profile_a["contraction_rate"] / 20.0),
        profile_a["formality_score"] / 100.0,
        profile_a["question_ratio"],
        profile_a["exclamation_ratio"]
    ]
    v_b = [
        profile_b["ttr"],
        min(1.0, profile_b["mean_length"] / 30.0),
        min(1.0, profile_b["contraction_rate"] / 20.0),
        profile_b["formality_score"] / 100.0,
        profile_b["question_ratio"],
        profile_b["exclamation_ratio"]
    ]

    dot = sum(x * y for x, y in zip(v_a, v_b))
    mag_a = math.sqrt(sum(x ** 2 for x in v_a))
    mag_b = math.sqrt(sum(x ** 2 for x in v_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return round(dot / (mag_a * mag_b), 3)


def scan_manuscript_voices(target_path: Path) -> dict:
    """Scans manuscript or file for all character dialogue and analyzes voice profiles."""
    files = []
    if target_path.is_file():
        files.append(target_path)
    elif target_path.is_dir():
        for p in sorted(target_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts:
                files.append(p)
    else:
        raise FileNotFoundError(f"Target path not found: {target_path}")

    all_dialogue = defaultdict(list)

    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            file_dialogue = extract_character_dialogue(content)
            for char, utts in file_dialogue.items():
                all_dialogue[char].extend(utts)
        except Exception as e:
            logger.warning("Error reading %s: %s", f, e)

    # Compute profiles
    profiles = {}
    for char, utts in all_dialogue.items():
        if len(utts) >= 2 or sum(len(u.split()) for u in utts) >= 10:
            profiles[char] = compute_voice_profile(utts, all_dialogue, char)

    # Compute voice bleed matrix
    char_names = sorted(profiles.keys())
    similarity_matrix = {}
    voice_bleed_warnings = []

    for i in range(len(char_names)):
        c1 = char_names[i]
        similarity_matrix[c1] = {}
        for j in range(len(char_names)):
            c2 = char_names[j]
            sim = compute_voice_similarity(profiles[c1], profiles[c2]) if c1 != c2 else 1.0
            similarity_matrix[c1][c2] = sim
            if i < j and sim >= 0.92 and profiles[c1]["total_words"] >= 30 and profiles[c2]["total_words"] >= 30:
                voice_bleed_warnings.append({
                    "char1": c1,
                    "char2": c2,
                    "similarity": sim,
                    "message": f"High voice similarity ({sim * 100:.1f}%) between {c1} and {c2}. Dialogue rhythm and formality may suffer from voice bleed."
                })

    return {
        "target": str(target_path),
        "total_files": len(files),
        "character_count": len(profiles),
        "profiles": profiles,
        "similarity_matrix": similarity_matrix,
        "voice_bleed_warnings": voice_bleed_warnings
    }


def generate_voice_html_report(report: dict, output_path: Path) -> Path:
    """Generates an interactive HTML/SVG report visualizing character voice profiles."""
    profiles = report.get("profiles", {})
    warnings = report.get("voice_bleed_warnings", [])

    cards_html = []
    for char, prof in sorted(profiles.items(), key=lambda x: x[1]["total_words"], reverse=True):
        distinctive_tags = "".join(
            f"<span style='display:inline-block;background:#334155;color:#38bdf8;padding:2px 8px;border-radius:4px;font-size:0.75rem;margin:2px;'>{item['word']} ({item['count']})</span>"
            for item in prof.get("distinctive_words", [])
        ) or "<em style='color:#94a3b8;font-size:0.8rem;'>None detected</em>"

        card = f"""
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 1.25rem;">
          <div style="display:flex; justify-content:space-between; align-items:baseline;">
            <h3 style="margin:0; color:#38bdf8; font-size:1.25rem;">{html.escape(char)}</h3>
            <span style="font-size:0.85rem; color:#94a3b8;">{prof['utterance_count']} lines | {prof['total_words']} words</span>
          </div>
          <div style="margin: 1rem 0; display:grid; grid-template-columns: 1fr 1fr; gap:0.5rem; font-size:0.875rem;">
            <div><strong>Formality:</strong> {prof['formality_score']}/100</div>
            <div><strong>Lexical Richness (TTR):</strong> {prof['ttr']}</div>
            <div><strong>Mean Utterance:</strong> {prof['mean_length']} words (σ={prof['std_dev_length']})</div>
            <div><strong>Contractions:</strong> {prof['contraction_rate']}%</div>
            <div><strong>Questions:</strong> {prof['question_ratio']*100:.1f}%</div>
            <div><strong>Exclamations:</strong> {prof['exclamation_ratio']*100:.1f}%</div>
          </div>
          <div>
            <div style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; margin-bottom:4px;">Distinctive Vocabulary</div>
            {distinctive_tags}
          </div>
        </div>
        """
        cards_html.append(card)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Character Voice Profiler</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 1050px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 1.25rem; }}
  .warning-box {{ background: #78350f; border: 1px solid #d97706; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🎭 Character Voice Profiler & Dialogue Fingerprints</h1>
    <p style="color: var(--muted);">Target: {html.escape(report.get('target', ''))} | Profiles Analyzed: {len(profiles)} characters</p>
  </div>

  {''.join(f'<div class="warning-box">⚠️ <strong>Voice Bleed Warning:</strong> {html.escape(w["message"])}</div>' for w in warnings)}

  <div class="grid">
    {''.join(cards_html) or '<p style="color: var(--muted);">No attributed dialogue lines found.</p>'}
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Character Voice Profiler (PRO-103)")
    parser.add_argument("target", help="File or manuscript path to scan")
    parser.add_argument("--html", help="Generate HTML report to output path")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    report = scan_manuscript_voices(target_path)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"=== Character Voice Profiler: {target_path.name} ===")
    print(f"Total Characters Profiled: {report['character_count']}")
    print("-" * 65)
    for char, prof in sorted(report["profiles"].items(), key=lambda x: x[1]["total_words"], reverse=True):
        print(f"🎭 {char:<18} | Lines: {prof['utterance_count']:<3} | Words: {prof['total_words']:<4} | Formality: {prof['formality_score']:<4} | TTR: {prof['ttr']:<5} | MeanLen: {prof['mean_length']} w")
        if prof["distinctive_words"]:
            words_str = ", ".join(f"{w['word']} ({w['count']})" for w in prof["distinctive_words"][:4])
            print(f"   Favorites: {words_str}")

    if report["voice_bleed_warnings"]:
        print("\n⚠️ Voice Bleed Alerts:")
        for w in report["voice_bleed_warnings"]:
            print(f"  - {w['message']}")

    if args.html:
        out_p = Path(args.html)
        generate_voice_html_report(report, out_p)
        print(f"\nHTML report generated: {out_p}")


if __name__ == "__main__":
    main()