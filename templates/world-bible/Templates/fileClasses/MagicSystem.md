---
fileClass: MagicSystem
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - magic_tech_system
  classification:
    type: Select
    options:
      values:
        - Hard Magic
        - Soft Magic
        - Cybernetic Tech
        - Bio-Engineering
        - Alchemy / Potioncraft
        - Ritual / Divine
  source_of_power:
    type: Input
  prevalence:
    type: Select
    options:
      values:
        - Ubiquitous
        - Common
        - Restricted to Guilds
        - Rare
        - Forbidden
        - Lost
  danger_cost:
    type: Select
    options:
      values:
        - Low
        - Moderate
        - High
        - Lethal / Soul Toll
---
# MagicSystem FileClass Schema
Defines structured frontmatter fields and rules validation for magic and technological systems via Metadata Menu.
