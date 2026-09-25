# Ars Arcanum Overland, Naval & Aerial Journey Modeler Guide (`docs/JOURNEY.md`)

---

## 1. Overview & System Mission

The **Ars Arcanum Journey Engine** (`scripts/lib/journey.py`) is an offline expedition planning, terrain friction, travel pace, and party supply consumption modeler for fantasy, historical, and speculative fiction authors.

Maintaining realistic travel times, terrain difficulties, and supply logistics is one of the hardest aspects of worldbuilding. Characters frequently cross continental mountain ranges in days or carry months of rations without pack animals. The Journey Engine provides mathematical rigor to overland expeditions, naval voyages, and aerial sorties.

---

## 2. Terrain Friction Coefficients

Terrain type alters base movement speeds according to environmental friction:

| Terrain Type | Speed Multiplier | Description |
| :--- | :---: | :--- |
| **`paved-road` / `highway`** | `1.00x` | Maintained stone imperial road. Full standard pace. |
| **`dirt-road` / `trail`** | `0.85x` | Beaten dirt pathway or wagon trail. Minor resistance. |
| **`plains` / `grassland`** | `0.75x` | Open steppe, savanna, or meadow without roads. |
| **`hills`** | `0.60x` | Rolling hills, moderate incline, and broken ground. |
| **`forest` / `woods`** | `0.50x` | Temperate canopy, brush, and uneven forest floor. |
| **`desert` / `dunes`** | `0.40x` | Shifting sand, heat exhaustion, and high friction. |
| **`mountain-pass` / `mountains`**| `0.35x` | Steep rocky trails, high altitude, and narrow paths. |
| **`tundra` / `snow`** | `0.35x` | Frozen permafrost, deep snowdrifts, and icy crust. |
| **`jungle` / `rainforest`** | `0.30x` | Dense tropical undergrowth requiring machetes. |
| **`swamp` / `marsh` / `bog`** | `0.25x` | Deep mud, stagnant waters, and sinking terrain. |
| **`peaks`** | `0.20x` | Treacherous unmapped summit passes and cliffs. |
| **`river-downstream`** | `1.20x` | River navigation traveling with the current. |
| **`river-upstream`** | `0.50x` | River navigation rowing or towing against the current. |
| **`ocean` / `coastal-sea`** | `1.00x` | Open deepwater or coastal sea lanes. |

---

## 3. Travel Modes & Base Speeds

Pace is computed over a standard 8-hour travel day:

| Mode Identifier | Mode Name | Base Speed (km/day) | Domain | Notes |
| :--- | :--- | :---: | :---: | :--- |
| `foot-normal` | Foot (Normal March) | **24.0 km/d** | Land | Sustainable indefinitely. |
| `foot-fast` | Foot (Fast March) | **32.0 km/d** | Land | Heavy exertion. |
| `foot-forced` | Foot (Forced March) | **40.0 km/d** | Land | Fatigue risk; cumulative exhaustion. |
| `foot-cautious` | Foot (Cautious / Stealth) | **16.0 km/d** | Land | Scouting and avoiding detection. |
| `caravan-wagon` | Caravan (Heavy Oxen Wagons) | **18.0 km/d** | Land | Bulk cargo freight. |
| `caravan-mules` | Caravan (Pack Mule Train) | **22.0 km/d** | Land | Mountain-capable cargo train. |
| `horse-walk` | Mounted (Walking Pace) | **32.0 km/d** | Land | Cavalry march saving horse stamina. |
| `horse-trot` | Mounted (Cruising Trot) | **48.0 km/d** | Land | Standard cruising speed for riders. |
| `horse-relay` | Mounted (Courier / Relay Gallop)| **80.0 km/d** | Land | Requires fresh horse remount stations. |
| `ship-galley` | Naval (Rowed Galley) | **40.0 km/d** | Water | Requires large rowing crew. |
| `ship-cog` | Naval (Merchant Sailing Cog)| **80.0 km/d** | Water | Standard merchant sailing vessel. |
| `ship-longship` | Naval (Viking Longship) | **90.0 km/d** | Water | Shallow draft; rowing and sail. |
| `ship-frigate` | Naval (Fast Caravel / Frigate) | **140.0 km/d** | Water | Multi-mast oceanic warship. |
| `aerial-airship`| Aerial (Steam / Magic Airship) | **200.0 km/d** | Air | Ignores ground terrain friction. |
| `aerial-dragon` | Aerial (Dragon Flight) | **350.0 km/d** | Air | High-speed aerial transit. |

---

## 4. Supply & Ration Logistics Mathematics

The engine models daily consumption rates for parties and livestock:

- **Food Rations**: $1.0\text{ kg} / \text{person} / \text{day}$
- **Drinking Water (Standard)**: $3.0\text{ Liters} / \text{person} / \text{day}$
- **Drinking Water (Desert / Arid)**: $4.5\text{ Liters} / \text{person} / \text{day}$
- **Mount Feed (Hay / Grain)**: $8.0\text{ kg} / \text{mount} / \text{day}$
- **Mount Water**: $25.0\text{ Liters} / \text{mount} / \text{day}$

$$\text{Total Cargo Weight} = \text{Food}(\text{kg}) + \text{Water}(\text{kg}) + \text{Mount Feed}(\text{kg})$$

If the author specifies an initial supply allotment (`--rations-days`), the engine flags potential starvation or dehydration points along the route.

---

## 5. Command-Line Interface (CLI)

```bash
# Calculate travel duration and supplies for an overland march
arcanum journey --dist "120 km" --terrain "mountains" --mode "foot-normal" --party 4

# Model a cavalry trek with mounts through plains
arcanum journey --dist "200 km" --terrain "plains" --mode "horse-trot" --party 2 --mounts 2

# Plan a naval voyage and export an interactive HTML itinerary
arcanum journey --dist "500 km" --terrain "ocean" --mode "ship-frigate" --party 20 --html voyage_plan.html
```

---

## 6. HTML Itinerary Report & Security Guarantee

Generated HTML expedition reports include day-by-day distance milestones, cumulative ration consumption, and remaining distance indicators with strict offline security headers:

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
```
