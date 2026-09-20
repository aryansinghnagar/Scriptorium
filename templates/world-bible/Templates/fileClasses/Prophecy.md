---
fileClass: Prophecy
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - prophecy
  source:
    type: File
    path: Characters
  date_uttered:
    type: Input
  target_entity:
    type: Input
  status:
    type: Select
    options:
      values:
        - unfulfilled
        - partially_fulfilled
        - fulfilled
        - subverted
        - broken
  clauses:
    type: List
  resolution_criteria:
    type: Input
---
# Prophecy FileClass Schema
Defines prophetic lifecycle tracking, oracle sources, and resolution verification fields for Metadata Menu.
