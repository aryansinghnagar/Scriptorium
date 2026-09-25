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

import argparse
import json
import logging
import os
import sys
from pathlib import Path

try:
    import lib._bootstrap  # noqa: F401
except ImportError:
    import _bootstrap  # noqa: F401

logger = logging.getLogger("arcanum.config")

CONFIG_DIR_NAME = "ars-arcanum"
LEGACY_CONFIG_DIR_NAME = "arcanum"
CONFIG_FILE_NAME = "config.json"


def get_config_dir() -> Path:
    """Returns the XDG configuration directory for Ars Arcanum."""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config_home) if xdg_config_home else Path.home() / ".config"
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
        with open(config_path, encoding="utf-8") as f:
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


DOCX_PRESETS = {
    "standard-submission": {
        "name": "Standard Submission (Shunn / Industry)",
        "description": "William Shunn standard manuscript format. Times New Roman 12pt, double-spaced, 1-inch margins, 0.5-inch indent, '#' scene breaks.",
        "font_family": "Times New Roman",
        "font_size_pt": 12.0,
        "line_spacing": 2.0,
        "margin_inches": 1.0,
        "first_line_indent_inches": 0.5,
        "scene_break_symbol": "#",
        "page_break_chapters": True,
        "include_header_slug": True,
    },
    "modern-manuscript": {
        "name": "Modern Manuscript",
        "description": "Clean modern editorial layout. Georgia 11.5pt, 1.35 line spacing, 1-inch margins, 0.35-inch indent, '* * *' scene breaks.",
        "font_family": "Georgia",
        "font_size_pt": 11.5,
        "line_spacing": 1.35,
        "margin_inches": 1.0,
        "first_line_indent_inches": 0.35,
        "scene_break_symbol": "* * *",
        "page_break_chapters": True,
        "include_header_slug": True,
    },
    "classic-trade": {
        "name": "Classic Literary & Trade",
        "description": "Classic book proportions. EB Garamond 12pt, 1.5 line spacing, 1-inch margins, 0.5-inch indent.",
        "font_family": "EB Garamond",
        "font_size_pt": 12.0,
        "line_spacing": 1.5,
        "margin_inches": 1.0,
        "first_line_indent_inches": 0.5,
        "scene_break_symbol": "* * *",
        "page_break_chapters": True,
        "include_header_slug": False,
    },
    "custom": {
        "name": "Custom User Formatting",
        "description": "User-customized manuscript typography and spacing.",
        "font_family": "Times New Roman",
        "font_size_pt": 12.0,
        "line_spacing": 2.0,
        "margin_inches": 1.0,
        "first_line_indent_inches": 0.5,
        "scene_break_symbol": "#",
        "page_break_chapters": True,
        "include_header_slug": True,
    }
}


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


def get_active_docx_preset_name() -> str:
    """Returns the name of the currently active DOCX preset."""
    cfg = load_config()
    docx_cfg = cfg.get("docx_formatting", {})
    preset = docx_cfg.get("active_preset", "standard-submission")
    if preset not in DOCX_PRESETS:
        preset = "standard-submission"
    return preset


def get_docx_config() -> dict:
    """Returns the resolved DOCX formatting dictionary."""
    cfg = load_config()
    docx_cfg = cfg.get("docx_formatting", {})
    preset_name = docx_cfg.get("active_preset", "standard-submission")
    base = dict(DOCX_PRESETS.get(preset_name, DOCX_PRESETS["standard-submission"]))
    base["active_preset"] = preset_name
    # Merge custom overrides if custom preset or explicit overrides present
    if "custom_overrides" in docx_cfg and isinstance(docx_cfg["custom_overrides"], dict):
        base.update(docx_cfg["custom_overrides"])
    return base


def set_docx_preset(preset_name: str) -> bool:
    """Sets the active DOCX formatting preset."""
    if preset_name not in DOCX_PRESETS:
        logger.error("Unknown DOCX preset: %s", preset_name)
        return False
    cfg = load_config()
    if "docx_formatting" not in cfg or not isinstance(cfg["docx_formatting"], dict):
        cfg["docx_formatting"] = {}
    cfg["docx_formatting"]["active_preset"] = preset_name
    return save_config(cfg)


def set_docx_option(key: str, val) -> bool:
    """Sets a specific DOCX formatting option."""
    cfg = load_config()
    if "docx_formatting" not in cfg or not isinstance(cfg["docx_formatting"], dict):
        cfg["docx_formatting"] = {}
    if "custom_overrides" not in cfg["docx_formatting"] or not isinstance(cfg["docx_formatting"]["custom_overrides"], dict):
        cfg["docx_formatting"]["custom_overrides"] = {}
    cfg["docx_formatting"]["custom_overrides"][key] = val
    cfg["docx_formatting"]["active_preset"] = "custom"
    return save_config(cfg)


def list_docx_presets() -> dict:
    """Returns all available DOCX presets."""
    return DOCX_PRESETS


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

    # docx-preset subcommand
    preset_parser = subparsers.add_parser("docx-preset", help="Manage DOCX formatting presets")
    preset_parser.add_argument("preset", nargs="?", help="Preset name to activate (standard-submission, modern-manuscript, classic-trade, custom)")

    # docx-presets list subcommand
    subparsers.add_parser("docx-presets", help="List all available DOCX formatting presets")

    # docx-config subcommand
    dcfg_parser = subparsers.add_parser("docx-config", help="View or set DOCX formatting options")
    dcfg_parser.add_argument("key", nargs="?", help="Option key (e.g. font_family, font_size_pt, line_spacing, margin_inches)")
    dcfg_parser.add_argument("value", nargs="?", help="Option value")

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
                print("[!] Error saving configuration.", file=sys.stderr)
                sys.exit(1)
        elif args.action == "clear":
            if clear_backup_dest():
                print("[CONFIG] Secure backup destination cleared.")
                sys.exit(0)
            else:
                print("[!] Error updating configuration.", file=sys.stderr)
                sys.exit(1)

    elif args.subcommand == "docx-preset":
        if args.preset:
            if set_docx_preset(args.preset):
                print(f"[CONFIG] Active DOCX preset set to: {args.preset}")
                sys.exit(0)
            else:
                print(f"[!] Error: Invalid preset '{args.preset}'. Available: {', '.join(DOCX_PRESETS.keys())}", file=sys.stderr)
                sys.exit(1)
        else:
            print(get_active_docx_preset_name())
            sys.exit(0)

    elif args.subcommand == "docx-presets":
        active = get_active_docx_preset_name()
        print("=== Ars Arcanum DOCX Formatting Presets ===")
        for pid, info in DOCX_PRESETS.items():
            mark = " (active)" if pid == active else ""
            print(f"- {pid}{mark}: {info['name']}")
            print(f"    Font: {info['font_family']} {info['font_size_pt']}pt | Spacing: {info['line_spacing']}x | Margins: {info['margin_inches']}\"")
            print(f"    Description: {info['description']}")
        sys.exit(0)

    elif args.subcommand == "docx-config":
        if args.key and args.value is not None:
            val = args.value
            # Type cast numbers
            try:
                val = float(val) if "." in val else int(val)
            except ValueError:
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
            if set_docx_option(args.key, val):
                print(f"[CONFIG] DOCX option '{args.key}' set to: {val}")
                sys.exit(0)
            else:
                print("[!] Error updating DOCX option.", file=sys.stderr)
                sys.exit(1)
        elif args.key:
            cfg = get_docx_config()
            if args.key in cfg:
                print(cfg[args.key])
                sys.exit(0)
            else:
                print(f"[!] Key '{args.key}' not found in DOCX configuration.", file=sys.stderr)
                sys.exit(1)
        else:
            print(json.dumps(get_docx_config(), indent=2))
            sys.exit(0)


if __name__ == "__main__":
    main()
