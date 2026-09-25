#!/usr/bin/env python3
"""
Ars Arcanum Speculative Fiction Plugin Marketplace Engine
(scripts/lib/plugin_market.py)
================================================================================
Zero-dependency, 100% offline curated plugin catalog, package verification,
and sandbox installation manager for community-crafted speculative fiction plugins.

Capabilities:
1. Catalog Inspection & Discovery:
   - Searches local curated `configs/plugin_catalog.json` and user catalogs.
   - Filters by category (craft, lore, speculative, continuity, audit) and tags.
2. Integrity Verification:
   - Validates plugin schemas, manifests, and Python hook syntax prior to installation.
3. Safe User-Space & Workspace Installation:
   - Atomically installs plugins into workspace `configs/plugins/` or user `~/.config/ars-arcanum/plugins/`.
   - Verifies dynamic loading compatibility via `PluginManager`.
4. Clean Uninstallation:
   - Safely removes installed marketplace plugins without residual artifacts.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import ast
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import PROJECT_ROOT, atomic_write, sanitize_identifier
    from lib.plugins import VALID_CATEGORIES, VALID_HOOKS, PluginManager
except ImportError:
    try:
        from _bootstrap import PROJECT_ROOT, atomic_write, sanitize_identifier
        from plugins import VALID_CATEGORIES, VALID_HOOKS, PluginManager
    except ImportError:
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

        def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(content, encoding=encoding)
            os.replace(tmp, path)

        def sanitize_identifier(name: str) -> str:
            import re
            return re.sub(r"[^A-Za-z0-9_-]", "_", name)

        VALID_CATEGORIES = {"craft", "lore", "continuity", "format", "audit", "speculative", "general"}
        VALID_HOOKS = {"validate_entity", "validate_manuscript", "custom_metric", "export_transform"}
        PluginManager = None  # type: ignore

logger = logging.getLogger("arcanum.market")


def find_default_catalog_path() -> Path:
    """Locates the default plugin catalog JSON file in repository or user configs."""
    candidates = [
        PROJECT_ROOT / "configs" / "plugin_catalog.json",
        Path.home() / ".config" / "ars-arcanum" / "plugin_catalog.json",
        Path.cwd() / "configs" / "plugin_catalog.json",
        Path.cwd() / "plugin_catalog.json",
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    return candidates[0]


def load_marketplace_catalog(catalog_path: Path | str | None = None) -> dict[str, Any]:
    """Loads and returns the parsed JSON catalog."""
    path = Path(catalog_path) if catalog_path else find_default_catalog_path()
    if not path.is_file():
        raise FileNotFoundError(f"Plugin marketplace catalog not found at '{path}'")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def list_marketplace_plugins(
    category: str | None = None,
    query: str | None = None,
    catalog_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Lists plugins available in the marketplace, filtered by category or search query."""
    catalog = load_marketplace_catalog(catalog_path)
    plugins = catalog.get("plugins", [])

    filtered = []
    q = query.lower().strip() if query else None

    for p in plugins:
        # Category filter
        if category and p.get("category", "").lower() != category.lower():
            continue

        # Search query filter (matches ID, name, description, or tags)
        if q:
            match_id = q in p.get("id", "").lower()
            match_name = q in p.get("name", "").lower()
            match_desc = q in p.get("description", "").lower()
            match_tags = any(q in t.lower() for t in p.get("tags", []))
            if not (match_id or match_name or match_desc or match_tags):
                continue

        filtered.append(p)

    return filtered


def get_marketplace_plugin(
    plugin_id: str,
    catalog_path: Path | str | None = None,
) -> dict[str, Any] | None:
    """Retrieves detailed catalog record for a specific plugin ID."""
    clean_id = sanitize_identifier(plugin_id)
    plugins = list_marketplace_plugins(catalog_path=catalog_path)
    for p in plugins:
        if p.get("id") == clean_id:
            return p
    return None


def verify_catalog_integrity(catalog_path: Path | str | None = None) -> tuple[bool, list[str]]:
    """
    Validates structural correctness and syntax of all plugins declared in the catalog.
    Returns (is_valid, list_of_issues).
    """
    issues: list[str] = []
    try:
        catalog = load_marketplace_catalog(catalog_path)
    except Exception as e:
        return False, [f"Failed to load catalog: {e}"]

    plugins = catalog.get("plugins", [])
    if not plugins:
        issues.append("Catalog contains no plugin entries.")

    seen_ids = set()
    for idx, p in enumerate(plugins, 1):
        pid = p.get("id")
        if not pid:
            issues.append(f"Plugin #{idx} missing required 'id' field.")
            continue
        if pid in seen_ids:
            issues.append(f"Duplicate plugin ID '{pid}' detected.")
        seen_ids.add(pid)

        # Validate category
        cat = p.get("category", "")
        if cat not in VALID_CATEGORIES:
            issues.append(f"Plugin '{pid}' has invalid category '{cat}'.")

        # Validate hooks
        hooks = p.get("hooks", [])
        for h in hooks:
            if h not in VALID_HOOKS:
                issues.append(f"Plugin '{pid}' declares unknown hook '{h}'.")

        # Validate files payload
        files = p.get("files", {})
        if not files:
            issues.append(f"Plugin '{pid}' contains no files payload.")
            continue

        if "plugin.json" not in files:
            issues.append(f"Plugin '{pid}' missing 'plugin.json' manifest in files.")
        else:
            try:
                manifest_data = json.loads(files["plugin.json"])
                if manifest_data.get("id") != pid:
                    issues.append(f"Plugin '{pid}' manifest ID mismatch: '{manifest_data.get('id')}'.")
            except Exception as e:
                issues.append(f"Plugin '{pid}' manifest JSON parse error: {e}")

        if "plugin.py" in files:
            try:
                ast.parse(files["plugin.py"])
            except SyntaxError as e:
                issues.append(f"Plugin '{pid}' python syntax error in plugin.py: {e}")

    return len(issues) == 0, issues


def get_default_install_destination(plugin_id: str, in_workspace: bool = True) -> Path:
    """Returns target directory for plugin installation."""
    clean_id = sanitize_identifier(plugin_id)
    if in_workspace:
        return PROJECT_ROOT / "configs" / "plugins" / clean_id
    return Path.home() / ".config" / "ars-arcanum" / "plugins" / clean_id


def install_marketplace_plugin(
    plugin_id: str,
    target_dir: Path | str | None = None,
    catalog_path: Path | str | None = None,
    force: bool = False,
) -> tuple[bool, str]:
    """
    Installs a curated plugin from the catalog into workspace or user directory.
    Returns (success, message).
    """
    clean_id = sanitize_identifier(plugin_id)
    plugin_data = get_marketplace_plugin(clean_id, catalog_path=catalog_path)
    if not plugin_data:
        return False, f"Plugin '{clean_id}' not found in marketplace catalog."

    dest_dir = Path(target_dir).resolve() if target_dir else get_default_install_destination(clean_id)

    if dest_dir.exists() and not force:
        return False, f"Destination directory '{dest_dir}' already exists. Use --force to overwrite."

    dest_dir.mkdir(parents=True, exist_ok=True)

    files = plugin_data.get("files", {})
    if not files:
        return False, f"Plugin '{clean_id}' has no file contents defined in catalog."

    # Write plugin files atomically
    for filename, content in files.items():
        # Prevent path traversal in catalog file definitions
        safe_name = Path(filename).name
        file_path = dest_dir / safe_name
        atomic_write(file_path, content)

    # Verify installation with PluginManager if available
    if PluginManager is not None:
        mgr = PluginManager(search_paths=[dest_dir.parent])
        mgr.discover_plugins()
        installed = mgr.get_plugin(clean_id)
        if not installed:
            return False, f"Plugin files written to '{dest_dir}', but PluginManager failed discovery."

    return True, f"Successfully installed '{plugin_data.get('name', clean_id)}' (v{plugin_data.get('version', '1.0.0')}) to: {dest_dir}"


def uninstall_marketplace_plugin(
    plugin_id: str,
    target_dir: Path | str | None = None,
) -> tuple[bool, str]:
    """
    Uninstalls a plugin by removing its directory.
    Returns (success, message).
    """
    clean_id = sanitize_identifier(plugin_id)
    dest_dir = Path(target_dir).resolve() if target_dir else get_default_install_destination(clean_id)

    if not dest_dir.exists() or not dest_dir.is_dir():
        # Also check user home directory
        user_dest = Path.home() / ".config" / "ars-arcanum" / "plugins" / clean_id
        if user_dest.exists() and user_dest.is_dir():
            dest_dir = user_dest
        else:
            return False, f"Plugin '{clean_id}' is not installed at '{dest_dir}'."

    try:
        shutil.rmtree(dest_dir)
        return True, f"Successfully uninstalled plugin '{clean_id}' from: {dest_dir}"
    except Exception as e:
        return False, f"Failed to delete directory '{dest_dir}': {e}"


# ==============================================================================
# CLI Entry Point
# ==============================================================================

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arcanum market",
        description="Ars Arcanum Speculative Fiction Plugin Marketplace",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Marketplace command")

    # list / search
    p_list = subparsers.add_parser("list", help="List plugins in marketplace")
    p_list.add_argument("-c", "--category", help="Filter by category (craft, lore, speculative, continuity, audit)")
    p_list.add_argument("-q", "--query", help="Filter by search query")
    p_list.add_argument("--json", action="store_true", help="Output results in JSON format")
    p_list.add_argument("--catalog", help="Custom catalog JSON file path")

    p_search = subparsers.add_parser("search", help="Search marketplace for keywords")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("-c", "--category", help="Filter by category")
    p_search.add_argument("--json", action="store_true", help="Output results in JSON format")
    p_search.add_argument("--catalog", help="Custom catalog JSON file path")

    # info
    p_info = subparsers.add_parser("info", help="Display details for a plugin")
    p_info.add_argument("plugin_id", help="ID of plugin")
    p_info.add_argument("--catalog", help="Custom catalog JSON file path")

    # install
    p_install = subparsers.add_parser("install", help="Install a marketplace plugin")
    p_install.add_argument("plugin_id", help="ID of plugin to install")
    p_install.add_argument("-t", "--target", help="Custom installation target directory")
    p_install.add_argument("-f", "--force", action="store_true", help="Overwrite existing installation")
    p_install.add_argument("--catalog", help="Custom catalog JSON file path")

    # uninstall
    p_uninstall = subparsers.add_parser("uninstall", help="Uninstall an installed plugin")
    p_uninstall.add_argument("plugin_id", help="ID of plugin to uninstall")
    p_uninstall.add_argument("-t", "--target", help="Custom installation target directory")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify integrity of marketplace catalog")
    p_verify.add_argument("--catalog", help="Custom catalog JSON file path")

    args = parser.parse_args(argv)

    if not args.subcommand or args.subcommand in ("list", "search"):
        cat = getattr(args, "category", None)
        query = getattr(args, "query", None)
        catalog_path = getattr(args, "catalog", None)
        as_json = getattr(args, "json", False)

        plugins = list_marketplace_plugins(category=cat, query=query, catalog_path=catalog_path)

        if as_json:
            print(json.dumps(plugins, indent=2))
            return 0

        print(f"Ars Arcanum Curated Plugin Marketplace ({len(plugins)} available):\n")
        print(f"{'ID':<24} {'Category':<14} {'Version':<10} {'Name / Description'}")
        print("-" * 80)
        for p in plugins:
            cat_badge = f"[{p.get('category', 'general').upper()}]"
            desc = p.get('description', '')
            short_desc = (desc[:45] + '...') if len(desc) > 45 else desc
            print(f"{p.get('id', ''):<24} {cat_badge:<14} {p.get('version', '1.0.0'):<10} {p.get('name', '')}")
            if short_desc:
                print(f"  └─ {short_desc}")
        print("\nInstall with: arcanum market install <ID>")
        return 0

    elif args.subcommand == "info":
        p = get_marketplace_plugin(args.plugin_id, catalog_path=args.catalog)
        if not p:
            print(f"Error: Plugin '{args.plugin_id}' not found in marketplace catalog.", file=sys.stderr)
            return 1

        print(f"Plugin: {p.get('name')} ({p.get('id')})")
        print(f"Version:     {p.get('version', '1.0.0')}")
        print(f"Author:      {p.get('author', 'Anonymous')}")
        print(f"Category:    {p.get('category', 'general')}")
        print(f"Min Arcanum: {p.get('min_arcanum_version', '1.6.0')}")
        print(f"Hooks:       {', '.join(p.get('hooks', []))}")
        print(f"Tags:        {', '.join(p.get('tags', []))}")
        print("\nDescription:")
        print(f"  {p.get('description', 'No description provided.')}")
        print("\nFiles in package:")
        for fname in p.get("files", {}):
            print(f"  - {fname}")
        return 0

    elif args.subcommand == "install":
        success, msg = install_marketplace_plugin(
            plugin_id=args.plugin_id,
            target_dir=args.target,
            catalog_path=args.catalog,
            force=args.force,
        )
        if success:
            print(msg)
            return 0
        else:
            print(f"Error: {msg}", file=sys.stderr)
            return 1

    elif args.subcommand == "uninstall":
        success, msg = uninstall_marketplace_plugin(
            plugin_id=args.plugin_id,
            target_dir=args.target,
        )
        if success:
            print(msg)
            return 0
        else:
            print(f"Error: {msg}", file=sys.stderr)
            return 1

    elif args.subcommand == "verify":
        is_valid, issues = verify_catalog_integrity(catalog_path=args.catalog)
        if is_valid:
            print("✓ Marketplace catalog integrity verified: 0 errors detected.")
            return 0
        else:
            print("✗ Marketplace catalog integrity verification failed:", file=sys.stderr)
            for issue in issues:
                print(f"  - {issue}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
