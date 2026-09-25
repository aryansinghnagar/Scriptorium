#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Dynamic Tactical Combat Simulator (scripts/lib/tactical_sim.py).
Validates:
- WOR-104: Fighter attributes, armor mitigation, initiative, and morale checks.
- Terrain modifiers (open field, castle walls, dense forest, dungeon corridor).
- Monte Carlo probability analysis and blow-by-blow narrative fight logs.
- MVP tracking, combatant type coverage, win rate arithmetic.
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
    DEFAULT_SIDE2,
    TERRAIN_MODIFIERS,
)


class TestTacticalSimulator(unittest.TestCase):

    # ------------------------------------------------------------------ #
    # Original 3 tests                                                     #
    # ------------------------------------------------------------------ #

    def test_single_battle_simulation(self):
        """simulate_single_battle must return a valid result dict with winner in {0,1,2}."""
        battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field")
        self.assertIn(battle["winner"], (0, 1, 2))
        self.assertGreater(battle["rounds_lasted"], 0)
        self.assertGreater(len(battle["log"]), 3)
        self.assertIn("mvp", battle)

    def test_monte_carlo_probability(self):
        """run_monte_carlo must return runs count and non-negative win rates."""
        mc = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", runs=20)
        self.assertEqual(mc["runs"], 20)
        self.assertGreaterEqual(mc["side1_win_rate"], 0.0)
        self.assertGreaterEqual(mc["side2_win_rate"], 0.0)
        self.assertGreater(mc["avg_rounds"], 0)

    def test_castle_walls_defense_advantage(self):
        """simulate_single_battle with castle_walls terrain must complete and return winner_name."""
        battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="castle_walls")
        self.assertIsNotNone(battle["winner_name"])

    # ------------------------------------------------------------------ #
    # New tests 4–12                                                       #
    # ------------------------------------------------------------------ #

    def test_simulate_returns_winner_key_valid(self):
        """Winner must be 0 (draw), 1 (Side 1 wins), or 2 (Side 2 wins)."""
        for terrain in ("open_field", "dense_forest", "dungeon_corridor"):
            battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain=terrain)
            self.assertIn(
                battle["winner"],
                (0, 1, 2),
                msg=f"Unexpected winner value {battle['winner']} for terrain={terrain}",
            )

    def test_simulate_log_non_empty(self):
        """Battle log must contain at least one entry."""
        battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field")
        self.assertGreater(len(battle["log"]), 0)

    def test_simulate_rounds_lasted_positive(self):
        """rounds_lasted must be >= 1 for any non-trivial battle."""
        battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field")
        self.assertGreaterEqual(battle["rounds_lasted"], 1)

    def test_mvp_fields_present(self):
        """MVP dict must have name, side, kills, and damage fields."""
        battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field")
        mvp = battle["mvp"]
        for field in ("name", "side", "kills", "damage"):
            self.assertIn(field, mvp, msg=f"MVP dict is missing field '{field}'")

    def test_terrain_modifiers_dict_coverage(self):
        """TERRAIN_MODIFIERS must include all four canonical terrain types."""
        for key in ("open_field", "castle_walls", "dense_forest", "dungeon_corridor"):
            self.assertIn(
                key,
                TERRAIN_MODIFIERS,
                msg=f"TERRAIN_MODIFIERS is missing required terrain '{key}'",
            )

    def test_terrain_modifiers_schema(self):
        """Each terrain modifier must have name, ranged_mod, def_bonus, and desc."""
        required = {"name", "ranged_mod", "def_bonus", "desc"}
        for terrain, mod in TERRAIN_MODIFIERS.items():
            missing = required - mod.keys()
            self.assertEqual(
                missing, set(), msg=f"Terrain '{terrain}' modifier is missing keys: {missing}"
            )

    def test_monte_carlo_win_rates_sum_to_100(self):
        """side1_win_rate + side2_win_rate + draw_rate must equal 100.0 (within float tolerance)."""
        mc = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", runs=50)
        total = mc["side1_win_rate"] + mc["side2_win_rate"] + mc["draw_rate"]
        self.assertAlmostEqual(
            total,
            100.0,
            delta=0.2,
            msg=f"Win rates sum to {total}, expected 100.0",
        )

    def test_monte_carlo_runs_count_exact(self):
        """Monte Carlo with runs=30 must report runs == 30."""
        mc = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, runs=30)
        self.assertEqual(mc["runs"], 30)

    def test_heavily_armored_side_wins_more(self):
        """A heavily armored side (armor=15) should win significantly more often against unarmored opponents."""
        armored = [{"name": "Tank", "hp": 40, "armor": 15, "attack": 7, "damage": 10, "type": "melee", "agility": 3, "morale": 95}]
        glass = [{"name": "Glass", "hp": 40, "armor": 0, "attack": 7, "damage": 10, "type": "melee", "agility": 3, "morale": 95}]
        mc = run_monte_carlo(armored, glass, terrain="open_field", runs=100)
        # Armored side (side1) should win more than 55% of the time
        self.assertGreater(
            mc["side1_win_rate"],
            55.0,
            msg=f"Expected armored side to win >55%, got {mc['side1_win_rate']}%",
        )

    def test_ranged_type_present_in_defaults(self):
        """At least one default combatant must have type == 'ranged'."""
        all_combatants = DEFAULT_SIDE1 + DEFAULT_SIDE2
        ranged = [c for c in all_combatants if c.get("type") == "ranged"]
        self.assertGreater(len(ranged), 0, msg="No ranged combatant found in DEFAULT_SIDE1 or DEFAULT_SIDE2")

    def test_dense_forest_ranged_penalty(self):
        """Dense forest must penalize ranged units (ranged_mod < 1.0)."""
        forest_mod = TERRAIN_MODIFIERS["dense_forest"]["ranged_mod"]
        self.assertLess(
            forest_mod,
            1.0,
            msg=f"Expected dense_forest ranged_mod < 1.0, got {forest_mod}",
        )


if __name__ == "__main__":
    unittest.main()
