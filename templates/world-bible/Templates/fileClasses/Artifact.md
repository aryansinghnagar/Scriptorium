---
fileClass: Artifact
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - artifact
  artifact_type:
    type: Select
    options:
      values:
        - Weapon
        - Relic
        - Grimoire
        - Neural Device
        - Talisman
  rarity:
    type: Select
    options:
      values:
        - Unique
        - Legendary
        - Rare
        - Relic
  creator:
    type: File
    path: Characters
  current_bearer:
    type: File
    path: Characters
  current_location:
    type: File
    path: Locations
  attunement_required:
    type: Boolean
---
# Artifact FileClass Schema
Defines structured frontmatter fields and controlled input validation for magical artifacts, relics, and legendary gear via Metadata Menu.
