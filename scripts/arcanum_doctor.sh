#!/usr/bin/env bash
# ==============================================================================
# Ars Arcanum Unified Doctor (Workstream 3.1)
# Purpose: Comprehensive system, toolchain, workspace, world, and backup diagnostics.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

command -v python3 &>/dev/null || { echo "Error: python3 is required." >&2; exit 2; }

export PROJECT_ROOT
exec python3 "${SCRIPT_DIR}/lib/diagnostics.py" "$@"
