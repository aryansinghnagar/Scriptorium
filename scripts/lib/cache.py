#!/usr/bin/env python3
"""
Ars Arcanum Cache Engine (scripts/lib/cache.py)
High-performance mtime-keyed in-memory & on-disk cache layer for World Bibles and Manuscripts.
Ensures sub-millisecond treeview rendering and accelerated diagnostic passes.
"""

import os
import sys
import json
import re
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
            p.write_text(data, encoding=encoding)

logger = logging.getLogger("arcanum.cache")

CACHE_VERSION = 2
CACHE_FILENAME = ".arcanum_cache.json"

# ANA-01: canonical word-count definition shared by cache.py,
# wordcount_report.sh, and ui_gtk3.py. Policy: strip YAML frontmatter and
# fenced codeblocks, drop @metadata lines and Typst `%` comment lines,
# then count unicode word boundaries (\b\w+\b). Hyphenated compounds
# count as two words; isolated punctuation counts as zero.
# PRF-02: bound per-file reads; world_doctor uses 2 MiB, wordcount 8 MiB —
# cache sits between at 4 MiB to avoid RAM exhaustion on huge .md files.
MAX_BYTES = 4 * 1024 * 1024

# PRF-02: never index generated/published artifacts — they bloat the cache
# and pollute word counts with compiled output.
EXCLUDE_DIR_NAMES = frozenset({
    ".obsidian", ".git",
    "Exports", "04-Publishing", "04_Publishing",
    "Backups", "05-Backups", "05_Backups",
    "04_Back_Matter", "04-Back-Matter",
})

TAG_REGEXES = {
    "pov": re.compile(r"^@pov:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "characters": re.compile(r"^@(?:chars?|characters?):\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "location": re.compile(r"^@(?:location|loc|setting):\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "thread": re.compile(r"^@(?:thread|subplot|plot):\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "status": re.compile(r"^@(?:status|state):\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "time": re.compile(r"^@(?:time|date|era):\s*(.+)$", re.IGNORECASE | re.MULTILINE),
}

WIKILINK_REGEX = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
FENCED_CODE_REGEX = re.compile(r"```.*?```", re.DOTALL)
WORD_REGEX = re.compile(r"\b\w+\b", re.UNICODE)
NW_TAG_LINE_REGEX = re.compile(r"^@[A-Za-z0-9_-]+:")


def get_cache_path(project_dir: str) -> Path:
    return Path(project_dir) / CACHE_FILENAME


def load_cache(project_dir: str) -> dict:
    cache_path = get_cache_path(project_dir)
    if not cache_path.is_file():
        legacy_path = Path(project_dir) / ".scriptorium_cache.json"
        if legacy_path.is_file():
            cache_path = legacy_path
        else:
            return {"version": CACHE_VERSION, "files": {}}
    try:
        with open(cache_path, encoding="utf-8") as f:
            data = json.load(f)
            if data.get("version") == CACHE_VERSION and isinstance(data.get("files"), dict):
                return data
    except Exception as e:
        logger.debug("Failed to load or parse cache at %s: %s", cache_path, e)
    return {"version": CACHE_VERSION, "files": {}}


def save_cache(project_dir: str, cache_data: dict) -> bool:
    cache_path = get_cache_path(project_dir)
    try:
        content = json.dumps(cache_data, indent=2, ensure_ascii=False)
        atomic_write(cache_path, content)
        return True
    except Exception as e:
        logger.error("Failed to save cache to %s: %s", cache_path, e)
        return False


def count_words(text: str) -> int:
    """ANA-01 canonical word count. All consumers must use this."""
    clean = FRONTMATTER_REGEX.sub("", text)
    clean = FENCED_CODE_REGEX.sub("", clean)
    # Drop scene-metadata and Typst comment lines (not prose).
    lines = []
    for ln in clean.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("@") and NW_TAG_LINE_REGEX.match(s):
            continue
        if s.startswith("%"):
            continue
        lines.append(ln)
    return len(WORD_REGEX.findall("\n".join(lines)))


def parse_frontmatter(content: str) -> dict:
    match = FRONTMATTER_REGEX.match(content)
    if not match:
        return {}
    raw_yaml = match.group(1)
    meta = {}
    for line in raw_yaml.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip("\"'")
            if val.startswith("[") and val.endswith("]"):
                items = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
                meta[key] = items
            else:
                meta[key] = val
    return meta


def parse_markdown_file(file_path: Path) -> dict:
    truncated = False
    try:
        stat = file_path.stat()
        mtime = stat.st_mtime
        size = stat.st_size
        # PRF-02: bounded read — never load a multi-GB file fully into RAM.
        with open(file_path, "rb") as fh:
            data = fh.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            truncated = True
            data = data[:MAX_BYTES]
        content = data.decode("utf-8", errors="replace")

        words = count_words(content)

        # Extract tags
        tags = {}
        for tag_name, rx in TAG_REGEXES.items():
            matches = rx.findall(content)
            if matches:
                tags[tag_name] = [m.strip() for m in matches]

        # Extract wikilinks
        wikilinks = sorted(list(set(WIKILINK_REGEX.findall(content))))

        # Frontmatter
        frontmatter = parse_frontmatter(content)

        entry = {
            "mtime": mtime,
            "size": size,
            "word_count": words,
            "tags": tags,
            "wikilinks": wikilinks,
            "frontmatter": frontmatter,
        }
        if truncated:
            # DOC-02: explicit truncation flag — callers must not mistake
            # a capped count for a complete one.
            entry["truncated"] = True
            entry["error"] = f"file exceeds {MAX_BYTES // (1024 * 1024)} MiB read cap; content truncated"
        return entry
    except Exception as e:
        logger.warning("Error reading or parsing markdown file %s: %s", file_path, e)
        return {
            "mtime": 0,
            "size": 0,
            "word_count": 0,
            "tags": {},
            "wikilinks": [],
            "frontmatter": {},
            "error": str(e),
        }


def scan_project(project_dir: str, force: bool = False) -> dict:
    pdir = Path(project_dir).resolve()
    if not pdir.is_dir():
        return {"version": CACHE_VERSION, "files": {}}
    cache = {"version": CACHE_VERSION, "files": {}} if force else load_cache(str(pdir))
    files_cache = cache.get("files", {})
    updated = False

    current_files = set()
    errors = 0
    for md_path in pdir.rglob("*.md"):
        if ".obsidian" in md_path.parts or ".git" in md_path.parts or md_path.name.startswith("."):
            continue
        if any(part in EXCLUDE_DIR_NAMES for part in md_path.parts):
            continue
        rel_path = str(md_path.relative_to(pdir)).replace("\\", "/")
        current_files.add(rel_path)

        try:
            stat = md_path.stat()
            cached_entry = files_cache.get(rel_path)
            if (
                not cached_entry
                or cached_entry.get("mtime") != stat.st_mtime
                or cached_entry.get("size") != stat.st_size
            ):
                parsed = parse_markdown_file(md_path)
                files_cache[rel_path] = parsed
                if parsed.get("error"):
                    errors += 1
                updated = True
            elif cached_entry.get("error"):
                errors += 1
        except Exception as e:
            # DOC-02: stat failures are health signals, not silent skips.
            logger.warning("Failed to inspect %s: %s", md_path, e)
            errors += 1
            continue

    # Remove deleted files from cache
    stale_keys = [k for k in files_cache if k not in current_files]
    if stale_keys:
        for k in stale_keys:
            del files_cache[k]
        updated = True

    cache["files"] = files_cache
    # DOC-02: cache health travels with the payload so fast-path consumers
    # can fail closed when the index is uncertain.
    cache["errors"] = errors
    cache["healthy"] = errors == 0
    if updated or force or not get_cache_path(str(pdir)).exists():
        save_cache(str(pdir), cache)

    return cache


def compute_wordcounts(project_dir: str) -> dict:
    cache = scan_project(project_dir)
    total_words = 0
    by_folder = {}

    for rel_path, data in cache.get("files", {}).items():
        wc = data.get("word_count", 0)
        total_words += wc
        folder = os.path.dirname(rel_path) or "(root)"
        by_folder[folder] = by_folder.get(folder, 0) + wc

    return {
        "project": os.path.basename(project_dir),
        "total_words": total_words,
        "total_files": len(cache.get("files", {})),
        "by_folder": by_folder,
    }


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Fast Cache Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_cmd = subparsers.add_parser("scan", help="Scan and update project cache")
    scan_cmd.add_argument("path", help="Project directory path")
    scan_cmd.add_argument("--force", action="store_true", help="Force full rescan")

    wc_cmd = subparsers.add_parser("wordcounts", help="Get aggregated word counts")
    wc_cmd.add_argument("path", help="Project directory path")
    wc_cmd.add_argument("--json", action="store_true", help="Output JSON format")

    clear_cmd = subparsers.add_parser("clear", help="Clear cache file")
    clear_cmd.add_argument("path", help="Project directory path")

    args = parser.parse_args()

    if args.command == "scan":
        res = scan_project(args.path, force=args.force)
        count = len(res.get("files", {}))
        print(f"[CACHE] Indexed {count} Markdown files in {args.path}")
        sys.exit(0)

    elif args.command == "wordcounts":
        res = compute_wordcounts(args.path)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Project: {res['project']}")
            print(f"Total Word Count: {res['total_words']:,} words across {res['total_files']} files\n")
            print("Breakdown by folder:")
            for folder, count in sorted(res["by_folder"].items()):
                print(f"  - {folder}: {count:,} words")
        sys.exit(0)

    elif args.command == "clear":
        cp = get_cache_path(args.path)
        legacy_cp = Path(args.path) / ".scriptorium_cache.json"
        cleared = False
        if cp.exists():
            cp.unlink()
            print(f"[CACHE] Cleared {cp}")
            cleared = True
        if legacy_cp.exists():
            legacy_cp.unlink()
            print(f"[CACHE] Cleared {legacy_cp}")
            cleared = True
        if not cleared:
            print(f"[CACHE] No cache found at {cp}")
        sys.exit(0)


if __name__ == "__main__":
    main()
