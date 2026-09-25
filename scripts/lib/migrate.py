#!/usr/bin/env python3
"""
Ars Arcanum Schema & Project Migration Engine (scripts/lib/migrate.py)
Upgrades older project vaults, legacy folder layouts, and manifests to schema_version 1.0.
"""

import argparse
import json
import logging
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("arcanum.migrate")

CURRENT_SCHEMA_VERSION = "1.0"


REQUIRED_GITIGNORE_ENTRIES = [
    ".arcanum_cache.json",
    ".sync_state.json",
    "*.lock",
]


def ensure_gitignore_entries(repo_path: Path) -> list[str]:
    """Ensures that repository .gitignore includes cache, sync state, and lock patterns."""
    actions = []
    gi_path = repo_path / ".gitignore"
    if not gi_path.is_file():
        return actions

    content = gi_path.read_text(encoding="utf-8", errors="replace")
    missing = [entry for entry in REQUIRED_GITIGNORE_ENTRIES if entry not in content]
    if missing:
        updated = content.rstrip() + "\n# Ars Arcanum Cache and Sync State\n" + "\n".join(missing) + "\n"
        atomic_write(gi_path, updated)
        actions.append(f"Added {', '.join(missing)} to .gitignore")
    return actions


def migrate_universe(u_path: Path) -> list[str]:
    """Migrates a Universe root to schema_version 1.0."""
    actions = []
    manifest = u_path / "universe.yaml"
    if not manifest.is_file():
        content = f'schema_version: "{CURRENT_SCHEMA_VERSION}"\nname: "{u_path.name}"\ndescription: "Narrative Universe."\n'
        atomic_write(manifest, content)
        actions.append(f"Created universe.yaml with schema_version: {CURRENT_SCHEMA_VERSION}")
    else:
        text = manifest.read_text(encoding="utf-8", errors="replace")
        if "schema_version:" not in text:
            updated = f'schema_version: "{CURRENT_SCHEMA_VERSION}"\n' + text
            atomic_write(manifest, updated)
            actions.append(f"Added schema_version: {CURRENT_SCHEMA_VERSION} to universe.yaml")
    actions.extend(ensure_gitignore_entries(u_path))
    return actions


def migrate_world(w_path: Path) -> list[str]:
    """Migrates a World Vault to schema_version 1.0."""
    actions = []
    
    # 1. Legacy folder migration
    legacy_bak = w_path / "05-Backups"
    modern_bak = w_path / "Backups"
    if legacy_bak.is_dir() and not modern_bak.is_dir():
        legacy_bak.rename(modern_bak)
        actions.append("Renamed legacy 05-Backups/ to Backups/")

    # 2. Legacy manifest migration (scriptorium.yaml -> world.yaml)
    legacy_manifest = w_path / "scriptorium.yaml"
    modern_manifest = w_path / "world.yaml"
    if legacy_manifest.is_file() and not modern_manifest.is_file():
        content = legacy_manifest.read_text(encoding="utf-8", errors="replace")
        if "schema_version:" not in content:
            content = f'schema_version: "{CURRENT_SCHEMA_VERSION}"\n' + content
        atomic_write(modern_manifest, content)
        actions.append("Migrated scriptorium.yaml to world.yaml")
    elif modern_manifest.is_file():
        text = modern_manifest.read_text(encoding="utf-8", errors="replace")
        if "schema_version:" not in text:
            updated = f'schema_version: "{CURRENT_SCHEMA_VERSION}"\n' + text
            atomic_write(modern_manifest, updated)
            actions.append(f"Added schema_version: {CURRENT_SCHEMA_VERSION} to world.yaml")
    else:
        content = f'schema_version: "{CURRENT_SCHEMA_VERSION}"\nname: "{w_path.name}"\ndescription: "World Lore Vault."\n'
        atomic_write(modern_manifest, content)
        actions.append(f"Created world.yaml with schema_version: {CURRENT_SCHEMA_VERSION}")

    # 3. Ensure gitignore entries
    actions.extend(ensure_gitignore_entries(w_path))
    return actions


def migrate_manuscript(m_path: Path) -> list[str]:
    """Migrates a Manuscript project to schema_version 1.0."""
    actions = []
    
    # 1. Legacy folder migrations
    legacy_pub = m_path / "04-Publishing"
    modern_exp = m_path / "Exports"
    if legacy_pub.is_dir() and not modern_exp.is_dir():
        legacy_pub.rename(modern_exp)
        actions.append("Renamed legacy 04-Publishing/ to Exports/")

    legacy_bak = m_path / "05-Backups"
    modern_bak = m_path / "Backups"
    if legacy_bak.is_dir() and not modern_bak.is_dir():
        legacy_bak.rename(modern_bak)
        actions.append("Renamed legacy 05-Backups/ to Backups/")

    # 2. Manifest migration
    manifest = m_path / "manuscript.yaml"
    if manifest.is_file():
        text = manifest.read_text(encoding="utf-8", errors="replace")
        if "schema_version:" not in text:
            updated = f'schema_version: "{CURRENT_SCHEMA_VERSION}"\n' + text
            atomic_write(manifest, updated)
            actions.append(f"Added schema_version: {CURRENT_SCHEMA_VERSION} to manuscript.yaml")
    else:
        content = f'schema_version: "{CURRENT_SCHEMA_VERSION}"\ntitle: "{m_path.name}"\nauthor: "Author"\n'
        atomic_write(manifest, content)
        actions.append(f"Created manuscript.yaml with schema_version: {CURRENT_SCHEMA_VERSION}")

    # 3. Ensure gitignore entries
    actions.extend(ensure_gitignore_entries(m_path))
    return actions


def migrate_project(target_path: Path) -> dict:
    """Detects and migrates project at target_path."""
    tpath = Path(target_path).resolve()
    if not tpath.is_dir():
        raise ValueError(f"Target path {tpath} is not a valid directory.")

    results = {
        "target": str(tpath),
        "type": "unknown",
        "actions": [],
        "success": True
    }

    if (tpath / "universe.yaml").is_file() or (tpath / "Universe-Index.md").is_file():
        results["type"] = "universe"
        results["actions"].extend(migrate_universe(tpath))
        # Migrate child worlds
        for child in tpath.iterdir():
            if child.is_dir() and not child.name.startswith(".") and ((child / "Characters").is_dir() or (child / "world.yaml").is_file()):
                w_actions = migrate_world(child)
                if w_actions:
                    results["actions"].extend([f"[{child.name}] {a}" for a in w_actions])

    elif (tpath / "Characters").is_dir() or (tpath / "world.yaml").is_file() or (tpath / "scriptorium.yaml").is_file():
        results["type"] = "world"
        results["actions"].extend(migrate_world(tpath))

    elif (tpath / "manuscript.yaml").is_file() or (tpath / "Book-01").is_dir() or (tpath / "nwProject.nwx").is_file():
        results["type"] = "manuscript"
        results["actions"].extend(migrate_manuscript(tpath))
    else:
        # Check subdirectories
        for sub in tpath.iterdir():
            if sub.is_dir() and not sub.name.startswith("."):
                try:
                    sub_res = migrate_project(sub)
                    if sub_res["actions"]:
                        results["actions"].extend([f"[{sub.name}] {a}" for a in sub_res["actions"]])
                except Exception:
                    pass

    return results


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Project Migration Engine")
    parser.add_argument("path", nargs="?", default=".", help="Path to Universe, World, or Manuscript directory (default: current dir)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    target = Path(args.path)
    res = migrate_project(target)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("=== Ars Arcanum Migration Engine ===")
        print(f"Target:  {res['target']}")
        print(f"Type:    {res['type']}")
        if res["actions"]:
            print("Applied Migrations:")
            for a in res["actions"]:
                print(f"  ✓ {a}")
        else:
            print("Status:  Already up-to-date with schema_version 1.0.")


if __name__ == "__main__":
    main()
