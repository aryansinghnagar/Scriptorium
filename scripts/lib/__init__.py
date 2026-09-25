"""
Ars Arcanum Python Library Package (scripts/lib)
================================================
Core craft engines, utilities, diagnostics, and desktop UI presentation modules.
"""

import sys
from pathlib import Path

# Ensure scripts directory and lib directory are in sys.path
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
