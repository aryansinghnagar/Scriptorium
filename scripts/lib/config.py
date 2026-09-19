#!/usr/bin/env python3
"""
Ars Arcanum Configuration Engine (scripts/lib/config.py)
========================================================
Manages local user preferences and global configuration in standard XDG directories
(~/.config/ars-arcanum/config.json).

Provides programmatic API and CLI commands for managing:
- Secure external backup destinations
- Default trim sizes and export presets
- Active author profiles
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

logger = logging.getLogger("arcanum.config")

CONFIG_DIR_NAME = "ars-arcanum"
LEGACY_CONFIG_DIR_NAME = "arcanum"
CONFIG_FILE_NAME = "config.json"


def get_config_dir() -> Path:
    """Returns the XDG configuration directory for Ars Arcanum."""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        base = Path(xdg_config_home)
    else:
        base = Path.home() / ".config"
    return base / CONFIG_DIR_NAME


def get_config_file_path() -> Path:
    """Returns the primary configuration file path, checking legacy fallback if needed."""
    primary_dir = get_config_dir()
    primary_file = primary_dir / CONFIG_FILE_NAME
    if primary_file.is_file():
        return primary_file

    # Check legacy fallback
    legacy_dir = primary_dir.parent / LEGACY_CONFIG_DIR_NAME
    legacy_file = legacy_dir / CONFIG_FILE_NAME
    if legacy_file.is_file():
        return legacy_file

    return primary_file


def load_config() -> dict:
    """Loads configuration dictionary from disk."""
    config_path = get_config_file_path()
    if not config_path.is_file():
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception as e:
        logger.warning("Failed to parse configuration file at %s: %s", config_path, e)
    return {}


def save_config(config_data: dict) -> bool:
    """Saves configuration dictionary to disk with restrictive 0o600 permissions."""
    config_path = get_config_file_path()
    config_dir = config_path.parent
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = config_path.with_suffix(".tmp")
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = os.open(tmp_path, flags, 0o600)
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        try:
            os.chmod(tmp_path, 0o600)
        except OSError:
            pass
        tmp_path.replace(config_path)
        return True
    except Exception as e:
        logger.error("Failed to write configuration file at %s: %s", config_path, e)
        return False


def get_backup_dest() -> str:
    """Returns configured external secure backup destination path or empty string."""
    cfg = load_config()
    dest = cfg.get("secure_backup_destination") or cfg.get("backup_destination") or ""
    return str(dest).strip()


def set_backup_dest(dest_path: str) -> bool:
    """Sets and persists the secure external backup destination."""
    cfg = load_config()
    clean_path = str(Path(dest_path).expanduser().resolve())
    cfg["secure_backup_destination"] = clean_path
    return save_config(cfg)


def clear_backup_dest() -> bool:
    """Clears the configured secure external backup destination."""
    cfg = load_config()
    cfg.pop("secure_backup_destination", None)
    cfg.pop("backup_destination", None)
    return save_config(cfg)


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Configuration Tool")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # backup-dest subcommand
    bd_parser = subparsers.add_parser("backup-dest", help="Manage secure backup destination")
    bd_sub = bd_parser.add_subparsers(dest="action", required=True)

    bd_sub.add_parser("get", help="Print current secure backup destination")

    set_p = bd_sub.add_parser("set", help="Set secure backup destination")
    set_p.add_argument("path", help="Absolute or relative path to secure backup directory")

    bd_sub.add_parser("clear", help="Clear configured secure backup destination")

    args = parser.parse_args()

    if args.subcommand == "backup-dest":
        if args.action == "get":
            dest = get_backup_dest()
            if dest:
                print(dest)
                sys.exit(0)
            else:
                sys.exit(1)
        elif args.action == "set":
            if set_backup_dest(args.path):
                print(f"[CONFIG] Secure backup destination set to: {get_backup_dest()}")
                sys.exit(0)
            else:
                print(f"[!] Error saving configuration.", file=sys.stderr)
                sys.exit(1)
        elif args.action == "clear":
            if clear_backup_dest():
                print("[CONFIG] Secure backup destination cleared.")
                sys.exit(0)
            else:
                print(f"[!] Error updating configuration.", file=sys.stderr)
                sys.exit(1)


if __name__ == "__main__":
    main()
