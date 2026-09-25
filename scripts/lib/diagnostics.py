#!/usr/bin/env python3
"""
Ars Arcanum System Diagnostics & Bug Triage Engine (scripts/lib/diagnostics.py)
=============================================================================
Provides:
1. Structured rotating file logging to $XDG_STATE_HOME/ars-arcanum/arcanum.log.
2. Toolchain and runtime environment inspection (Python, Git, Pandoc, Typst, GUI).
3. Comprehensive Unified Doctor diagnostic reports for workspace, worlds, and manuscripts.
4. Redacted diagnostic bug-report bundle generation (arcanum doctor --report).
"""

import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import lib._bootstrap  # noqa: F401
except ImportError:
    import _bootstrap  # noqa: F401

VERSION = "1.6.1"


def get_state_dir() -> Path:
    """Return platform-appropriate persistent state directory."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        state_dir = Path(base) / "ars-arcanum"
    else:
        base = os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state"))
        state_dir = Path(base) / "ars-arcanum"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def setup_logging(
    log_name: str = "arcanum.log",
    level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> logging.Logger:
    """Configure rotating structured logger for Ars Arcanum."""
    logger = logging.getLogger("arcanum")
    if logger.handlers:
        return logger

    logger.setLevel(level)
    try:
        log_path = get_state_dir() / log_name
        handler = RotatingFileHandler(
            str(log_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s:%(module)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception as e:
        logger.addHandler(logging.NullHandler())
        sys.stderr.write(f"Warning: Failed to initialize file logger ({e})\n")

    return logger


def redact_sensitive_paths(text: str) -> str:
    """Sanitize home directory paths and author usernames for public issue reports."""
    home = str(Path.home())
    text = text.replace(home, "~")
    home_win = home.replace("/", "\\")
    text = text.replace(home_win, "~")
    return text


def get_command_version(cmd: list[str]) -> str | None:
    """Safely query external CLI tool version."""
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        out = (res.stdout or res.stderr or "").strip()
        lines = out.splitlines()
        return lines[0].strip() if lines else None
    except Exception:
        return None


def get_toolchain_diagnostics() -> dict[str, Any]:
    """Inspect all system compilers, runtimes, and dependencies."""
    tools = {
        "python": {
            "version": sys.version.split()[0],
            "executable": sys.executable,
            "available": True,
        },
        "git": {
            "version": get_command_version(["git", "--version"]),
            "executable": shutil.which("git"),
            "available": shutil.which("git") is not None,
        },
        "pandoc": {
            "version": get_command_version(["pandoc", "--version"]),
            "executable": shutil.which("pandoc"),
            "available": shutil.which("pandoc") is not None,
        },
        "typst": {
            "version": get_command_version(["typst", "--version"]),
            "executable": shutil.which("typst"),
            "available": shutil.which("typst") is not None,
            "compile_test": None,
        },
        "ruff": {
            "version": get_command_version(["ruff", "--version"]),
            "executable": shutil.which("ruff"),
            "available": shutil.which("ruff") is not None,
        },
        "shellcheck": {
            "version": get_command_version(["shellcheck", "--version"]),
            "executable": shutil.which("shellcheck"),
            "available": shutil.which("shellcheck") is not None,
        },
    }

    if tools["typst"]["available"]:
        sample_path = Path(__file__).resolve().parent.parent.parent / "templates" / "typst" / "preview_sample.typ"
        if sample_path.is_file():
            import tempfile
            try:
                with tempfile.TemporaryDirectory() as td:
                    test_pdf = Path(td) / "test.pdf"
                    res = subprocess.run(
                        ["typst", "compile", str(sample_path), str(test_pdf)],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=str(sample_path.parent),
                    )
                    if res.returncode == 0:
                        tools["typst"]["compile_test"] = "passed"
                    else:
                        tools["typst"]["compile_test"] = f"failed: {res.stderr.strip()}"
            except Exception as ex:
                tools["typst"]["compile_test"] = f"error: {ex}"

    # GUI typelib check
    gui_status = {"available": False, "toolkit": None, "error": None}
    try:
        import gi
        gi.require_version("Gtk", "4.0")
        gui_status["available"] = True
        gui_status["toolkit"] = "GTK4 / Libadwaita"
    except Exception as e4:
        try:
            import gi
            gi.require_version("Gtk", "3.0")
            gui_status["available"] = True
            gui_status["toolkit"] = "GTK3"
        except Exception:
            gui_status["available"] = False
            gui_status["error"] = str(e4)

    return {
        "tools": tools,
        "gui": gui_status,
    }


def generate_diagnostic_report(
    project_path: str | None = None,
    redact_sensitive: bool = True,
) -> dict[str, Any]:
    """Compile comprehensive system diagnostic and bug triage report."""
    tc = get_toolchain_diagnostics()

    recent_logs = []
    log_file = get_state_dir() / "arcanum.log"
    if log_file.exists():
        try:
            lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            recent_logs = lines[-50:]
        except Exception:
            pass

    report: dict[str, Any] = {
        "version": VERSION,
        "system": {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "python_compiler": platform.python_compiler(),
        },
        "toolchain": tc,
        "recent_logs": recent_logs,
    }

    if project_path:
        p = Path(project_path).resolve()
        project_info = {
            "path": str(p),
            "is_dir": p.is_dir(),
            "has_world_bible": (p / "00-World-Bible").is_dir() or (p / "Characters").is_dir(),
            "has_manuscript": (p / "01-Manuscript").is_dir() or (p / "01_Chapters").is_dir(),
            "manifest_found": (p / "manuscript.yaml").exists() or (p / "world.yaml").exists(),
        }
        report["project"] = project_info

    if redact_sensitive:
        report_str = json.dumps(report)
        redacted_str = redact_sensitive_paths(report_str)
        return json.loads(redacted_str)

    return report


def format_diagnostic_report_markdown(report: dict[str, Any]) -> str:
    """Format diagnostic bundle as clean GitHub Flavored Markdown."""
    lines = [
        "# Ars Arcanum Diagnostic Triage Report",
        f"- **Version**: v{report.get('version', VERSION)}",
        f"- **Platform**: {report['system']['os']} {report['system']['os_release']} ({report['system']['architecture']})",
        f"- **Python**: {report['system']['python_version']}",
        "",
        "## Toolchain & Dependencies",
        "| Tool | Available | Version | Path |",
        "| :--- | :--- | :--- | :--- |",
    ]

    tools = report["toolchain"]["tools"]
    for t_name, t_data in tools.items():
        avail = "✓ Yes" if t_data.get("available") else "✗ No"
        ver = t_data.get("version") or "N/A"
        exe = t_data.get("executable") or "N/A"
        lines.append(f"| `{t_name}` | {avail} | {ver} | `{exe}` |")

    lines.append("")
    gui = report["toolchain"]["gui"]
    lines.append(f"**GUI Runtime**: {gui.get('toolkit') or 'Unavailable'} (Available: {gui.get('available')})")
    if gui.get("error"):
        lines.append(f"- *GUI Warning*: `{gui['error']}`")

    if "project" in report:
        lines.append("")
        lines.append("## Target Project Inspection")
        prj = report["project"]
        lines.append(f"- **Path**: `{prj.get('path')}`")
        lines.append(f"- **World Bible Present**: {prj.get('has_world_bible')}")
        lines.append(f"- **Manuscript Present**: {prj.get('has_manuscript')}")

    if report.get("recent_logs"):
        lines.append("")
        lines.append("## Recent Log Output (Sanitized)")
        lines.append("```log")
        lines.extend(report["recent_logs"])
        lines.append("```")

    return "\n".join(lines)


def run_doctor_report(
    world_filter: str | None = None,
    manuscript_filter: str | None = None,
    all_worlds: bool = False,
    as_json: bool = False,
) -> int:
    """Execute unified system, workspace, and world diagnostics."""
    report = generate_diagnostic_report(redact_sensitive=False)
    findings: dict[str, Any] = {
        "version": VERSION,
        "system": report["system"],
        "toolchain": report["toolchain"]["tools"],
        "gui": report["toolchain"]["gui"],
        "worlds": [],
        "errors": 0,
        "warnings": 0,
    }

    # Toolchain errors
    for t_name, t_data in findings["toolchain"].items():
        if not t_data.get("available") and t_name in ("python", "git", "pandoc"):
            findings["errors"] += 1
        elif not t_data.get("available"):
            findings["warnings"] += 1

    # World checks if requested
    if world_filter or all_worlds:
        try:
            from lib.world_doctor import check_world
        except ImportError:
            from world_doctor import check_world

        universes_base = Path(os.environ.get("UNIVERSES_BASE", Path.home() / "Universes"))
        worlds_to_check = []

        if world_filter:
            # Look up specific world
            w_path = Path(world_filter)
            if not w_path.is_dir() and universes_base.is_dir():
                for u in universes_base.iterdir():
                    if u.is_dir() and (u / world_filter).is_dir():
                        w_path = u / world_filter
                        break
            if w_path.is_dir():
                worlds_to_check.append(w_path)
        elif all_worlds and universes_base.is_dir():
            for u in universes_base.iterdir():
                if u.is_dir():
                    for w in u.iterdir():
                        if w.is_dir() and ((w / "world.yaml").is_file() or (w / "00-World-Bible").is_dir()):
                            worlds_to_check.append(w)

        for w_dir in worlds_to_check:
            try:
                w_res = check_world(str(w_dir))
                findings["worlds"].append(w_res)
                findings["errors"] += len(w_res.get("broken_links", []))
                findings["errors"] += len(w_res.get("missing_required_fields", []))
                findings["warnings"] += len(w_res.get("orphans", []))
            except Exception as e:
                findings["errors"] += 1
                findings["worlds"].append({"world": str(w_dir), "error": str(e)})

    if as_json:
        print(json.dumps(findings, indent=2))
        return 0 if findings["errors"] == 0 else 1

    print(f"Ars Arcanum Unified Doctor — v{VERSION}")
    print("========================================")
    print(f"OS: {findings['system']['os']} {findings['system']['os_release']} ({findings['system']['architecture']})")
    print(f"Python: {findings['system']['python_version']}")
    print("\n[Toolchain Status]")
    for name, data in findings["toolchain"].items():
        status = "✓ Ready" if data["available"] else "✗ Missing"
        ver = f"({data['version']})" if data.get("version") else ""
        print(f"  • {name:<12} [{status}] {ver}")

    if findings["gui"]["available"]:
        print(f"  • GUI:         [✓ Ready] ({findings['gui']['toolkit']})")
    else:
        print("  • GUI:         [✗ Disabled] (Headless / Missing PyGObject)")

    if findings["worlds"]:
        print("\n[World Lore Vault Audits]")
        for w in findings["worlds"]:
            if "error" in w:
                print(f"  • {w['world']}: Error ({w['error']})")
            else:
                bl = len(w.get("broken_links", []))
                mf = len(w.get("missing_required_fields", []))
                print(f"  • {w['world']}: {w.get('notes', 0)} notes (Broken Links: {bl}, Missing Fields: {mf})")

    print("\n========================================")
    status_str = "HEALTHY" if findings["errors"] == 0 else "ISSUES DETECTED"
    print(f"Status: {status_str} ({findings['errors']} errors, {findings['warnings']} warnings)")
    return 0 if findings["errors"] == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ars Arcanum Diagnostic & System Health Suite",
        prog="diagnostics",
    )
    parser.add_argument("--report", action="store_true", help="Generate complete redacted bug report bundle")
    parser.add_argument("--json", action="store_true", help="Emit report in JSON format")
    parser.add_argument("-w", "--world", help="Run diagnostics on a specific world lore vault")
    parser.add_argument("-m", "--manuscript", help="Optional manuscript project to cross-validate")
    parser.add_argument("--all-worlds", action="store_true", help="Run diagnostics on all discovered worlds")
    parser.add_argument("project", nargs="?", help="Optional project directory to inspect")

    args = parser.parse_args(argv)

    if args.report:
        report = generate_diagnostic_report(project_path=args.project or args.world, redact_sensitive=True)
        print(format_diagnostic_report_markdown(report))
        return 0

    return run_doctor_report(
        world_filter=args.world or args.project,
        manuscript_filter=args.manuscript,
        all_worlds=args.all_worlds,
        as_json=args.json,
    )


if __name__ == "__main__":
    sys.exit(main())
