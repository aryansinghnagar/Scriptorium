#!/usr/bin/env python3
"""
Ars Arcanum Earth-Eponym Scanner & Idiom De-Immersion Engine (scripts/lib/idioms.py)
===================================================================================
Zero-dependency, offline manuscript scanner that detects Earth-specific eponyms,
mythological/religious idioms, and real-world flora/fauna clichés that break
narrative immersion in secondary speculative worlds.

Capabilities:
1. Earth-Eponym Scanner (IDM-101):
   - Catches Achilles' heel, Pyrrhic victory, Draconian laws, Spartan, Machiavellian,
     Caesarean, Gordian knot, Stockholm syndrome, Sisyphean, Boycott, Sandwich, Diesel, etc.
2. Earth Mythological & Scriptural Idioms (IDM-102):
   - Catches "by Jove", "devil's advocate", "crossing the Rubicon", "Pandora's box",
     "good Samaritan", "Damocles sword", "Midas touch", "holy grail", etc.
3. Earth-Specific Flora/Fauna Clichés (IDM-103):
   - Catches "canary in a coal mine", "elephant in the room", "red herring",
     "crocodile tears", "barking up the wrong tree", "scapegoat", etc.
4. Whitelist Configuration:
   - Reads global `configs/idioms.json` or `config/idioms.json`.
   - Supports world-level and CLI whitelist overrides.

Zero external dependencies; 100% offline privacy.
"""

import sys
import re
import json
import html
import argparse
import logging
from pathlib import Path

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

logger = logging.getLogger("arcanum.idioms")


def load_idioms_config(custom_config_path: Path = None) -> dict:
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
    config: dict = None,
    custom_whitelist: list = None
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
    parser = argparse.ArgumentParser(description="Ars Arcanum Earth-Eponym Scanner & Idiom De-Immersion Engine")
    parser.add_argument("manuscript", nargs="?", help="Manuscript draft directory")
    parser.add_argument("-m", "--manuscript", dest="ms_flag", help="Manuscript draft directory")
    parser.add_argument("--config", help="Path to custom idioms.json config file")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--html", help="Path to export standalone HTML report")
    parser.add_argument("--whitelist", nargs="+", help="Additional words/phrases to whitelist")

    args = parser.parse_args()

    raw_ms = getattr(args, "ms_flag", None) or getattr(args, "manuscript", None)
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
            print("\033[32m[OK] No Earth-specific eponyms or immersion clichés detected in manuscript.\033[0m\n")
        else:
            for fd in findings:
                print(f"\033[33m[{fd['id']}]\033[0m \033[1m{fd['phrase']}\033[0m ({fd['category']})")
                print(f"  Origin    : {fd['origin']}")
                print(f"  Suggestion: \033[32m{fd['suggestion']}\033[0m")
                print(f"  Location  : {fd['file']}:{fd['line']}")
                print(f"  Snippet   : \"{fd['snippet']}\"\n")

    if args.html:
        out_p = Path(args.html)
        generate_idioms_html_report(audit_data, out_p)
        print(f"Interactive HTML report written to: {out_p}")

    sys.exit(1 if len(findings) > 0 else 0)


if __name__ == "__main__":
    main()
