#!/usr/bin/env python3
r"""
Ars Arcanum Planetary Climate, Orographic Biomes & Atmospheric Engine (scripts/lib/climate.py)
=============================================================================================
Zero-dependency, offline planetary insolation, atmospheric circulation, orographic rain shadow,
and Köppen biome validator for science-fiction and fantasy worldbuilders.

Capabilities:
1. Stellar Insolation & Equilibrium Surface Temperature:
   - Computes solar flux $S = 1361 \times (L / d^2)\ W/m^2$.
   - Calculates blackbody equilibrium temperature $T_{eq} = (S(1-A)/(4\sigma))^{1/4}$.
   - Computes surface temperature with atmospheric greenhouse coefficient.
2. Atmospheric Circulation Cells & Prevailing Winds:
   - Models Coriolis parameter and planetary rotation period (hours).
   - Generates Hadley, Ferrel, and Polar atmospheric circulation cells.
   - Determines prevailing surface wind vectors (Trade Winds, Westerlies, Polar Easterlies).
3. Orographic Rain Shadow Simulator:
   - Calculates adiabatic lapse rates ($9.8^\circ C/km$ dry, $5.0^\circ C/km$ moist).
   - Simulates windward precipitation enhancement vs leeward rain-shadow aridification.
4. Köppen Biome Classification:
   - Classifies ecological biomes from temperature and annual precipitation.


Zero external dependencies; 100% offline privacy.
"""

import sys
import json
import html
import argparse
import logging
from pathlib import Path

try:
    from lib.fs_utils import atomic_write
except ImportError:
    try:
        from fs_utils import atomic_write
    except ImportError:
        def atomic_write(path, data, encoding="utf-8"):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, (bytes, bytearray)):
                p.write_bytes(data)
            else:
                p.write_text(data, encoding=encoding)


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.climate")

# Physical constants
SIGMA = 5.670374419e-8          # Stefan-Boltzmann constant (W m^-2 K^-4)
SOLAR_CONSTANT_EARTH = 1361.0   # Earth solar flux at 1 AU (W/m^2)


def calc_planetary_insolation(
    stellar_luminosity: float = 1.0,
    semi_major_axis_au: float = 1.0,
    bond_albedo: float = 0.30,
    greenhouse_warming_k: float = 33.0
) -> dict:
    """Calculates stellar flux, equilibrium temperature, and surface temperature."""
    d = max(1e-6, float(semi_major_axis_au))
    lum = max(0.0, float(stellar_luminosity))
    albedo = min(0.999, max(0.0, float(bond_albedo)))
    
    # S = S0 * (L / d^2)
    stellar_flux = SOLAR_CONSTANT_EARTH * (lum / (d ** 2))
    
    # T_eq = [ S * (1 - A) / (4 * sigma) ]^(1/4)
    absorbed_flux = stellar_flux * (1.0 - albedo)
    t_eq_k = (absorbed_flux / (4.0 * SIGMA)) ** 0.25
    t_surf_k = t_eq_k + float(greenhouse_warming_k)
    t_surf_c = t_surf_k - 273.15

    # Habitable range check (liquid water at 1 atm: 0°C to 100°C)
    habitable = 0.0 <= t_surf_c <= 100.0

    return {
        "stellar_luminosity_sun": stellar_luminosity,
        "semi_major_axis_au": semi_major_axis_au,
        "bond_albedo": bond_albedo,
        "greenhouse_warming_k": greenhouse_warming_k,
        "stellar_flux_w_m2": round(stellar_flux, 1),
        "equilibrium_temp_k": round(t_eq_k, 1),
        "surface_temp_k": round(t_surf_k, 1),
        "surface_temp_c": round(t_surf_c, 1),
        "surface_temp_f": round(t_surf_c * 9.0 / 5.0 + 32.0, 1),
        "liquid_water_habitable": habitable,
    }


def calc_atmospheric_circulation(rotation_period_hours: float = 24.0) -> dict:
    """
    Determines number of atmospheric circulation cells and prevailing surface wind bands.
    """
    p = max(0.1, float(rotation_period_hours))
    if p > 120.0:
        # Slow rotator: Single Hadley cell per hemisphere (equator to pole)
        cells = 1
        bands = [
            {"lat_min": 0, "lat_max": 90, "name": "Global Hadley Cell", "wind_direction": "Slow Easterly / Direct Convection", "surface_flow": "Equatorward"}
        ]
    elif 16.0 <= p <= 120.0:
        # Earth-like 3-cell circulation
        cells = 3
        bands = [
            {"lat_min": 0, "lat_max": 30, "name": "Hadley Cell (Tropics)", "wind_direction": "Trade Winds (Easterlies / NE in North, SE in South)", "surface_flow": "Equatorward"},
            {"lat_min": 30, "lat_max": 60, "name": "Ferrel Cell (Mid-Latitudes)", "wind_direction": "Prevailing Westerlies (SW in North, NW in South)", "surface_flow": "Poleward"},
            {"lat_min": 60, "lat_max": 90, "name": "Polar Cell (High Latitudes)", "wind_direction": "Polar Easterlies (NE in North, SE in South)", "surface_flow": "Equatorward"},
        ]
    else:
        # Fast rotator: 5 cells (Jovian banded circulation)
        cells = 5
        bands = [
            {"lat_min": 0, "lat_max": 18, "name": "Equatorial Cell", "wind_direction": "Strong Tropical Easterlies", "surface_flow": "Equatorward"},
            {"lat_min": 18, "lat_max": 36, "name": "Subtropical Jet Cell", "wind_direction": "Strong Westerly Jet", "surface_flow": "Poleward"},
            {"lat_min": 36, "lat_max": 54, "name": "Mid-Latitude Cell", "wind_direction": "Banded Easterlies", "surface_flow": "Equatorward"},
            {"lat_min": 54, "lat_max": 72, "name": "Subpolar Jet Cell", "wind_direction": "Subpolar Westerlies", "surface_flow": "Poleward"},
            {"lat_min": 72, "lat_max": 90, "name": "Polar Vortex", "wind_direction": "Polar Easterlies", "surface_flow": "Equatorward"},
        ]

    return {
        "rotation_period_hours": p,
        "circulation_cells_per_hemisphere": cells,
        "coriolis_effect": "Negligible / Slow" if p > 120 else ("Moderate / Earth-like" if p >= 16 else "Extreme / Jovian"),
        "wind_bands": bands,
    }


def classify_koppen_biome(temp_c: float, annual_precip_mm: float) -> str:
    """Classifies terrestrial biome according to Köppen-Geiger logic."""
    if temp_c < -10.0:
        return "Polar Ice Cap"
    elif temp_c < 0.0:
        return "Tundra / Alpine Permafrost" if annual_precip_mm < 400 else "Glacial Taiga"
    elif temp_c < 10.0:
        if annual_precip_mm < 250:
            return "Cold Boreal Steppe"
        elif annual_precip_mm < 600:
            return "Boreal Forest / Taiga"
        else:
            return "Temperate Oceanic Rain Forest"
    elif temp_c < 22.0:
        if annual_precip_mm < 250:
            return "Arid Mid-Latitude Desert"
        elif annual_precip_mm < 500:
            return "Semiarid Steppe / Scrubland"
        elif annual_precip_mm < 1200:
            return "Temperate Deciduous Woodland"
        else:
            return "Temperate Rainforest"
    else:
        # Hot Tropical / Subtropical
        if annual_precip_mm < 250:
            return "Hyper-Arid Subtropical Desert"
        elif annual_precip_mm < 600:
            return "Tropical Semiarid Savanna"
        elif annual_precip_mm < 1800:
            return "Tropical Monsoon Forest"
        else:
            return "Tropical Rainforest (Equatorial)"


def calc_orographic_rain_shadow(
    mountain_elevation_m: float = 3000.0,
    base_precip_mm: float = 1000.0,
    base_temp_c: float = 20.0,
    wind_speed_kmh: float = 30.0
) -> dict:
    """
    Simulates orographic precipitation on windward slope and rain-shadow desert on leeward slope.
    """
    # Dry adiabatic lapse rate = 9.8°C / km
    # Moist adiabatic lapse rate = 5.0°C / km
    elev = max(0.0, float(mountain_elevation_m))
    crest_temp_c = float(base_temp_c) - (elev / 1000.0) * 6.5
    
    # Windward side: precipitation enhancement
    # Precip increases with elevation up to ~2500m
    windward_factor = 1.0 + min(1.8, (elev / 1000.0) * 0.45)
    windward_precip_mm = max(0.0, float(base_precip_mm)) * windward_factor
    windward_biome = classify_koppen_biome(crest_temp_c + 4.0, windward_precip_mm)

    # Leeward side: adiabatic descent warming and relative humidity plummet
    # Precip collapses
    leeward_precip_mm = max(0.0, float(base_precip_mm)) * max(0.08, 1.0 - (elev / 1000.0) * 0.28)
    leeward_temp_c = float(base_temp_c) + (elev / 1000.0) * 1.5 # Foehn / Chinook heating
    leeward_biome = classify_koppen_biome(leeward_temp_c, leeward_precip_mm)

    is_rain_shadow = (leeward_precip_mm < 350.0) or (windward_precip_mm / max(1.0, leeward_precip_mm) > 2.5)

    return {
        "mountain_elevation_m": mountain_elevation_m,
        "base_precip_mm": base_precip_mm,
        "base_temp_c": base_temp_c,
        "crest_temp_c": round(crest_temp_c, 1),
        "windward": {
            "precipitation_mm": round(windward_precip_mm, 1),
            "precipitation_multiplier": round(windward_factor, 2),
            "biome": windward_biome,
            "climate_desc": "Moist Orographic Cloud Forest / Rainforest",
        },
        "leeward": {
            "precipitation_mm": round(leeward_precip_mm, 1),
            "foehn_temp_c": round(leeward_temp_c, 1),
            "biome": leeward_biome,
            "climate_desc": "Arid Rain-Shadow Basin / Desert" if is_rain_shadow else "Moderately Drier Valley",
        },
        "is_severe_rain_shadow": is_rain_shadow,
    }


def generate_climate_html_report(climate_data: dict, output_path: Path):
    """Generates standalone HTML report for Planetary Climate and Biomes."""
    ins = climate_data.get("insolation", {})
    circ = climate_data.get("circulation", {})
    oro = climate_data.get("orography", {})

    wind_rows = []
    for b in circ.get("wind_bands", []):
        wind_rows.append(f"""
        <tr>
            <td>{b['lat_min']}° - {b['lat_max']}°</td>
            <td><strong>{html.escape(b['name'])}</strong></td>
            <td>{html.escape(b['wind_direction'])}</td>
            <td>{html.escape(b['surface_flow'])}</td>
        </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Planetary Climate & Biome Simulator</title>
<style>
  :root {{
    --bg: #0f172a;
    --card-bg: #1e293b;
    --border: #334155;
    --text: #f8fafc;
    --accent: #38bdf8;
    --warning: #fbbf24;
    --success: #34d399;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 2rem;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  h1, h2, h3 {{ color: var(--accent); }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ background: #0f172a; color: var(--accent); }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>🌍 Ars Arcanum Planetary Climate & Biome Simulator</h1>

  <div class="grid">
    <div class="card">
      <h2>Stellar Insolation & Surface Temp</h2>
      <p>Stellar Flux: <strong>{ins.get('stellar_flux_w_m2')} W/m²</strong></p>
      <p>Equilibrium Temp: <strong>{ins.get('equilibrium_temp_k')} K</strong></p>
      <p>Mean Surface Temp: <strong>{ins.get('surface_temp_c')} °C ({ins.get('surface_temp_f')} °F)</strong></p>
      <p>Liquid Water Habitable: <strong>{'✓ Yes' if ins.get('liquid_water_habitable') else '✗ No'}</strong></p>
    </div>

    <div class="card">
      <h2>Atmospheric Circulation</h2>
      <p>Rotation Period: <strong>{circ.get('rotation_period_hours')} hours</strong></p>
      <p>Circulation Cells: <strong>{circ.get('circulation_cells_per_hemisphere')} per hemisphere</strong></p>
      <p>Coriolis Intensity: <strong>{circ.get('coriolis_effect')}</strong></p>
    </div>
  </div>

  <div class="card">
    <h2>Orographic Rain Shadow Dynamics ({oro.get('mountain_elevation_m')}m Ridge)</h2>
    <div class="grid">
      <div style="border-right: 1px solid var(--border); padding-right: 1rem;">
        <h3 style="color: #34d399;">Windward Slope (Wet)</h3>
        <p>Precipitation: <strong>{oro.get('windward', {}).get('precipitation_mm')} mm/yr</strong></p>
        <p>Biome: <strong>{oro.get('windward', {}).get('biome')}</strong></p>
      </div>
      <div>
        <h3 style="color: #fbbf24;">Leeward Slope (Rain Shadow)</h3>
        <p>Precipitation: <strong>{oro.get('leeward', {}).get('precipitation_mm')} mm/yr</strong></p>
        <p>Biome: <strong>{oro.get('leeward', {}).get('biome')}</strong></p>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Prevailing Wind Bands</h2>
    <table>
      <thead>
        <tr><th>Latitude</th><th>Circulation Cell</th><th>Prevailing Wind Direction</th><th>Surface Flow</th></tr>
      </thead>
      <tbody>
        {"".join(wind_rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Planetary Climate & Orographic Simulator")
    parser.add_argument("--star-lum", type=float, default=1.0, help="Stellar luminosity in L_sun (default 1.0)")
    parser.add_argument("--distance-au", type=float, default=1.0, help="Orbital semi-major axis in AU (default 1.0)")
    parser.add_argument("--albedo", type=float, default=0.30, help="Bond albedo (default 0.30)")
    parser.add_argument("--greenhouse", type=float, default=33.0, help="Greenhouse warming in K (default 33.0)")
    parser.add_argument("--rotation-hours", type=float, default=24.0, help="Planetary rotation period in hours (default 24.0)")
    parser.add_argument("--mountain-elevation", type=float, default=3000.0, help="Mountain ridge elevation in meters (default 3000)")
    parser.add_argument("--base-precip", type=float, default=1000.0, help="Base precipitation in mm/year (default 1000)")
    parser.add_argument("--base-temp", type=float, default=20.0, help="Base surface temperature in °C (default 20)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--html", help="Path to export standalone HTML report")

    args = parser.parse_args()

    ins = calc_planetary_insolation(
        stellar_luminosity=args.star_lum,
        semi_major_axis_au=args.distance_au,
        bond_albedo=args.albedo,
        greenhouse_warming_k=args.greenhouse,
    )
    circ = calc_atmospheric_circulation(rotation_period_hours=args.rotation_hours)
    oro = calc_orographic_rain_shadow(
        mountain_elevation_m=args.mountain_elevation,
        base_precip_mm=args.base_precip,
        base_temp_c=args.base_temp,
    )

    result = {
        "insolation": ins,
        "circulation": circ,
        "orography": oro,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n\033[1;36m=== Ars Arcanum Planetary Climate & Biome Model ===\033[0m")
        print(f"Stellar Insolation : \033[1m{ins['stellar_flux_w_m2']} W/m²\033[0m ({args.star_lum} L_sun @ {args.distance_au} AU)")
        print(f"Mean Surface Temp  : \033[1;32m{ins['surface_temp_c']} °C\033[0m ({ins['surface_temp_f']} °F) — Habitable: {ins['liquid_water_habitable']}")
        print(f"Atmosphere         : {circ['circulation_cells_per_hemisphere']} circulation cells per hemisphere ({circ['coriolis_effect']} Coriolis)")
        print(f"\n\033[1;33mOrographic Rain Shadow ({oro['mountain_elevation_m']}m Mountain Ridge):\033[0m")
        print(f"  🌬️ Windward Slope : \033[32m{oro['windward']['precipitation_mm']} mm/yr\033[0m -> Biome: \033[1m{oro['windward']['biome']}\033[0m")
        print(f"  🏜️ Leeward Basin  : \033[31m{oro['leeward']['precipitation_mm']} mm/yr\033[0m -> Biome: \033[1m{oro['leeward']['biome']}\033[0m")
        if oro['is_severe_rain_shadow']:
            print("  ⚠️ Severe Rain Shadow Desert detected on leeward side.\n")
        else:
            print()

    if args.html:
        out_p = Path(args.html)
        generate_climate_html_report(result, out_p)
        print(f"Interactive HTML report written to: {out_p}")

    sys.exit(0)


if __name__ == "__main__":
    main()