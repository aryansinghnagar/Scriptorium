---
fileClass: Cosmology
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - cosmology
  concept_type:
    type: Select
    options:
      values:
        - Deity
        - Cosmic Force
        - Plane of Existence
        - Constellation
        - Mythos
  domain:
    type: Input
  plane_of_origin:
    type: Input
  worship_status:
    type: Select
    options:
      values:
        - Primary Pantheon
        - Forgotten Cult
        - Forbidden
        - Universally Acknowledged
  associated_faction:
    type: File
    path: Factions
  days_per_year:
    type: Number
  hours_per_day:
    type: Number
  months:
    type: List
  weekdays:
    type: List
  moons:
    type: List
---
# Cosmology FileClass Schema
Defines structured frontmatter fields and controlled input validation for deities, cosmic planes, and mythos concepts via Metadata Menu.
