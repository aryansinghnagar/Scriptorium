# Sovereign Multi-Perspective Editorial Council Engine
`scripts/lib/editorial_council.py` / `arcanum council`

---

## 1. Overview & Craft Philosophy

Novelists and screenwriters often rely on diverse editorial perspectives throughout different revision passes — from microscopic line rhythm to high-level developmental pacing and worldbuilding consistency.

**Ars Arcanum's Autonomous Editorial Council** convenes four specialized sovereign personas to conduct a multi-dimensional manuscript workshop with **zero external dependencies and 100% offline privacy**:

1. ✒️ **The Master Line Editor (*Lady Cassian*)**: Focuses on sentence length variance (standard deviation $\sigma$), sensory immersion across 6 dimensions, dialogue attribution discipline, and stylistic echoes.
2. 📜 **The Lore & Worldbuilding Inquisitor (*Archon Vaelor*)**: Audits magic tier limits, faction alignment consistency, geographical journey distances, and calendar alignments against active World Bibles.
3. 🏛️ **The Developmental Story Architect (*Grand Architect Soren*)**: Evaluates narrative progression against 9 canonical structural paradigms, dialogue-to-narrative density, and dramatic tension curves.
4. ⏳ **The Continuity & Canon Overseer (*Chronicler Mirella*)**: Verifies character trait stability, POV focus, chronological causality, and detects bilocation paradoxes.

---

## 2. CLI Usage

```bash
# Convene full Editorial Council with active World Bible
arcanum council ~/Manuscripts/The-Silver-Chronicles/Book-01/Draft-01 -w ~/Universes/Eldoria/Eldoria-Prime

# Generate standalone interactive HTML5 dashboard
arcanum council ~/Manuscripts/MyNovel --html dist/council_review.html

# Save structured Markdown report
arcanum council ~/Manuscripts/MyNovel -r dist/council_report.md

# Filter specific personas (e.g. Line & Lore only)
arcanum council ~/Manuscripts/MyNovel --personas line,lore

# Machine-readable JSON output for CI/CD pipelines
arcanum council ~/Manuscripts/MyNovel --json
```

---

## 3. Consensus Scoring & Dissent Thresholds

The Council aggregates individual persona evaluations into a unified **Consensus Readiness Score** ($0-100\%$):

| Score Range | Verdict | Meaning |
| :--- | :--- | :--- |
| **88 – 100%** | `Consensus Approved: Publication Ready` | Exceptional prose, lore, and structural alignment. |
| **75 – 87%** | `Consensus Approved: Minor Editorial Polish Needed` | Strong overall execution with targeted craft polish. |
| **60 – 74%** | `Conditional Consensus: Targeted Revisions Required` | Specific deficits detected (e.g. dialogue density, pacing). |
| **< 60%** | `Developmental Hold: Core Realignment Needed` | Major structural or canon inconsistencies detected. |

### Dissent Mechanism
If any persona's evaluation deviates by $\ge 12$ points from the consensus average, the report issues a formal **Chamber Dissent** or **Commendation**, preventing homogeneous groupthink and highlighting specific craft blind spots.

---

## 4. Master Revision Action Checklist

Every review automatically generates a consolidated, prioritized checklist of actionable directives:
- **High Priority**: Immediate structural or lore fixes required before drafting further.
- **Medium Priority**: Stylistic refinements, sensory grounding, or dialogue tag polishing.
- **Low Priority**: Minor cosmetic touches and cross-reference enrichments.
