---
fileClass: Faction
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - faction
  faction_type:
    type: Select
    options:
      values:
        - Empire / Realm
        - Guild / Order
        - Religious Cult / Sect
        - Rebel / Resistance
        - Corporation / Syndicate
  leader:
    type: File
    path: Characters
  headquarters:
    type: File
    path: Locations
  influence_level:
    type: Select
    options:
      values:
        - Dominant
        - Regional
        - Local
        - Underground
---
# Faction FileClass Schema
Defines structured frontmatter fields and controlled input validation for factions via Metadata Menu.
