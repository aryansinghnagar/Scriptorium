---
fileClass: TimelineEvent
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - timeline_event
  era:
    type: Input
  year:
    type: Number
  start_year:
    type: Number
  end_year:
    type: Number
  key_participants:
    type: List
  primary_location:
    type: File
    path: Locations
---
# TimelineEvent FileClass Schema
Defines structured frontmatter fields and chronological validation for timeline events via Metadata Menu and Calendarium.
