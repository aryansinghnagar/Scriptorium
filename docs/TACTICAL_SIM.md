# TACTICAL_SIM — Dynamic Tactical Combat Simulator

> **Module**: `scripts/lib/tactical_sim.py`  
> **CLI Command**: `arcanum tactical`  
> **Purpose**: Simulates turn-based tactical battles between authored combatant rosters, applies terrain modifiers, tracks morale collapse, identifies MVPs, and supports Monte Carlo probability analysis for encounter design.

---

## Table of Contents

1. [Overview](#overview)
2. [CLI Usage](#cli-usage)
3. [Key API Reference](#key-api-reference)
4. [Combatant YAML Schema](#combatant-yaml-schema)
5. [Terrain Modifiers](#terrain-modifiers)
6. [Combat Mechanics](#combat-mechanics)
7. [Behavioral Notes](#behavioral-notes)
8. [Example Workflow](#example-workflow)

---

## Overview

The `tactical_sim` module is the Ars Arcanum **encounter design tool**. Authors define combatant rosters in YAML, specify a terrain, and the simulator runs a full round-by-round battle with prose-style logging. The Monte Carlo runner executes hundreds of simulations to yield win-rate statistics — invaluable for ensuring encounters are balanced without being trivially one-sided.

**Primary use cases:**

- **Encounter balancing** — test whether a named hero can survive a fortress assault, and at what statistical odds.
- **Lore consistency** — verify that your world's elite units actually outperform conscript armies in simulation.
- **Chapter planning** — know which side is likely to win before writing the scene, then subvert it consciously.
- **MVP narration** — the simulator tracks the highest-damage combatant, giving authors a data-backed suggestion for who to spotlight in the battle scene.

---

## CLI Usage

```
arcanum tactical [OPTIONS]
```

### Options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--side1 FILE` | path | *(required)* | YAML file defining team 1 roster |
| `--side2 FILE` | path | *(required)* | YAML file defining team 2 roster |
| `--terrain TERRAIN` | choice | `open_field` | Terrain key (see [Terrain Modifiers](#terrain-modifiers)) |
| `--runs N` | int | `1` | If N > 1, runs a Monte Carlo simulation of N battles |
| `--json` | flag | off | Output raw JSON result instead of formatted prose |
| `--log` | flag | off | Print the full round-by-round prose battle log |

### Quick Examples

```powershell
# Single battle, dense forest terrain
arcanum tactical --side1 knights.yaml --side2 bandits.yaml --terrain dense_forest --log

# Monte Carlo: 500 runs, castle walls
arcanum tactical --side1 garrison.yaml --side2 siege_force.yaml --terrain castle_walls --runs 500

# JSON output for programmatic use
arcanum tactical --side1 s1.yaml --side2 s2.yaml --json

# Single battle, output log to file (PowerShell redirection)
arcanum tactical --side1 heroes.yaml --side2 dungeon.yaml --terrain dungeon_corridor --log > battle_log.txt
```

> [!TIP]
> Run `--runs 100` first as a quick sanity check on encounter balance, then use `--runs 1000` for publication-grade statistics.

---

## Key API Reference

### `simulate_single_battle`

```python
simulate_single_battle(
    side1_data: list[dict],
    side2_data: list[dict],
    terrain: str = "open_field"
) -> dict
```

Runs a single complete battle simulation and returns a structured result dictionary.

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `side1_data` | `list[dict]` | List of combatant attribute dicts (see schema below) |
| `side2_data` | `list[dict]` | List of combatant attribute dicts |
| `terrain` | `str` | Terrain key from `TERRAIN_MODIFIERS` |

**Return dict fields:**

| Field | Type | Description |
|---|---|---|
| `winner` | `int` | `0` = draw, `1` = side 1 wins, `2` = side 2 wins |
| `winner_name` | `str` | Name of the winning side (derived from first combatant name) or `"Draw"` |
| `rounds_lasted` | `int` | Number of combat rounds before battle ended |
| `terrain` | `str` | Terrain key used |
| `team1_survivors` | `list[str]` | Names of surviving side 1 combatants |
| `team2_survivors` | `list[str]` | Names of surviving side 2 combatants |
| `team1_casualties` | `list[str]` | Names of fallen side 1 combatants |
| `team2_casualties` | `list[str]` | Names of fallen side 2 combatants |
| `mvp` | `dict` | `{name, side, kills, damage}` — top damage dealer of the battle |
| `log` | `list[str]` | Ordered list of prose narrative strings, one per round event |

---

### `run_monte_carlo`

```python
run_monte_carlo(
    side1_data: list[dict],
    side2_data: list[dict],
    terrain: str = "open_field",
    runs: int = 100
) -> dict
```

Executes `runs` independent simulations and aggregates statistics.

**Return dict fields:**

| Field | Type | Description |
|---|---|---|
| `runs` | `int` | Total number of simulations executed |
| `terrain` | `str` | Terrain key used |
| `side1_win_rate` | `float` | Fraction of runs won by side 1 (0.0–1.0) |
| `side2_win_rate` | `float` | Fraction of runs won by side 2 (0.0–1.0) |
| `draw_rate` | `float` | Fraction of runs ending in draw |
| `avg_rounds` | `float` | Mean number of rounds across all simulations |

> [!NOTE]
> Each simulation in the Monte Carlo run initialises combatants from scratch so HP, morale, and routing state are fully reset between runs. Dice rolls are independently seeded per run.

---

### `Combatant` Class (Internal)

```python
class Combatant:
    hp: int
    armor: int
    attack: int
    damage: int
    type: str        # "melee" | "ranged" | "magic"
    agility: int
    morale: int
```

This class is **internal** to the simulation engine. Authors interact with it exclusively through YAML roster files. It is documented here for reference when debugging raw JSON output.

---

### `TERRAIN_MODIFIERS` Dictionary

```python
TERRAIN_MODIFIERS: dict[str, dict]
```

Module-level dictionary of terrain configurations. Keys match `--terrain` CLI values.

Each entry has:

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Display name |
| `ranged_mod` | `float` | Multiplier on ranged-type combatant attack rolls |
| `def_bonus` | `int` | Flat bonus added to defender armor |
| `desc` | `str` | Human-readable terrain description |

---

## Combatant YAML Schema

Each roster file is a YAML list of combatant objects:

```yaml
- name: "Knight Commander Vaelor"
  hp: 45
  armor: 6
  attack: 8
  damage: 12
  type: melee        # melee | ranged | magic
  agility: 5
  morale: 90

- name: "Arcanist Selenne"
  hp: 22
  armor: 2
  attack: 10
  damage: 18
  type: magic
  agility: 7
  morale: 75

- name: "Sharpshooter Daven"
  hp: 28
  armor: 3
  attack: 9
  damage: 10
  type: ranged
  agility: 8
  morale: 80
```

### Field Reference

| Field | Type | Range | Description |
|---|---|---|---|
| `name` | string | — | Combatant's display name (appears in logs and MVP report) |
| `hp` | int | 1–999 | Hit points; combatant is defeated when HP reaches 0 |
| `armor` | int | 0–20 | Flat damage reduction applied per incoming hit |
| `attack` | int | 1–20 | Attack roll modifier; higher values increase hit probability |
| `damage` | int | 1–99 | Base damage dealt per successful hit (before armor reduction) |
| `type` | string | `melee \| ranged \| magic` | Combat archetype; affects terrain modifier application |
| `agility` | int | 1–20 | Influences initiative order and dodge probability |
| `morale` | int | 0–100 | Morale score; checked during collapse threshold events |

> [!IMPORTANT]
> All six numeric fields are **required**. A missing field will raise a `KeyError` and abort the simulation. Use the schema above as your roster template.

---

## Terrain Modifiers

| Key | Display Name | `ranged_mod` | `def_bonus` | Description |
|---|---|---|---|---|
| `open_field` | Open Field | 1.0 | 0 | No modifiers; neutral ground |
| `castle_walls` | Castle Walls | 1.2 | 3 | Defenders benefit; ranged fire gets elevated-position bonus |
| `dense_forest` | Dense Forest | 0.7 | 1 | Obstructed sight lines penalise ranged units |
| `dungeon_corridor` | Dungeon Corridor | 0.8 | 0 | Confined quarters; ranged partially penalised, no defensive cover |

**Terrain modifier application:**

- `ranged_mod` is applied as a **multiplier** to the attack roll of any combatant whose `type` is `ranged`.
- `def_bonus` is added as a **flat bonus** to the armor of every combatant on the **defending side** (the side that did not initiate the round's first strike).
- `magic` type combatants are **not affected** by `ranged_mod` (spells bypass line-of-sight penalties).

---

## Combat Mechanics

### Round Structure

Each round proceeds as follows:

1. **Initiative sort** — all living combatants from both sides are ordered by `agility` (descending) with a random tiebreaker.
2. **Attack resolution** — each combatant selects a random living target from the opposing side and resolves an attack:
   - **Hit check**: `roll(1, 20) + attack` vs. target's `roll(1, 20) + agility`. Hit if attacker roll ≥ defender roll.
   - **Damage**: `damage - target.armor` (minimum 1). Ranged attackers apply `terrain.ranged_mod` to their attack roll.
3. **Death check** — combatants with HP ≤ 0 are removed from the active roster and added to their side's casualty list.
4. **Morale collapse check** — triggered when ≥ 50% of a team's original count has become casualties (see below).
5. **Victory check** — if one side has zero living combatants (or all survivors have routed), the battle ends.

### Morale Collapse

When a team reaches the **50% casualty threshold**, each surviving combatant on that team rolls a morale check:

```
roll(1, 100) <= combatant.morale  →  holds ground
roll(1, 100) >  combatant.morale  →  routes (removed from battle as if defeated)
```

A routed combatant does not die but is counted as a non-participant. They are listed in casualties for battle-result purposes.

> [!NOTE]
> Morale collapse is checked **once per team**, at the moment the threshold is first crossed. Subsequent casualties do not re-trigger the check.

### MVP Calculation

The MVP is the **combatant with the highest cumulative damage dealt** across all rounds of the battle, regardless of which side they belong to. In the event of a tie, the combatant with the most kills (opponents reduced to 0 HP) wins the tiebreak.

---

## Behavioral Notes

- **Minimum damage floor**: Damage after armor reduction is clamped to a minimum of **1** per hit. Heavily armoured combatants can always be worn down.
- **Magic bypasses terrain**: `magic`-type combatants ignore `ranged_mod` but do not ignore `def_bonus`.
- **Draw condition**: If both sides reach zero living combatants in the same round (mutual annihilation), `winner` is `0` and `winner_name` is `"Draw"`.
- **Round cap**: To prevent infinite loops with very high-armor, low-damage configurations, the simulation enforces a maximum of **500 rounds**. If this cap is hit, the side with more surviving HP is declared the winner.
- **Determinism**: By default, dice rolls use Python's `random` module (not seeded). For reproducible results, seed before calling: `random.seed(42)`.
- **Log verbosity**: The `log` field in the result dict is only populated when `--log` is passed via CLI; via the Python API it is always populated.

---

## Example Workflow

### Workflow 1: Author a Roster and Run a Quick Battle

**`knights.yaml`:**
```yaml
- name: "Commander Vaelor"
  hp: 45
  armor: 6
  attack: 8
  damage: 12
  type: melee
  agility: 5
  morale: 90

- name: "Sister Orvaine"
  hp: 30
  armor: 4
  attack: 7
  damage: 9
  type: magic
  agility: 6
  morale: 85
```

**`bandits.yaml`:**
```yaml
- name: "Cutthroat Bren"
  hp: 25
  armor: 2
  attack: 7
  damage: 8
  type: melee
  agility: 9
  morale: 55

- name: "Marksman Yell"
  hp: 20
  armor: 1
  attack: 9
  damage: 10
  type: ranged
  agility: 10
  morale: 50
```

```powershell
arcanum tactical --side1 knights.yaml --side2 bandits.yaml --terrain dense_forest --log
```

**Sample output:**
```
Round 1: Marksman Yell targets Sister Orvaine — MISS (terrain penalty applied)
Round 1: Commander Vaelor strikes Cutthroat Bren for 8 damage (10 dmg - 2 armor)
...
Winner: Team 1 (Knights) in 7 rounds
MVP: Commander Vaelor — 34 total damage, 2 kills
```

### Workflow 2: Monte Carlo Encounter Balance Check

```powershell
arcanum tactical --side1 garrison.yaml --side2 siege_force.yaml --terrain castle_walls --runs 500
```

**Sample output:**
```
Monte Carlo Results (500 runs, castle_walls)
  Side 1 Win Rate:  71.4%
  Side 2 Win Rate:  26.2%
  Draw Rate:         2.4%
  Avg Rounds:       11.3
```

A 71% win rate suggests the garrison has a significant advantage — consider buffing the siege force or reducing the `def_bonus` terrain if you want a more dramatic scene.

### Workflow 3: Python API

```python
import yaml
from scripts.lib.tactical_sim import simulate_single_battle, run_monte_carlo

with open("knights.yaml") as f:
    side1 = yaml.safe_load(f)
with open("bandits.yaml") as f:
    side2 = yaml.safe_load(f)

# Single battle
result = simulate_single_battle(side1, side2, terrain="castle_walls")
print(f"Winner: {result['winner_name']} in {result['rounds_lasted']} rounds")
print(f"MVP: {result['mvp']['name']} ({result['mvp']['damage']} damage)")

# Monte Carlo
stats = run_monte_carlo(side1, side2, terrain="castle_walls", runs=1000)
print(f"Side 1 wins {stats['side1_win_rate']*100:.1f}% of the time")
```

---

*Part of the **Ars Arcanum Scriptorium** craft engine. For platform-wide CLI reference, see `docs/CLI_REFERENCE.md`.*
