#!/usr/bin/env python3
"""
Corpus unit tests for Series Continuity character mortality and trait extraction (tests/test_series_continuity_corpus.py).
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LIB_DIR = REPO_ROOT / "scripts" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from series_continuity import extract_book_entities, DEATH_PATTERNS


class TestSeriesContinuityCorpus(unittest.TestCase):

    def test_death_patterns_positive_matches(self):
        phrases = [
            ("Aeloria died in the snowy pass.", "Aeloria"),
            ("Lord Kaelen was slain by the shadow beast.", "Kaelen"),
            ("Archmage Theron perished amidst the flames.", "Theron"),
            ("The brave soldier succumbed to poison.", "Soldier"),
            ("Sir Ronald fell in battle at the bridge.", "Ronald"),
            ("The traitor was executed at dawn.", "Traitor"),
            ("Old Gregor breathed their last as dusk fell.", "Gregor"),
            ("Lady Morwen was killed in the throne room.", "Morwen"),
            ("King Alden was murdered in his sleep.", "Alden"),
            ("High Chancellor Kenneth met their end in exile.", "Kenneth"),
            ("The elder passed away peacefully.", "Elder"),
            ("General Robert drew their last breath.", "Robert"),
            ("The scout lost their life in the canyon.", "Scout"),
            ("Emperor Valerius was assassinated by guards.", "Valerius"),
            ("Prince Jason was struck down outside the gates.", "Jason"),
            ("Countess Diana lay lifeless on the altar.", "Diana"),
            ("The prisoner succumbed to wounds.", "Prisoner"),
            ("The mourners gathered for the death of Lysander.", "Lysander"),
            ("The city wept at the murder of Cassian.", "Cassian"),
            ("All witnessed Bran's death with heavy hearts.", "Bran"),
            ("The kingdom celebrated the execution of Malakor.", "Malakor"),
        ]

        for text, expected_name in phrases:
            matched = False
            for p in DEATH_PATTERNS:
                m = p.search(text)
                if m and expected_name.lower() in m.group(1).lower():
                    matched = True
                    break
            self.assertTrue(matched, f"Failed to detect death in: '{text}' (expected '{expected_name}')")

    def test_extract_book_entities_with_frontmatter_mortality(self):
        with tempfile.TemporaryDirectory() as td:
            book_dir = Path(td) / "Book-01"
            draft_dir = book_dir / "Draft-01"
            draft_dir.mkdir(parents=True)

            ch1 = draft_dir / "01_Chapter.md"
            ch1.write_text(
                "---\nname: Aeloria\nis_deceased: true\ndeath_date: 1240-08-14\n---\n"
                "Aeloria had violet eyes and golden hair. She fought bravely.\n"
                "Lord Kaelen was slain in the courtyard.\n",
                encoding="utf-8",
            )

            entities = extract_book_entities(book_dir)
            self.assertIn("Aeloria", entities["deaths"])
            self.assertIn("Kaelen", entities["deaths"])
            self.assertIn("violet", entities["traits"]["Aeloria"]["eyes"])
            self.assertIn("golden", entities["traits"]["Aeloria"]["hair"])


if __name__ == "__main__":
    unittest.main()
