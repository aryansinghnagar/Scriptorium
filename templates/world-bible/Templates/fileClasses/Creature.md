---
fileClass: Creature
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - creature
  classification:
    type: Select
    options:
      values:
        - Beast
        - Monster
        - Flora
        - Construct
        - Apex Predator
  threat_level:
    type: Select
    options:
      values:
        - Harmless
        - Low
        - Moderate
        - Lethal
        - Calamity
  habitat:
    type: File
    path: Locations
  diet:
    type: Select
    options:
      values:
        - Herbivore
        - Carnivore
        - Omnivore
        - Essence Feeder
  domesticated:
    type: Select
    options:
      values:
        - Wild
        - Trainable
        - Domesticated
        - Untamable
---
# Creature FileClass Schema
Defines structured frontmatter fields and ecological validation for bestiary, fauna, and flora notes via Metadata Menu.
