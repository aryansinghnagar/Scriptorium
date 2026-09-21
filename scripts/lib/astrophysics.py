#!/usr/bin/env python3
"""
Ars Arcanum Astrophysics & Relativistic Spaceflight Engine (scripts/lib/astrophysics.py)
=======================================================================================
Zero-dependency, offline astrophysics and relativistic trajectory calculator for
science-fiction worldbuilders and authors.

Capabilities:
1. Relativistic Brachistochrone (1g constant acceleration midpoint turnover) Trajectories:
   - Ship proper time (tau) vs coordinate observer time (t)
   - Midpoint turnover peak velocity (v_max / fraction of c)
   - Peak Lorentz factor (gamma)
   - Effective delta-v and relativistic rocket propellant mass ratios
2. Relativistic Kinematics & Time Dilation:
   - Lorentz factor gamma = 1 / sqrt(1 - (v/c)^2)
   - Coordinate time vs proper time dilation
   - Gravitational time dilation (Schwarzschild metric)
3. Orbital Transfers & Keplerian Mechanics:
   - Vis-viva circular and escape orbital velocities
   - Hohmann transfer delta-v and half-orbit transfer durations
   - Synodic period between planetary orbits
4. Light-Speed Communication & Signal Latencies:
   - One-way and round-trip communication delays across astronomical baselines
   - Built-in solar system and interstellar distance presets
5. Planetary Surface Gravity & Circumstellar Habitable Zone (HZ):
   - Surface gravity in m/s^2 and Earth-g equivalents
   - Escape velocities
   - Kopparapu conservative/optimistic habitable zone boundaries based on stellar luminosity

Outputs:
- Terminal ANSI formatted summary tables
- Machine-readable JSON (--json)
- Standalone interactive HTML report (--html <file>)
"""

import sys
import os
import re
import math
import json
import argparse
import html
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

# --- Physical & Astronomical Constants (SI Units) ---
C = 299792458.0                          # Speed of light in vacuum (m/s)
C_SQ = C * C                             # c^2 (m^2/s^2)
G = 6.67430e-11                          # Gravitational constant (m^3 kg^-1 s^-2)
G0 = 9.80665                             # Standard Earth surface gravity (m/s^2, 1g)
AU = 149597870700.0                      # Astronomical Unit (meters)
LIGHT_YEAR = 9460730472580800.0          # 1 Light Year (meters)
PARSEC = 30856775814913700.0             # 1 Parsec (meters)
SOLAR_MASS = 1.98847e30                  # Solar Mass M_sun (kg)
EARTH_MASS = 5.9722e24                   # Earth Mass M_earth (kg)
EARTH_RADIUS = 6371000.0                 # Earth volumetric mean radius (meters)
SOLAR_LUMINOSITY = 3.828e26              # Solar Luminosity L_sun (Watts)
SOLAR_RADIUS = 6.957e8                   # Solar Radius R_sun (meters)
SECONDS_PER_DAY = 86400.0
SECONDS_PER_YEAR = 31557600.0            # Julian year (365.25 days)

# --- Standard Distance Presets (meters) ---
DISTANCE_PRESETS = {
    "earth-moon": 384400000.0,
    "earth-mars-min": 54600000000.0,
    "earth-mars-avg": 225000000000.0,
    "earth-mars-max": 401000000000.0,
    "earth-jupiter-min": 588000000000.0,
    "earth-jupiter-avg": 778500000000.0,
    "earth-jupiter-max": 968000000000.0,
    "earth-saturn": 1433000000000.0,
    "earth-neptune": 4500000000000.0,
    "earth-pluto": 5900000000000.0,
    "kuiper-belt-inner": 30.0 * AU,
    "oort-cloud-inner": 2000.0 * AU,
    "proxima-centauri": 4.2465 * LIGHT_YEAR,
    "alpha-centauri": 4.37 * LIGHT_YEAR,
    "sirius": 8.611 * LIGHT_YEAR,
    "vega": 25.04 * LIGHT_YEAR,
    "trappist-1": 39.46 * LIGHT_YEAR,
    "galactic-center": 26000.0 * LIGHT_YEAR,
    "andromeda": 2537000.0 * LIGHT_YEAR,
}

# --- Standard Body Presets ---
BODY_PRESETS = {
    "sun": {"mass": SOLAR_MASS, "radius": SOLAR_RADIUS, "name": "Sun"},
    "mercury": {"mass": 3.3011e23, "radius": 2439700.0, "semi_major_au": 0.3871, "name": "Mercury"},
    "venus": {"mass": 4.8675e24, "radius": 6051800.0, "semi_major_au": 0.7233, "name": "Venus"},
    "earth": {"mass": EARTH_MASS, "radius": EARTH_RADIUS, "semi_major_au": 1.0, "name": "Earth"},
    "moon": {"mass": 7.342e22, "radius": 1737400.0, "name": "Moon"},
    "mars": {"mass": 6.4171e23, "radius": 3389500.0, "semi_major_au": 1.5237, "name": "Mars"},
    "jupiter": {"mass": 1.8982e27, "radius": 69911000.0, "semi_major_au": 5.2044, "name": "Jupiter"},
    "saturn": {"mass": 5.6834e26, "radius": 58232000.0, "semi_major_au": 9.5826, "name": "Saturn"},
    "uranus": {"mass": 8.6810e25, "radius": 25362000.0, "semi_major_au": 19.2184, "name": "Uranus"},
    "neptune": {"mass": 1.02413e26, "radius": 24622000.0, "semi_major_au": 30.1104, "name": "Neptune"},
}


def parse_distance(val_str: str) -> float:
    """Parses human string representation of distance to meters."""
    s = val_str.strip().lower()
    if s in DISTANCE_PRESETS:
        return DISTANCE_PRESETS[s]
    
    # Check suffixes (longest / multi-word first)
    if s.endswith("million-km") or s.endswith("million km") or s.endswith("mkm") or s.endswith("million kilometers") or s.endswith("million kilometer"):
        num_str = re.split(r"(?:million[-\s]?km|mkm|million[-\s]?kilometer[s]?)", s)[0].strip()
        return float(num_str) * 1e9
    if s.endswith("billion-km") or s.endswith("billion km") or s.endswith("bkm") or s.endswith("billion kilometers") or s.endswith("billion kilometer"):
        num_str = re.split(r"(?:billion[-\s]?km|bkm|billion[-\s]?kilometer[s]?)", s)[0].strip()
        return float(num_str) * 1e12
    if s.endswith("kpc") or s.endswith("kiloparsec") or s.endswith("kiloparsecs"):
        num_str = re.split(r"(?:kpc|kiloparsec[s]?)", s)[0].strip()
        return float(num_str) * 1e3 * PARSEC
    if s.endswith("mpc") or s.endswith("megaparsec") or s.endswith("megaparsecs"):
        num_str = re.split(r"(?:mpc|megaparsec[s]?)", s)[0].strip()
        return float(num_str) * 1e6 * PARSEC
    if s.endswith("parsec") or s.endswith("parsecs") or s.endswith("pc"):
        num_str = re.split(r"(?:parsec[s]?|pc)", s)[0].strip()
        return float(num_str) * PARSEC
    if s.endswith("light-years") or s.endswith("light-year") or s.endswith("lightyear") or s.endswith("lightyears") or s.endswith("ly"):
        num_str = re.split(r"(?:light[-\s]?year[s]?|ly)", s)[0].strip()
        return float(num_str) * LIGHT_YEAR
    if s.endswith("astronomical unit") or s.endswith("astronomical units") or s.endswith("au"):
        num_str = re.split(r"(?:astronomical\s+unit[s]?|au)", s)[0].strip()
        return float(num_str) * AU
    if s.endswith("kilometer") or s.endswith("kilometers") or s.endswith("km"):
        num_str = re.split(r"(?:kilometer[s]?|km)", s)[0].strip()
        return float(num_str) * 1000.0
    if s.endswith("meter") or s.endswith("meters") or s.endswith("m"):
        num_str = re.split(r"(?:meter[s]?|m)", s)[0].strip()
        return float(num_str)

    return float(s)


def parse_acceleration(val_str: str) -> float:
    """Parses acceleration string to m/s^2."""
    s = val_str.strip().lower()
    if s.endswith("g"):
        num = float(s[:-1].strip() or "1")
        return num * G0
    if s.endswith("m/s^2") or s.endswith("m/s2"):
        num = float(s.split("m/s")[0].strip())
        return num
    return float(s)


def format_duration(seconds: float) -> str:
    """Formats seconds into human readable duration string (years, days, hours, mins, secs)."""
    if seconds < 0:
        return "0s"
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    if seconds < 3600:
        mins = seconds / 60.0
        return f"{mins:.2f} minutes ({int(seconds // 60)}m {int(seconds % 60)}s)"
    if seconds < SECONDS_PER_DAY:
        hours = seconds / 3600.0
        m = int((seconds % 3600) // 60)
        return f"{hours:.2f} hours ({int(hours)}h {m}m)"
    if seconds < SECONDS_PER_YEAR:
        days = seconds / SECONDS_PER_DAY
        h = int((seconds % SECONDS_PER_DAY) // 3600)
        return f"{days:.2f} days ({int(days)}d {h}h)"
    
    years = seconds / SECONDS_PER_YEAR
    rem_days = (seconds % SECONDS_PER_YEAR) / SECONDS_PER_DAY
    return f"{years:.3f} years ({int(years)}y {int(rem_days)}d)"


def format_distance(meters: float) -> str:
    """Formats meters into most intuitive astronomical unit."""
    if meters >= PARSEC * 1000.0:
        return f"{meters / (PARSEC * 1000.0):.2f} kpc ({meters / LIGHT_YEAR:.1f} ly)"
    if meters >= LIGHT_YEAR * 0.1:
        return f"{meters / LIGHT_YEAR:.3f} ly ({meters / PARSEC:.3f} pc)"
    if meters >= AU * 0.1:
        return f"{meters / AU:.3f} AU ({meters / 1e9:.2f} million km)"
    if meters >= 1e6:
        return f"{meters / 1000.0:,.0f} km ({meters / AU:.4f} AU)"
    return f"{meters:,.1f} m"


# ==============================================================================
# Core Calculation Engines
# ==============================================================================

def calc_brachistochrone(distance_m: float, acc_mps2: float = G0, exhaust_vel_mps: float = None) -> dict:
    """
    Calculates exact relativistic 1-turnover (accelerate to midpoint, decelerate to stop)
    continuous-thrust Brachistochrone spaceflight trajectory.
    """
    a = acc_mps2
    d = distance_m
    half_d = d / 2.0

    # Relativistic parameter alpha = a * d_half / c^2
    alpha = (a * half_d) / C_SQ
    gamma_max = 1.0 + alpha
    
    # Peak velocity at turnover midpoint
    if gamma_max > 1.0:
        beta_max = math.sqrt(1.0 - 1.0 / (gamma_max * gamma_max))
        v_max = beta_max * C
    else:
        beta_max = 0.0
        v_max = 0.0

    # Ship Proper Time (tau): tau = 2 * (c / a) * acosh(1 + a*d / (2*c^2))
    # acosh(x) = ln(x + sqrt(x^2 - 1))
    tau_sec = 2.0 * (C / a) * math.acosh(gamma_max)

    # Coordinate / Observer Time (t): t = 2 * (c / a) * sqrt((1 + a*d / (2*c^2))^2 - 1)
    t_sec = 2.0 * (C / a) * math.sqrt(gamma_max * gamma_max - 1.0)

    # Time lag between observer and crew
    time_dilation_lag_sec = t_sec - tau_sec

    # Newtonian (classical) non-relativistic comparison
    t_newton_sec = 2.0 * math.sqrt(d / a)
    v_newton_mps = math.sqrt(a * d)

    # Effective total delta-v: 2 * c * atanh(v_max / c) = a * tau
    effective_deltav = a * tau_sec

    # Propellant mass ratio if exhaust velocity is specified
    # Using relativistic rocket equation: m0/mf = exp(effective_deltav / ve)
    mass_ratio = None
    if exhaust_vel_mps and exhaust_vel_mps > 0:
        mass_ratio = math.exp(effective_deltav / exhaust_vel_mps)
    
    # Photon rocket ideal mass ratio: sqrt((1 + beta_max)/(1 - beta_max)) for each leg
    photon_mass_ratio = ((1.0 + beta_max) / (1.0 - beta_max)) if beta_max < 1.0 else float("inf")

    return {
        "distance_m": d,
        "distance_formatted": format_distance(d),
        "acceleration_mps2": a,
        "acceleration_g": a / G0,
        "proper_time_sec": tau_sec,
        "proper_time_formatted": format_duration(tau_sec),
        "coordinate_time_sec": t_sec,
        "coordinate_time_formatted": format_duration(t_sec),
        "time_dilation_lag_sec": time_dilation_lag_sec,
        "time_dilation_lag_formatted": format_duration(time_dilation_lag_sec),
        "peak_velocity_mps": v_max,
        "peak_velocity_c_fraction": beta_max,
        "peak_gamma": gamma_max,
        "effective_deltav_mps": effective_deltav,
        "effective_deltav_kms": effective_deltav / 1000.0,
        "newtonian_time_sec": t_newton_sec,
        "newtonian_time_formatted": format_duration(t_newton_sec),
        "newtonian_peak_velocity_mps": v_newton_mps,
        "exhaust_velocity_mps": exhaust_vel_mps,
        "propellant_mass_ratio": mass_ratio,
        "photon_mass_ratio": photon_mass_ratio,
    }


def calc_time_dilation(v_mps: float = None, beta: float = None, gamma: float = None,
                       grav_mass_kg: float = None, grav_radius_m: float = None) -> dict:
    """Calculates special and general relativistic time dilation."""
    res = {}
    if beta is not None:
        v_mps = beta * C
    elif v_mps is not None:
        beta = v_mps / C
    elif gamma is not None:
        if gamma < 1.0:
            raise ValueError("Lorentz factor gamma must be >= 1.0")
        beta = math.sqrt(1.0 - 1.0 / (gamma * gamma))
        v_mps = beta * C
    else:
        v_mps = 0.0
        beta = 0.0

    if beta >= 1.0:
        raise ValueError("Velocity cannot equal or exceed the speed of light c")

    kin_gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    tau_per_day = SECONDS_PER_DAY / kin_gamma
    lag_per_day = SECONDS_PER_DAY - tau_per_day

    res["kinematic"] = {
        "velocity_mps": v_mps,
        "velocity_kms": v_mps / 1000.0,
        "beta": beta,
        "gamma": kin_gamma,
        "crew_time_ratio": 1.0 / kin_gamma,
        "proper_seconds_per_observer_day": tau_per_day,
        "proper_per_observer_day_formatted": format_duration(tau_per_day),
        "lag_per_observer_day_formatted": format_duration(lag_per_day),
    }

    if grav_mass_kg and grav_radius_m:
        r_schwarzschild = (2.0 * G * grav_mass_kg) / C_SQ
        if grav_radius_m <= r_schwarzschild:
            grav_factor = 0.0
        else:
            grav_factor = math.sqrt(1.0 - r_schwarzschild / grav_radius_m)
        res["gravitational"] = {
            "mass_kg": grav_mass_kg,
            "radius_m": grav_radius_m,
            "schwarzschild_radius_m": r_schwarzschild,
            "gravitational_dilation_factor": grav_factor,
            "time_rate_vs_infinity": grav_factor,
        }

    return res


def calc_orbital_transfer(primary_body: str = "sun", r1_m: float = None, r2_m: float = None,
                          primary_mass_kg: float = None) -> dict:
    """Calculates Keplerian Hohmann orbital transfer delta-v and durations."""
    m_primary = primary_mass_kg
    body_name = primary_body.capitalize()
    if primary_body.lower() in BODY_PRESETS:
        preset = BODY_PRESETS[primary_body.lower()]
        m_primary = preset["mass"]
        body_name = preset["name"]
    elif not m_primary:
        m_primary = SOLAR_MASS
        body_name = "Sun (Standard)"

    mu = G * m_primary

    # Circular orbit velocities
    v1 = math.sqrt(mu / r1_m)
    v2 = math.sqrt(mu / r2_m)

    # Orbital periods
    t1_sec = 2.0 * math.pi * math.sqrt((r1_m ** 3) / mu)
    t2_sec = 2.0 * math.pi * math.sqrt((r2_m ** 3) / mu)

    # Transfer ellipse semi-major axis
    a_trans = (r1_m + r2_m) / 2.0
    transfer_time_sec = math.pi * math.sqrt((a_trans ** 3) / mu)

    # Delta-v burns
    v_trans_1 = math.sqrt(mu * (2.0 / r1_m - 1.0 / a_trans))
    v_trans_2 = math.sqrt(mu * (2.0 / r2_m - 1.0 / a_trans))

    dv1 = abs(v_trans_1 - v1)
    dv2 = abs(v2 - v_trans_2)
    dv_total = dv1 + dv2

    # Synodic period between orbits
    synodic_sec = None
    if abs(t1_sec - t2_sec) > 1e-3:
        synodic_sec = 1.0 / abs(1.0 / t1_sec - 1.0 / t2_sec)

    return {
        "primary_body": body_name,
        "primary_mass_kg": m_primary,
        "r1_m": r1_m,
        "r1_formatted": format_distance(r1_m),
        "r2_m": r2_m,
        "r2_formatted": format_distance(r2_m),
        "v1_mps": v1,
        "v1_kms": v1 / 1000.0,
        "v2_mps": v2,
        "v2_kms": v2 / 1000.0,
        "period_r1_formatted": format_duration(t1_sec),
        "period_r2_formatted": format_duration(t2_sec),
        "transfer_duration_sec": transfer_time_sec,
        "transfer_duration_formatted": format_duration(transfer_time_sec),
        "delta_v1_mps": dv1,
        "delta_v1_kms": dv1 / 1000.0,
        "delta_v2_mps": dv2,
        "delta_v2_kms": dv2 / 1000.0,
        "delta_v_total_mps": dv_total,
        "delta_v_total_kms": dv_total / 1000.0,
        "synodic_period_formatted": format_duration(synodic_sec) if synodic_sec else "N/A",
    }


def calc_comms_delay(distance_m: float) -> dict:
    """Calculates electromagnetic signal propagation latencies."""
    one_way_sec = distance_m / C
    rtt_sec = 2.0 * one_way_sec
    return {
        "distance_m": distance_m,
        "distance_formatted": format_distance(distance_m),
        "one_way_seconds": one_way_sec,
        "one_way_formatted": format_duration(one_way_sec),
        "round_trip_seconds": rtt_sec,
        "round_trip_formatted": format_duration(rtt_sec),
    }


def calc_habitability_gravity(mass_kg: float, radius_m: float, star_luminosity_watts: float = SOLAR_LUMINOSITY) -> dict:
    """Calculates planetary surface gravity, escape velocity, and stellar habitable zone."""
    g_surf = (G * mass_kg) / (radius_m * radius_m)
    g_ratio = g_surf / G0
    v_esc = math.sqrt((2.0 * G * mass_kg) / radius_m)

    l_rel = star_luminosity_watts / SOLAR_LUMINOSITY
    hz_inner_au = math.sqrt(l_rel) * 0.95
    hz_outer_au = math.sqrt(l_rel) * 1.37
    hz_optimistic_inner_au = math.sqrt(l_rel) * 0.75
    hz_optimistic_outer_au = math.sqrt(l_rel) * 1.77

    return {
        "mass_kg": mass_kg,
        "mass_earth_ratio": mass_kg / EARTH_MASS,
        "radius_m": radius_m,
        "radius_earth_ratio": radius_m / EARTH_RADIUS,
        "surface_gravity_mps2": g_surf,
        "surface_gravity_g": g_ratio,
        "escape_velocity_mps": v_esc,
        "escape_velocity_kms": v_esc / 1000.0,
        "stellar_luminosity_rel_sun": l_rel,
        "habitable_zone_conservative": {
            "inner_au": hz_inner_au,
            "outer_au": hz_outer_au,
            "inner_m": hz_inner_au * AU,
            "outer_m": hz_outer_au * AU,
        },
        "habitable_zone_optimistic": {
            "inner_au": hz_optimistic_inner_au,
            "outer_au": hz_optimistic_outer_au,
        }
    }


# ==============================================================================
# HTML Export Generator
# ==============================================================================

def generate_astrophysics_html_report(title: str, results: dict, output_file: Path):
    """Generates an interactive standalone HTML report."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Ars Arcanum Astrophysics Report</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --accent: #58a6ff;
    --success: #3fb950;
    --warning: #d29922;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  body {{
    background-color: var(--bg);
    color: var(--text);
    font-family: var(--font);
    line-height: 1.6;
    margin: 0;
    padding: 24px;
  }}
  .container {{
    max-width: 900px;
    margin: 0 auto;
  }}
  header {{
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px;
    margin-bottom: 24px;
  }}
  h1 {{ color: var(--accent); margin: 0 0 8px 0; }}
  .badge {{
    background: #1f6feb22;
    color: var(--accent);
    border: 1px solid var(--accent);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
  }}
  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }}
  h2 {{ margin-top: 0; color: #f0f6fc; font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
  }}
  th, td {{
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  th {{ color: #8b949e; font-weight: 600; width: 40%; }}
  td {{ color: #f0f6fc; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
  .val-highlight {{ color: var(--success); font-weight: bold; }}
  footer {{
    text-align: center;
    font-size: 12px;
    color: #8b949e;
    margin-top: 40px;
    border-top: 1px solid var(--border);
    padding-top: 16px;
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🌌 {html.escape(title)}</h1>
    <span class="badge">Ars Arcanum Relativistic & Astrophysics Engine</span>
  </header>
"""
    for section_title, data in results.items():
        html_content += f"""  <div class="card">\n    <h2>{html.escape(section_title)}</h2>\n    <table>\n"""
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    v_str = ", ".join(f"{sub_k}: {sub_v}" for sub_k, sub_v in v.items())
                else:
                    v_str = str(v)
                html_content += f"""      <tr><th>{html.escape(k.replace('_', ' ').title())}</th><td>{html.escape(v_str)}</td></tr>\n"""
        html_content += """    </table>\n  </div>\n"""

    html_content += f"""
  <footer>
    Generated by Ars Arcanum • 100% Offline Speculative Authoring Suite
  </footer>
</div>
</body>
</html>
"""
    atomic_write(output_file, html_content)


# ==============================================================================
# CLI Entrypoint & Formatting
# ==============================================================================

def print_table(title: str, rows: list):
    """Prints a styled terminal table."""
    print(f"\n\033[1;36m=== {title} ===\033[0m")
    max_k = max(len(k) for k, _ in rows) + 2
    for k, v in rows:
        print(f"  \033[1m{k:<{max_k}}\033[0m: \033[32m{v}\033[0m")
    print()


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Astrophysics & Relativistic Flight Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Astrophysics subcommands")

    # 1. Transit / Brachistochrone
    p_transit = subparsers.add_parser("transit", help="Calculate relativistic Brachistochrone trajectory")
    p_transit.add_argument("distance", help="Distance (e.g. 'alpha-centauri', '1.5 AU', '4.2 ly', '54 mkm')")
    p_transit.add_argument("-a", "--accel", default="1g", help="Constant acceleration (default: '1g', or '9.81 m/s^2')")
    p_transit.add_argument("--ve", default=None, help="Exhaust velocity in m/s for rocket propellant mass ratio calculation")
    p_transit.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_transit.add_argument("--html", help="Path to export interactive HTML report")

    # 2. Time Dilation
    p_td = subparsers.add_parser("time-dilation", help="Calculate relativistic velocity and gravitational time dilation")
    p_td.add_argument("-v", "--velocity", help="Velocity (e.g. '0.99c', '200000 km/s', '10000000 m/s')")
    p_td.add_argument("--beta", type=float, help="Velocity as fraction of light speed (0.0 to 0.99999)")
    p_td.add_argument("--gamma", type=float, help="Lorentz factor gamma (>= 1.0)")
    p_td.add_argument("--mass", type=float, help="Primary body mass (kg) for gravitational dilation")
    p_td.add_argument("--radius", type=float, help="Orbital/surface radius (meters) for gravitational dilation")
    p_td.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 3. Orbit / Hohmann Transfer
    p_orbit = subparsers.add_parser("orbit", help="Calculate Keplerian orbital mechanics and Hohmann transfers")
    p_orbit.add_argument("--primary", default="sun", help="Primary body ('sun', 'earth', 'jupiter', etc.)")
    p_orbit.add_argument("--r1", required=True, help="Initial orbit radius (e.g. '1.0 AU', '7000 km')")
    p_orbit.add_argument("--r2", required=True, help="Target orbit radius (e.g. '1.52 AU', '42164 km')")
    p_orbit.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 4. Comms Latency
    p_comms = subparsers.add_parser("comms", help="Calculate light-speed communication delays")
    p_comms.add_argument("distance", help="Baseline distance (e.g. 'earth-mars-avg', '5.2 AU', '4.3 ly')")
    p_comms.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 5. Habitability & Surface Gravity
    p_hab = subparsers.add_parser("habitability", help="Calculate planetary surface gravity & habitable zone boundaries")
    p_hab.add_argument("--mass", default="1.0", help="Planet mass in Earth masses (e.g. '1.0', or '5.97e24 kg')")
    p_hab.add_argument("--radius", default="1.0", help="Planet radius in Earth radii (e.g. '1.0', or '6371 km')")
    p_hab.add_argument("--star-lum", default="1.0", help="Host star luminosity relative to Sun (default: 1.0)")
    p_hab.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    try:
        if args.subcommand == "transit":
            d_m = parse_distance(args.distance)
            a_mps2 = parse_acceleration(args.accel)
            ve = float(args.ve) if args.ve else None
            res = calc_brachistochrone(d_m, a_mps2, ve)

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                table = [
                    ("Mission Distance", f"{res['distance_formatted']} ({res['distance_m']:,.0f} m)"),
                    ("Constant Acceleration", f"{res['acceleration_g']:.3f} g ({res['acceleration_mps2']:.2f} m/s²)"),
                    ("Ship Proper Time (Crew)", res["proper_time_formatted"]),
                    ("Coordinate Time (Observer)", res["coordinate_time_formatted"]),
                    ("Time Dilation Difference", res["time_dilation_lag_formatted"]),
                    ("Peak Velocity (Turnover)", f"{res['peak_velocity_c_fraction'] * 100:.3f}% c ({res['peak_velocity_mps']/1000:,.1f} km/s)"),
                    ("Peak Lorentz Factor (γ)", f"{res['peak_gamma']:.4f}"),
                    ("Effective Total Delta-V", f"{res['effective_deltav_kms']:,.1f} km/s"),
                    ("Classical Newtonian Time", res["newtonian_time_formatted"]),
                ]
                if res["propellant_mass_ratio"]:
                    table.append(("Required Fuel Mass Ratio (m0/mf)", f"{res['propellant_mass_ratio']:.2e}"))
                print_table("Relativistic Brachistochrone Trajectory", table)

            if args.html:
                out_p = Path(args.html)
                generate_astrophysics_html_report(f"Brachistochrone Flight ({args.distance})", {"Trajectory Metrics": res}, out_p)
                print(f"Interactive HTML report written to: {out_p}")

        elif args.subcommand == "time-dilation":
            beta_val = args.beta
            v_val = None
            if args.velocity:
                v_str = args.velocity.strip().lower()
                if v_str.endswith("c"):
                    beta_val = float(v_str[:-1])
                elif v_str.endswith("km/s"):
                    v_val = float(v_str[:-4]) * 1000.0
                elif v_str.endswith("m/s"):
                    v_val = float(v_str[:-3])
                else:
                    v_val = float(v_str)

            res = calc_time_dilation(
                v_mps=v_val,
                beta=beta_val,
                gamma=args.gamma,
                grav_mass_kg=args.mass,
                grav_radius_m=args.radius
            )

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                kin = res["kinematic"]
                table = [
                    ("Velocity", f"{kin['velocity_kms']:,.2f} km/s ({kin['beta']*100:.4f}% c)"),
                    ("Lorentz Factor (γ)", f"{kin['gamma']:.6f}"),
                    ("Ship Time per 1 Earth Day", kin["proper_per_observer_day_formatted"]),
                    ("Time Dilation Lag per Day", kin["lag_per_observer_day_formatted"]),
                ]
                if "gravitational" in res:
                    g_info = res["gravitational"]
                    table.extend([
                        ("Gravitational Dilation Factor", f"{g_info['gravitational_dilation_factor']:.6f}"),
                        ("Schwarzschild Radius", f"{g_info['schwarzschild_radius_m']:,.2f} m"),
                    ])
                print_table("Relativistic Time Dilation", table)

        elif args.subcommand == "orbit":
            r1_m = parse_distance(args.r1)
            r2_m = parse_distance(args.r2)
            res = calc_orbital_transfer(primary_body=args.primary, r1_m=r1_m, r2_m=r2_m)

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                table = [
                    ("Primary Celestial Body", res["primary_body"]),
                    ("Initial Orbit Radius (R1)", f"{res['r1_formatted']} (v={res['v1_kms']:.2f} km/s, T={res['period_r1_formatted']})"),
                    ("Target Orbit Radius (R2)", f"{res['r2_formatted']} (v={res['v2_kms']:.2f} km/s, T={res['period_r2_formatted']})"),
                    ("Transfer Transit Duration", res["transfer_duration_formatted"]),
                    ("Burn 1 Injection Δv", f"{res['delta_v1_kms']:.3f} km/s"),
                    ("Burn 2 Circularization Δv", f"{res['delta_v2_kms']:.3f} km/s"),
                    ("Total Transfer Budget Δv", f"{res['delta_v_total_kms']:.3f} km/s"),
                    ("Synodic Launch Window Period", res["synodic_period_formatted"]),
                ]
                print_table("Hohmann Orbital Transfer", table)

        elif args.subcommand == "comms":
            d_m = parse_distance(args.distance)
            res = calc_comms_delay(d_m)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                table = [
                    ("Baseline Distance", res["distance_formatted"]),
                    ("One-Way Signal Delay", res["one_way_formatted"]),
                    ("Round-Trip Ping Latency (RTT)", res["round_trip_formatted"]),
                ]
                print_table("Electromagnetic Communication Delay", table)

        elif args.subcommand == "habitability":
            # parse mass
            m_str = str(args.mass).strip().lower()
            if m_str.endswith("kg"):
                m_kg = float(m_str[:-2])
            else:
                m_kg = float(m_str) * EARTH_MASS

            # parse radius
            r_str = str(args.radius).strip().lower()
            if r_str.endswith("km"):
                r_m = float(r_str[:-2]) * 1000.0
            elif r_str.endswith("m"):
                r_m = float(r_str[:-1])
            else:
                r_m = float(r_str) * EARTH_RADIUS

            l_star = float(args.star_lum) * SOLAR_LUMINOSITY
            res = calc_habitability_gravity(m_kg, r_m, l_star)

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                hz = res["habitable_zone_conservative"]
                table = [
                    ("Surface Gravity", f"{res['surface_gravity_g']:.3f} g ({res['surface_gravity_mps2']:.2f} m/s²)"),
                    ("Escape Velocity", f"{res['escape_velocity_kms']:.2f} km/s"),
                    ("Planet Mass", f"{res['mass_earth_ratio']:.2f} M_Earth"),
                    ("Planet Radius", f"{res['radius_earth_ratio']:.2f} R_Earth"),
                    ("Conservative Habitable Zone", f"{hz['inner_au']:.2f} AU – {hz['outer_au']:.2f} AU"),
                ]
                print_table("Planetary Habitability & Gravity Analysis", table)

    except Exception as e:
        print(f"\033[31mError: {e}\033[0m", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
