---
fileClass: Character
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - character
  role:
    type: Select
    options:
      values:
        - Protagonist
        - Antagonist
        - Supporting
        - Minor
  status:
    type: Select
    options:
      values:
        - Alive
        - Deceased
        - Missing
        - Unknown
  faction:
    type: File
    path: Factions
  house:
    type: Input
  title:
    type: Input
  current_location:
    type: File
    path: Locations
  origin:
    type: File
    path: Locations
  born:
    type: Input
  died:
    type: Input
  parents:
    type: List
  spouses:
    type: List
  children:
    type: List
  succession_order:
    type: Number
  magic_tier:
    type: Number
  catalyst:
    type: Input
---
# Character FileClass Schema
Defines structured frontmatter fields and controlled input validation for characters via Metadata Menu.
