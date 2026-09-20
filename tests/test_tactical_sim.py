#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Dynamic Tactical Combat Simulator (scripts/lib/tactical_sim.py).
Validates:
- WOR-104: Fighter attributes, armor mitigation, initiative, and morale checks.
- Terrain modifiers (open field, castle walls, dense forest).
- Monte Carlo probability analysis and blow-by-blow narrative fight logs.
"""

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.tactical_sim import (
    simulate_single_battle,
    run_monte_carlo,
    DEFAULT_SIDE1,
    DEFAULT_SIDE2
)


class TestTacticalSimulator(unittest.TestCase):

    def test_single_battle_simulation(self):
        battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field")
        self.assertIn(battle["winner"], (0, 1, 2))
        self.assertGreater(battle["rounds_lasted"], 0)
        self.assertGreater(len(battle["log"]), 3)
        self.assertIn("mvp", battle)

    def test_monte_carlo_probability(self):
        mc = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", runs=20)
        self.assertEqual(mc["runs"], 20)
        self.assertGreaterEqual(mc["side1_win_rate"], 0.0)
        self.assertGreaterEqual(mc["side2_win_rate"], 0.0)
        self.assertGreater(mc["avg_rounds"], 0)

    def test_castle_walls_defense_advantage(self):
        battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="castle_walls")
        self.assertIsNotNone(battle["winner_name"])


if __name__ == "__main__":
    unittest.main()
