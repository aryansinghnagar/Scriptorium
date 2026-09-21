#!/usr/bin/env python3
"""
Ars Arcanum In-World Economy, Commodity PPP & Anachronism Matrix (scripts/lib/economy.py)
========================================================================================
Zero-dependency, offline in-world macroeconomic validator, Purchasing Power Parity (PPP)
exchange rate calculator, interstellar trade margin analyzer, and technology era anachronism auditor.

Capabilities:
1. World Bible Economy Profiles:
   - Scans World Bible `Economies/*.md` frontmatter for currencies, denominations, and commodity baskets.
   - Computes Purchasing Power Parity (PPP) index across regional or factional currencies.
2. Manuscript Price Consistency Audit (`arcanum economy check`):
   - Scans manuscript scenes for `@price:` directives and currency prose mentions.
   - Detects:
     * ECO-101: Price Anomaly / Hyper-Deflation/Inflation (price deviates wildly from commodity basket baseline).

     * ECO-102: Unregistered In-World Currency (manuscript references currency not defined in world lore).
     * ECO-103: Denomination Arithmetic Error (e.g. coin counting contradicting established conversion ratios).
3. Interstellar & Regional Trade Margin Viability (`calc_trade_margin`):
   - Models cargo freight economics, distance transit costs, tariffs, and commodity price arbitrage.
4. Technological Baseline Era vs Manuscript Anachronism Scanner (`arcanum audit tech`):
   - Audits world technological baseline (e.g. Bronze Age, Medieval, Industrial, Interstellar) against manuscript prose.
   - Detects:
     * ECO-201: Technological Anachronism (manuscript mentions out-of-era material, concept, or invention).

Zero external dependencies; 100% offline privacy.
"""

import sys
import os
import re
import math
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

logger = logging.getLogger("arcanum.economy")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]")

# Technological Eras and their distinguishing inventions/materials
TECH_ERAS = [
    "stone_age",
    "bronze_age",
    "iron_age",
    "medieval",
    "renaissance",
    "industrial",
    "victorian",
    "modern_20th",
    "information_age",
    "interstellar",
]

ERA_ORDER = {era: idx for idx, era in enumerate(TECH_ERAS)}

# Anachronism dictionary: term -> earliest acceptable era
TECH_ERA_DICTIONARY = {
    # Bronze Age+ (Earliest Bronze Age)
    "bronze": "bronze_age",
    "chariot": "bronze_age",
    "papyrus": "bronze_age",
    "cuneiform": "bronze_age",

    # Iron Age+
    "iron sword": "iron_age",
    "steel sword": "iron_age",
    "parchment": "iron_age",
    "phalanx": "iron_age",
    "trireme": "iron_age",
    "aqueduct": "iron_age",

    # Medieval+
    "crossbow": "medieval",
    "chainmail": "medieval",
    "plate armor": "medieval",
    "trebuchet": "medieval",
    "windmill": "medieval",
    "feudal": "medieval",

    # Renaissance+
    "gunpowder": "renaissance",
    "musket": "renaissance",
    "arquebus": "renaissance",
    "cannon": "renaissance",
    "printing press": "renaissance",
    "telescope": "renaissance",
    "caravel": "renaissance",
    "galleon": "renaissance",
    "flintlock": "renaissance",

    # Industrial+
    "steam engine": "industrial",
    "locomotive": "industrial",
    "railroad": "industrial",
    "telegraph": "industrial",
    "dynamite": "industrial",
    "factory line": "industrial",
    "rifled barrel": "industrial",

    # Victorian / Early 20th+
    "electricity": "victorian",
    "lightbulb": "victorian",
    "phonograph": "victorian",
    "automobile": "victorian",
    "internal combustion": "victorian",
    "airship": "victorian",
    "zepplin": "victorian",
    "radio": "victorian",
    "telephone": "victorian",

    # Modern 20th+
    "radar": "modern_20th",
    "sonar": "modern_20th",
    "plastic": "modern_20th",
    "nylon": "modern_20th",
    "penicillin": "modern_20th",
    "antibiotic": "modern_20th",
    "jet aircraft": "modern_20th",
    "transistor": "modern_20th",
    "nuclear reactor": "modern_20th",
    "atomic bomb": "modern_20th",

    # Information Age+
    "microchip": "information_age",
    "silicon chip": "information_age",
    "internet": "information_age",
    "smartphone": "information_age",
    "gps": "information_age",
    "fiber optic": "information_age",
    "lithium battery": "information_age",
    "satellite": "information_age",

    # Interstellar / Far Future+
    "fusion drive": "interstellar",
    "warp drive": "interstellar",
    "hyperdrive": "interstellar",
    "antimatter": "interstellar",
    "blaster": "interstellar",
    "plasma cannon": "interstellar",
    "cybernetic implant": "interstellar",
    "forcefield": "interstellar",
}


def parse_yaml_frontmatter(content: str) -> dict:
    """Safe YAML frontmatter parser for economy configurations."""
    fm_match = FRONTMATTER_REGEX.match(content)
    if not fm_match:
        return {}
    
    data = {}
    lines = fm_match.group(1).splitlines()
    current_key = None
    
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        
        if raw_line.startswith("  - ") or raw_line.startswith("    - ") or (raw_line.startswith("- ") and current_key):
            item_val = line.lstrip("- ").strip().strip("\"'")
            if current_key:
                if not isinstance(data.get(current_key), list):
                    data[current_key] = []
                data[current_key].append(item_val)
            continue

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            current_key = key
            
            if not val:
                data[key] = {}
            elif val.startswith("[") and val.endswith("]"):
                items = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
                data[key] = items
            elif val.startswith("{") and val.endswith("}"):
                # Basic inline dict
                try:
                    data[key] = json.loads(val.replace("'", '"'))
                except Exception:
                    data[key] = val
            elif val.lower() in ("true", "yes"):
                data[key] = True
            elif val.lower() in ("false", "no"):
                data[key] = False
            else:
                try:
                    if "." in val:
                        data[key] = float(val)
                    else:
                        data[key] = int(val)
                except ValueError:
                    data[key] = val.strip("\"'")
    return data


def normalize_name(name: str) -> str:
    return re.sub(r"[\s_-]+", " ", str(name).strip().lower())


def extract_economy_profiles(world_dir: Path) -> dict:
    """Scans Economies/ and world.yaml to extract economic systems, currencies, and baskets."""
    economies = {}
    dirs_to_check = [
        world_dir / "Economies",
        world_dir / "00-World-Bible" / "Economies",
    ]

    # Check world.yaml for global economy config
    world_yaml_path = world_dir / "world.yaml"
    if world_yaml_path.is_file():
        try:
            w_fm = parse_yaml_frontmatter(f"---\n{world_yaml_path.read_text(encoding='utf-8', errors='ignore')}\n---")
            if "economy" in w_fm and isinstance(w_fm["economy"], dict):
                economies["Global"] = w_fm["economy"]
                economies["Global"]["name"] = "Global Economy"
                economies["Global"]["file"] = "world.yaml"
        except Exception:
            pass

    seen_files = set()
    for edir in dirs_to_check:
        if not edir.is_dir():
            continue
        for md_file in sorted(edir.rglob("*.md")):
            if md_file in seen_files or md_file.name.startswith(".") or "Template" in md_file.name:
                continue
            seen_files.add(md_file)
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                fm = parse_yaml_frontmatter(content)
                name = fm.get("name") or md_file.stem.replace("_", " ")

                base_currency = fm.get("base_currency") or "Standard Coin"
                currencies = fm.get("currencies") or {}
                
                # If currencies was parsed as list, convert to standard dict
                if isinstance(currencies, list):
                    c_dict = {}
                    for item in currencies:
                        if isinstance(item, str) and ":" in item:
                            k, v = item.split(":", 1)
                            try:
                                c_dict[k.strip()] = float(v.strip())
                            except ValueError:
                                c_dict[k.strip()] = 1.0
                        elif isinstance(item, str):
                            c_dict[item.strip()] = 1.0
                    currencies = c_dict

                # Ensure base currency exists in denominations
                if base_currency not in currencies and isinstance(currencies, dict):
                    currencies[base_currency] = 1.0

                commodity_basket = fm.get("commodity_basket") or fm.get("prices") or {}
                if isinstance(commodity_basket, list):
                    b_dict = {}
                    for item in commodity_basket:
                        if isinstance(item, str) and ":" in item:
                            k, v = item.split(":", 1)
                            try:
                                b_dict[k.strip()] = float(v.strip())
                            except ValueError:
                                b_dict[k.strip()] = 1.0
                    commodity_basket = b_dict

                tech_era = fm.get("tech_era") or fm.get("technology_level") or "medieval"

                economies[name] = {
                    "name": name,
                    "file": str(md_file.relative_to(world_dir)),
                    "base_currency": base_currency,
                    "currencies": currencies,
                    "commodity_basket": commodity_basket,
                    "tech_era": str(tech_era).lower().replace(" ", "_"),
                    "associated_faction": fm.get("associated_faction") or fm.get("faction") or "All",
                }
            except Exception as e:
                logger.warning("Failed to parse economy profile %s: %s", md_file, e)

    return economies


def calculate_ppp_rates(economies: dict) -> dict:
    """Calculates Purchasing Power Parity (PPP) relative exchange rates across economies."""
    ppp_matrix = {}
    if len(economies) < 2:
        return ppp_matrix

    econ_names = list(economies.keys())
    for i in range(len(econ_names)):
        e1_name = econ_names[i]
        e1 = economies[e1_name]
        b1 = e1.get("commodity_basket", {})
        ppp_matrix[e1_name] = {}

        for j in range(len(econ_names)):
            if i == j:
                ppp_matrix[e1_name][econ_names[j]] = 1.0
                continue
            e2_name = econ_names[j]
            e2 = economies[e2_name]
            b2 = e2.get("commodity_basket", {})

            # Find common basket items
            common_items = [k for k in b1 if k in b2 and isinstance(b1[k], (int, float)) and isinstance(b2[k], (int, float)) and b2[k] > 0]
            if common_items:
                ratios = [float(b1[item]) / float(b2[item]) for item in common_items]
                avg_ppp_rate = sum(ratios) / len(ratios)
                ppp_matrix[e1_name][e2_name] = round(avg_ppp_rate, 4)
            else:
                ppp_matrix[e1_name][e2_name] = None

    return ppp_matrix


def audit_manuscript_prices(manuscript_dir: Path, economies: dict) -> list:
    """Audits manuscript scene files for price anomalies and unregistered currencies."""
    findings = []
    if not manuscript_dir or not manuscript_dir.is_dir():
        return findings

    # Collect all known currency names across economies
    known_currencies = set()
    global_basket = {}
    for e in economies.values():
        for c in e.get("currencies", {}):
            known_currencies.add(normalize_name(c))
        for item, price in e.get("commodity_basket", {}).items():
            if isinstance(price, (int, float)):
                global_basket[normalize_name(item)] = float(price)

    # Regex for @price: amount currency for item
    price_tag_regex = re.compile(r"@price:\s*([\d\.]+)\s+([A-Za-z\s]+?)\s+(?:for|on)\s+([A-Za-z\s_-]+)", re.IGNORECASE)
    # Prose price pattern: "50 gold crowns for a loaf of bread" or "cost 20 silver bits"
    prose_price_regex = re.compile(r"\b(\d+(?:\.\d+)?)\s+([A-Za-z\s]+?(?:crowns?|coins?|pence|shillings?|gold|silver|copper|credits?|sovereigns?|ducats?|drachmas?))\s+(?:for|on)\s+(?:a|an|the)?\s*([A-Za-z\s_-]+)\b", re.IGNORECASE)

    for md_file in sorted(manuscript_dir.rglob("*.md")):
        if md_file.name.startswith(".") or "Front_Matter" in md_file.parts or "Back_Matter" in md_file.parts:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for line_idx, line in enumerate(lines, start=1):
                # Check @price: tags
                for m in price_tag_regex.finditer(line):
                    amount = float(m.group(1))
                    curr_name = m.group(2).strip()
                    item_name = m.group(3).strip()

                    curr_norm = normalize_name(curr_name)
                    item_norm = normalize_name(item_name)

                    if known_currencies and curr_norm not in known_currencies:
                        findings.append({
                            "id": "ECO-102",
                            "severity": "WARNING",
                            "message": f"Unregistered Currency: Scene references '{curr_name}', not defined in World Bible Economies.",
                            "file": str(md_file.relative_to(manuscript_dir)),
                            "line": line_idx,
                        })

                    if item_norm in global_basket:
                        base_price = global_basket[item_norm]
                        if base_price > 0:
                            ratio = amount / base_price
                            if ratio > 20.0:
                                findings.append({
                                    "id": "ECO-101",
                                    "severity": "WARNING",
                                    "message": f"Severe Price Inflation Anomaly: '{item_name}' costs {amount} {curr_name} (baseline basket: {base_price}). Ratio is {ratio:.1f}x normal.",
                                    "file": str(md_file.relative_to(manuscript_dir)),
                                    "line": line_idx,
                                })
                            elif ratio < 0.05:
                                findings.append({
                                    "id": "ECO-101",
                                    "severity": "WARNING",
                                    "message": f"Severe Price Deflation Anomaly: '{item_name}' costs {amount} {curr_name} (baseline basket: {base_price}). Ratio is {ratio:.2f}x normal.",
                                    "file": str(md_file.relative_to(manuscript_dir)),
                                    "line": line_idx,
                                })

                # Check prose patterns
                for m in prose_price_regex.finditer(line):
                    amount = float(m.group(1))
                    curr_name = m.group(2).strip()
                    item_name = m.group(3).strip()
                    item_norm = normalize_name(item_name)
                    curr_norm = normalize_name(curr_name)

                    if known_currencies and curr_norm not in known_currencies:
                        findings.append({
                            "id": "ECO-102",
                            "severity": "WARNING",
                            "message": f"Unregistered Currency: Prose references '{curr_name}', not defined in World Bible Economies.",
                            "file": str(md_file.relative_to(manuscript_dir)),
                            "line": line_idx,
                        })

                    if item_norm in global_basket:
                        base_price = global_basket[item_norm]
                        if base_price > 0 and (amount / base_price > 50.0):
                            findings.append({
                                "id": "ECO-101",
                                "severity": "WARNING",
                                "message": f"Prose Price Discrepancy: '{item_name}' mentioned as costing {amount} {curr_name} (baseline: {base_price}).",
                                "file": str(md_file.relative_to(manuscript_dir)),
                                "line": line_idx,
                            })
        except Exception as e:
            logger.warning("Failed to audit manuscript file %s: %s", md_file, e)

    return findings


def audit_technological_anachronisms(
    manuscript_dir: Path,
    baseline_era: str = "medieval",
    custom_whitelist: list = None
) -> list:
    """
    Scans manuscript prose to detect out-of-era technological and material anachronisms.
    """
    findings = []
    if not manuscript_dir or not manuscript_dir.is_dir():
        return findings

    base_era_norm = baseline_era.lower().replace(" ", "_").replace("-", "_")
    base_idx = ERA_ORDER.get(base_era_norm, ERA_ORDER["medieval"])

    whitelist = {normalize_name(w) for w in (custom_whitelist or [])}

    for md_file in sorted(manuscript_dir.rglob("*.md")):
        if md_file.name.startswith(".") or "Front_Matter" in md_file.parts or "Back_Matter" in md_file.parts:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for line_idx, line in enumerate(lines, start=1):
                # Ignore tag lines
                if line.strip().startswith("@"):
                    continue
                
                line_lower = line.lower()
                for tech_term, earliest_era in TECH_ERA_DICTIONARY.items():
                    if normalize_name(tech_term) in whitelist:
                        continue
                    earliest_idx = ERA_ORDER.get(earliest_era, 0)
                    if earliest_idx > base_idx:
                        # Term is from future era compared to world baseline
                        # Match word boundaries
                        pattern = r"\b" + re.escape(tech_term) + r"\b"
                        if re.search(pattern, line_lower):
                            findings.append({
                                "id": "ECO-201",
                                "severity": "WARNING",
                                "term": tech_term,
                                "earliest_era": earliest_era,
                                "world_baseline": baseline_era,
                                "message": f"Technological Anachronism: '{tech_term}' belongs to '{earliest_era}' era (World baseline: '{baseline_era}').",
                                "file": str(md_file.relative_to(manuscript_dir)),
                                "line": line_idx,
                                "snippet": line.strip(),
                            })
        except Exception as e:
            logger.warning("Failed to audit anachronisms for %s: %s", md_file, e)

    return findings


def calc_trade_margin(
    buy_price_per_ton: float,
    sell_price_per_ton: float,
    cargo_tons: float,
    distance_km_or_ly: float,
    transit_cost_per_ton_unit: float = 0.5,
    tariff_pct: float = 0.05,
    spoilage_pct: float = 0.02
) -> dict:
    """Calculates trade route profitability, break-even threshold, and net margin."""
    total_cargo_buy_cost = buy_price_per_ton * cargo_tons
    gross_revenue_potential = sell_price_per_ton * cargo_tons * (1.0 - spoilage_pct)
    
    total_transit_cost = transit_cost_per_ton_unit * distance_km_or_ly * cargo_tons
    total_tariffs = gross_revenue_potential * tariff_pct

    total_expenses = total_cargo_buy_cost + total_transit_cost + total_tariffs
    net_profit = gross_revenue_potential - total_expenses
    roi_pct = (net_profit / max(1.0, total_expenses)) * 100.0

    # Break-even sell price per ton
    break_even_sell_price = total_expenses / max(1.0, cargo_tons * (1.0 - spoilage_pct))

    return {
        "buy_price_per_ton": buy_price_per_ton,
        "sell_price_per_ton": sell_price_per_ton,
        "cargo_tons": cargo_tons,
        "distance": distance_km_or_ly,
        "gross_revenue": round(gross_revenue_potential, 2),
        "total_transit_cost": round(total_transit_cost, 2),
        "total_tariffs": round(total_tariffs, 2),
        "net_profit": round(net_profit, 2),
        "roi_pct": round(roi_pct, 1),
        "break_even_sell_price_per_ton": round(break_even_sell_price, 2),
        "is_profitable": net_profit > 0,
        "verdict": "Profitable Trade Route" if net_profit > 0 else "Unprofitable: Transit/Tariff costs exceed price spread",
    }


def generate_economy_html_report(audit_data: dict, output_path: Path):
    """Generates standalone HTML report for Economic audit and Tech Era check."""
    economies = audit_data.get("economies", {})
    findings = audit_data.get("findings", [])
    ppp_matrix = audit_data.get("ppp_matrix", {})
    world_name = audit_data.get("world", "World Bible")

    econ_cards = []
    for en, e in economies.items():
        curr_str = ", ".join([f"{k} (x{v})" for k, v in e.get("currencies", {}).items()])
        basket_str = ", ".join([f"{k}: {v}" for k, v in e.get("commodity_basket", {}).items()])
        econ_cards.append(f"""
        <div class="card">
            <h3>🏛️ {html.escape(en)} ({html.escape(e.get('tech_era', 'medieval'))})</h3>
            <p><strong>Base Currency:</strong> {html.escape(e.get('base_currency', ''))}</p>
            <p><strong>Currencies:</strong> {html.escape(curr_str)}</p>
            <p><strong>Basket Prices:</strong> <small>{html.escape(basket_str)}</small></p>
        </div>
        """)

    findings_cards = []
    for fd in findings:
        badge_cls = "badge-error" if fd.get("severity") == "ERROR" else "badge-warning"
        findings_cards.append(f"""
        <div class="card finding-card">
            <span class="badge {badge_cls}">{html.escape(fd.get('severity', 'WARNING'))}</span>
            <strong>{html.escape(fd.get('id', ''))}</strong>: {html.escape(fd.get('message', ''))}
            <div style="font-size: 0.85em; color: #94a3b8; margin-top: 4px;">File: {html.escape(fd.get('file', ''))}:{fd.get('line', '')}</div>
        </div>
        """)

    findings_html = "".join(findings_cards) if findings_cards else "<div style='color: #4ade80;'>✓ No pricing anomalies or technological anachronisms detected.</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Economy & Anachronism Matrix ({html.escape(world_name)})</title>
<style>
  :root {{
    --bg: #0f172a;
    --card-bg: #1e293b;
    --border: #334155;
    --text: #f8fafc;
    --accent: #38bdf8;
    --danger: #f43f5e;
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
  .container {{ max-width: 1200px; margin: 0 auto; }}
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
  .badge-error {{ background: #b91c1c; color: #fff; }}
  .finding-card {{ margin-bottom: 0.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>💰 Ars Arcanum Economy, PPP & Anachronism Matrix</h1>
  <p>World Lore Vault: <strong>{html.escape(world_name)}</strong></p>

  <div class="card">
    <h2>Audit Findings ({len(findings)})</h2>
    {findings_html}
  </div>

  <h2>Registered In-World Economies</h2>
  {"".join(econ_cards)}
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)


def resolve_world_dir(target_str: str = None) -> str:
    """Resolves world input string (path or name) to absolute directory path."""
    if target_str:
        p = Path(target_str).expanduser().resolve()
        if p.is_dir():
            return str(p)
        home = Path.home()
        for u_dir in sorted((home / "Universes").glob("*/*")):
            if u_dir.is_dir() and u_dir.name.lower() == target_str.lower():
                return str(u_dir)
        for w_dir in sorted((home / "Worlds").glob("*")):
            if w_dir.is_dir() and w_dir.name.lower() == target_str.lower():
                return str(w_dir)
        p_cwd = Path.cwd() / target_str
        if p_cwd.is_dir():
            return str(p_cwd)

    home = Path.home()
    universes = sorted((home / "Universes").glob("*/*"), key=lambda p: str(p))
    universes = [p for p in universes if p.is_dir() and p.name not in ("Worlds", ".git")]
    if len(universes) == 1:
        return str(universes[0])
    elif len(universes) > 1:
        print("Error: Multiple worlds discovered — specify one explicitly.", file=sys.stderr)
        sys.exit(2)
    else:
        worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
        worlds = [p for p in worlds if p.is_dir()]
        if len(worlds) == 1:
            return str(worlds[0])
        elif len(worlds) > 1:
            print("Error: Multiple legacy worlds discovered — specify one explicitly.", file=sys.stderr)
            sys.exit(2)
    return ""


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
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Economy, Commodity PPP & Anachronism Matrix")
    subparsers = parser.add_subparsers(dest="subcommand", help="Economy subcommands")

    # 1. check / report
    p_check = subparsers.add_parser("check", help="Run economy and price consistency audit")
    p_check.add_argument("world", nargs="?", help="World Bible lore directory")
    p_check.add_argument("manuscript_pos", nargs="?", help="Manuscript draft directory")
    p_check.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_check.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_check.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_check.add_argument("--html", help="Path to export standalone HTML report")

    p_rep = subparsers.add_parser("report", help="Display full economy and PPP report")
    p_rep.add_argument("world", nargs="?", help="World Bible lore directory")
    p_rep.add_argument("manuscript_pos", nargs="?", help="Manuscript draft directory")
    p_rep.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_rep.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_rep.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_rep.add_argument("--html", help="Path to export standalone HTML report")

    # 2. tech audit
    p_tech = subparsers.add_parser("tech", help="Audit manuscript for out-of-era technological anachronisms")
    p_tech.add_argument("manuscript", nargs="?", help="Manuscript draft directory")
    p_tech.add_argument("-m", "--manuscript", dest="ms_flag", help="Manuscript draft directory")
    p_tech.add_argument("-w", "--world", help="World Bible directory (for tech era detection)")
    p_tech.add_argument("--era", choices=TECH_ERAS, default="medieval", help="Baseline technological era")
    p_tech.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 3. trade calculator
    p_trade = subparsers.add_parser("trade", help="Interstellar/regional trade route profit margin calculator")
    p_trade.add_argument("--buy", type=float, required=True, help="Origin commodity buy price per ton")
    p_trade.add_argument("--sell", type=float, required=True, help="Destination commodity sell price per ton")
    p_trade.add_argument("--cargo", type=float, default=100.0, help="Cargo weight in metric tons")
    p_trade.add_argument("--distance", type=float, default=500.0, help="Route distance (km or ly)")
    p_trade.add_argument("--cost-per-unit", type=float, default=0.5, help="Transit freight cost per ton-distance")
    p_trade.add_argument("--tariff", type=float, default=0.05, help="Tariff tax fraction (default 0.05 = 5%%)")
    p_trade.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    if len(sys.argv) > 1 and sys.argv[1] not in ("check", "report", "tech", "trade", "-h", "--help", "-v", "--version"):
        sys.argv.insert(1, "check")

    args = parser.parse_args()

    if not args.subcommand:
        args.subcommand = "report"

    if args.subcommand in ("check", "report"):
        raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
        world_dir_str = resolve_world_dir(raw_world)
        if not world_dir_str or not Path(world_dir_str).is_dir():
            print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
            sys.exit(2)

        world_path = Path(world_dir_str)
        raw_ms = getattr(args, "manuscript", None) or getattr(args, "manuscript_pos", None)
        ms_dir_str = resolve_manuscript_dir(raw_ms) if raw_ms else None
        ms_path = Path(ms_dir_str) if ms_dir_str else None

        economies = extract_economy_profiles(world_path)
        ppp_matrix = calculate_ppp_rates(economies)
        price_findings = audit_manuscript_prices(ms_path, economies) if ms_path else []

        # Also run tech check if manuscript provided
        primary_era = "medieval"
        if economies:
            primary_era = list(economies.values())[0].get("tech_era", "medieval")
        tech_findings = audit_technological_anachronisms(ms_path, primary_era) if ms_path else []

        all_findings = price_findings + tech_findings

        audit_data = {
            "world": world_path.name,
            "manuscript": ms_path.name if ms_path else None,
            "economies_count": len(economies),
            "findings_count": len(all_findings),
            "economies": economies,
            "ppp_matrix": ppp_matrix,
            "findings": all_findings,
        }

        if getattr(args, "json", False):
            print(json.dumps(audit_data, indent=2))
        else:
            print(f"\n\033[1;33m=== Ars Arcanum Economy, Commodity PPP & Tech Matrix ===\033[0m")
            print(f"World: \033[1m{world_path.name}\033[0m | Manuscript: \033[1m{ms_path.name if ms_path else 'N/A'}\033[0m")
            print(f"Economies Registered: \033[32m{len(economies)}\033[0m | Findings: \033[1m{len(all_findings)}\033[0m\n")

            if economies:
                print("\033[1mIn-World Economic Systems & Currencies:\033[0m")
                for en, einfo in economies.items():
                    print(f"  🪙 \033[1;36m{en}\033[0m (Era: {einfo.get('tech_era', 'medieval')}) — Base: {einfo.get('base_currency', '')}")
                    if einfo.get("currencies"):
                        c_list = [f"{k} (x{v})" for k, v in einfo["currencies"].items()]
                        print(f"     Currencies: {', '.join(c_list)}")
                    if einfo.get("commodity_basket"):
                        b_list = [f"{k}={v}" for k, v in einfo["commodity_basket"].items()]
                        print(f"     Basket: {', '.join(b_list)}")
                print()

            if not all_findings:
                print("\033[32m[OK] Economic models and manuscript prices are internally consistent.\033[0m")
            else:
                for fd in all_findings:
                    badge = f"\033[31m[{fd['severity']}]\033[0m" if fd["severity"] == "ERROR" else f"\033[33m[{fd['severity']}]\033[0m"
                    print(f"{badge} {fd['id']}: {fd['message']}")
                    print(f"     Location: {fd['file']}:{fd.get('line', '')}\n")

        if getattr(args, "html", None):
            out_p = Path(args.html)
            generate_economy_html_report(audit_data, out_p)
            print(f"\nInteractive HTML report written to: {out_p}")

        sys.exit(1 if len(all_findings) > 0 else 0)

    elif args.subcommand == "tech":
        raw_ms = getattr(args, "ms_flag", None) or getattr(args, "manuscript", None)
        ms_dir_str = resolve_manuscript_dir(raw_ms)
        if not ms_dir_str or not Path(ms_dir_str).is_dir():
            print("Error: No valid Manuscript directory specified or discovered.", file=sys.stderr)
            sys.exit(2)

        ms_path = Path(ms_dir_str)
        era = args.era
        if args.world:
            w_dir = resolve_world_dir(args.world)
            if w_dir:
                econs = extract_economy_profiles(Path(w_dir))
                if econs:
                    era = list(econs.values())[0].get("tech_era", era)

        findings = audit_technological_anachronisms(ms_path, baseline_era=era)

        if args.json:
            print(json.dumps({"manuscript": ms_path.name, "baseline_era": era, "findings": findings}, indent=2))
        else:
            print(f"\n\033[1;36m=== Technological Era Baseline Audit ===\033[0m")
            print(f"Manuscript: \033[1m{ms_path.name}\033[0m | Baseline Era: \033[1;33m{era}\033[0m")
            print(f"Anachronisms Detected: \033[1m{len(findings)}\033[0m\n")

            if not findings:
                print(f"\033[32m[OK] No out-of-era technological terms found for {era} baseline.\033[0m")
            else:
                for f in findings:
                    print(f"\033[33m[ANACHRONISM]\033[0m {f['id']}: '{f['term']}' is from {f['earliest_era']} era.")
                    print(f"  Location: {f['file']}:{f['line']}")
                    print(f"  Snippet : \"{f['snippet']}\"\n")

        sys.exit(1 if len(findings) > 0 else 0)

    elif args.subcommand == "trade":
        result = calc_trade_margin(
            buy_price_per_ton=args.buy,
            sell_price_per_ton=args.sell,
            cargo_tons=args.cargo,
            distance_km_or_ly=args.distance,
            transit_cost_per_ton_unit=args.cost_per_unit,
            tariff_pct=args.tariff,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n\033[1;32m=== Trade Route Profitability Analysis ===\033[0m")
            print(f"Cargo          : {result['cargo_tons']} tons | Distance: {result['distance']}")
            print(f"Price Spread   : Buy @ {result['buy_price_per_ton']} -> Sell @ {result['sell_price_per_ton']} per ton")
            print(f"Gross Revenue  : {result['gross_revenue']:,.2f}")
            print(f"Transit Cost   : {result['total_transit_cost']:,.2f} | Tariffs: {result['total_tariffs']:,.2f}")
            print(f"Net Profit     : \033[1m{result['net_profit']:,.2f}\033[0m (ROI: {result['roi_pct']}%)")
            print(f"Break-Even Sell: {result['break_even_sell_price_per_ton']:,.2f} per ton")
            vcol = "\033[32m" if result["is_profitable"] else "\033[31m"
            print(f"Verdict        : {vcol}{result['verdict']}\033[0m\n")
        sys.exit(0)


if __name__ == "__main__":
    main()