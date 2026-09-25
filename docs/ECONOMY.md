# Ars Arcanum In-World Macroeconomics & Anachronism Matrix Guide (`docs/ECONOMY.md`)

---

## 1. Overview & System Mission

The **Ars Arcanum Economy Engine** (`scripts/lib/economy.py`) is a zero-dependency, 100% offline macroeconomic validator, Purchasing Power Parity (PPP) exchange rate calculator, trade route freight margin modeler, and technological era anachronism auditor.

In fantasy, science fiction, and historical fiction worldbuilding, economic coherence and technological consistency are critical to immersion. Writers often struggle with:
1. **Price Inflation/Deflation Anomalies**: A loaf of bread costing 2 silver coins in Chapter 1, but 50 gold coins in Chapter 10 without narrative justification.
2. **Currency Drift**: Referencing currencies not defined in the world bible or failing to maintain consistent denomination exchange ratios.
3. **Trade Arbitrage Viability**: Caravans or interstellar cargo freighters operating on impossible margins given travel distances and transit costs.
4. **Technological Anachronisms**: Accidentally referencing anachronistic materials or inventions (e.g. "plastic", "radar", "dynamite") in medieval or bronze age settings.

---

## 2. World Lore Schema: Economy Profiles

Economy profiles are defined in `World/Economies/*.md` (or `00-World-Bible/Economies/*.md`) using standard YAML frontmatter:

```markdown
---
name: "Solar Standard Economy"
base_currency: "Solar Crown"
tech_era: "medieval"
associated_faction: "Solar Empire"
currencies:
  - "Solar Crown: 1.0"
  - "Silver Sovereign: 0.1"
  - "Copper Bit: 0.01"
commodity_basket:
  - "loaf_of_bread: 2"
  - "pint_of_ale: 1"
  - "iron_dagger: 15"
  - "riding_horse: 500"
  - "wagon: 200"
---

# Solar Standard Economy

The official monetary system of the Solar Empire, backed by the Imperial Mint.
```

### Key Frontmatter Attributes:
- `name`: Human-readable name of the economic system.
- `base_currency`: The reference coin or credit unit.
- `tech_era`: Baseline technological epoch (`stone_age`, `bronze_age`, `iron_age`, `medieval`, `renaissance`, `industrial`, `victorian`, `modern_20th`, `information_age`, `interstellar`).
- `currencies`: List of denomination strings with relative exchange values against the base currency.
- `commodity_basket`: Standardized price list for reference goods used in Purchasing Power Parity calculations.

---

## 3. Purchasing Power Parity (PPP) Exchange Rates

When multiple economies exist in a universe, the economy engine calculates the relative Purchasing Power Parity (PPP) matrix based on common goods in their commodity baskets:

$$\text{PPP}_{A \to B} = \frac{1}{N} \sum_{i=1}^{N} \frac{\text{Price}_A(\text{Good}_i)}{\text{Price}_B(\text{Good}_i)}$$

This allows authors to convert prices accurately between realms without arbitrary guesswork.

---

## 4. Manuscript Annotations & Audit Diagnostics

Authors can annotate explicit transactions using the `@price:` directive in scene markdown files, or let the engine scan natural prose:

```markdown
# Chapter 4: The Whispering Bazaar

The merchant unfolded the bolt of dyed silk.
@price: 25 Solar Crown for silk_bolt

"That will be fifty copper bits for the lantern," the stall keeper muttered.
```

### Diagnostic Codes

| Code | Severity | Description | Remediation |
| :--- | :--- | :--- | :--- |
| **`ECO-101`** | `WARNING` | **Severe Price Inflation / Deflation Anomaly**: Price deviates by more than 20x from baseline basket. | Adjust the transaction price or explain the local scarcity / inflation in narrative. |
| **`ECO-102`** | `WARNING` | **Unregistered Currency**: Manuscript references a currency not defined in world lore. | Add the currency to an existing `World/Economies/*.md` profile or fix typo. |
| **`ECO-103`** | `WARNING` | **Denomination Arithmetic Error**: Coin count contradicts conversion ratios. | Check denomination conversions in the scene dialogue. |
| **`ECO-201`** | `WARNING` | **Technological Anachronism**: Prose mentions an out-of-era invention or material. | Replace the modern term with an era-appropriate equivalent or adjust lore tech baseline. |

---

## 5. Trade Freight Margin Modeling

The engine models trade logistics for caravans, merchant ships, and interstellar freighters using `calc_trade_margin`:

- **Parameters**:
  - `buy_price_per_ton`: Sourcing cost at origin.
  - `sell_price_per_ton`: Market price at destination.
  - `cargo_tons`: Total payload weight.
  - `distance_km_or_ly`: Transit distance.
  - `transit_cost_per_ton_unit`: Freight cost per ton per km (or light-year).
  - `tariff_pct`: Import/export customs duties.
- **Outputs**:
  - Gross Revenue, Freight Cost, Tariffs, Net Profit, Profit Margin (%), Return on Investment (ROI %), and Breakeven Price.

---

## 6. Command-Line Interface (CLI)

```bash
# Audit manuscript prices and currencies
arcanum economy check [MANUSCRIPT] [-w WORLD] [--html] [--json]

# Calculate Purchasing Power Parity exchange rates across world economies
arcanum economy ppp [-w WORLD] [--json]

# Model trade route profitability
arcanum economy trade --buy 100 --sell 300 --cargo 50 --dist 200 --cost 0.5 --tariff 0.05

# Scan for technological era anachronisms
arcanum audit tech [MANUSCRIPT] --era medieval [--html] [--json]
```

---

## 7. Security & Offline Guarantee

- **Zero External Dependencies**: Operates 100% within the Python standard library.
- **Strict Content Security Policy**: Generated HTML reports enforce offline sandbox isolation:
  ```html
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  ```
- **Atomic POSIX/Windows File I/O**: Report exports use `atomic_write()` to eliminate corruption risk.
