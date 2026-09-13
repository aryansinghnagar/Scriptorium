// ==============================================================================
// Scriptorium Novel Typesetting Template (Typst)
// Designed for book-quality fiction & trade paperback publishing.
// ==============================================================================

#let book-layout(
  title: "Book Title",
  subtitle: "",
  author: "Author Name",
  dedication: "",
  epigraph: "",
  epigraph-author: "",
  year: "2026",
  isbn: "978-0-000000-00-0",
  publisher: "Scriptorium Press",
  paper-size: "us-trade", // Options: "us-trade" (6x9in), "trade" (5.5x8.5in), "pocket" (5x8in)
  body-font: "Linux Libertine",
  heading-font: "Linux Libertine",
  font-size: 10.5pt,
  line-spacing: 0.65em,
  body
) = {

  // Map paper size to physical dimensions
  let (width, height) = if paper-size == "trade" {
    (5.5in, 8.5in)
  } else if paper-size == "pocket" {
    (5in, 8in)
  } else {
    (6in, 9in) // Default: US Trade 6x9 in
  }

  // Set document metadata
  set document(title: title, author: author)

  // Configure base text styles
  set text(
    font: (body-font, "Libertinus Serif", "EB Garamond", "DejaVu Serif"),
    size: font-size,
    lang: "en"
  )

  // Standard fiction paragraph formatting: justified, first line indent, no gap between paragraphs
  set par(
    justify: true,
    first-line-indent: 1.3em,
    leading: line-spacing
  )

  // Page setup with alternating margins (gutter binding)
  // Front matter renders with no header/footer (M4); body headers are
  // enabled after front matter via a second `set page` below.
  set page(
    width: width,
    height: height,
    margin: (
      inside: 0.85in,
      outside: 0.70in,
      top: 0.75in,
      bottom: 0.75in
    ),
    header: none,
    footer: none,
  )

  // ---------------------------------------------------------------------------
  // FRONT MATTER
  // ---------------------------------------------------------------------------

  // 1. Half-Title Page
  align(center + horizon)[
    #text(font: heading-font, size: 18pt, weight: "bold", tracking: 0.1em, upper(title))
  ]
  pagebreak()

  // 2. Blank Verso
  pagebreak()

  // 3. Full Title Page
  align(center + horizon)[
    #v(-2in)
    #text(font: heading-font, size: 24pt, weight: "bold", tracking: 0.12em, upper(title))
    
    #if subtitle != "" [
      #v(0.5em)
      #text(font: heading-font, size: 13pt, style: "italic", subtitle)
    ]
    
    #v(3em)
    #text(font: body-font, size: 14pt, style: "italic", author)
    
    #v(4em)
    #text(font: body-font, size: 10pt, tracking: 0.15em, upper(publisher))
  ]
  pagebreak()

  // 4. Copyright Page
  align(bottom + left)[
    #set text(size: 8pt)
    #set par(first-line-indent: 0pt, leading: 0.5em)
    #upper(title)
    
    Copyright © #year by #author. All rights reserved.
    
    Published by #publisher.
    
    No part of this publication may be reproduced, stored in a retrieval system, or transmitted in any form or by any means without the prior written permission of the author, except for brief quotations embodied in critical articles or reviews.
    
    This is a work of fiction. Names, characters, places, and incidents are either the products of the author's imagination or are used fictitiously.
    
    ISBN: #isbn
    
    Printed in the United States of America / First Edition
  ]
  pagebreak()

  // 5. Dedication / Epigraph (if provided)
  if dedication != "" or epigraph != "" [
    align(center + horizon)[
      #if dedication != "" [
        #text(size: 11pt, style: "italic", dedication)
        #v(3em)
      ]
      #if epigraph != "" [
        #block(width: 80%)[
          #align(left)[
            #text(size: 10.5pt, style: "italic", [“#epigraph”])
            #v(0.5em)
            #align(right)[#text(size: 9.5pt, [— #epigraph-author])]
          ]
        ]
      ]
    ]
    pagebreak()
  ]

  // ---------------------------------------------------------------------------
  // MAIN BODY (Manuscript Content)
  // ---------------------------------------------------------------------------

  // Enable running headers/footers from here on. Front matter above stays
  // clean regardless of dedication/epigraph length (M4). Uses `context` +
  // page counter (M2: `locate` is deprecated in Typst >= 0.12).
  set page(
    header: context {
      let page-num = counter(page).get().first()
      // Alternating headers: Left (Verso) shows Author, Right (Recto) shows Title
      if calc.even(page-num) {
        align(center)[#text(size: 8.5pt, style: "italic", tracking: 0.05em, upper(author))]
      } else {
        align(center)[#text(size: 8.5pt, style: "italic", tracking: 0.05em, upper(title))]
      }
    },
    footer: context {
      let page-num = counter(page).get().first()
      align(center)[#text(size: 9pt, str(page-num))]
    },
  )
  // Restart body pagination at 1 so front matter does not shift numbering
  counter(page).update(1)

  // Heading 1 (# Chapter) configuration
  // NOTE: `pagebreak` MUST NOT be wrapped in a `block()` container — Typst
  // 0.12+ rejects pagebreaks inside containers ("pagebreaks are not allowed
  // inside of containers"), which killed every level-1 chapter compile.
  show heading.where(level: 1): it => {
    pagebreak(to: "odd")
    v(1.5in)
    align(center)[
      #text(font: heading-font, size: 16pt, weight: "bold", tracking: 0.1em, upper(it.body))
    ]
    v(1.2in)
  }

  // Heading 2 (Sub-sections)
  show heading.where(level: 2): it => block(width: 100%)[
    #v(1.5em)
    #align(center)[
      #text(font: heading-font, size: 12pt, weight: "bold", it.body)
    ]
    #v(1em)
  ]

  // Map horizontal lines / dividers to ornamental scene breaks
  show line: it => {
    scene-break()
  }

  body
}

// Scene break ornament helper
#let scene-break() = {
  v(1.2em)
  align(center)[#text(size: 10pt, tracking: 0.4em, "✦ ✦ ✦")]
  v(1.2em)
}

// Flush-left first paragraph helper
#let unindented(body) = {
  set par(first-line-indent: 0pt)
  body
}

// Backward-compat alias: older export_book.sh imported `chapter-title`.
// New code should use `= Chapter Title` (level-1 heading) instead.
#let chapter-title(title) = heading(level: 1, title)
