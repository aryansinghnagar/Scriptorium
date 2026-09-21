#!/usr/bin/env python3
"""
Ars Arcanum Query Letter & Submission Package Scaffolder
(scripts/init_query.py)
================================================================================
Zero-dependency, offline agent query & submission package generator.

Capabilities (PUB-106):
1. Complete Submission Package Scaffolding (Submissions/):
   - 01_Query_Letter.md: 1-page standard literary agent query letter (Hook,
     3-paragraph pitch, comps, word count/genre, bio).
   - 02_One_Page_Synopsis.md: Complete plot arc synopsis including ending.
   - 03_Extended_Synopsis.md: Comprehensive chapter-by-chapter outline.
   - 04_Pitch_Loglines.md: Elevator pitches, loglines, and short hooks.
   - 05_Agent_Tracker.csv & 05_Agent_Tracker.md: Submissions tracking matrix.
2. Template customization via CLI arguments or automatic manuscript metadata reading.

Zero external dependencies; 100% offline privacy.
"""

import sys
import json
import argparse
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.query")


def build_query_letter(title: str, author: str, genre: str, comps: str, words: int, protagonist: str = "[Protagonist Name]") -> str:
    return f"""# Literary Agent Query Letter: {title}

**Target Agent:** [Agent Name]  
**Agency:** [Agency Name]  
**Date:** [Date]  

Dear [Agent Name],

Because of your stated interest in [genre / theme / MSWL element], I am writing to seek representation for **{title.upper()}**, a {genre} novel complete at {words:,} words. Given your appreciation for {comps}, I believe this story will resonate with your list.

[**THE HOOK / INCITING INCIDENT**]  
{protagonist} only wanted [core starting goal]. But when [inciting incident occurs], everything they believed about [status quo] collapses.

[**THE ESCALATION & CONFLICT**]  
Forced into [new environment / alliance], {protagonist} discovers that [antagonistic force] is orchestrating [major catastrophic threat]. To survive, they must [key action or journey], navigating [internal struggle] while racing against [ticking clock].

[**THE CLIMACTIC CHOICE & STAKES**]  
When [midpoint catastrophe strikes], {protagonist} faces an impossible dilemma: [Choice A with tragic sacrifice] or [Choice B with devastating risk]. In the end, saving [what they love] might require sacrificing [core identity / belief].

**About the Author:**  
{author} is a writer and worldbuilder based in [Location]. [Include 1–2 sentences of writing credentials, relevant career experience, or publication history]. When not writing, {author} can be found [personal hobby / interest].

Thank you for your time and consideration. Per your submission guidelines, I have pasted [sample pages / synopsis] below.

Warm regards,

**{author}**  
[Email Address] | [Phone Number]  
[Author Website] | [Social Handle]  
"""


def build_one_page_synopsis(title: str, author: str, genre: str) -> str:
    return f"""# One-Page Narrative Synopsis: {title}
**Author:** {author} | **Genre:** {genre}

### Act I: Status Quo & The Catalyst
In [Setting], [Protagonist Name], a [flawed character role], struggles under [initial conflict]. When [Inciting Event occurs], [Protagonist] is thrust into [Main Conflict]. Despite initial reluctance, [Protagonist] makes the proactive decision to [Cross Threshold / Enter Act II].

### Act II-A: The Promise of the Premise & Rising Action
In the unfamiliar world of [Special World], [Protagonist] teams up with [Key Ally/Mentor]. Together, they face rising pressure from [Antagonist]. A series of trials reveals that [Core Mystery / Revelation].

### Act II-B: The Midpoint Shift & The Lowest Point
At the Midpoint, [Protagonist] achieves a [False Victory or Suffers Severe Ambush], realizing the true stakes. [Antagonist forces close in], culminating in [All Hope Is Lost Moment]: [Mentor dies / Secret betrayed / Plan shatters]. During the Dark Night of the Soul, [Protagonist] realizes the thematic truth they must embrace to win.

### Act III: Climax & Resolution
Synthesizing their internal growth with new tactics, [Protagonist] orchestrates a final confrontation at [Climactic Location]. In a climactic showdown, [Protagonist] defeats [Antagonist] by sacrificing [Old Flaw / Prized Object]. The story concludes with a transformed status quo where [Resolution State / New World Order].
"""


def build_pitch_loglines(title: str, genre: str) -> str:
    return f"""# Pitch Hooks & Loglines: {title}

### 1. The One-Sentence Elevator Logline (25 Words)
When [Inciting Incident happens], a [Flawed Protagonist Description] must [Take Action] before [Catastrophic Stakes Occur].

### 2. The 50-Word Short Pitch
In a world where [Unique Setting Element], [Protagonist] uncovers [Dangerous Secret]. Hunted by [Antagonist Faction], they must choose between [Personal Desire] and [Greater Good] before [Final Disaster].

### 3. Twitter / X 280-Character Pitch
[PROTAGONIST] thought [status quo], until [inciting disaster]. Now, to stop [villain], they must ally with their worst enemy and risk [ultimate sacrifice].

{title.upper()} is a {genre} perfect for fans of [COMP 1] and [COMP 2]. #PitMad #QueryPitch
"""


def build_agent_tracker_csv() -> str:
    return """Agent Name,Agency,Submission Date,Materials Sent,Status,Response Date,Notes/Feedback
Jane Doe,Starlight Literary Agency,2026-10-01,Query + 10 Pages,Submitted,,Requested via MSWL
John Smith,Apex Talent,2026-10-05,Query + 3 Chapters,Submitted,,Referred by author friend
"""


def build_agent_tracker_md() -> str:
    return """# Literary Agent Submission Tracker

| Agent Name | Agency | Date Sent | Materials Sent | Status | Response Date | Notes / Feedback |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Jane Doe | Starlight Literary | 2026-10-01 | Query + 10 Pages | Submitted | — | Looked for secondary world fantasy |
| John Smith | Apex Talent | 2026-10-05 | Query + 3 Chapters | Submitted | — | QueryTracker fast responder |
"""


def scaffold_submission_package(manuscript_path: Path, metadata: dict, force: bool = False) -> dict:
    """Creates complete query and submission package in manuscript directory."""
    sub_dir = manuscript_path / "Submissions"
    sub_dir.mkdir(parents=True, exist_ok=True)

    title = metadata.get("title", manuscript_path.name.replace("_", " "))
    author = metadata.get("author", "Author Name")
    genre = metadata.get("genre", "Speculative Fiction")
    comps = metadata.get("comps", "THE NAME OF THE WIND and DUNE")
    words = int(metadata.get("word_count", 95000))

    files_to_create = {
        "01_Query_Letter.md": build_query_letter(title, author, genre, comps, words),
        "02_One_Page_Synopsis.md": build_one_page_synopsis(title, author, genre),
        "03_Extended_Synopsis.md": f"# Extended Synopsis: {title}\n\n[Chapter-by-Chapter Summary Outline]\n",
        "04_Pitch_Loglines.md": build_pitch_loglines(title, genre),
        "05_Agent_Tracker.csv": build_agent_tracker_csv(),
        "05_Agent_Tracker.md": build_agent_tracker_md(),
    }

    created = []
    skipped = []

    for fname, content in files_to_create.items():
        fp = sub_dir / fname
        if fp.is_file() and not force:
            skipped.append(str(fp))
        else:
            fp.write_text(content, encoding="utf-8")
            created.append(str(fp))

    return {
        "target": str(manuscript_path),
        "submission_dir": str(sub_dir),
        "created_count": len(created),
        "skipped_count": len(skipped),
        "created": created,
        "skipped": skipped
    }


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Query Letter & Synopsis Scaffolder (PUB-106)")
    parser.add_argument("target", help="Manuscript directory path")
    parser.add_argument("--title", help="Novel title")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--genre", help="Novel genre")
    parser.add_argument("--comps", help="Comparative titles (e.g. 'BOOK A and BOOK B')")
    parser.add_argument("--words", type=int, help="Total word count")
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing query files")
    parser.add_argument("--json", action="store_true", help="Output JSON results")

    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    meta = {
        "title": target_path.name.replace("_", " "),
        "author": "Author Name",
        "genre": "Speculative Fiction",
        "comps": "THE WAY OF KINGS meets FOUNDATION",
        "word_count": 95000
    }

    # Manifest read
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
    if args.genre:
        meta["genre"] = args.genre
    if args.comps:
        meta["comps"] = args.comps
    if args.words:
        meta["word_count"] = args.words

    res = scaffold_submission_package(target_path, meta, force=args.force)

    if args.json:
        print(json.dumps(res, indent=2))
        return

    print(f"=== Query Package Scaffolder: {meta['title']} ===")
    print(f"Directory: {res['submission_dir']}")
    print(f"Created: {res['created_count']} files | Skipped (already exist): {res['skipped_count']} files")
    print("-" * 65)
    for c in res["created"]:
        print(f"  ✓ {Path(c).name}")
    for s in res["skipped"]:
        print(f"  · {Path(s).name} (already exists)")


if __name__ == "__main__":
    main()
