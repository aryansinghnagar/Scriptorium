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
        - Kingdom / Duchy
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
  military_strength:
    type: Number
  allies:
    type: List
  rivals:
    type: List
  vassals:
    type: List
  treaties:
    type: List
---
# Faction FileClass Schema
Defines structured frontmatter fields, diplomatic allegiances, and military strength validation for factions via Metadata Menu.
