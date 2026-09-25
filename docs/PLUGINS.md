# Ars Arcanum Speculative Fiction & Craft Plugin Guide (`docs/PLUGINS.md`)

## 1. Overview & Architectural Principles

Ars Arcanum features a modular, zero-dependency **Plugin Architecture** designed specifically for speculative fiction worldbuilders, novelists, and editorial craft guilds.

### Core Tenets
1. **Zero-Pip Guarantee**: Core plugin execution uses Python standard library primitives and optional local packages without requiring pip dependencies.
2. **Fail-Safe Crash Isolation**: Plugins execute in sandboxed try-catch wrappers. A faulty or crashing community plugin will never crash core authoring workflows, corrupt manuscripts, or disrupt typesetting.
3. **Multi-Tier Search Paths**:
   - **Workspace**: `<project_root>/configs/plugins/` (Version-controlled with project)
   - **User**: `~/.config/ars-arcanum/plugins/` (Available to all user projects)
   - **System**: `/usr/share/ars-arcanum/plugins/` (Global system-wide installations)

---

## 2. Plugin Anatomy & Manifest Specification

Every plugin lives in a directory containing at minimum:
1. `plugin.json` — Declarative metadata and hook declarations.
2. `plugin.py` — Python entry point implementing hook functions.
3. `README.md` — Author documentation.

### `plugin.json` Schema

```json
{
  "id": "magic_system_audit",
  "name": "Hard Magic System & Arcane Consistency Auditor",
  "version": "1.0.0",
  "author": "Brandonian Arcane Society",
  "description": "Enforces Sandersonian hard magic principles, cost-limitation balance, and conservation invariants.",
  "category": "speculative",
  "entry_point": "plugin.py",
  "hooks": [
    "validate_entity",
    "validate_manuscript"
  ],
  "min_arcanum_version": "1.6.0"
}
```

### Manifest Fields
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `string` | Unique identifier (alphanumeric and underscores). |
| `name` | `string` | Human-readable plugin name. |
| `version` | `string` | Semantic versioning (e.g. `1.0.0`). |
| `author` | `string` | Author name or organization. |
| `description`| `string` | Summary of plugin purpose. |
| `category` | `string` | One of: `craft`, `lore`, `continuity`, `format`, `audit`, `speculative`, `general`. |
| `entry_point`| `string` | Python file containing hooks (default: `plugin.py`). |
| `hooks` | `array` | List of declared hook lifecycle names. |

---

## 3. Hook Lifecycle Reference

### `hook_validate_entity(entity, context)`
Called during world bible validation on character, location, faction, and magic lore files.

```python
def hook_validate_entity(entity: dict, context: dict) -> list[dict]:
    """
    Args:
        entity: {'name': str, 'path': str, 'content': str}
        context: {'target_path': str, 'known_names': list[str]}
    Returns:
        List of diagnostic dicts:
        [{
            'severity': 'info' | 'warning' | 'error',
            'message': 'Description of issue',
            'target': 'Entity Name',
            'details': {}
        }]
    """
```

### `hook_validate_manuscript(manuscript, context)`
Called during manuscript audits on drafts, chapters, and scenes.

```python
def hook_validate_manuscript(manuscript: dict, context: dict) -> list[dict]:
    """
    Args:
        manuscript: {'title': str, 'chapters': [{'title': str, 'content': str, 'word_count': int}]}
        context: {'target_path': str}
    """
```

### `hook_custom_metric(text, context)`
Calculates domain-specific numerical metrics for analytics dashboards.

```python
def hook_custom_metric(text: str, context: dict) -> dict:
    """
    Returns:
        {'metric_key': numeric_value, ...}
    """
```

---

## 4. Built-in Reference Plugins

Ars Arcanum includes three reference plugins located in `configs/plugins/`:

1. **`speculative_naming`**:
   - Analyzes fantasy/sci-fi proper nouns for dangerous phonetic collisions ($\ge 85\%$ Levenshtein similarity) and dense consonant clusters ($5+$ consecutive consonants) that impede pronunciation.
2. **`magic_system_audit`**:
   - Enforces Sanderson's Second Law of Magic: audits arcane lore entries to verify explicit declarations of **Cost**, **Limitation**, or **Drawback**.
3. **`pacing_heat_map`**:
   - Analyzes dialogue-to-exposition density and multi-sensory grounding (Sight, Sound, Smell, Taste, Touch) across manuscript chapters.

---

## 5. CLI Commands

```bash
# List all discovered plugins
arcanum plugin list
arcanum plugin list --json

# View plugin details
arcanum plugin info magic_system_audit

# Run a plugin against a World Vault or Manuscript
arcanum plugin run magic_system_audit ~/Universes/Cosmos/Eldoria-Prime
arcanum audit plugin pacing_heat_map ~/Manuscripts/Novel-Draft

# Scaffold a new plugin template
arcanum plugin create my_custom_plugin --name "My Custom Plugin" --author "Author Name"

# Enable or disable plugins
arcanum plugin disable magic_system_audit
arcanum plugin enable magic_system_audit
```
