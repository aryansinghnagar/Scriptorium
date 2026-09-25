#!/usr/bin/env python3
"""
Ars Arcanum Unified YAML Frontmatter Engine (scripts/lib/frontmatter.py)
=======================================================================
High-performance, pure-Python standard library YAML frontmatter parser and extractor.
Provides safe, zero-dependency parsing of YAML frontmatter headers across all lore
bibles, world vaults, and manuscript files.
"""

import re
from typing import Any

FRONTMATTER_DELIM = "---"
FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def _coerce_scalar(val: str) -> Any:
    """Coerces a string scalar to int, float, bool, or unquoted string."""
    stripped = val.strip()
    if (stripped.startswith('"') and stripped.endswith('"')) or (stripped.startswith("'") and stripped.endswith("'")):
        return stripped[1:-1]

    lower = stripped.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower in ("none", "null", "~"):
        return None

    # Integer
    if re.match(r"^[+-]?\d+$", stripped):
        try:
            return int(stripped)
        except ValueError:
            pass

    # Float
    if re.match(r"^[+-]?\d+\.\d+$", stripped):
        try:
            return float(stripped)
        except ValueError:
            pass

    return stripped


def _parse_yaml_lines(lines: list[str]) -> dict[str, Any]:
    """Parses a list of YAML lines into a dictionary."""
    data: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Check list item under current key
        if raw_line.startswith("  - ") or raw_line.startswith("    - ") or (raw_line.startswith("- ") and current_key):
            item_val = line.lstrip("- ").strip()
            item_val = _coerce_scalar(item_val)
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
                # Key with empty value or impending list
                data[key] = ""
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                if not inner:
                    data[key] = []
                else:
                    data[key] = [_coerce_scalar(v.strip()) for v in inner.split(",") if v.strip()]
            else:
                data[key] = _coerce_scalar(val)

    return data


def parse_yaml_frontmatter(content: str) -> dict[str, Any]:
    """
    Parses YAML frontmatter block from Markdown content into a dictionary.
    Supports key-value pairs, inline lists ([a, b]), bulleted lists (- item),
    and scalar coercion. Returns an empty dict if no valid frontmatter is found.
    """
    fm_match = FRONTMATTER_REGEX.match(content)
    if not fm_match:
        return {}

    lines = fm_match.group(1).splitlines()
    return _parse_yaml_lines(lines)


def parse_yaml_document(content: str) -> dict[str, Any]:
    """
    Parses a YAML document (such as manuscript.yaml or world.yaml) or frontmatter block.
    """
    fm_match = FRONTMATTER_REGEX.match(content)
    if fm_match:
        return parse_yaml_frontmatter(content)

    lines = content.splitlines()
    if lines and lines[0].strip() == FRONTMATTER_DELIM:
        lines = lines[1:]
    if lines and lines[-1].strip() == FRONTMATTER_DELIM:
        lines = lines[:-1]

    return _parse_yaml_lines(lines)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], bool]:
    """
    Strict flat-subset parser returning (frontmatter_dict, success_boolean).
    Used by world_doctor for structural verification.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, True

    fm: dict[str, Any] = {}
    i = 1
    n = len(lines)
    while i < n and lines[i].strip() != FRONTMATTER_DELIM:
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        m = re.match(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$", stripped)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val == "":
                items = []
                j = i + 1
                while j < n and re.match(r"^[ \t]+-[ \t]+", lines[j]):
                    items.append(re.sub(r"^[ \t]+-[ \t]+", "", lines[j]).strip().strip('"\''))
                    j += 1
                if items:
                    fm[key] = items
                    i = j
                    continue
                fm[key] = ""
                i += 1
                continue
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [v.strip().strip('"\'') for v in val[1:-1].split(",") if v.strip()]
            else:
                fm[key] = val.strip('"\'')
            i += 1
            continue
        return fm, False

    if i >= n:
        return fm, False
    return fm, True


def extract_frontmatter_and_body(content: str) -> tuple[dict[str, Any], str]:
    """Splits markdown content into frontmatter metadata dictionary and body text."""
    fm_match = FRONTMATTER_REGEX.match(content)
    if not fm_match:
        return {}, content

    fm_dict = parse_yaml_frontmatter(content)
    body = content[fm_match.end():]
    return fm_dict, body
