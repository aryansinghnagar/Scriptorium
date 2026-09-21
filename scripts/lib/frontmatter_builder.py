#!/usr/bin/env python3
"""
Ars Arcanum Modular Front & Back Matter Publishing Builder
(scripts/lib/frontmatter_builder.py)
================================================================================
Zero-dependency, offline modular publishing matter generator for authors.

Capabilities (PUB-103):
1. Front Matter Generation (00_Front_Matter/):
   - 01_Half_Title.md: Clean single-title leaf
   - 02_Title_Page.md: Full title, subtitle, author, and publisher imprint
   - 03_Copyright.md: Complete legal copyright, fictional disclaimer, edition notice,
     ISBN, cover design credit, and library cataloging placeholder
   - 04_Dedication.md: Standard italicized dedication layout
   - 05_Epigraph.md: Thematic opening quotation with attribution
2. Back Matter Generation (04_Back_Matter/):
   - 01_Acknowledgments.md: Author gratitude, beta readers & editorial team
   - 02_About_the_Author.md: Author biography, social links & website
   - 03_Also_By.md: Backlist catalog and series reading order
   - 04_Discussion_Questions.md: Book club reading group guide
   - 05_Reader_CTA.md: Newsletter signup and review call-to-action
3. Preset-driven and interactive CLI scaffolding.

Zero external dependencies; 100% offline privacy.
"""

import sys
import json
import datetime
import argparse
import logging
from pathlib import Path

try:
    from lib.fs_utils import atomic_write
except ImportError:
    try:
        from fs_utils import atomic_write
    except ImportError:
        def atomic_write(path, data, encoding="utf-8"):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, (bytes, bytearray)):
                p.write_bytes(data)
            else:
                p.write_text(data, encoding=encoding)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.frontmatter_builder")


def generate_frontmatter_modules(metadata: dict) -> dict[str, str]:
    """Generates standard front matter Markdown documents."""
    title = metadata.get("title", "Untitled Novel")
    subtitle = metadata.get("subtitle", "")
    author = metadata.get("author", "Author Name")
    publisher = metadata.get("publisher", "Independent Publishing Press")
    year = metadata.get("copyright_year", str(datetime.date.today().year))
    isbn = metadata.get("isbn", "978-0-000000-00-0")
    edition = metadata.get("edition", "First Edition")
    dedication_text = metadata.get("dedication", "For those who dream among the stars and build worlds in the quiet dark.")
    epigraph_text = metadata.get("epigraph", "“The universe is not required to be in harmony with human ambition.”")
    epigraph_attr = metadata.get("epigraph_author", "Carl Sagan")

    half_title = f"""# {title}
"""

    title_page = f"""# {title}

{'### ' + subtitle if subtitle else ''}

**{author}**

---

*{publisher}*
"""

    copyright_page = f"""# Copyright

Copyright © {year} by {author}
All rights reserved.

Published by {publisher}
{edition}

No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the publisher, except in the case of brief quotations embodied in critical reviews and certain other noncommercial uses permitted by copyright law.

This book is a work of fiction. Names, characters, places, and incidents either are products of the author’s imagination or are used fictitiously. Any resemblance to actual persons, living or dead, events, or locales is entirely coincidental.

Paperback ISBN: {isbn}
Cover Design by: Studio Arcanum

Printed in the United States of America
"""

    dedication_page = f"""# Dedication

*{dedication_text}*
"""

    epigraph_page = f"""# Epigraph

*{epigraph_text}*

— **{epigraph_attr}**
"""

    return {
        "01_Half_Title.md": half_title,
        "02_Title_Page.md": title_page,
        "03_Copyright.md": copyright_page,
        "04_Dedication.md": dedication_page,
        "05_Epigraph.md": epigraph_page,
    }


def generate_backmatter_modules(metadata: dict) -> dict[str, str]:
    """Generates standard back matter Markdown documents."""
    title = metadata.get("title", "Untitled Novel")
    author = metadata.get("author", "Author Name")
    newsletter_url = metadata.get("newsletter_url", "https://authorwebsite.com/newsletter")
    website_url = metadata.get("website_url", "https://authorwebsite.com")

    acknowledgments = f"""# Acknowledgments

Writing *{title}* has been a monumental journey that could not have been completed in isolation.

First and foremost, thank you to my family and loved ones for their enduring patience and encouragement through long drafting hours and quiet revisions.

Immense gratitude to my early alpha and beta readers, whose sharp critiques and discerning eyes shaped these chapters into their truest form.

Finally, to every reader who picks up this story and walks alongside these characters: thank you for keeping sovereign storytelling alive.
"""

    about_the_author = f"""# About the Author

**{author}** is a novelist and worldbuilder passionate about immersive speculative fiction and sovereign storytelling.

When not crafting secondary worlds and charting celestial orbits, {author} enjoys hiking, historical research, and tinkering with open-source writing tools.

Connect with the author online:
- Website: [{website_url}]({website_url})
- Newsletter: [{newsletter_url}]({newsletter_url})
"""

    also_by = f"""# Also by {author}

### The Core Universe Series
1. *Book I: The Awakening*
2. *Book II: The Broken Crown*
3. *Book III: The Celestial Gate*

### Standalone Novels
- *Wanderers of the Void*
- *Echoes in Iron*
"""

    discussion_questions = """# Discussion Questions for Book Clubs

1. How did the opening status quo establish the protagonist's core internal flaw?
2. What role did the secondary world setting play in shaping the moral choices of the characters?
3. At the narrative midpoint, how did the shift from reactive survival to proactive resistance change the group dynamics?
4. Which faction's ideological stance did you find most compelling, and why?
5. Did the resolution provide a satisfying emotional transformation for the central protagonist?
"""

    reader_cta = f"""# A Note from the Author

Thank you for reading *{title}*!

If you enjoyed this journey, please consider leaving a brief review on your favorite book platform. Reviews are the lifeblood of independent authors and help fellow readers discover new worlds.

### Join the Sovereign Reader Circle
Get exclusive bonus epilogues, high-resolution world maps, and advance reader copies of upcoming releases:

👉 **[{newsletter_url}]({newsletter_url})**
"""

    return {
        "01_Acknowledgments.md": acknowledgments,
        "02_About_the_Author.md": about_the_author,
        "03_Also_By.md": also_by,
        "04_Discussion_Questions.md": discussion_questions,
        "05_Reader_CTA.md": reader_cta,
    }


def scaffold_matter(manuscript_path: Path, metadata: dict, force: bool = False) -> dict:
    """Writes modular front matter and back matter into manuscript directories."""
    front_matter_dir = manuscript_path / "00_Front_Matter"
    back_matter_dir = manuscript_path / "04_Back_Matter"

    front_matter_dir.mkdir(parents=True, exist_ok=True)
    back_matter_dir.mkdir(parents=True, exist_ok=True)

    front_files = generate_frontmatter_modules(metadata)
    back_files = generate_backmatter_modules(metadata)

    created = []
    skipped = []

    for name, content in front_files.items():
        fp = front_matter_dir / name
        if fp.is_file() and not force:
            skipped.append(str(fp))
        else:
            atomic_write(fp, content)
            created.append(str(fp))

    for name, content in back_files.items():
        fp = back_matter_dir / name
        if fp.is_file() and not force:
            skipped.append(str(fp))
        else:
            atomic_write(fp, content)
            created.append(str(fp))

    return {
        "target": str(manuscript_path),
        "created_count": len(created),
        "skipped_count": len(skipped),
        "created": created,
        "skipped": skipped
    }


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Modular Front & Back Matter Builder (PUB-103)")
    subparsers = parser.add_subparsers(dest="command", help="Command mode")

    p_build = subparsers.add_parser("build", help="Scaffold front & back matter into manuscript")
    p_build.add_argument("target", help="Manuscript directory path")
    p_build.add_argument("--title", help="Novel title")
    p_build.add_argument("--author", help="Author name")
    p_build.add_argument("--isbn", help="ISBN-13 number")
    p_build.add_argument("--year", help="Copyright year")
    p_build.add_argument("--publisher", help="Publisher imprint")
    p_build.add_argument("-f", "--force", action="store_true", help="Overwrite existing matter files")
    p_build.add_argument("--json", action="store_true", help="Output JSON results")

    args = parser.parse_args()

    if not args.command or args.command != "build":
        parser.print_help()
        sys.exit(0)

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    meta = {
        "title": target_path.name.replace("_", " "),
        "author": "Author Name",
        "isbn": "978-0-000000-00-0",
        "copyright_year": str(datetime.date.today().year),
        "publisher": "Ars Arcanum Press"
    }

    # If manuscript.yaml exists, read it
    manifest_path = target_path / "manuscript.yaml"
    if manifest_path.is_file():
        for line in manifest_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip().strip('"\'')
                if v:
                    meta[k] = v

    # Explicit CLI arguments always override defaults / manifest
    if args.title:
        meta["title"] = args.title
    if args.author:
        meta["author"] = args.author
    if args.isbn:
        meta["isbn"] = args.isbn
    if args.year:
        meta["copyright_year"] = args.year
    if args.publisher:
        meta["publisher"] = args.publisher

    res = scaffold_matter(target_path, meta, force=args.force)

    if args.json:
        print(json.dumps(res, indent=2))
        return

    print(f"=== Modular Front & Back Matter Scaffolder: {target_path.name} ===")
    print(f"Created: {res['created_count']} files | Skipped (already exist): {res['skipped_count']} files")
    print("-" * 65)
    for c in res["created"]:
        print(f"  ✓ Created: {Path(c).relative_to(target_path)}")
    for s in res["skipped"]:
        print(f"  · Exists (use --force to overwrite): {Path(s).relative_to(target_path)}")


if __name__ == "__main__":
    main()
