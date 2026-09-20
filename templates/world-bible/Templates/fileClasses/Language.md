---
fileClass: Language
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - language
  language_family:
    type: Input
  spoken_by:
    type: Input
  status:
    type: Select
    options:
      values:
        - Living
        - Liturgical
        - Extinct
        - Secret Dialect
        - Trade Pidgin
  writing_system:
    type: Select
    options:
      values:
        - Runic Glyphs
        - Syllabary
        - Cuneiform
        - Latin Script
        - Logographic
        - Oral Only
  consonants:
    type: List
  vowels:
    type: List
  syllable_structures:
    type: List
  forbidden_clusters:
    type: List
  stress_rule:
    type: Input
  sound_changes:
    type: List
---
# Language FileClass Schema
Defines structured frontmatter fields and linguistic validation for languages, dialects, and conlangs via Metadata Menu.
