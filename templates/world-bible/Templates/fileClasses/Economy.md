---
fileClass: Economy
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - economy
  associated_faction:
    type: File
    path: Factions
  tech_era:
    type: Select
    options:
      values:
        - stone_age
        - bronze_age
        - iron_age
        - medieval
        - renaissance
        - industrial
        - victorian
        - modern_20th
        - information_age
        - interstellar
  base_currency:
    type: Input
  currencies:
    type: List
  commodity_basket:
    type: List
---
# Economy FileClass Schema
Defines macroeconomic currencies, tech baseline era, denominations, and PPP commodity baskets for Metadata Menu.
