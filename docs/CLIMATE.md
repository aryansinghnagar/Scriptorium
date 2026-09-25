# CLIMATE — Planetary Climate, Orographic Biomes & Atmospheric Engine

> **Module**: `scripts/lib/climate.py`  
> **CLI Command**: `arcanum climate`  
> **Purpose**: Deterministic, zero-dependency astrophysical climate simulator that calculates planetary insolation, surface temperatures, atmospheric circulation cells, orographic rain-shadow dynamics, and Köppen biome classifications for speculative fiction worldbuilders.

---

## Table of Contents

1. [Overview](#overview)
2. [CLI Usage](#cli-usage)
3. [Key API Reference](#key-api-reference)
4. [Insolation & Surface Temperature Model](#insolation--surface-temperature-model)
5. [Atmospheric Circulation & Wind Bands](#atmospheric-circulation--wind-bands)
6. [Orographic Rain Shadow Dynamics](#orographic-rain-shadow-dynamics)
7. [Köppen-Geiger Biome Classification](#köppen-geiger-biome-classification)
8. [Standalone HTML Report](#standalone-html-report)
9. [Example Workflows](#example-workflows)

---

## Overview

The `climate` engine provides mathematically rigorous planetary climatology and biome modeling for sci-fi and fantasy worldbuilders. It translates astronomical and geographical parameters into concrete ecological realities:

- **Insolation & Habitability**: Computes solar constant scaling ($S = 1361 \times \frac{L}{d^2}\ \text{W/m}^2$) and Stefan-Boltzmann blackbody radiation equilibrium temperatures ($T_{eq} = \left[\frac{S(1-A)}{4\sigma}\right]^{1/4}$) factoring in atmospheric greenhouse heating.
- **Atmospheric Circulation Cells**: Derives 1-cell (slow rotator / Venusian), 3-cell (Earth-like), or 5-cell (Jovian / rapid rotator) circulation systems from the planetary rotation period.
- **Orographic Rain Shadows**: Simulates adiabatic lapse rate cooling ($6.5^\circ\text{C/km}$ average, $9.8^\circ\text{C/km}$ dry, $5.0^\circ\text{C/km}$ moist) on windward slopes versus adiabatic descent heating (Foehn/Chinook effect) and precipitation collapse on leeward basins.
- **Köppen Biome Classification**: Maps temperature and precipitation coordinates directly into standard terrestrial biome designations.

---

## CLI Usage

```bash
arcanum climate [OPTIONS]
```

### Options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--star-lum FLOAT` | float | `1.0` | Stellar luminosity in solar units ($L_\odot$) |
| `--distance-au FLOAT` | float | `1.0` | Orbital semi-major axis in Astronomical Units (AU) |
| `--albedo FLOAT` | float | `0.30` | Planetary Bond albedo ($0.0 \le A < 1.0$) |
| `--greenhouse FLOAT` | float | `33.0` | Atmospheric greenhouse warming in Kelvin ($\Delta T_g$) |
| `--rotation-hours FLOAT` | float | `24.0` | Planetary rotation period (sidereal day) in hours |
| `--mountain-elevation FLOAT` | float | `3000.0` | Mountain ridge elevation in meters ($m$) |
| `--base-precip FLOAT` | float | `1000.0` | Base sea-level precipitation in mm/year |
| `--base-temp FLOAT` | float | `20.0` | Base sea-level surface temperature in $^\circ\text{C}$ |
| `--json` | flag | off | Output machine-readable structured JSON payload |
| `--html PATH` | path | *(none)* | Export standalone, offline-ready interactive HTML report |

---

## Key API Reference

```python
from lib.climate import (
    calc_planetary_insolation,
    calc_atmospheric_circulation,
    calc_orographic_rain_shadow,
    classify_koppen_biome,
    generate_climate_html_report,
)
```

### `calc_planetary_insolation(...) -> dict`

```python
def calc_planetary_insolation(
    stellar_luminosity: float = 1.0,
    semi_major_axis_au: float = 1.0,
    bond_albedo: float = 0.30,
    greenhouse_warming_k: float = 33.0
) -> dict
```

Calculates stellar flux, equilibrium radiation temperature, and effective surface temperature.

**Return Keys**:
- `stellar_luminosity_sun` (`float`): Stellar luminosity in $L_\odot$.
- `semi_major_axis_au` (`float`): Semi-major axis distance in AU.
- `bond_albedo` (`float`): Surface/atmospheric reflection ratio.
- `greenhouse_warming_k` (`float`): Greenhouse temperature delta in Kelvin.
- `stellar_flux_w_m2` (`float`): Total stellar irradiance at orbit ($W/m^2$).
- `equilibrium_temp_k` (`float`): Blackbody equilibrium temperature in Kelvin.
- `surface_temp_k` (`float`): Surface temperature in Kelvin ($T_{eq} + \Delta T_g$).
- `surface_temp_c` (`float`): Surface temperature in $^\circ\text{C}$.
- `surface_temp_f` (`float`): Surface temperature in $^\circ\text{F}$.
- `liquid_water_habitable` (`bool`): True if $0^\circ\text{C} \le T_{\text{surf}} \le 100^\circ\text{C}$ at 1 atm.

---

### `calc_atmospheric_circulation(...) -> dict`

```python
def calc_atmospheric_circulation(rotation_period_hours: float = 24.0) -> dict
```

Calculates planetary atmospheric circulation regime and prevailing surface wind vectors from rotation period.

**Return Keys**:
- `rotation_period_hours` (`float`): Rotational period in hours.
- `circulation_cells_per_hemisphere` (`int`): 1 (slow rotator, $>120\text{h}$), 3 (Earth-like, $16\text{–}120\text{h}$), or 5 (rapid rotator, $<16\text{h}$).
- `coriolis_effect` (`str`): Qualitative strength (`"Negligible / Slow"`, `"Moderate / Earth-like"`, `"Extreme / Jovian"`).
- `wind_bands` (`list[dict]`): List of latitudinal wind bands with `lat_min`, `lat_max`, `name`, `wind_direction`, and `surface_flow`.

---

### `calc_orographic_rain_shadow(...) -> dict`

```python
def calc_orographic_rain_shadow(
    mountain_elevation_m: float = 3000.0,
    base_precip_mm: float = 1000.0,
    base_temp_c: float = 20.0,
    wind_speed_kmh: float = 30.0
) -> dict
```

Simulates orographic precipitation enhancement on windward slopes and rain-shadow aridification on leeward slopes.

**Return Keys**:
- `mountain_elevation_m` (`float`): Elevation of the mountain crest.
- `base_precip_mm` (`float`): Unobstructed baseline precipitation.
- `base_temp_c` (`float`): Unobstructed baseline temperature.
- `crest_temp_c` (`float`): Temperature at mountain crest.
- `windward` (`dict`): Precipitation amount, enhancement multiplier, biome classification, and climate description.
- `leeward` (`dict`): Precipitation amount, adiabatic Foehn heating temperature, biome classification, and climate description.
- `is_severe_rain_shadow` (`bool`): True if leeward precipitation drops below $350\text{ mm}$ or windward/leeward ratio exceeds $2.5\times$.

---

### `classify_koppen_biome(temp_c: float, annual_precip_mm: float) -> str`

Classifies ecological biome according to thermal and hygric conditions.

| Mean Temp ($^\circ\text{C}$) | Annual Precip (mm) | Köppen Biome Designation |
|---|---|---|
| $< -10$ | Any | Polar Ice Cap |
| $-10 \le T < 0$ | $< 400$ | Tundra / Alpine Permafrost |
| $-10 \le T < 0$ | $\ge 400$ | Glacial Taiga |
| $0 \le T < 10$ | $< 250$ | Cold Boreal Steppe |
| $0 \le T < 10$ | $250\text{–}600$ | Boreal Forest / Taiga |
| $0 \le T < 10$ | $> 600$ | Temperate Oceanic Rain Forest |
| $10 \le T < 22$ | $< 250$ | Arid Mid-Latitude Desert |
| $10 \le T < 22$ | $250\text{–}500$ | Semiarid Steppe / Scrubland |
| $10 \le T < 22$ | $500\text{–}1200$ | Temperate Deciduous Woodland |
| $10 \le T < 22$ | $> 1200$ | Temperate Rainforest |
| $\ge 22$ | $< 250$ | Hyper-Arid Subtropical Desert |
| $\ge 22$ | $250\text{–}600$ | Tropical Semiarid Savanna |
| $\ge 22$ | $600\text{–}1800$ | Tropical Monsoon Forest |
| $\ge 22$ | $> 1800$ | Tropical Rainforest (Equatorial) |

---

## Standalone HTML Report

The `--html` option generates a self-contained, offline-compatible HTML report:
- Declares strict CSP headers (`default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:;`).
- Renders visual atmospheric circulation diagrams and latitudinal wind bands.
- Visualizes windward vs. leeward precipitation profiles and Köppen biome badges.

---

## Example Workflows

### 1. Habitable World Around a Red Dwarf (M-Dwarf)
```bash
# Dim star (0.05 L_sun), close orbit (0.15 AU), high greenhouse (40K), tidal lock / slow rotation (200h)
arcanum climate --star-lum 0.05 --distance-au 0.15 --greenhouse 40.0 --rotation-hours 200.0 --html reports/m_dwarf_climate.html
```

### 2. High-Altitude Continental Rain Shadow
```bash
# Earth-like sun and orbit, but 4500m mountain range blocking oceanic winds
arcanum climate --mountain-elevation 4500 --base-precip 1200 --base-temp 22
```
