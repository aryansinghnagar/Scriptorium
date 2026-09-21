#!/usr/bin/env python3
"""
Ars Arcanum UI Controller Layer (scripts/lib/ui_controller.py)
============================================================
Decouples application state management, project discovery, studio engine routing,
and background command execution from the GTK presentation layer.
"""

from dataclasses import dataclass, field
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from lib.registry import get_registry, list_engines, EngineSpec, EngineCategory
    from lib.diagnostics import get_toolchain_diagnostics
except ImportError:
    try:
        from registry import get_registry, list_engines, EngineSpec, EngineCategory
        from diagnostics import get_toolchain_diagnostics
    except ImportError:
        pass


@dataclass
class ProjectInfo:
    name: str
    path: Path
    project_type: str  # "universe", "world", "manuscript"
    universe_name: Optional[str] = None
    last_modified: float = 0.0
    extra: Dict[str, Any] = field(default_factory=dict)


class UIController:
    """Headless state and business logic controller for Ars Arcanum applications."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.home()
        self.active_project: Optional[ProjectInfo] = None

    def discover_universes(self) -> List[ProjectInfo]:
        """Discover narrative universes under ~/Universes/."""
        uni_root = self.base_dir / "Universes"
        results = []
        if uni_root.is_dir():
            for d in sorted(uni_root.iterdir()):
                if d.is_dir() and not d.name.startswith("."):
                    mtime = d.stat().st_mtime
                    results.append(ProjectInfo(
                        name=d.name,
                        path=d,
                        project_type="universe",
                        last_modified=mtime,
                    ))
        return results

    def discover_worlds(self) -> List[ProjectInfo]:
        """Discover World Lore Vaults under ~/Universes/*/00-World-Bible or ~/Worlds/*/."""
        results = []
        # Check ~/Universes/*/
        uni_root = self.base_dir / "Universes"
        if uni_root.is_dir():
            for u in sorted(uni_root.iterdir()):
                if u.is_dir() and not u.name.startswith("."):
                    # Check for worlds inside universe
                    for w in sorted(u.iterdir()):
                        if w.is_dir() and not w.name.startswith("."):
                            if (w / "00-World-Bible").is_dir() or (w / "Characters").is_dir() or (w / "world.yaml").exists():
                                results.append(ProjectInfo(
                                    name=w.name,
                                    path=w,
                                    project_type="world",
                                    universe_name=u.name,
                                    last_modified=w.stat().st_mtime,
                                ))
        # Check standalone ~/Worlds/
        w_root = self.base_dir / "Worlds"
        if w_root.is_dir():
            for w in sorted(w_root.iterdir()):
                if w.is_dir() and not w.name.startswith("."):
                    if (w / "00-World-Bible").is_dir() or (w / "Characters").is_dir() or (w / "world.yaml").exists():
                        results.append(ProjectInfo(
                            name=w.name,
                            path=w,
                            project_type="world",
                            universe_name=None,
                            last_modified=w.stat().st_mtime,
                        ))
        return results

    def discover_manuscripts(self) -> List[ProjectInfo]:
        """Discover manuscripts under ~/Manuscripts/ or ~/Universes/*/*/01-Manuscript."""
        results = []
        ms_root = self.base_dir / "Manuscripts"
        if ms_root.is_dir():
            for m in sorted(ms_root.iterdir()):
                if m.is_dir() and not m.name.startswith("."):
                    results.append(ProjectInfo(
                        name=m.name,
                        path=m,
                        project_type="manuscript",
                        last_modified=m.stat().st_mtime,
                    ))
        return results

    def discover_all_projects(self) -> Dict[str, List[ProjectInfo]]:
        """Return categorized dictionary of all discovered projects."""
        return {
            "universes": self.discover_universes(),
            "worlds": self.discover_worlds(),
            "manuscripts": self.discover_manuscripts(),
        }

    def set_active_project(self, project: ProjectInfo) -> None:
        self.active_project = project

    def get_studio_engines(self, studio_tab: str) -> List[Any]:
        """Return registered engines belonging to a specific Studio / UI Tab."""
        all_engines = list_engines(enabled_only=True)
        return [e for e in all_engines if e.studio_tab and e.studio_tab.lower() == studio_tab.lower()]

    def get_system_health_summary(self) -> Dict[str, Any]:
        """Inspect toolchain health."""
        return get_toolchain_diagnostics()

    def run_command_sync(self, cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Synchronously execute CLI command and return (exit_code, stdout, stderr)."""
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return (res.returncode, res.stdout or "", res.stderr or "")
        except subprocess.TimeoutExpired:
            return (124, "", "Command execution timed out.")
        except Exception as e:
            return (1, "", str(e))
