# Ars Arcanum Multi-Paradigm Story Structure & Beat Sheet Enforcer Guide (`docs/STRUCTURE.md`)

---

## 1. Overview & System Mission

The **Ars Arcanum Structure Engine** (`scripts/lib/structure.py`) is an offline narrative structural analyzer and pacing paradigm enforcer supporting 9 canonical story architectures.

Writers often struggle to assess whether major narrative turning points (Inciting Incident, Midpoint reversal, All Hope Is Lost crisis, Climax) occur at optimal pacing milestones across a manuscript. The Structure Engine maps actual chapter word counts against ideal structural percentage windows, computes structural drift penalties, and scores overall Structural Harmony ($0 \text{ to } 100\%$).

---

## 2. Supported Narrative Paradigms (9 Models)

The engine supports 9 Western and Eastern story models:

### 2.1 Classic Three-Act Structure (`three_act`)
1. **Opening Status Quo** ($5\%$): Ordinary world baseline.
2. **Inciting Incident** ($12\%$): Disturbance triggering the journey.
3. **Plot Point 1 / Break into Act II** ($25\%$): Irrevocable crossing into the special world.
4. **First Pinch Point** ($37\%$): Reminder of antagonistic force and stakes.
5. **Midpoint** ($50\%$): Reactive to proactive pivot; false victory/defeat.
6. **Second Pinch Point** ($62\%$): Antagonistic pressure mounts.
7. **All Hope Is Lost / Crisis** ($75\%$): Rock bottom; old beliefs fail.
8. **Climax** ($88\%$): Final confrontation resolving core conflict.
9. **Resolution / Denouement** ($96\%$): New equilibrium.

### 2.2 Save the Cat! 15 Beat Sheet (`save_the_cat`)
- Opening Image ($1\%$), Theme Stated ($5\%$), Set-Up ($8\%$), Catalyst ($12\%$), Debate ($18\%$), Break into Two ($23\%$), B Story ($25\%$), Fun and Games ($37\%$), Midpoint ($50\%$), Bad Guys Close In ($62\%$), All Hope Is Lost ($75\%$), Dark Night of the Soul ($78\%$), Break into Three ($82\%$), Finale ($90\%$), Final Image ($99\%$).

### 2.3 Hero's Journey / Monomyth (`heros_journey`)
- 1. Ordinary World ($5\%$), 2. Call to Adventure ($12\%$), 3. Refusal of the Call ($18\%$), 4. Meeting the Mentor ($22\%$), 5. Crossing the Threshold ($28\%$), 6. Tests, Allies & Enemies ($40\%$), 7. Approach Inmost Cave ($55\%$), 8. The Ordeal ($65\%$), 9. Reward ($75\%$), 10. The Road Back ($82\%$), 11. Resurrection ($90\%$), 12. Return with Elixir ($98\%$).

### 2.4 Dan Harmon Story Circle (`story_circle`)
- 1. You ($8\%$), 2. Need ($20\%$), 3. Go ($32\%$), 4. Search ($45\%$), 5. Find ($58\%$), 6. Take ($72\%$), 7. Return ($85\%$), 8. Change ($96\%$).

### 2.5 7-Point Story Structure (`seven_point`)
- 1. Hook ($5\%$), 2. Plot Turn 1 ($22\%$), 3. Pinch Point 1 ($37\%$), 4. Midpoint ($50\%$), 5. Pinch Point 2 ($65\%$), 6. Plot Turn 2 ($80\%$), 7. Resolution ($95\%$).

### 2.6 8-Sequence Method (`eight_sequence`)
- Sequence A through Sequence H ($12.5\%$ intervals) modeling cinematic screenwriting sequence structures.

### 2.7 The Fichtean Curve (`fichtean_curve`)
- Exposition ($8\%$), Crisis 1 ($22\%$), Rising Action ($38\%$), Crisis 2 ($52\%$), Crisis 3 ($70\%$), Climax ($88\%$), Falling Action ($96\%$).

### 2.8 Kishōtenketsu (`kishotenketsu`)
- 起 Ki / Introduction ($15\%$), 承 Shō / Development ($40\%$), 転 Ten / The Twist ($75\%$), 結 Ketsu / Reconciliation ($95\%$).

### 2.9 Freytag's Dramatic Pyramid (`freytags_pyramid`)
- 1. Exposition ($7\%$), 2. Inciting Force ($18\%$), 3. Rising Action ($35\%$), 4. Climax / Turning Point ($52\%$), 5. Falling Action ($70\%$), 6. Final Suspense ($84\%$), 7. Catastrophe ($96\%$).

---

## 3. Structural Alignment & Harmony Scoring

For each beat, the engine checks:
$$\text{Drift} = |\text{Actual Percentage} - \text{Target Percentage}|$$
If the assigned chapter falls outside the allowable window $[\text{Window}_{\text{min}}, \text{Window}_{\text{max}}]$, a drift penalty is deducted from the Structural Harmony Score:
$$\text{Harmony Score} = \max\left(0.0, \min\left(100.0, 100.0 - \overline{\text{Penalty}} \times 2.5\right)\right)$$

---

## 4. Command-Line Interface (CLI)

```bash
# Evaluate manuscript against Three-Act structure
arcanum structure [MANUSCRIPT]

# Evaluate against Save the Cat! 15 beats
arcanum structure [MANUSCRIPT] --paradigm save_the_cat

# Evaluate against Kishōtenketsu and export HTML report
arcanum structure [MANUSCRIPT] --paradigm kishotenketsu --html structure_report.html

# Output JSON data
arcanum structure [MANUSCRIPT] --json
```

---

## 5. Security & Offline Guarantee

The generated HTML report features visual progress bars for each beat and adheres to strict offline security headers:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
```
