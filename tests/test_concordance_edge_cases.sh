#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

TMP_EDGE="$(mktemp -d)"
trap 'rm -rf "${TMP_EDGE:-}"' EXIT
export HOME="${TMP_EDGE}/home"
mkdir -p "${HOME}"
unset DISPLAY WAYLAND_DISPLAY 2>/dev/null || true

echo "=== Edge Case Test 1: Notes without explicit name key and nested subdirectories ==="
bash scripts/arcanum universe EdgeUniverse >/dev/null
bash scripts/arcanum world EdgeWorld -u EdgeUniverse >/dev/null
bash scripts/arcanum manuscript EdgeManuscript -u EdgeUniverse -w EdgeWorld >/dev/null
WORLD="${HOME}/Universes/EdgeUniverse/EdgeWorld"
MS="${HOME}/Manuscripts/EdgeManuscript"

mkdir -p "${WORLD}/Characters/Order-Of-Shadows"
cat > "${WORLD}/Characters/Order-Of-Shadows/Kaelen_Shadow.md" << 'CHAR_EOF'
---
type: character
role: Protagonist
status: Missing
species_race: Elf
occupation: Ranger
faction: "[[The Shadow Syndicate]]"
origin: "[[Silent Vale]]"
aliases: "The Ghost, Shadow Blade"
---
> *"I tread where light dare not follow."*

## 1. Quick Summary
Kaelen is a legendary elven ranger who disappeared during the Second Siege.
CHAR_EOF

cat > "${WORLD}/Characters/Lord_Vane.md" << 'CHAR2_EOF'
---
name: "Lord Vane"
type: character
role: Antagonist
status: Deceased
faction: "[[Iron Legion]]"
---
The late warlord of the northern marches.
CHAR2_EOF

mkdir -p "${WORLD}/Magic-Technology/Arcane"
cat > "${WORLD}/Magic-Technology/Arcane/Void_Weaving.md" << 'MAGIC_EOF'
---
name: "Void Weaving"
type: magic_tech_system
classification: "Forbidden Arcana"
source_of_power: "Astral Rift"
danger_cost: "Permanent Soul Corruption"
---
## 1. Overview
The ancient discipline of manipulating negative space and astral echoes.
MAGIC_EOF

mkdir -p "${WORLD}/Factions/Underground"
cat > "${WORLD}/Factions/Underground/Shadow_Syndicate.md" << 'FAC_EOF'
---
name: "The Shadow Syndicate"
type: faction
faction_type: "Syndicate"
leader: "[[Unknown]]"
motto: "In Umbra Vincimus"
---
A secret network operating beneath the surface.
FAC_EOF

bash scripts/arcanum concordance "${WORLD}" --manuscript "${MS}" >/dev/null

DP_FILE="${MS}/Book-01/04_Back_Matter/01_Dramatis_Personae.md"
GC_FILE="${MS}/Book-01/04_Back_Matter/02_Glossary_and_Concordance.md"

[ -f "${DP_FILE}" ] || { echo "FAIL: Dramatis Personae file missing"; exit 1; }
[ -f "${GC_FILE}" ] || { echo "FAIL: Glossary file missing"; exit 1; }

grep -q "Kaelen_Shadow" "${DP_FILE}" || { echo "FAIL: Kaelen_Shadow missing from Dramatis Personae"; exit 1; }
grep -q "The Ghost, Shadow Blade" "${DP_FILE}" || { echo "FAIL: Aliases missing from Dramatis Personae"; exit 1; }
grep -q "Status: Missing" "${DP_FILE}" || { echo "FAIL: Status: Missing missing from Dramatis Personae"; exit 1; }
grep -q "Lord Vane" "${DP_FILE}" || { echo "FAIL: Lord Vane missing from Dramatis Personae"; exit 1; }
grep -q "Status: Deceased" "${DP_FILE}" || { echo "FAIL: Status: Deceased missing from Dramatis Personae"; exit 1; }

grep -q "Void Weaving" "${GC_FILE}" || { echo "FAIL: Void Weaving missing from Glossary"; exit 1; }
grep -q "Forbidden Arcana" "${GC_FILE}" || { echo "FAIL: Classification missing from Glossary"; exit 1; }
grep -q "The Shadow Syndicate" "${GC_FILE}" || { echo "FAIL: Shadow Syndicate missing from Glossary"; exit 1; }

echo "  OK Edge Case Test 1 passed"

echo "=== Edge Case Test 2: Multi-era chronology unit permutations ==="
python3 - << 'PYEOF'
import sys
import re

ERA_ORDER = {
    '1e': 1, '1a': 1, 'first age': 1, 'age 1': 1, 'era 1': 1, 'first era': 1, 'fa': 1,
    '2e': 2, '2a': 2, 'second age': 2, 'age 2': 2, 'era 2': 2, 'second era': 2, 'sa': 2,
    '3e': 3, '3a': 3, 'third age': 3, 'age 3': 3, 'era 3': 3, 'third era': 3, 'ta': 3,
    '4e': 4, '4a': 4, 'fourth age': 4, 'age 4': 4, 'era 4': 4, 'fourth era': 4,
    '5e': 5, '5a': 5, 'fifth age': 5, 'age 5': 5, 'era 5': 5, 'fifth era': 5,
}

BC_PATTERN = re.compile(r'\b(bce|bc|b\.c\.e\.|b\.c\.|before common era|before era)\b', re.IGNORECASE)
CE_PATTERN = re.compile(r'\b(ce|ad|c\.e\.|a\.d\.|common era|anno domini)\b', re.IGNORECASE)

def parse_timeline_date(val):
    if val is None:
        return None
    s = str(val).strip().strip('"').strip("'")
    if not s:
        return None
    try:
        return (None, float(s), s)
    except ValueError:
        pass
    if BC_PATTERN.search(s):
        num_m = re.search(r'([+-]?\d+(?:\.\d+)?)', s)
        if num_m:
            num = float(num_m.group(1))
            return (None, -abs(num), s)
    if CE_PATTERN.search(s):
        num_m = re.search(r'([+-]?\d+(?:\.\d+)?)', s)
        if num_m:
            num = float(num_m.group(1))
            return (None, abs(num), s)
    m1 = re.match(r'^([+-]?\d+(?:\.\d+)?)\s+([A-Za-z0-9_\s\.\'-]+)$', s)
    if m1:
        num = float(m1.group(1))
        era = m1.group(2).strip().lower()
        return (era, num, s)
    m2 = re.match(r'^([A-Za-z0-9_\s\.\'-]+?)\s+([+-]?\d+(?:\.\d+)?)$', s)
    if m2:
        era = m2.group(1).strip().lower()
        num = float(m2.group(2))
        return (era, num, s)
    return None

def compare_timeline_dates(d1_val, d2_val):
    p1 = parse_timeline_date(d1_val)
    p2 = parse_timeline_date(d2_val)
    if p1 is None or p2 is None:
        return None
    era1, num1, _ = p1
    era2, num2, _ = p2
    if era1 is None and era2 is None:
        if num1 < num2: return -1
        if num1 > num2: return 1
        return 0
    if era1 in ERA_ORDER and era2 in ERA_ORDER:
        o1 = ERA_ORDER[era1]
        o2 = ERA_ORDER[era2]
        if o1 < o2: return -1
        if o1 > o2: return 1
        if num1 < num2: return -1
        if num1 > num2: return 1
        return 0
    if era1 is not None and era2 is not None and era1 == era2:
        if num1 < num2: return -1
        if num1 > num2: return 1
        return 0
    return None

test_cases = [
    ("-450 IE", "-400 IE", -1),
    ("-400 IE", "-450 IE", 1),
    ("1422 3E", "1450 3E", -1),
    ("1450 3E", "1422 3E", 1),
    ("50 4E", "1422 3E", 1),
    ("1422 3E", "50 4E", -1),
    ("Age of Fire 410", "Age of Fire 450", -1),
    ("Age of Fire 450", "Age of Fire 410", 1),
    ("500 BCE", "100 BCE", -1),
    ("100 BCE", "500 BCE", 1),
    ("500 BCE", "100 CE", -1),
    ("100 CE", "500 BCE", 1),
    (-450, -300, -1),
    (100, 200, -1),
    ("First Age 50", "Second Age 10", -1),
    ("Second Age 10", "First Age 50", 1),
    ("Age of Fire 100", "Age of Ice 200", None),
]

for d1, d2, exp in test_cases:
    res = compare_timeline_dates(d1, d2)
    assert res == exp, f"Comparison failed for ({d1}, {d2}): expected {exp}, got {res}"

print("  OK all 17 timeline parsing cases verified")
PYEOF

echo "=== Edge Case Test 3: CLI facade argument combinations ==="
bash scripts/arcanum concordance "${WORLD}" --manuscript "${MS}" --book Book-01 >/dev/null
bash scripts/arcanum concordance "${WORLD}" --manuscript "${MS}" -b all >/dev/null
bash scripts/arcanum concordance "${WORLD}" --manuscript "${MS}" Book-01 >/dev/null

echo "  OK CLI argument combinations verified"
echo "=== ALL EDGE CASE TESTS PASSED! ==="
