# Ars Arcanum (Scriptorium) — Domain Knowledge & Technical Specifications

## 1. Domain Ontologies & Taxonomy
Ars Arcanum aligns 11 entity types across Obsidian `fileClasses`, Markdown frontmatter, directory hierarchies, and diagnostic code families:

| Entity Type | Directory | fileClass | Description |
| :--- | :--- | :--- | :--- |
| **Universe** | `~/Universes/<U>` | — | Top-level narrative multiverse root with `universe.yaml`. |
| **World** | `~/Universes/<U>/<W>` | — | Sovereign Lore Vault / Obsidian Vault with `world.yaml`. |
| **Character** | `Characters/` | `Character` | Dramatis Personae, physical traits, psychology, voice. |
| **Location** | `Locations/` | `Location` | Geography, biomes, settlements, coordinates. |
| **Faction** | `Factions/` | `Faction` | Political alliances, military strength, doctrine. |
| **Economy** | `Economies/` | `Economy` | Currency denominations, trade goods, purchasing power. |
| **Magic/Tech** | `Magic-Technology/` | `Magic-Technology` | Power limits, resource costs, failure consequences. |
| **Bestiary** | `Bestiary/` | `Creature` | Trophic levels, diet, natural habitats, threats. |
| **Artifact** | `Artifacts/` | `Artifact` | Relics, provenance, attunement, historical impact. |
| **Cosmology** | `Cosmology/` | `Cosmology` | Pantheons, celestial mechanics, calendars. |
| **Prophecy** | `Cosmology/Prophecies/` | `Prophecy` | Oracles, fulfillment conditions, branching timelines. |
| **History** | `History/` | `Timeline-Event` | Chronological era markers, causality chains. |
| **Language** | `Languages/` | `Language` | Conlang phonology, grammar, lexicon, scripts. |

---

## 2. Scientific & Engineering Formulas
Golden-value test invariants validated in `tests/test_domain_golden_values.py`:
- **Kepler's Third Law**:
  $$T = 2\pi \sqrt{\frac{a^3}{G(M_1 + M_2)}}$$
- **Lanchester's Square Law (Aimed Fire)**:
  $$\frac{dA}{dt} = -\beta B(t), \quad \frac{dB}{dt} = -\alpha A(t)$$
- **Lorentz Relativistic Dilation**:
  $$\gamma = \frac{1}{\sqrt{1 - \frac{v^2}{c^2}}}$$
- **WCAG 2.1 Color Contrast Ratio**:
  $$L = 0.2126 R + 0.7152 G + 0.0722 B, \quad \text{Ratio} = \frac{L_{\text{lighter}} + 0.05}{L_{\text{darker}} + 0.05}$$

---

## 3. Toolchain Specifications
- **Typst Binary**: Version `0.14.2` (`x86_64-unknown-linux-musl`), SHA-256 verified fail-closed on installation.
- **Obsidian Plugins**: 10 vendored plugins pinned by exact cryptographic hashes in `dependencies.lock`.
- **Pandoc**: Markdown $\leftrightarrow$ OpenXML (`.docx`) conversion with UTF-8 character encoding preservation.
- **Exit Code Contract**:
  - `0`: Success
  - `1`: Operational / Business Logic failure (missing world, validation error)
  - `2`: Environment / Dependency failure (missing binary, tool not in PATH)
  - `3`: User Argument / CLI Syntax error
