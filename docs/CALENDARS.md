# Ars Arcanum — Custom Planetary Calendars & Multi-Moon Engine Guide
> **Engine**: `scripts/lib/calendar.py` | **CLI**: `arcanum calendar`

---

## 1. Overview & Purpose

The **Custom Planetary Calendars & Multi-Moon Phase Engine** calculates arbitrary planetary cycles, non-Gregorian year structures, multi-moon synodic cycles, illumination percentages, and astronomical conjunctions (syzygies and solar/lunar eclipses). It integrates directly with World Bible `Cosmology/*.md` lore dossiers.

### Core Capabilities
- **Non-Standard Planetary Calendar Arithmetic**: Supports arbitrary days per year, hours per day, custom month divisions, and custom weekday names.
- **Multi-Moon Synodic Phase Tracker**: Real-time phase tracking (New Moon, Waxing Crescent, First Quarter, Waxing Gibbous, Full Moon, Waning Gibbous, Third Quarter, Waning Crescent) and Unicode glyphs (`🌑`, `🌓`, `🌕`, `🌗`) for any number of orbiting moons.
- **Celestial Syzygy & Eclipse Detection**: Automatically flags dates when multiple moons align in simultaneous Full Moon or New Moon phases (Dark Convergence).
- **Visualizers & Export**: Formatted ANSI monthly calendar grid with moon annotations, standalone offline HTML dashboard, and structured JSON output.

---

## 2. Cosmology Calendar Schema (`World/Cosmology/Planetary_System.md`)

```markdown
---
name: "Solaris Prime"
type: cosmology
days_per_year: 400
hours_per_day: 28
months:
  - "Dawn"
  - "Sunhigh"
  - "Dusk"
  - "Nightfall"
weekdays:
  - "Moonday"
  - "Fireday"
  - "Waterday"
  - "Earthday"
  - "Starday"
moons:
  - name: "Selene"
    period: 25.0
    offset: 0.0
  - name: "Umbra"
    period: 12.5
    offset: 2.0
---
# Solaris Prime
The primary world of the Hegemony, orbiting a twin-star barycenter.
```

---

## 3. Moon Phase & Illumination Formula

For absolute day $D$, orbital period $P$, and phase offset $\delta$:
$$\text{Cycle Position} = \frac{(D + \delta) \pmod P}{P} \in [0, 1)$$
$$\text{Illumination Fraction} = \frac{1 - \cos(2\pi \cdot \text{Cycle Position})}{2} \in [0, 1]$$

| Cycle Position | Phase Name | Unicode Glyph | Illumination |
| :--- | :--- | :--- | :--- |
| $[0.00, 0.06) \cup [0.94, 1.00)$ | **New Moon** | `🌑` | $\approx 0\%$ |
| $[0.06, 0.19)$ | **Waxing Crescent** | `🌒` | $0\% \to 50\%$ |
| $[0.19, 0.31)$ | **First Quarter** | `🌓` | $\approx 50\%$ |
| $[0.31, 0.44)$ | **Waxing Gibbous** | `🌔` | $50\% \to 100\%$ |
| $[0.44, 0.56)$ | **Full Moon** | `🌕` | $\approx 100\%$ |
| $[0.56, 0.69)$ | **Waning Gibbous** | `🌖` | $100\% \to 50\%$ |
| $[0.69, 0.81)$ | **Third Quarter** | `🌗` | $\approx 50\%$ |
| $[0.81, 0.94)$ | **Waning Crescent** | `🌘` | $50\% \to 0\%$ |

---

## 4. CLI Command Reference

### Inspect World Calendar & Moon Phases
```bash
# View current month calendar and moon phase breakdown
arcanum calendar World/ -y 1 -m 1 -d 1

# Advance date by +45 days and inspect new celestial state
arcanum calendar World/ -y 1 -m 1 -d 1 --advance 45

# Output machine-readable JSON
arcanum calendar World/ --json
```

### Export Standalone Interactive HTML Calendar
```bash
# Generate visual monthly calendar report
arcanum calendar World/ -y 1 -m 2 --html exports/month_2_calendar.html
```

---

## 5. Architectural Invariants

- **Zero External Dependencies**: Pure Python standard library (`math`, `html`, `json`, `re`, `pathlib`).
- **Atomic Writing**: HTML reports written via `atomic_write()` from `lib._bootstrap.py`.
- **Strict Content Security Policy**:
  ```html
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  ```
