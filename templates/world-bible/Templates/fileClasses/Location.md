---
fileClass: Location
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - location
  region:
    type: Input
  dominant_faction:
    type: File
    path: Factions
  scale:
    type: Select
    options:
      values:
        - Continent
        - Realm / Nation
        - Province / Region
        - Settlement / City
        - Landmark / Site
        - Building / Interior
---
# Location FileClass Schema
Defines structured frontmatter fields and controlled input validation for locations via Metadata Menu.
