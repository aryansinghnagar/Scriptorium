#!/usr/bin/env bash
# ==============================================================================
# Scriptorium Unified Doctor (Workstream 3.1)
# Purpose: Comprehensive system, toolchain, workspace, world, and backup diagnostics.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORLDS_BASE="${HOME}/Worlds"

usage() {
    cat << 'USAGE'
Scriptorium Unified Doctor — diagnose system, toolchain, workspace, and world health.

Usage:
  scriptorium_doctor.sh [OPTIONS]

Options:
  -w, --world NAME         Run deep domain diagnostics on a specific world
  -m, --manuscript NAME    Specify manuscript project for cross-validation
  --all-worlds             Run domain diagnostics on all discovered worlds
  --json                   Output report as machine-readable JSON
  -h, --help               Show this help and exit

Exit codes:
  0  all systems and checked worlds healthy
  1  warnings or diagnostic issues detected
  2  usage error or missing core runtime (e.g. python3)
USAGE
}

WORLD_FILTER=""
MANUSCRIPT_FILTER=""
ALL_WORLDS=0
JSON_OUTPUT=0

while [ $# -gt 0 ]; do
    case "$1" in
        -w|--world)
            [ $# -ge 2 ] || { echo "Error: --world requires a value." >&2; exit 2; }
            WORLD_FILTER="$2"; shift 2 ;;
        -m|--manuscript)
            [ $# -ge 2 ] || { echo "Error: --manuscript requires a value." >&2; exit 2; }
            MANUSCRIPT_FILTER="$2"; shift 2 ;;
        --all-worlds)
            ALL_WORLDS=1; shift ;;
        --json)
            JSON_OUTPUT=1; shift ;;
        -h|--help)
            usage; exit 0 ;;
        *)
            echo "Error: unknown option: $1 (see --help)" >&2; exit 2 ;;
    esac
done

command -v python3 &>/dev/null || { echo "Error: python3 is required." >&2; exit 2; }

PROJECT_ROOT="${PROJECT_ROOT}" \
WORLDS_BASE="${WORLDS_BASE}" \
WORLD_FILTER="${WORLD_FILTER}" \
MANUSCRIPT_FILTER="${MANUSCRIPT_FILTER}" \
ALL_WORLDS="${ALL_WORLDS}" \
JSON_OUT="${JSON_OUTPUT}" \
python3 - << 'PYEOF'
import os
import sys
import json
import shutil
import subprocess
import platform

PROJECT_ROOT = os.environ["PROJECT_ROOT"]
WORLDS_BASE = os.environ["WORLDS_BASE"]
WORLD_FILTER = os.environ["WORLD_FILTER"]
MANUSCRIPT_FILTER = os.environ.get("MANUSCRIPT_FILTER", "")
ALL_WORLDS = os.environ["ALL_WORLDS"] == "1"
JSON_OUT = os.environ["JSON_OUT"] == "1"

findings = {
    "system": {},
    "toolchain": {},
    "workspace": {},
    "worlds": [],
    "backups": [],
    "summary": {"errors": 0, "warnings": 0, "status": "healthy"}
}

# 1. SYSTEM DIAGNOSTICS
os_info = "Unknown Linux"
if os.path.exists("/etc/os-release"):
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    os_info = line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass

disk_free_gb = 0.0
try:
    stat = shutil.disk_usage(os.path.expanduser("~"))
    disk_free_gb = round(stat.free / (1024**3), 2)
except Exception:
    pass

worlds_exists = os.path.isdir(WORLDS_BASE)
worlds_writable = os.access(WORLDS_BASE, os.W_OK) if worlds_exists else os.access(os.path.expanduser("~"), os.W_OK)

findings["system"] = {
    "os": os_info,
    "platform": platform.platform(),
    "architecture": platform.machine(),
    "python_version": platform.python_version(),
    "free_disk_gb": disk_free_gb,
    "worlds_dir": WORLDS_BASE,
    "worlds_dir_exists": worlds_exists,
    "worlds_dir_writable": worlds_writable,
}

if disk_free_gb < 2.0:
    findings["summary"]["warnings"] += 1
if not worlds_writable:
    findings["summary"]["errors"] += 1

# 2. TOOLCHAIN DIAGNOSTICS
def check_tool(bin_name, version_cmd=None, required=True):
    path = shutil.which(bin_name)
    installed = path is not None
    ver = "unknown"
    if installed and version_cmd:
        try:
            out = subprocess.check_output(version_cmd, stderr=subprocess.STDOUT, timeout=5).decode("utf-8", "ignore")
            ver = out.splitlines()[0].strip() if out.splitlines() else "present"
        except Exception:
            ver = "installed (version check failed)"
    status = "ok" if installed else ("missing_required" if required else "missing_optional")
    if not installed:
        if required:
            findings["summary"]["errors"] += 1
        else:
            findings["summary"]["warnings"] += 1
    return {"installed": installed, "path": path or "", "version": ver, "status": status}

findings["toolchain"]["git"] = check_tool("git", ["git", "--version"], required=True)
findings["toolchain"]["pandoc"] = check_tool("pandoc", ["pandoc", "--version"], required=True)
findings["toolchain"]["typst"] = check_tool("typst", ["typst", "--version"], required=False)
findings["toolchain"]["python3"] = check_tool("python3", ["python3", "--version"], required=True)
findings["toolchain"]["zenity"] = check_tool("zenity", ["zenity", "--version"], required=False)
findings["toolchain"]["focuswriter"] = check_tool("focuswriter", ["focuswriter", "--version"], required=False)

# Check Flatpaks if flatpak command exists
flatpak_apps = {
    "obsidian": "md.obsidian.Obsidian",
    "novelwriter": "io.gitlab.novelwriter.novelWriter",
    "calibre": "com.calibre_ebook.calibre"
}
flatpak_bin = shutil.which("flatpak")
for label, app_id in flatpak_apps.items():
    installed = False
    if flatpak_bin:
        try:
            rc = subprocess.call(["flatpak", "info", app_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            installed = (rc == 0)
        except Exception:
            pass
    findings["toolchain"][label] = {
        "installed": installed,
        "type": "flatpak",
        "app_id": app_id,
        "status": "ok" if installed else "not_installed"
    }

# 3. WORKSPACE DIAGNOSTICS
desktop_dir = os.path.expanduser("~/Desktop")
app_dir = os.path.expanduser("~/.local/share/applications")

launchers = ["init-world.desktop", "init-manuscript.desktop", "export-book.desktop", "save-snapshot.desktop", "scriptorium-control-center.desktop"]
installed_launchers = [lf for lf in launchers if os.path.isfile(os.path.join(app_dir, lf)) or os.path.isfile(os.path.join(desktop_dir, lf))]

leechblock_json = os.path.join(PROJECT_ROOT, "configs", "leechblock_scriptorium_rules.json")
leechblock_valid = False
if os.path.isfile(leechblock_json):
    try:
        with open(leechblock_json) as f:
            data = json.load(f)
            leechblock_valid = "blockSets" in data
    except Exception:
        pass

findings["workspace"] = {
    "launchers_installed": len(installed_launchers),
    "total_launchers": len(launchers),
    "leechblock_config_valid": leechblock_valid,
    "templates_present": os.path.isdir(os.path.join(PROJECT_ROOT, "templates")),
}

# 4. WORLDS & MANUSCRIPTS & BACKUPS DIAGNOSTICS
discovered_worlds = []
universes_base = os.path.expanduser("~/Universes")
if os.path.isdir(universes_base):
    for u in sorted(os.listdir(universes_base)):
        u_dir = os.path.join(universes_base, u)
        if os.path.isdir(u_dir) and not u.startswith("."):
            # Check direct worlds under ~/Universes/<Universe>/<World>
            for w in sorted(os.listdir(u_dir)):
                full = os.path.join(u_dir, w)
                if os.path.isdir(full) and not w.startswith(".") and w not in ("Worlds", ".git"):
                    discovered_worlds.append(full)
            # Check legacy ~/Universes/<Universe>/Worlds/<World>
            u_worlds = os.path.join(u_dir, "Worlds")
            if os.path.isdir(u_worlds):
                for w in sorted(os.listdir(u_worlds)):
                    full = os.path.join(u_worlds, w)
                    if os.path.isdir(full) and not w.startswith(".") and full not in discovered_worlds:
                        discovered_worlds.append(full)

manuscripts_base = os.path.expanduser("~/Manuscripts")
if os.path.isdir(manuscripts_base):
    for m in sorted(os.listdir(manuscripts_base)):
        full = os.path.join(manuscripts_base, m)
        if os.path.isdir(full) and not m.startswith(".") and full not in discovered_worlds:
            discovered_worlds.append(full)

if os.path.isdir(WORLDS_BASE):
    for d in sorted(os.listdir(WORLDS_BASE)):
        full = os.path.join(WORLDS_BASE, d)
        if os.path.isdir(full) and not d.startswith(".") and full not in discovered_worlds:
            discovered_worlds.append(full)

target_worlds = []
if WORLD_FILTER:
    if os.path.isdir(WORLD_FILTER):
        target_worlds = [WORLD_FILTER]
    else:
        matched = [w for w in discovered_worlds if os.path.basename(w) == WORLD_FILTER]
        target_worlds = matched if matched else [os.path.join(WORLDS_BASE, WORLD_FILTER)]
elif ALL_WORLDS:
    target_worlds = discovered_worlds
elif discovered_worlds:
    target_worlds = [discovered_worlds[0]]

world_doctor_bin = os.path.join(PROJECT_ROOT, "scripts", "world_doctor.sh")

for wdir in target_worlds:
    wname = os.path.basename(wdir)
    if not os.path.isdir(wdir):
        findings["worlds"].append({"world": wname, "status": "not_found", "path": wdir})
        findings["summary"]["errors"] += 1
        continue

    # Run world_doctor if this is a world lore vault
    # DOC-01: 60s budget for large vaults (was 15s); timeouts surface as
    # actionable warnings instead of a silent {"error": ...} blob.
    wdoctor_report = {}
    if os.path.isfile(world_doctor_bin) and (os.path.isdir(os.path.join(wdir, "Characters")) or os.path.isdir(os.path.join(wdir, "00-World-Bible"))):
        try:
            cmd = ["bash", world_doctor_bin, wdir, "--json", "--fast"]
            if MANUSCRIPT_FILTER:
                cmd.extend(["-m", MANUSCRIPT_FILTER])
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.stdout:
                wdoctor_report = json.loads(res.stdout)
            if res.stderr and "falling back to full scan" in res.stderr:
                wdoctor_report["_note"] = "fast cache unavailable; full scan used"
        except subprocess.TimeoutExpired:
            wdoctor_report = {"error": "world_doctor timed out after 60s — vault is very large; re-run 'world_doctor <world> --fast' directly or split the vault"}
        except Exception as e:
            wdoctor_report = {"error": str(e)}

    # Check Git snapshot status
    git_commits = 0
    git_clean = True
    if os.path.isdir(os.path.join(wdir, ".git")):
        try:
            git_commits = int(subprocess.check_output(["git", "-C", wdir, "rev-list", "--count", "HEAD"], stderr=subprocess.DEVNULL).decode().strip())
            status_out = subprocess.check_output(["git", "-C", wdir, "status", "--porcelain"], stderr=subprocess.DEVNULL).decode().strip()
            git_clean = (len(status_out) == 0)
        except Exception:
            pass

    # Check backups in Backups or 05-Backups
    backup_dir = os.path.join(wdir, "Backups")
    if not os.path.isdir(backup_dir):
        backup_dir = os.path.join(wdir, "05-Backups")
    backups_list = []
    if os.path.isdir(backup_dir):
        for bf in sorted(os.listdir(backup_dir)):
            if bf.endswith(".tar.gz"):
                bpath = os.path.join(backup_dir, bf)
                sha_file = os.path.join(backup_dir, bf.replace(".tar.gz", ".sha256"))
                has_sha = os.path.isfile(sha_file)
                backups_list.append({
                    "archive": bf,
                    "size_bytes": os.path.getsize(bpath),
                    "has_sha256": has_sha
                })

    has_bible = os.path.isdir(os.path.join(wdir, "00-World-Bible")) or os.path.isdir(os.path.join(wdir, "Characters"))
    has_ms = os.path.isdir(os.path.join(wdir, "01-Manuscript")) or os.path.isdir(os.path.join(wdir, "Book-01"))

    world_info = {
        "world": wname,
        "path": wdir,
        "has_world_bible": has_bible,
        "has_manuscript": has_ms,
        "git_initialized": os.path.isdir(os.path.join(wdir, ".git")),
        "git_snapshots_count": git_commits,
        "git_clean": git_clean,
        "backup_count": len(backups_list),
        "latest_backup": backups_list[-1] if backups_list else None,
        "doctor": wdoctor_report
    }
    findings["worlds"].append(world_info)

# Status summary
if findings["summary"]["errors"] > 0:
    findings["summary"]["status"] = "issues_detected"
elif findings["summary"]["warnings"] > 0:
    findings["summary"]["status"] = "warnings_detected"
else:
    findings["summary"]["status"] = "healthy"

if JSON_OUT:
    print(json.dumps(findings, indent=2))
else:
    print("============================================================")
    print("  Scriptorium Unified Doctor Diagnostic Report")
    print("============================================================")
    print(f"System:       {findings['system']['os']} ({findings['system']['architecture']})")
    print(f"Disk Free:    {findings['system']['free_disk_gb']} GB")
    print(f"Worlds Base:  {findings['system']['worlds_dir']} (Writable: {findings['system']['worlds_dir_writable']})")
    print("\nToolchain Status:")
    for tool, data in findings["toolchain"].items():
        sym = "✓" if data.get("installed") else "!"
        v = data.get("version") or data.get("app_id") or ""
        print(f"  [{sym}] {tool:<14} : {v}")

    print("\nWorkspace Configuration:")
    print(f"  Launchers:        {findings['workspace']['launchers_installed']}/{findings['workspace']['total_launchers']} active")
    print(f"  LeechBlock Rules: {'✓ Valid' if findings['workspace']['leechblock_config_valid'] else '! Missing/Invalid'}")

    if findings["worlds"]:
        print("\nWorld Status:")
        for w in findings["worlds"]:
            print(f"  • World: {w['world']}")
            print(f"    - Git Snapshots: {w['git_snapshots_count']} (Working tree clean: {w['git_clean']})")
            print(f"    - Standalone Backups: {w['backup_count']}")
            if w.get("doctor") and "notes" in w["doctor"]:
                print(f"    - Lore Notes Scanned: {w['doctor']['notes']}")
                broken = len(w["doctor"].get("broken_links", []))
                dangling = len(w["doctor"].get("dangling_frontmatter_refs", []))
                orphans = len(w["doctor"].get("orphans", []))
                ms_drift = len(w["doctor"].get("manuscript_name_drift", []))
                print(f"    - Lore & Manuscript Consistency: {broken} broken links, {dangling} dangling refs, {orphans} orphans, {ms_drift} manuscript drift")

    print("\n============================================================")
    print(f"Diagnostic Result: {findings['summary']['status'].upper()} ({findings['summary']['errors']} errors, {findings['summary']['warnings']} warnings)")
    print("============================================================")

sys.exit(1 if findings["summary"]["errors"] > 0 else 0)
PYEOF
