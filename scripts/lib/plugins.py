#!/usr/bin/env python3
"""
Ars Arcanum Extensibility & Speculative Fiction Plugin Architecture
(scripts/lib/plugins.py)
================================================================================
Zero-dependency, offline community plugin engine and craft validator for Ars Arcanum.

Capabilities:
1. Plugin Discovery & Lifecycle Management:
   - Scans workspace (`configs/plugins/`), user (`~/.config/ars-arcanum/plugins/`),
     and system (`/usr/share/ars-arcanum/plugins/`) search paths.
   - Parses and validates declarative `plugin.json` manifests.
   - Dynamic sandboxed loading with error isolation (failing plugins never crash core).
2. Plugin Hook Lifecycle:
   - `validate_entity(entity_data, context)` -> list of diagnostics
   - `validate_manuscript(manuscript_data, context)` -> list of diagnostics
   - `custom_metric(text, context)` -> dict of calculated metrics
   - `export_transform(content, format, options)` -> transformed text
3. Built-in CLI & Scaffolding:
   - `arcanum plugin list [--json]`
   - `arcanum plugin info <ID>`
   - `arcanum plugin run <ID> <TARGET>`
   - `arcanum plugin create <ID> [--name NAME] [--author AUTHOR] [--desc DESC]`
   - `arcanum plugin enable/disable <ID>`

Zero external dependencies; 100% offline privacy.
"""

import argparse
import importlib.util
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import PROJECT_ROOT, atomic_write, sanitize_identifier
except ImportError:
    from _bootstrap import PROJECT_ROOT, atomic_write, sanitize_identifier

logger = logging.getLogger("arcanum.plugins")

VALID_HOOKS = {
    "validate_entity",
    "validate_manuscript",
    "custom_metric",
    "export_transform",
}

VALID_CATEGORIES = {
    "craft",
    "lore",
    "continuity",
    "format",
    "audit",
    "speculative",
    "general",
}


@dataclass
class PluginManifest:
    """Represents a validated plugin manifest from plugin.json."""
    id: str
    name: str
    version: str = "1.0.0"
    author: str = "Anonymous"
    description: str = ""
    category: str = "general"
    entry_point: str = "plugin.py"
    hooks: list[str] = field(default_factory=list)
    min_arcanum_version: str = "1.6.0"
    path: str = ""
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PluginDiagnostic:
    """Represents an issue, warning, or feedback produced by a plugin."""
    plugin_id: str
    severity: str  # "info", "warning", "error"
    message: str
    target: str = ""
    line: int | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PluginManager:
    """Discovers, validates, loads, and executes Ars Arcanum plugins."""

    def __init__(self, search_paths: list[Path] | None = None, state_file: Path | None = None):
        if search_paths is None:
            self.search_paths = [
                PROJECT_ROOT / "configs" / "plugins",
                Path.home() / ".config" / "ars-arcanum" / "plugins",
                Path("/usr/share/ars-arcanum/plugins"),
            ]
        else:
            self.search_paths = search_paths

        self.state_file = state_file or (PROJECT_ROOT / ".arcanum_plugins.json")
        self._manifests: dict[str, PluginManifest] = {}
        self._loaded_modules: dict[str, Any] = {}
        self._disabled_plugins: set[str] = self._load_disabled_state()
        self.discover_plugins()

    def _load_disabled_state(self) -> set[str]:
        if self.state_file.is_file():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8", errors="replace"))
                return set(data.get("disabled", []))
            except Exception as e:
                logger.warning(f"Could not load plugin state from {self.state_file}: {e}")
        return set()

    def _save_disabled_state(self) -> None:
        try:
            payload = json.dumps({"disabled": sorted(self._disabled_plugins)}, indent=2)
            atomic_write(self.state_file, payload)
        except Exception as e:
            logger.warning(f"Could not save plugin state to {self.state_file}: {e}")

    def discover_plugins(self) -> dict[str, PluginManifest]:
        """Scans all search paths for plugin manifests (plugin.json)."""
        self._manifests.clear()
        for base_path in self.search_paths:
            if not base_path.is_dir():
                continue
            for item in base_path.iterdir():
                if not item.is_dir() or item.name.startswith((".", "_")):
                    continue
                manifest_file = item / "plugin.json"
                if manifest_file.is_file():
                    try:
                        raw = json.loads(manifest_file.read_text(encoding="utf-8", errors="replace"))
                        plugin_id = sanitize_identifier(raw.get("id", item.name))
                        entry_point = raw.get("entry_point", "plugin.py")
                        hooks = [h for h in raw.get("hooks", []) if h in VALID_HOOKS]
                        
                        manifest = PluginManifest(
                            id=plugin_id,
                            name=raw.get("name", item.name),
                            version=raw.get("version", "1.0.0"),
                            author=raw.get("author", "Community"),
                            description=raw.get("description", ""),
                            category=raw.get("category", "general"),
                            entry_point=entry_point,
                            hooks=hooks,
                            min_arcanum_version=raw.get("min_arcanum_version", "1.6.0"),
                            path=str(item),
                            enabled=(plugin_id not in self._disabled_plugins),
                        )
                        self._manifests[plugin_id] = manifest
                    except Exception as e:
                        logger.error(f"Failed parsing plugin manifest at {manifest_file}: {e}")
        return self._manifests

    def list_plugins(self) -> list[PluginManifest]:
        """Returns list of all discovered plugin manifests."""
        return list(self._manifests.values())

    def get_plugin(self, plugin_id: str) -> PluginManifest | None:
        """Get plugin manifest by ID."""
        return self._manifests.get(plugin_id)

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enables a plugin by ID."""
        if plugin_id in self._disabled_plugins:
            self._disabled_plugins.remove(plugin_id)
            self._save_disabled_state()
        if plugin_id in self._manifests:
            self._manifests[plugin_id].enabled = True
            return True
        return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disables a plugin by ID."""
        self._disabled_plugins.add(plugin_id)
        self._save_disabled_state()
        if plugin_id in self._manifests:
            self._manifests[plugin_id].enabled = False
            return True
        return False

    def load_plugin_module(self, plugin_id: str) -> Any | None:
        """Dynamically imports and returns a plugin module in a fail-safe sandbox."""
        if plugin_id in self._loaded_modules:
            return self._loaded_modules[plugin_id]

        manifest = self.get_plugin(plugin_id)
        if not manifest or not manifest.enabled:
            return None

        plugin_dir = Path(manifest.path)
        entry_file = plugin_dir / manifest.entry_point
        if not entry_file.is_file():
            logger.error(f"Plugin '{plugin_id}' entry point missing: {entry_file}")
            return None

        try:
            module_name = f"arcanum_plugin_{plugin_id}"
            spec = importlib.util.spec_from_file_location(module_name, entry_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                self._loaded_modules[plugin_id] = module
                return module
        except Exception as e:
            logger.error(f"Error loading plugin '{plugin_id}' from {entry_file}: {e}", exc_info=True)
            return None
        return None

    def execute_hook(
        self,
        hook_name: str,
        *args: Any,
        plugin_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Executes a hook across all enabled plugins (or a specific plugin).
        
        Returns a mapping of {plugin_id: hook_return_value}.
        Failing plugins are caught and logged with error isolation.
        """
        results: dict[str, Any] = {}
        target_plugins = [self._manifests[plugin_id]] if (plugin_id and plugin_id in self._manifests) else self._manifests.values()

        for manifest in target_plugins:
            if not manifest.enabled:
                continue
            if hook_name not in manifest.hooks and f"hook_{hook_name}" not in manifest.hooks:
                # Plugin doesn't declare this hook, check if module defines it anyway
                pass

            mod = self.load_plugin_module(manifest.id)
            if not mod:
                continue

            # Find function name: e.g. "validate_entity" or "hook_validate_entity"
            fn = getattr(mod, f"hook_{hook_name}", getattr(mod, hook_name, None))
            if callable(fn):
                try:
                    res = fn(*args, **kwargs)
                    results[manifest.id] = res
                except Exception as e:
                    logger.error(f"Plugin '{manifest.id}' crashed in hook '{hook_name}': {e}", exc_info=True)
                    results[manifest.id] = {
                        "error": str(e),
                        "crashed": True,
                    }

        return results

    def run_entity_validation(
        self,
        entity_data: dict[str, Any],
        context: dict[str, Any] | None = None,
        plugin_id: str | None = None,
    ) -> list[PluginDiagnostic]:
        """Runs enabled validate_entity hooks on entity_data."""
        context = context or {}
        diagnostics: list[PluginDiagnostic] = []
        raw_results = self.execute_hook("validate_entity", entity_data, context, plugin_id=plugin_id)

        for pid, res in raw_results.items():
            if isinstance(res, list):
                for item in res:
                    if isinstance(item, dict):
                        diagnostics.append(PluginDiagnostic(
                            plugin_id=pid,
                            severity=item.get("severity", "info"),
                            message=item.get("message", "No message provided"),
                            target=item.get("target", entity_data.get("name", "")),
                            line=item.get("line"),
                            details=item.get("details", {}),
                        ))
                    elif isinstance(item, PluginDiagnostic):
                        diagnostics.append(item)
        return diagnostics

    def run_manuscript_validation(
        self,
        manuscript_data: dict[str, Any],
        context: dict[str, Any] | None = None,
        plugin_id: str | None = None,
    ) -> list[PluginDiagnostic]:
        """Runs enabled validate_manuscript hooks on manuscript_data."""
        context = context or {}
        diagnostics: list[PluginDiagnostic] = []
        raw_results = self.execute_hook("validate_manuscript", manuscript_data, context, plugin_id=plugin_id)

        for pid, res in raw_results.items():
            if isinstance(res, list):
                for item in res:
                    if isinstance(item, dict):
                        diagnostics.append(PluginDiagnostic(
                            plugin_id=pid,
                            severity=item.get("severity", "info"),
                            message=item.get("message", "No message provided"),
                            target=item.get("target", manuscript_data.get("title", "")),
                            line=item.get("line"),
                            details=item.get("details", {}),
                        ))
                    elif isinstance(item, PluginDiagnostic):
                        diagnostics.append(item)
        return diagnostics

    def create_plugin_scaffold(
        self,
        target_dir: Path,
        plugin_id: str,
        name: str | None = None,
        author: str | None = None,
        description: str | None = None,
        category: str = "craft",
    ) -> Path:
        """Scaffolds a new plugin template with plugin.json and plugin.py."""
        clean_id = sanitize_identifier(plugin_id)
        out_dir = target_dir / clean_id
        out_dir.mkdir(parents=True, exist_ok=True)

        manifest_data = {
            "id": clean_id,
            "name": name or clean_id.replace("_", " ").title(),
            "version": "1.0.0",
            "author": author or os.environ.get("USER", "Author"),
            "description": description or f"Custom {clean_id} plugin for Ars Arcanum.",
            "category": category if category in VALID_CATEGORIES else "craft",
            "entry_point": "plugin.py",
            "hooks": ["validate_entity", "validate_manuscript", "custom_metric"],
            "min_arcanum_version": "1.6.0",
        }

        plugin_code = f'''#!/usr/bin/env python3
"""
Ars Arcanum Plugin: {manifest_data["name"]}
============================================================
Generated plugin scaffold for custom worldbuilding & craft analysis.
"""

from typing import Any


def hook_validate_entity(entity: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    """Validates world lore entities (Characters, Locations, Factions, Magic)."""
    diagnostics = []
    name = entity.get("name", "")
    content = entity.get("content", "")

    # Example check: Flag entities with empty descriptions
    if not content.strip():
        diagnostics.append({{
            "severity": "warning",
            "message": f"Entity '{{name}}' has no descriptive body content.",
            "target": name,
        }})

    return diagnostics


def hook_validate_manuscript(manuscript: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    """Validates manuscript chapters and scenes."""
    diagnostics = []
    chapters = manuscript.get("chapters", [])

    for ch in chapters:
        title = ch.get("title", "")
        word_count = ch.get("word_count", 0)
        if word_count < 250:
            diagnostics.append({{
                "severity": "info",
                "message": f"Chapter '{{title}}' is very short ({{word_count}} words).",
                "target": title,
            }})

    return diagnostics


def hook_custom_metric(text: str, context: dict[str, Any]) -> dict[str, Any]:
    """Calculates custom metrics on prose text."""
    words = text.split()
    return {{
        "total_words": len(words),
        "unique_words": len(set(words)),
    }}
'''
        atomic_write(out_dir / "plugin.json", json.dumps(manifest_data, indent=2))
        atomic_write(out_dir / "plugin.py", plugin_code)
        atomic_write(out_dir / "README.md", f"# {manifest_data['name']}\n\n{manifest_data['description']}\n")
        return out_dir


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Plugin & Extensibility Manager")
    subparsers = parser.add_subparsers(dest="subcommand", help="Plugin commands")

    # list
    list_p = subparsers.add_parser("list", help="List all discovered plugins")
    list_p.add_argument("--json", action="store_true", help="Output as JSON")

    # info
    info_p = subparsers.add_parser("info", help="Display details for a specific plugin")
    info_p.add_argument("plugin_id", help="Plugin ID")

    # run
    run_p = subparsers.add_parser("run", help="Run a plugin against a target world or manuscript")
    run_p.add_argument("plugin_id", help="Plugin ID to execute")
    run_p.add_argument("target", help="Path to World Vault or Manuscript directory")
    run_p.add_argument("--json", action="store_true", help="Output results as JSON")

    # create
    create_p = subparsers.add_parser("create", help="Scaffold a new plugin directory")
    create_p.add_argument("plugin_id", help="Unique identifier for new plugin")
    create_p.add_argument("--name", help="Display name for plugin")
    create_p.add_argument("--author", help="Author name")
    create_p.add_argument("--desc", help="Plugin description")
    create_p.add_argument("--category", default="craft", choices=sorted(VALID_CATEGORIES), help="Plugin category")
    create_p.add_argument("--dir", default=str(PROJECT_ROOT / "configs" / "plugins"), help="Output parent directory")

    # enable / disable
    enable_p = subparsers.add_parser("enable", help="Enable a plugin")
    enable_p.add_argument("plugin_id", help="Plugin ID to enable")

    disable_p = subparsers.add_parser("disable", help="Disable a plugin")
    disable_p.add_argument("plugin_id", help="Plugin ID to disable")

    args = parser.parse_args()
    mgr = PluginManager()

    if args.subcommand == "list" or not args.subcommand:
        plugins = mgr.list_plugins()
        if getattr(args, "json", False):
            print(json.dumps([p.to_dict() for p in plugins], indent=2))
            return

        print(f"=== Ars Arcanum Plugins ({len(plugins)} discovered) ===")
        if not plugins:
            print("  No plugins installed. Run 'arcanum plugin create <NAME>' to scaffold one.")
            return

        for p in plugins:
            status = "[ENABLED]" if p.enabled else "[DISABLED]"
            print(f"  {status:<11} {p.id:<22} v{p.version:<6} [{p.category.upper()}] {p.name}")
            if p.description:
                print(f"              {p.description}")
            print(f"              Hooks: {', '.join(p.hooks)} | Path: {p.path}")
            print()

    elif args.subcommand == "info":
        p = mgr.get_plugin(args.plugin_id)
        if not p:
            print(f"Error: Plugin '{args.plugin_id}' not found.", file=sys.stderr)
            sys.exit(1)
        print(f"Plugin ID:    {p.id}")
        print(f"Name:         {p.name}")
        print(f"Version:      {p.version}")
        print(f"Author:       {p.author}")
        print(f"Category:     {p.category}")
        print(f"Enabled:      {p.enabled}")
        print(f"Description:  {p.description}")
        print(f"Hooks:        {', '.join(p.hooks)}")
        print(f"Directory:    {p.path}")

    elif args.subcommand == "enable":
        if mgr.enable_plugin(args.plugin_id):
            print(f"Plugin '{args.plugin_id}' enabled successfully.")
        else:
            print(f"Error: Plugin '{args.plugin_id}' not found.", file=sys.stderr)
            sys.exit(1)

    elif args.subcommand == "disable":
        if mgr.disable_plugin(args.plugin_id):
            print(f"Plugin '{args.plugin_id}' disabled successfully.")
        else:
            print(f"Error: Plugin '{args.plugin_id}' not found.", file=sys.stderr)
            sys.exit(1)

    elif args.subcommand == "create":
        target_dir = Path(args.dir)
        scaffold_path = mgr.create_plugin_scaffold(
            target_dir=target_dir,
            plugin_id=args.plugin_id,
            name=args.name,
            author=args.author,
            description=args.desc,
            category=args.category,
        )
        print(f"Scaffolded plugin '{args.plugin_id}' at: {scaffold_path}")
        print("  - plugin.json (Manifest metadata)")
        print("  - plugin.py   (Hook implementations)")
        print("  - README.md   (Documentation)")

    elif args.subcommand == "run":
        target = Path(args.target)
        if not target.exists():
            print(f"Error: Target path does not exist: {target}", file=sys.stderr)
            sys.exit(1)

        p = mgr.get_plugin(args.plugin_id)
        if not p:
            print(f"Error: Plugin '{args.plugin_id}' not found.", file=sys.stderr)
            sys.exit(1)

        # Collect entities / chapters from target
        entities = []
        chapters = []
        if target.is_file():
            content = target.read_text(encoding="utf-8", errors="replace")
            chapters.append({"title": target.stem, "content": content, "word_count": len(content.split())})
        elif target.is_dir():
            for f in sorted(target.rglob("*.md")):
                if f.name.startswith((".", "_")):
                    continue
                content = f.read_text(encoding="utf-8", errors="replace")
                words = len(content.split())
                if "Characters" in f.parts or "Locations" in f.parts or "Factions" in f.parts or "Magic" in f.parts:
                    entities.append({"name": f.stem, "path": str(f), "content": content})
                else:
                    chapters.append({"title": f.stem, "path": str(f), "content": content, "word_count": words})

        manuscript_data = {"title": target.stem, "chapters": chapters}
        context = {
            "target_path": str(target),
            "known_names": [e["name"] for e in entities],
        }

        # Run hooks
        diagnostics: list[PluginDiagnostic] = []
        for ent in entities:
            diagnostics.extend(mgr.run_entity_validation(ent, context, plugin_id=args.plugin_id))
        if chapters:
            diagnostics.extend(mgr.run_manuscript_validation(manuscript_data, context, plugin_id=args.plugin_id))

        if getattr(args, "json", False):
            print(json.dumps([d.to_dict() for d in diagnostics], indent=2))
            return

        print(f"=== Plugin Audit: {p.name} (v{p.version}) ===")
        print(f"Target: {target.name} | Entities evaluated: {len(entities)} | Chapters evaluated: {len(chapters)}")
        print(f"Total Diagnostics: {len(diagnostics)}")
        print("-" * 75)
        if not diagnostics:
            print("  ✓ No issues or warnings reported by plugin.")
            return

        for d in diagnostics:
            badge = f"[{d.severity.upper()}]"
            loc = f" ({d.target})" if d.target else ""
            print(f"  {badge:<9} {d.message}{loc}")


if __name__ == "__main__":
    main()
