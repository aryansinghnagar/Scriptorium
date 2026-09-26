#!/usr/bin/env python3
"""
Ars Arcanum Stylistics, Dialogue Mechanics & Readability Rhythm Engine
(scripts/lib/stylistics.py)
================================================================================
Zero-dependency, offline prose linter and stylistic analysis suite for authors.

Capabilities:
1. Dialogue Mechanics (PRO-101):
   - Dialogue tag vs action beat classification
   - Said-bookisms detector (overwrought melodramatic verbs)
   - Adverb-heavy dialogue tag warnings
   - Punctuation and capitalization validation for dialogue quotes
   - Dialogue-to-narrative density ratio
2. Word Echoes (PRO-102):
   - Sliding window lexical repetition detector (configurable 100-500 words)
   - Built-in stopword filtering & morphological stem matching
   - Severity scoring based on proximity and word specificity
3. Readability Rhythm & Sentence Variance (PRO-105):
   - Sentence length distribution (mean, standard deviation, min, max)
   - Staccato rhythm alerts (strings of ultra-short sentences)
   - Monotone cadence alerts (low sentence length variance)
   - Standard readability metrics: Flesch Reading Ease, Flesch-Kincaid Grade,
     Gunning Fog Index, Coleman-Liau Index
4. Standalone HTML/SVG report generation with interactive charts.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import math
import re
import sys
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

logger = logging.getLogger("arcanum.stylistics")

# Comprehensive built-in English stopwords for word echo filtering
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves", "said", "asked", "replied", "answered",
    "thought", "just", "like", "one", "two", "back", "even", "now", "well"
}

# Overwrought said-bookisms to flag
SAID_BOOKISMS = {
    "ejaculated", "opined", "bellowed", "pontificated", "hissed", "snorted",
    "sneered", "barked", "queried", "blurted", "intoned", "vociferated",
    "remonstrated", "expostulated", "gasped", "croaked", "growled", "roared",
    "shrieked", "squeaked", "whined", "whimpered", "babbled", "stammered",
    "sputtered", "interjected", "asseverated", "averred", "ventured", "chortled",
    "guffawed", "simpered", "purred", "brayed", "snickered", "snarled"
}

# Common dialogue-tag adverbs
ADVERB_TAG_PATTERN = re.compile(
    r'\b(said|asked|whispered|shouted|murmured|replied|muttered|cried|screamed)\s+([a-z]+ly)\b',
    re.IGNORECASE
)

# Dialogue matching quotes pattern
DIALOGUE_PATTERN = re.compile(r'["“]([^"”]+)["”]|[\'‘]([^\'’]+)[\'’]')


def _simple_stem(word: str) -> str:
    """Basic morphological stemmer for English echo detection without external dependencies."""
    w = word.lower()
    if len(w) <= 4:
        return w
    for suffix in ("ing", "edly", "fully", "lessly", "ness", "ment", "able", "ible", "ous", "ies", "ied", "ed", "ly", "es", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            return w[:-len(suffix)]
    return w


def count_syllables(word: str) -> int:
    """Estimates syllable count of an English word."""
    w = re.sub(r'[^a-zA-Z]', '', word.lower())
    if not w:
        return 1
    if len(w) <= 3:
        return 1
    w = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', w)
    w = re.sub(r'^y', '', w)
    matches = re.findall(r'[aeiouy]{1,2}', w)
    return max(1, len(matches))


# -----------------------------------------------------------------------------
# PRO-101: Dialogue Mechanics Analyzer
# -----------------------------------------------------------------------------

def analyze_dialogue_mechanics(text: str) -> dict:
    """Analyzes dialogue tags, said-bookisms, adverb tags, and formatting rules."""
    lines = text.splitlines()
    dialogue_quotes = []
    said_bookisms_found = []
    adverb_tags_found = []
    formatting_issues = []
    total_words = 0
    dialogue_words = 0

    for line_num, line in enumerate(lines, 1):
        clean_line = line.strip()
        if not clean_line or clean_line.startswith(("@", "#", "---")):
            continue

        words = re.findall(r'\b\w+\b', clean_line)
        total_words += len(words)

        # Find quotes in line
        for match in re.finditer(r'["“]([^"”]+)["”]|[\'‘]([^\'’]+)[\'’]', clean_line):
            quote_text = match.group(1) or match.group(2) or ""
            q_words = re.findall(r'\b\w+\b', quote_text)
            dialogue_words += len(q_words)
            dialogue_quotes.append({
                "line": line_num,
                "text": quote_text,
                "word_count": len(q_words)
            })

            # Check punctuation inside quote boundary
            end_match = match.end()
            trailing = clean_line[end_match:end_match + 40]
            tag_match = re.match(r'^\s*([a-zA-Z]+)', trailing)
            if tag_match:
                tag_word = tag_match.group(1)
                # Check lowercase tag with period quote: "Hello." said John.
                if quote_text.rstrip().endswith(".") and tag_word[0].islower():
                    formatting_issues.append({
                        "line": line_num,
                        "type": "period_before_tag",
                        "message": f'Dialogue ending with period followed by lowercase tag "{tag_word}". Prefer comma inside quote: "...," {tag_word}',
                        "context": clean_line
                    })
                # Check capitalized pronoun with comma: "Hello," He said.
                if quote_text.rstrip().endswith(",") and tag_word in ("He", "She", "They", "It", "We", "I"):
                    formatting_issues.append({
                        "line": line_num,
                        "type": "capitalized_tag_pronoun",
                        "message": f'Dialogue tag pronoun "{tag_word}" is capitalized after comma. Prefer lowercase "{tag_word.lower()}".',
                        "context": clean_line
                    })

        # Check for said-bookisms in narrative tags
        for word in words:
            w_lower = word.lower()
            if w_lower in SAID_BOOKISMS:
                said_bookisms_found.append({
                    "line": line_num,
                    "word": word,
                    "context": clean_line
                })

        # Check for adverb-heavy tags
        for adv_m in ADVERB_TAG_PATTERN.finditer(clean_line):
            verb = adv_m.group(1)
            adverb = adv_m.group(2)
            adverb_tags_found.append({
                "line": line_num,
                "tag": f"{verb} {adverb}",
                "adverb": adverb,
                "context": clean_line
            })

    narrative_words = max(0, total_words - dialogue_words)
    dialogue_ratio = (dialogue_words / total_words) if total_words > 0 else 0.0

    return {
        "total_words": total_words,
        "dialogue_words": dialogue_words,
        "narrative_words": narrative_words,
        "dialogue_ratio": round(dialogue_ratio, 3),
        "quote_count": len(dialogue_quotes),
        "said_bookisms": said_bookisms_found,
        "said_bookisms_count": len(said_bookisms_found),
        "adverb_tags": adverb_tags_found,
        "adverb_tags_count": len(adverb_tags_found),
        "formatting_issues": formatting_issues,
        "formatting_issues_count": len(formatting_issues)
    }


# -----------------------------------------------------------------------------
# PRO-102: Word Echoes Analyzer (Sliding Window Repetition Detector)
# -----------------------------------------------------------------------------

def analyze_word_echoes(text: str, window_size: int = 300, min_word_len: int = 4) -> dict:
    """Detects closely repeated significant words (echoes) within a sliding word window."""
    lines = text.splitlines()
    word_tokens = []

    pos = 0
    for line_num, line in enumerate(lines, 1):
        clean_line = line.strip()
        if not clean_line or clean_line.startswith(("@", "#", "---")):
            continue
        for m in re.finditer(r'\b[A-Za-z]+\b', clean_line):
            raw_word = m.group(0)
            w_lower = raw_word.lower()
            if len(w_lower) >= min_word_len and w_lower not in STOPWORDS:
                stem = _simple_stem(w_lower)
                word_tokens.append({
                    "word": raw_word,
                    "lower": w_lower,
                    "stem": stem,
                    "line": line_num,
                    "pos": pos,
                    "context": clean_line
                })
            pos += 1

    echoes = []
    stem_last_seen = {}

    for token in word_tokens:
        stem = token["stem"]
        if stem in stem_last_seen:
            prev_token = stem_last_seen[stem]
            dist = token["pos"] - prev_token["pos"]
            if dist <= window_size:
                severity = "high" if dist < 50 else ("medium" if dist < 150 else "low")
                echoes.append({
                    "word": token["word"],
                    "prev_word": prev_token["word"],
                    "stem": stem,
                    "distance_words": dist,
                    "line": token["line"],
                    "prev_line": prev_token["line"],
                    "severity": severity,
                    "context": token["context"],
                    "prev_context": prev_token["context"]
                })
        stem_last_seen[stem] = token

    return {
        "total_analyzed_tokens": len(word_tokens),
        "window_size": window_size,
        "echo_count": len(echoes),
        "echoes": echoes
    }


# -----------------------------------------------------------------------------
# PRO-105: Readability Rhythm & Sentence Variance
# -----------------------------------------------------------------------------

def analyze_readability_rhythm(text: str) -> dict:
    """Calculates sentence lengths, rhythm standard deviation, and readability formulas."""
    clean_text = re.sub(r'^\s*[@#\-].*$', '', text, flags=re.MULTILINE)
    raw_sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    sentences = [s.strip() for s in raw_sentences if s.strip() and len(re.findall(r'\b\w+\b', s)) > 0]

    sentence_lengths = []
    total_syllables = 0
    total_words = 0
    total_letters = 0
    complex_words = 0

    for s in sentences:
        words = re.findall(r'\b[A-Za-z]+\b', s)
        w_count = len(words)
        sentence_lengths.append(w_count)
        total_words += w_count
        for w in words:
            total_letters += len(w)
            syl = count_syllables(w)
            total_syllables += syl
            if syl >= 3:
                complex_words += 1

    if not sentence_lengths:
        return {
            "sentence_count": 0,
            "word_count": 0,
            "mean_sentence_length": 0.0,
            "std_deviation": 0.0,
            "min_length": 0,
            "max_length": 0,
            "sentence_lengths": [],
            "staccato_clusters": [],
            "monotone_alerts": [],
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "gunning_fog_index": 0.0,
            "coleman_liau_index": 0.0
        }

    n_sentences = len(sentence_lengths)
    mean_len = total_words / n_sentences
    variance = sum((slen - mean_len) ** 2 for slen in sentence_lengths) / n_sentences
    std_dev = math.sqrt(variance)

    # Detect staccato strings (3+ consecutive sentences under 6 words)
    staccato_clusters = []
    streak = []
    for idx, slen in enumerate(sentence_lengths):
        if slen <= 6:
            streak.append(idx + 1)
        else:
            if len(streak) >= 3:
                staccato_clusters.append({
                    "start_sentence": streak[0],
                    "end_sentence": streak[-1],
                    "count": len(streak),
                    "snippet": " / ".join(sentences[i - 1] for i in streak[:3])
                })
            streak = []
    if len(streak) >= 3:
        staccato_clusters.append({
            "start_sentence": streak[0],
            "end_sentence": streak[-1],
            "count": len(streak),
            "snippet": " / ".join(sentences[i - 1] for i in streak[:3])
        })

    monotone_alerts = []
    if n_sentences >= 10 and std_dev < 3.5:
        monotone_alerts.append({
            "type": "low_variance",
            "message": f"Low sentence length variance (σ = {std_dev:.2f}). Prose rhythm may feel monotonous.",
            "std_dev": round(std_dev, 2)
        })

    asl = mean_len
    asw = (total_syllables / total_words) if total_words > 0 else 1.0
    l_100 = (total_letters / total_words * 100) if total_words > 0 else 0
    s_100 = (n_sentences / total_words * 100) if total_words > 0 else 0

    flesch_ease = 206.835 - (1.015 * asl) - (84.6 * asw)
    flesch_kincaid = (0.39 * asl) + (11.8 * asw) - 15.59
    gunning_fog = 0.4 * (asl + (100.0 * complex_words / total_words if total_words > 0 else 0))
    coleman_liau = (0.0588 * l_100) - (0.296 * s_100) - 15.8

    warning = None
    if total_words < 100:
        warning = "Sample contains fewer than 100 words. Readability metrics may be statistically noisy."

    return {
        "sentence_count": n_sentences,
        "word_count": total_words,
        "mean_sentence_length": round(mean_len, 2),
        "std_deviation": round(std_dev, 2),
        "min_length": min(sentence_lengths),
        "max_length": max(sentence_lengths),
        "sentence_lengths": sentence_lengths,
        "staccato_clusters": staccato_clusters,
        "monotone_alerts": monotone_alerts,
        "sample_size_warning": warning,
        "flesch_reading_ease": round(max(0.0, flesch_ease), 1),
        "flesch_kincaid_grade": round(max(0.0, flesch_kincaid), 1),
        "gunning_fog_index": round(max(0.0, gunning_fog), 1),
        "coleman_liau_index": round(max(0.0, coleman_liau), 1)
    }


# -----------------------------------------------------------------------------
# Full Prose Scan & Report Generation
# -----------------------------------------------------------------------------

def scan_text_or_path(target_path: Path) -> dict:
    """Scans a file or entire manuscript directory for stylistics, dialogue, and echoes."""
    files = []
    if target_path.is_file():
        files.append(target_path)
    elif target_path.is_dir():
        for p in sorted(target_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "Backups" not in p.parts:
                files.append(p)
    else:
        raise FileNotFoundError(f"Target not found: {target_path}")

    combined_text = ""
    file_reports = []

    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            combined_text += f"\n\n# {f.name}\n" + content
            dialogue = analyze_dialogue_mechanics(content)
            echoes = analyze_word_echoes(content)
            rhythm = analyze_readability_rhythm(content)
            file_reports.append({
                "file": str(f),
                "name": f.name,
                "dialogue": dialogue,
                "echoes": echoes,
                "rhythm": rhythm
            })
        except Exception as e:
            logger.warning("Error analyzing %s: %s", f, e)

    overall_dialogue = analyze_dialogue_mechanics(combined_text)
    overall_echoes = analyze_word_echoes(combined_text)
    overall_rhythm = analyze_readability_rhythm(combined_text)

    return {
        "target": str(target_path),
        "total_files": len(files),
        "overall": {
            "dialogue": overall_dialogue,
            "echoes": overall_echoes,
            "rhythm": overall_rhythm
        },
        "files": file_reports
    }


def generate_stylistics_html_report(report: dict, output_path: Path) -> Path:
    """Generates an offline, interactive HTML report with embedded SVG charts."""
    overall = report.get("overall", {})
    dia = overall.get("dialogue", {})
    ech = overall.get("echoes", {})
    rhy = overall.get("rhythm", {})

    lengths = rhy.get("sentence_lengths", [])[:80]
    svg_bars = []
    if lengths:
        max_h = max(lengths) if max(lengths) > 0 else 1
        w_bar = max(4, int(700 / len(lengths)))
        for i, length_val in enumerate(lengths):
            h_norm = int((length_val / max_h) * 120)
            x = i * (w_bar + 2)
            y = 130 - h_norm
            color = "#ef4444" if length_val <= 5 else ("#3b82f6" if length_val <= 25 else "#f59e0b")
            svg_bars.append(f'<rect x="{x}" y="{y}" width="{w_bar}" height="{h_norm}" fill="{color}" rx="2"><title>Sentence {i+1}: {length_val} words</title></rect>')

    svg_content = "\n".join(svg_bars)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Stylistics & Prose Craft Report</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444; --success: #10b981;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 1000px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .section {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
  h2 {{ color: var(--accent); margin-top: 0; }}
  .table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  .table th, .table td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid var(--border); }}
  .badge {{ display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
  .badge-high {{ background: #7f1d1d; color: #fecaca; }}
  .badge-med {{ background: #78350f; color: #fde68a; }}
  .badge-low {{ background: #1e3a8a; color: #bfdbfe; }}
  .chart-box {{ overflow-x: auto; padding: 1rem 0; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>✍️ Stylistics, Dialogue Mechanics & Readability Report</h1>
    <p style="color: var(--muted);">Target: {html.escape(report.get('target', ''))} | Total Files: {report.get('total_files', 0)}</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Dialogue Ratio</h3>
      <div class="metric">{dia.get('dialogue_ratio', 0) * 100:.1f}%</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">{dia.get('dialogue_words', 0):,} dialogue / {dia.get('total_words', 0):,} total</p>
    </div>
    <div class="card">
      <h3>Sentence Variance (σ)</h3>
      <div class="metric">σ = {rhy.get('std_deviation', 0):.1f}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Mean length: {rhy.get('mean_sentence_length', 0)} words</p>
    </div>
    <div class="card">
      <h3>Reading Grade</h3>
      <div class="metric">Gr {rhy.get('flesch_kincaid_grade', 0)}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Flesch: {rhy.get('flesch_reading_ease', 0)} / 100</p>
    </div>
    <div class="card">
      <h3>Word Echoes</h3>
      <div class="metric" style="color: {'var(--danger)' if ech.get('echo_count', 0) > 10 else 'var(--success)'};">{ech.get('echo_count', 0)}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Within {ech.get('window_size', 300)} words</p>
    </div>
  </div>

  <div class="section">
    <h2>🎵 Sentence Rhythm & Cadence Map</h2>
    <p style="color: var(--muted);">Visualization of consecutive sentence lengths (Red: ≤5 words, Blue: 6-25 words, Amber: >25 words):</p>
    <div class="chart-box">
      <svg width="720" height="140" style="background: #0f172a; border-radius: 6px; padding: 10px;">
        {svg_content}
      </svg>
    </div>
    {'<p style="color: var(--warn);">⚠️ ' + html.escape(rhy["monotone_alerts"][0]["message"]) + '</p>' if rhy.get("monotone_alerts") else ''}
  </div>

  <div class="section">
    <h2>💬 Dialogue Tags & Said-Bookisms ({dia.get('said_bookisms_count', 0)} detected)</h2>
    <table class="table">
      <thead><tr><th>Line</th><th>Term / Tag</th><th>Context</th></tr></thead>
      <tbody>
        {''.join(f"<tr><td>{item['line']}</td><td><span class='badge badge-high'>{html.escape(item['word'])}</span></td><td><code>{html.escape(item['context'])}</code></td></tr>" for item in dia.get('said_bookisms', [])[:15]) or '<tr><td colspan="3" style="color: var(--muted);">No overwrought said-bookisms detected.</td></tr>'}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>🔁 Lexical Echoes ({ech.get('echo_count', 0)} instances)</h2>
    <table class="table">
      <thead><tr><th>Word</th><th>Distance</th><th>Severity</th><th>Context Lines</th></tr></thead>
      <tbody>
        {''.join(f"<tr><td><strong>{html.escape(item['word'])}</strong></td><td>{item['distance_words']} words</td><td><span class='badge badge-{item['severity']}'>{item['severity']}</span></td><td>Line {item['prev_line']} → Line {item['line']}</td></tr>" for item in ech.get('echoes', [])[:20]) or '<tr><td colspan="4" style="color: var(--muted);">No close word echoes detected.</td></tr>'}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


# -----------------------------------------------------------------------------
# CLI Entrypoint
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Stylistics & Prose Linter")
    subparsers = parser.add_subparsers(dest="command", help="Analysis mode")

    # scan
    p_scan = subparsers.add_parser("scan", help="Complete stylistics, dialogue & echo scan")
    p_scan.add_argument("target", help="File or manuscript directory path")
    p_scan.add_argument("--html", help="Generate HTML report to path")
    p_scan.add_argument("--json", action="store_true", help="Output JSON results")

    # dialogue
    p_dia = subparsers.add_parser("dialogue", help="Dialogue mechanics and tag analysis")
    p_dia.add_argument("target", help="File or manuscript path")
    p_dia.add_argument("--json", action="store_true", help="Output JSON results")

    # echoes
    p_ech = subparsers.add_parser("echoes", help="Word echo repetition detection")
    p_ech.add_argument("target", help="File or manuscript path")
    p_ech.add_argument("--window", type=int, default=300, help="Sliding window size in words (default 300)")
    p_ech.add_argument("--json", action="store_true", help="Output JSON results")

    # rhythm
    p_rhy = subparsers.add_parser("rhythm", help="Sentence variance and readability rhythm")
    p_rhy.add_argument("target", help="File or manuscript path")
    p_rhy.add_argument("--json", action="store_true", help="Output JSON results")

        # idiom
    p_idiom = subparsers.add_parser("idiom", help="Earth-Eponym Scanner & Idiom De-Immersion Engine")
    p_idiom.add_argument("target", help="File or manuscript path", nargs="?")
    p_idiom.add_argument("-m", "--manuscript", dest="ms_flag", help="Manuscript draft directory")
    p_idiom.add_argument("--config", help="Path to custom idioms.json config file")
    p_idiom.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_idiom.add_argument("--html", help="Path to export standalone HTML report")
    p_idiom.add_argument("--whitelist", nargs="+", help="Additional words/phrases to whitelist")

    args = parser.parse_args()

    if not args.command:
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            target = Path(sys.argv[1])
            res = scan_text_or_path(target)
            print(f"=== Stylistics & Prose Report: {target.name} ===")
            ov = res["overall"]
            print(f"Total Words: {ov['dialogue']['total_words']:,} | Dialogue: {ov['dialogue']['dialogue_ratio']*100:.1f}%")
            print(f"Sentence Length: {ov['rhythm']['mean_sentence_length']} words (σ = {ov['rhythm']['std_deviation']})")
            print(f"Reading Ease: {ov['rhythm']['flesch_reading_ease']} | Grade: {ov['rhythm']['flesch_kincaid_grade']}")
            print(f"Said-Bookisms: {ov['dialogue']['said_bookisms_count']} | Adverb Tags: {ov['dialogue']['adverb_tags_count']}")
            print(f"Word Echoes: {ov['echoes']['echo_count']} (within 300 words)")
            sys.exit(0)
        parser.print_help()
        sys.exit(0)

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    if args.command == "dialogue":
        report = scan_text_or_path(target_path)
        d = report["overall"]["dialogue"]
        if getattr(args, "json", False):
            print(json.dumps(d, indent=2))
        else:
            print(f"=== Dialogue Mechanics: {target_path.name} ===")
            print(f"Dialogue Words: {d['dialogue_words']:,} / {d['total_words']:,} ({d['dialogue_ratio']*100:.1f}%)")
            print(f"Said-Bookisms: {d['said_bookisms_count']}")
            for sb in d['said_bookisms'][:10]:
                print(f"  Line {sb['line']}: '{sb['word']}' in {sb['context'][:60]}...")
            print(f"Adverb Tags: {d['adverb_tags_count']}")
            for adv in d['adverb_tags'][:10]:
                print(f"  Line {adv['line']}: '{adv['tag']}'")
            print(f"Formatting Issues: {d['formatting_issues_count']}")
            for fi in d['formatting_issues'][:10]:
                print(f"  Line {fi['line']}: {fi['message']}")

    elif args.command == "echoes":
        win = getattr(args, "window", 300)
        report = scan_text_or_path(target_path)
        e = report["overall"]["echoes"]
        if getattr(args, "json", False):
            print(json.dumps(e, indent=2))
        else:
            print(f"=== Word Echoes Scanner (Window: {win} words): {target_path.name} ===")
            print(f"Total Echoes Detected: {e['echo_count']}")
            for echo in e['echoes'][:15]:
                print(f"  [{echo['severity'].upper()}] '{echo['word']}' repeated {echo['distance_words']} words apart (Line {echo['prev_line']} -> Line {echo['line']})")

    elif args.command == "rhythm":
        report = scan_text_or_path(target_path)
        r = report["overall"]["rhythm"]
        if getattr(args, "json", False):
            print(json.dumps(r, indent=2))
        else:
            print(f"=== Readability Rhythm & Variance: {target_path.name} ===")
            print(f"Sentences: {r['sentence_count']} | Mean Length: {r['mean_sentence_length']} words | StdDev: σ = {r['std_deviation']}")
            print(f"Flesch Reading Ease: {r['flesch_reading_ease']} / 100")
            print(f"Flesch-Kincaid Grade: {r['flesch_kincaid_grade']}")
            print(f"Gunning Fog Index: {r['gunning_fog_index']}")
            print(f"Coleman-Liau Index: {r['coleman_liau_index']}")
            if r['staccato_clusters']:
                print(f"Staccato Clusters (Strings of <=5 word sentences): {len(r['staccato_clusters'])}")
                for sc in r['staccato_clusters'][:3]:
                    print(f"  Sentences {sc['start_sentence']}-{sc['end_sentence']}: {sc['snippet'][:70]}...")

    elif args.command == "idiom":
        raw_ms = getattr(args, "ms_flag", None) or getattr(args, "target", None)
        ms_dir_str = resolve_manuscript_dir(raw_ms)
        if not ms_dir_str or not Path(ms_dir_str).is_dir():
            print("Error: No valid Manuscript directory specified or discovered.", file=sys.stderr)
            sys.exit(2)

        ms_path = Path(ms_dir_str)
        cfg = load_idioms_config(Path(args.config) if args.config else None)
        findings = audit_manuscript_idioms(ms_path, config=cfg, custom_whitelist=args.whitelist)

        audit_data = {
            "manuscript": ms_path.name,
            "findings_count": len(findings),
            "findings": findings,
        }

        if args.json:
            print(json.dumps(audit_data, indent=2))
        else:
            print("\n\033[1;36m=== Ars Arcanum Earth Idiom & Immersion Audit ===\033[0m")
            print(f"Manuscript: \033[1m{ms_path.name}\033[0m | Potential Immersion Leaks: \033[1m{len(findings)}\033[0m\n")

            if not findings:
                print("\033[32m[OK] No Earth-specific eponyms or immersion clichéss detected in manuscript.\033[0m\n")
            else:
                for fd in findings:
                    print(f"\033[33m[{fd['id']}]\033[0m \033[1m{fd['phrase']}\033[0m ({fd['category']})")
                    print(f"  Origin    : {fd['origin']}")
                    print(f"  Suggestion: \033[32m{fd['suggestion']}\033[0m")
                    print(f"  Location  : {fd['file']}:{fd['line']}")
                    print(f"  Snippet   : \\\"{fd['snippet']}\\\"\\n")

        if args.html:
            out_p = Path(args.html)
            generate_idioms_html_report(audit_data, out_p)
            print(f"Interactive HTML report written to: {out_p}")

        sys.exit(1 if len(findings) > 0 else 0)

    elif args.command == "scan":
        report = scan_text_or_path(target_path)
        if getattr(args, "json", False):
            print(json.dumps(report, indent=2))
        else:
            ov = report["overall"]
            print(f"=== Stylistics & Prose Craft Analysis: {target_path.name} ===")
            print(f"Total Words: {ov['dialogue']['total_words']:,}")
            print(f"Dialogue: {ov['dialogue']['dialogue_ratio']*100:.1f}% | Narrative: {(1-ov['dialogue']['dialogue_ratio'])*100:.1f}%")
            print(f"Rhythm: Mean {ov['rhythm']['mean_sentence_length']} w/sent | σ = {ov['rhythm']['std_deviation']}")
            print(f"Readability: Flesch-Kincaid Gr {ov['rhythm']['flesch_kincaid_grade']} | Flesch Ease {ov['rhythm']['flesch_reading_ease']}")
            print(f"Echoes: {ov['echoes']['echo_count']} | Said-Bookisms: {ov['dialogue']['said_bookisms_count']}")
        if args.html:
            out_p = Path(args.html)
            generate_stylistics_html_report(report, out_p)
            print(f"HTML report written to: {out_p}")


if __name__ == "__main__":
    main()


# --- Idioms Integration ---



def load_idioms_config(custom_config_path: Path | None = None) -> dict:
    """Loads default idioms dictionary or custom configuration."""
    candidates = []
    if custom_config_path:
        candidates.append(Path(custom_config_path))
    
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    candidates.extend([
        repo_root / "configs" / "idioms.json",
        repo_root / "config" / "idioms.json",
        script_dir.parent / "configs" / "idioms.json",
    ])

    for c in candidates:
        if c.is_file():
            try:
                return json.loads(c.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning("Failed to parse %s: %s", c, e)

    # Built-in fallback
    return {
        "eponyms": {
            "achilles heel": {"origin": "Greek Hero Achilles", "suggestion": "vulnerable spot / mortal weakness"},
            "achilles' heel": {"origin": "Greek Hero Achilles", "suggestion": "vulnerable spot / mortal weakness"},
            "pyrrhic": {"origin": "King Pyrrhus of Epirus", "suggestion": "ruinous victory / costly triumph"},
            "draconian": {"origin": "Athenian Lawgiver Draco", "suggestion": "harsh / ruthless / merciless"},
            "spartan": {"origin": "City-state of Sparta", "suggestion": "austere / disciplined / bare"},
            "machiavellian": {"origin": "Niccolò Machiavelli", "suggestion": "cunning / scheming / duplicitous"},
            "caesarean": {"origin": "Julius Caesar", "suggestion": "surgical extraction / surgical birth"},
            "gordian knot": {"origin": "King Gordias of Phrygia", "suggestion": "insoluble tangle / intricate knot"},
            "trojan horse": {"origin": "Trojan War / Homer", "suggestion": "covert infiltrator / subterfuge gift"},
            "stockholm syndrome": {"origin": "Stockholm 1973 Bank Siege", "suggestion": "captor bond / hostage sympathy"},
            "sisyphean": {"origin": "Myth of Sisyphus", "suggestion": "futile labor / endless toil"},
            "tantalizing": {"origin": "Myth of Tantalus", "suggestion": "enticing / tormenting / just out of reach"},
            "boycott": {"origin": "Captain Charles Boycott", "suggestion": "embargo / shun / ostracize"},
            "sandwich": {"origin": "4th Earl of Sandwich", "suggestion": "filled loaf / layered bread"},
            "diesel": {"origin": "Rudolf Diesel", "suggestion": "heavy fuel / compression engine"},
        },
        "mythological_religious": {
            "by jove": {"origin": "Roman God Jupiter/Jove", "suggestion": "by the gods / by the heavens"},
            "devil's advocate": {"origin": "Catholic Canon Law Advocatus Diaboli", "suggestion": "contrarian stance / opposing argument"},
            "crossing the rubicon": {"origin": "Julius Caesar 49 BCE", "suggestion": "crossing the point of no return"},
            "pandora's box": {"origin": "Greek Hesiod Myth", "suggestion": "forbidden casket / unleashed curse"},
            "good samaritan": {"origin": "Parable in Gospel of Luke", "suggestion": "kind stranger / charitable traveler"},
            "damocles": {"origin": "Sword of Damocles", "suggestion": "impending doom / hanging blade"},
            "midas touch": {"origin": "King Midas", "suggestion": "golden touch / effortless wealth"},
            "holy grail": {"origin": "Arthurian Legend", "suggestion": "ultimate prize / supreme artifact"},
        },
        "flora_fauna_cliches": {
            "canary in a coal mine": {"origin": "British Mining Practice", "suggestion": "early warning sign / vanguard harbinger"},
            "elephant in the room": {"origin": "Earth Mega-Fauna Idiom", "suggestion": "unspoken truth / unavoidable reality"},
            "red herring": {"origin": "Earth Cured Fish Metaphor", "suggestion": "false trail / misleading decoy"},
            "scapegoat": {"origin": "Leviticus Ritual", "suggestion": "fall guy / blamed innocent"},
            "crocodile tears": {"origin": "Medieval Bestiary Myth", "suggestion": "feigned sorrow / false tears"},
            "barking up the wrong tree": {"origin": "American Raccoon Hunting", "suggestion": "following the wrong lead / misplaced suspicion"},
        },
        "whitelist": []
    }


def audit_manuscript_idioms(
    manuscript_dir: Path,
    config: dict | None = None,
    custom_whitelist: list | None = None
) -> list:
    """Scans all manuscript scenes for immersion-breaking idioms and eponyms."""
    findings = []
    if not manuscript_dir or not manuscript_dir.is_dir():
        return findings

    cfg = config or load_idioms_config()
    whitelist = set([str(w).lower().strip() for w in cfg.get("whitelist", [])])
    if custom_whitelist:
        for w in custom_whitelist:
            whitelist.add(str(w).lower().strip())

    categories = [
        ("eponyms", "IDM-101", "Earth-Specific Eponym"),
        ("mythological_religious", "IDM-102", "Earth Mythological / Scriptural Reference"),
        ("flora_fauna_cliches", "IDM-103", "Earth Flora / Fauna De-Immersion Cliché"),
    ]

    for md_file in sorted(manuscript_dir.rglob("*.md")):
        if md_file.name.startswith(".") or "Front_Matter" in md_file.parts or "Back_Matter" in md_file.parts:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            for line_idx, line in enumerate(lines, start=1):
                # Skip comments or metadata tag lines
                if line.strip().startswith("@") or line.strip().startswith("<!--"):
                    continue

                line_lower = line.lower()

                for cat_key, rule_id, rule_label in categories:
                    items = cfg.get(cat_key, {})
                    for phrase, meta in items.items():
                        phrase_lower = phrase.lower()
                        if phrase_lower in whitelist:
                            continue

                        # Match with word boundaries
                        pattern = r"\b" + re.escape(phrase_lower) + r"\b"
                        if re.search(pattern, line_lower):
                            findings.append({
                                "id": rule_id,
                                "category": rule_label,
                                "severity": "WARNING",
                                "phrase": phrase,
                                "origin": meta.get("origin", "Earth Cultural History"),
                                "suggestion": meta.get("suggestion", "Use in-world equivalent"),
                                "message": f"{rule_label}: '{phrase}' detected (Origin: {meta.get('origin', '')}). Suggestion: {meta.get('suggestion', '')}",
                                "file": str(md_file.relative_to(manuscript_dir)),
                                "line": line_idx,
                                "snippet": line.strip(),
                            })
        except Exception as e:
            logger.warning("Failed to scan %s: %s", md_file, e)

    return findings


def generate_idioms_html_report(audit_data: dict, output_path: Path):
    """Generates standalone HTML report for Idioms and De-Immersion audit."""
    findings = audit_data.get("findings", [])
    ms_name = audit_data.get("manuscript", "Manuscript")

    findings_cards = []
    for fd in findings:
        findings_cards.append(f"""
        <div class="card finding-card">
            <span class="badge badge-warning">{html.escape(fd.get('id', 'IDM-101'))}</span>
            <strong>{html.escape(fd.get('phrase', ''))}</strong> — <span style="color: #94a3b8;">{html.escape(fd.get('category', ''))}</span>
            <p style="margin: 0.5rem 0;"><em>"{html.escape(fd.get('snippet', ''))}"</em></p>
            <p style="margin: 0; font-size: 0.9em; color: #38bdf8;">
                <strong>Origin:</strong> {html.escape(fd.get('origin', ''))} | 
                <strong>Suggestion:</strong> {html.escape(fd.get('suggestion', ''))}
            </p>
            <div style="font-size: 0.8em; color: #64748b; margin-top: 4px;">File: {html.escape(fd.get('file', ''))}:{fd.get('line', '')}</div>
        </div>
        """)

    findings_html = "".join(findings_cards) if findings_cards else "<div style='color: #4ade80;'>✓ No Earth eponyms or de-immersion clichés detected in manuscript.</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Earth Idiom & Immersion Audit ({html.escape(ms_name)})</title>
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
  .container {{ max-width: 1000px; margin: 0 auto; }}
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
  .finding-card {{ margin-bottom: 1rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>🌍 Ars Arcanum Idiom & Immersion Audit</h1>
  <p>Manuscript: <strong>{html.escape(ms_name)}</strong> | Total Leaks Found: <strong>{len(findings)}</strong></p>

  <div class="card">
    <h2>Immersion Leaks & Eponym Findings</h2>
    {findings_html}
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)


def resolve_manuscript_dir(target_str: str | None = None) -> str:
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


