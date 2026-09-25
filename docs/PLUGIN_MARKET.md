# Speculative Fiction Plugin Marketplace & Curated Catalog
> **Ars Arcanum Module**: `scripts/lib/plugin_market.py` | **CLI**: `arcanum market` (alias: `plugin-market`)

---

## 1. Overview & Architectural Principles

The **Ars Arcanum Speculative Plugin Marketplace** provides a curated, zero-dependency, 100% offline ecosystem of community-crafted narrative validators, continuity audits, and speculative craft engines.

### Key Capabilities
1. **Curated Speculative Catalog**:
   - Out-of-the-box access to specialized plugins:
     - `mythic_pantheon`: Divine domain conflict detector and deity lineage validator.
     - `linguistic_drift`: Historical sound-shift mutation and conlang phonology checker.
     - `trope_inversion`: Speculative trope subversion and cliché fatigue diagnostic.
     - `hard_sf_chronometry`: Relativistic time dilation and Lorentz factor validator.
     - `grimdark_entropy`: Hope-to-despair ratio, mortality cadence, and grimdark tonal consistency.
2. **Offline Integrity & AST Verification**:
   - `arcanum market verify` statically inspects catalog schemas, manifests, and Python abstract syntax trees prior to writing files to disk.
3. **Sandbox & Workspace Isolation**:
   - Atomically installs plugins into workspace `configs/plugins/` or user `~/.config/ars-arcanum/plugins/`.
   - Failing plugins are sandboxed by `PluginManager` and can never crash the core application or corrupt manuscript data.

---

## 2. Marketplace CLI Reference

### 2.1 Discovering Available Plugins
```bash
# List all curated plugins in the marketplace
arcanum market list

# Filter plugins by speculative category (craft, lore, speculative, continuity, audit)
arcanum market list -c lore

# Search marketplace for keywords or tags
arcanum market search "relativity"
```

### 2.2 Inspecting Plugin Specifications
```bash
arcanum market info mythic_pantheon
```

### 2.3 Installing and Enabling Plugins
```bash
# Install plugin into local project workspace
arcanum market install mythic_pantheon

# Force overwrite of an existing plugin installation
arcanum market install mythic_pantheon --force

# Verify plugin was loaded into the engine registry
arcanum plugin list
```

### 2.4 Running Installed Plugins
```bash
# Run the newly installed mythic_pantheon validator on a World Lore Vault
arcanum plugin run mythic_pantheon ~/Universes/Cosmos/Worlds/Eldoria/
```

### 2.5 Uninstalling Plugins
```bash
arcanum market uninstall mythic_pantheon
```

---

## 3. Catalog Manifest Schema (`plugin_catalog.json`)

The marketplace uses declarative JSON catalog manifests located at `configs/plugin_catalog.json`:

```json
{
  "id": "mythic_pantheon",
  "name": "Mythic Pantheon & Divine Domain Validator",
  "version": "1.0.0",
  "author": "Ars Arcanum Craft Council",
  "category": "lore",
  "description": "Audits deity lineages, conflicting divine domains, and divine intervention paradoxes.",
  "min_arcanum_version": "1.6.0",
  "hooks": ["validate_entity", "custom_metric"],
  "tags": ["mythology", "deities", "pantheon"],
  "files": {
    "plugin.json": "...",
    "plugin.py": "..."
  }
}
```
