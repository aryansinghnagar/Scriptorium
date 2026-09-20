#!/usr/bin/env python3
"""
Ars Arcanum Overland & Naval Journey Modeler (scripts/lib/journey.py)
===================================================================
Offline expedition planning, terrain friction, travel pace, and supply consumption
calculator for fantasy, historical, and speculative worldbuilding.

Capabilities:
1. Terrain Friction Modifiers:
   - Paved Imperial Road (1.0x), Dirt Trail (0.85x), Plains (0.75x), Forest (0.5x),
     Jungle (0.3x), Hills (0.6x), Mountain Pass (0.35x), Treacherous Peaks (0.2x),
     Swamp (0.25x), Desert Dunes (0.4x), River Downstream (1.2x), River Upstream (0.5x),
     Ocean Sailing (1.0x), Arctic Tundra/Snow (0.35x)
2. Travel Modes & Paces:
   - Foot (Normal 24 km/d, Fast 32 km/d, Forced 40 km/d, Cautious 16 km/d)
   - Pack Caravan (Oxen Wagon 18 km/d, Mule Train 22 km/d)
   - Mounted Cavalry (Horse Walk 32 km/d, Trot 48 km/d, Gallop Relay 80 km/d)
   - Naval (Rowed Galley 40 km/d, Merchant Cog 80 km/d, Fast Frigate 140 km/d, Longship 90 km/d)
   - Aerial (Airship 200 km/d, Dragon Flight 350 km/d)
3. Party Supply & Ration Consumption:
   - Rations (1.0 kg/person/day) & Water (3.0 L/person/day, 4.5 L in desert)
   - Mount feed (8.0 kg/mount/day) & Mount water (25 L/mount/day)
   - Weight capacities, autonomous range, and starvation/dehydration risk points
4. Multi-Leg Expedition Itineraries & HTML Export

Zero external dependencies; 100% offline privacy.
"""

import sys
import os
import re
import json
import math
import html
import argparse
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.journey")

# Terrain friction coefficients
TERRAIN_MODIFIERS = {
    "paved-road": 1.0,
    "highway": 1.0,
    "road": 1.0,
    "dirt-road": 0.85,
    "trail": 0.85,
    "plains": 0.75,
    "grassland": 0.75,
    "hills": 0.60,
    "forest": 0.50,
    "woods": 0.50,
    "jungle": 0.30,
    "rainforest": 0.30,
    "mountain-pass": 0.35,
    "mountains": 0.35,
    "peaks": 0.20,
    "swamp": 0.25,
    "marsh": 0.25,
    "bog": 0.25,
    "desert": 0.40,
    "dunes": 0.40,
    "tundra": 0.35,
    "snow": 0.35,
    "river-downstream": 1.20,
    "river-upstream": 0.50,
    "coastal-sea": 1.0,
    "ocean": 1.0,
}

# Base pace speeds in km per standard travel day (8 hours travel)
TRAVEL_MODES = {
    "foot-normal": {"name": "Foot (Normal March)", "base_km_day": 24.0, "type": "land"},
    "foot-fast": {"name": "Foot (Fast March)", "base_km_day": 32.0, "type": "land"},
    "foot-forced": {"name": "Foot (Forced March)", "base_km_day": 40.0, "type": "land", "fatigue_risk": True},
    "foot-cautious": {"name": "Foot (Cautious / Stealth)", "base_km_day": 16.0, "type": "land"},
    "caravan-wagon": {"name": "Caravan (Oxen / Heavy Wagons)", "base_km_day": 18.0, "type": "land"},
    "caravan-mules": {"name": "Caravan (Pack Mule Train)", "base_km_day": 22.0, "type": "land"},
    "horse-walk": {"name": "Mounted (Walking Pace)", "base_km_day": 32.0, "type": "land"},
    "horse-trot": {"name": "Mounted (Cruising Trot)", "base_km_day": 48.0, "type": "land"},
    "horse-relay": {"name": "Mounted (Courier / Relay Gallop)", "base_km_day": 80.0, "type": "land"},
    "ship-galley": {"name": "Naval (Rowed Galley)", "base_km_day": 40.0, "type": "water"},
    "ship-cog": {"name": "Naval (Merchant Sailing Cog)", "base_km_day": 80.0, "type": "water"},
    "ship-frigate": {"name": "Naval (Fast Caravel / Frigate)", "base_km_day": 140.0, "type": "water"},
    "ship-longship": {"name": "Naval (Viking Longship)", "base_km_day": 90.0, "type": "water"},
    "aerial-airship": {"name": "Aerial (Steam / Magic Airship)", "base_km_day": 200.0, "type": "air"},
    "aerial-dragon": {"name": "Aerial (Dragon Flight)", "base_km_day": 350.0, "type": "air"},
}


def parse_distance_km(val_str: str) -> float:
    """Parses distance strings like '150 km', '100 miles', '50 leagues', '200000 m' to kilometers."""
    s = val_str.strip().lower()
    if s.endswith("km"):
        return float(s[:-2].strip())
    if s.endswith("miles") or s.endswith("mi"):
        num = float(s.split("mi")[0].strip())
        return num * 1.60934
    if s.endswith("leagues") or s.endswith("league"):
        num = float(s.split("league")[0].strip())
        return num * 4.82803  # 1 league ~ 3 miles ~ 4.8 km
    if s.endswith("m") and not s.endswith("km"):
        return float(s[:-1].strip()) / 1000.0
    return float(s)


def calculate_journey(distance_km: float, terrain: str = "road", mode: str = "foot-normal",
                      party_size: int = 4, mounts: int = 0, initial_rations_days: float = None) -> dict:
    """Calculates journey duration, daily travel rate, and supply requirements."""
    # Find mode
    mode_key = mode.lower()
    if mode_key not in TRAVEL_MODES:
        # Match closest mode
        matched = [k for k in TRAVEL_MODES if mode_key in k]
        mode_key = matched[0] if matched else "foot-normal"

    mode_info = TRAVEL_MODES[mode_key]
    base_speed = mode_info["base_km_day"]

    # Terrain friction
    terr_key = terrain.lower().replace(" ", "-")
    friction = TERRAIN_MODIFIERS.get(terr_key, 1.0)
    if mode_info["type"] == "air":
        friction = 1.0  # Aerial ignores ground terrain

    effective_speed = round(base_speed * friction, 6)
    total_days = distance_km / effective_speed if effective_speed > 0 else 0.0

    # Supply calculation
    water_per_person = 4.5 if "desert" in terr_key or "dunes" in terr_key else 3.0  # Liters
    ration_per_person = 1.0  # kg

    mount_water = 25.0  # Liters
    mount_feed = 8.0   # kg

    total_rations_kg = party_size * ration_per_person * total_days
    total_water_liters = party_size * water_per_person * total_days
    total_mount_feed_kg = mounts * mount_feed * total_days
    total_mount_water_liters = mounts * mount_water * total_days

    # Autonomous supply status
    supply_status = "Adequate"
    if initial_rations_days is not None:
        if initial_rations_days < total_days:
            supply_status = f"Deficit! Starvation risk at Day {initial_rations_days:.1f} (short by {total_days - initial_rations_days:.1f} days)"
        else:
            supply_status = f"Sufficient (+{initial_rations_days - total_days:.1f} surplus days)"

    # Daily itinerary breakdown
    itinerary = []
    accum_km = 0.0
    num_travel_days = math.ceil(round(total_days, 6))
    for day in range(1, num_travel_days + 1):
        day_dist = min(effective_speed, distance_km - accum_km)
        accum_km += day_dist
        itinerary.append({
            "day": day,
            "distance_today_km": round(day_dist, 1),
            "distance_total_km": round(accum_km, 1),
            "remaining_km": round(max(0.0, distance_km - accum_km), 1),
            "rations_used_kg": round(party_size * ration_per_person * day, 1),
            "water_used_l": round((party_size * water_per_person + mounts * mount_water) * day, 1),
        })

    return {
        "distance_km": distance_km,
        "terrain": terrain,
        "terrain_modifier": friction,
        "travel_mode": mode_info["name"],
        "base_speed_km_day": base_speed,
        "effective_speed_km_day": round(effective_speed, 2),
        "total_days": round(total_days, 2),
        "total_days_formatted": f"{total_days:.1f} days ({math.ceil(total_days)} travel days)",
        "party_size": party_size,
        "mounts": mounts,
        "supplies_required": {
            "rations_food_kg": round(total_rations_kg, 1),
            "water_liters": round(total_water_liters, 1),
            "mount_feed_kg": round(total_mount_feed_kg, 1),
            "mount_water_liters": round(total_mount_water_liters, 1),
            "total_cargo_weight_kg": round(total_rations_kg + total_water_liters + total_mount_feed_kg, 1)
        },
        "supply_status": supply_status,
        "itinerary": itinerary,
    }


def generate_journey_html_report(journey: dict, output_file: Path):
    """Generates an interactive HTML journey & expedition planning report."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Expedition Route Plan — {journey['distance_km']} km</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --accent: #e3b341;
    --success: #3fb950;
    --danger: #f85149;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  body {{ background-color: var(--bg); color: var(--text); font-family: var(--font); line-height: 1.6; margin: 0; padding: 24px; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  header {{ border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
  h1 {{ color: var(--accent); margin: 0 0 8px 0; }}
  .badge {{ background: #e3b34122; color: var(--accent); border: 1px solid var(--accent); padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
  h2 {{ margin-top: 0; color: #f0f6fc; font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; }}
  th {{ color: #8b949e; font-weight: 600; }}
  td {{ color: #f0f6fc; }}
  footer {{ text-align: center; font-size: 12px; color: #8b949e; margin-top: 40px; border-top: 1px solid var(--border); padding-top: 16px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🗺️ Expedition Route & Journey Plan</h1>
    <span class="badge">Distance: {journey['distance_km']} km</span>
    <span class="badge">Duration: {journey['total_days_formatted']}</span>
  </header>

  <div class="card">
    <h2>Journey Logistics Overview</h2>
    <table>
      <tr><th>Travel Mode</th><td>{html.escape(journey['travel_mode'])}</td></tr>
      <tr><th>Terrain Friction</th><td>{html.escape(journey['terrain'])} ({journey['terrain_modifier']}x speed modifier)</td></tr>
      <tr><th>Effective Travel Pace</th><td><strong>{journey['effective_speed_km_day']} km / day</strong> (Base: {journey['base_speed_km_day']} km/d)</td></tr>
      <tr><th>Party Size & Mounts</th><td>{journey['party_size']} persons • {journey['mounts']} mounts</td></tr>
      <tr><th>Food Rations Needed</th><td>{journey['supplies_required']['rations_food_kg']} kg</td></tr>
      <tr><th>Drinking Water Needed</th><td>{journey['supplies_required']['water_liters']} L</td></tr>
      <tr><th>Mount Feed / Water</th><td>{journey['supplies_required']['mount_feed_kg']} kg feed • {journey['supplies_required']['mount_water_liters']} L water</td></tr>
      <tr><th>Total Supply Cargo Weight</th><td><strong>{journey['supplies_required']['total_cargo_weight_kg']} kg</strong></td></tr>
      <tr><th>Supply Status</th><td>{html.escape(journey['supply_status'])}</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>Day-by-Day March Itinerary ({len(journey['itinerary'])} Days)</h2>
    <table>
      <tr><th>Day</th><th>March Dist</th><th>Total Distance</th><th>Remaining</th><th>Rations Burned</th><th>Water Burned</th></tr>
"""
    for row in journey["itinerary"]:
        html_content += f"""      <tr>
        <td><strong>Day {row['day']}</strong></td>
        <td>{row['distance_today_km']} km</td>
        <td>{row['distance_total_km']} km</td>
        <td>{row['remaining_km']} km</td>
        <td>{row['rations_used_kg']} kg</td>
        <td>{row['water_used_l']} L</td>
      </tr>\n"""

    html_content += """    </table>
  </div>
  <footer>
    Generated by Ars Arcanum • 100% Offline Speculative Authoring Suite
  </footer>
</div>
</body>
</html>
"""
    output_file.write_text(html_content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Overland & Naval Journey Modeler")
    parser.add_argument("distance", nargs="?", help="Distance to travel (e.g. '150 km', '80 miles', '25 leagues')")
    parser.add_argument("-d", "--dist", help="Distance argument alternative")
    parser.add_argument("-t", "--terrain", default="road", help="Terrain type (road, trail, plains, hills, forest, jungle, mountains, swamp, desert, ocean, etc.)")
    parser.add_argument("-p", "--pace", default="foot-normal", help="Travel mode & pace (foot-normal, foot-fast, horse-walk, horse-trot, caravan-wagon, ship-cog, aerial-dragon, etc.)")
    parser.add_argument("--party", type=int, default=4, help="Party headcount (default: 4)")
    parser.add_argument("--mounts", type=int, default=0, help="Number of mounts/pack animals (default: 0)")
    parser.add_argument("--supplies", type=float, help="Days of rations/supplies carried")
    parser.add_argument("--html", help="Path to export standalone HTML report")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    dist_str = args.distance or args.dist
    if not dist_str:
        parser.print_help()
        sys.exit(0)

    try:
        dist_km = parse_distance_km(dist_str)
        journey = calculate_journey(
            distance_km=dist_km,
            terrain=args.terrain,
            mode=args.pace,
            party_size=args.party,
            mounts=args.mounts,
            initial_rations_days=args.supplies
        )

        if args.json:
            print(json.dumps(journey, indent=2))
        else:
            print(f"\n\033[1;33m=== Ars Arcanum Overland & Expedition Route Plan ===\033[0m")
            print(f"Total Distance: \033[1;36m{journey['distance_km']} km\033[0m | Terrain: \033[32m{journey['terrain']}\033[0m (Speed Factor: {journey['terrain_modifier']}x)")
            print(f"Travel Mode: \033[1m{journey['travel_mode']}\033[0m (Effective Pace: \033[32m{journey['effective_speed_km_day']} km/day\033[0m)")
            print(f"Estimated Duration: \033[1;35m{journey['total_days_formatted']}\033[0m\n")

            print("\033[1mLogistics & Supply Requirements:\033[0m")
            sup = journey["supplies_required"]
            print(f"  Party: {journey['party_size']} persons | Mounts: {journey['mounts']}")
            print(f"  Food Rations: \033[33m{sup['rations_food_kg']} kg\033[0m | Water: \033[36m{sup['water_liters']} L\033[0m")
            if journey["mounts"] > 0:
                print(f"  Mount Feed: \033[33m{sup['mount_feed_kg']} kg\033[0m | Mount Water: \033[36m{sup['mount_water_liters']} L\033[0m")
            print(f"  Total Cargo Load: \033[1m{sup['total_cargo_weight_kg']} kg\033[0m")
            print(f"  Supply Readiness: \033[32m{journey['supply_status']}\033[0m\n")

            if len(journey["itinerary"]) <= 15:
                print("\033[1mDaily March Schedule:\033[0m")
                for r in journey["itinerary"]:
                    print(f"  Day {r['day']:<2}: +{r['distance_today_km']:>5.1f} km  (Total: {r['distance_total_km']:>6.1f} km | Rem: {r['remaining_km']:>6.1f} km)")
                print()

        if args.html:
            out_p = Path(args.html)
            generate_journey_html_report(journey, out_p)
            print(f"Interactive HTML report written to: {out_p}")

    except Exception as e:
        print(f"\033[31mError: {e}\033[0m", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
