#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Conlang Phonotactics & Sound-Change Applier (scripts/lib/conlang.py).
Covers phonotactic word/name generation, cluster filtering, historical sound shift rules,
lexicon extraction, and CSV exporting.
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.conlang import (
    generate_words,
    load_conlang_profile,
    mutate_text,
)


class TestConlangEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.lang_dir = self.world_dir / "Languages"
        self.lang_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_load_conlang_profile(self) -> None:
        """load_conlang_profile parses phoneme inventories, clusters, and markdown lexicon table."""
        (self.lang_dir / "Solar_Tongue.md").write_text("""---
name: "Solar Tongue"
type: language
consonants: [k, l, r, m, n, s, v, th]
vowels: [a, e, i, o, u]
syllable_structures: ["CV", "CVC"]
forbidden_clusters: ["thk", "sr"]
stress_rule: "penultimate"
sound_changes:
  - "k > ch / _[e,i]"
---
# Solar Tongue
## 3. Essential Lexicon & Vocabulary
| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |
| :--- | :--- | :--- | :--- | :--- |
| *Aethel* | Noun | /ˈaɪ.θəl/ | Sun King | Royal honorific |
| *Vaelor* | Noun | /ˈvaɪ.lɔːr/ | Shield | Military vow |
""", encoding="utf-8")

        profile = load_conlang_profile(self.world_dir, "Solar")
        self.assertEqual(profile["name"], "Solar Tongue")
        self.assertIn("k", profile["consonants"])
        self.assertIn("CV", profile["syllable_structures"])
        self.assertIn("thk", profile["forbidden_clusters"])
        self.assertEqual(len(profile["lexicon"]), 2)
        self.assertEqual(profile["lexicon"][0]["word"], "Aethel")

    def test_load_conlang_profile_not_found_raises(self) -> None:
        """load_conlang_profile raises FileNotFoundError when language note does not exist."""
        with self.assertRaises(FileNotFoundError):
            load_conlang_profile(self.world_dir, "NonexistentLang")

    def test_generate_words_phonotactics(self) -> None:
        """generate_words produces legal syllables and excludes banned phonetic clusters."""
        profile = {
            "name": "Valen",
            "consonants": ["p", "t", "k", "s", "m", "n", "l", "r"],
            "vowels": ["a", "e", "i", "o", "u"],
            "syllable_structures": ["CV", "CVC"],
            "forbidden_clusters": ["sr", "kp"],
        }
        words = generate_words(profile, count=15, num_syllables=2, word_type="name", seed=42)
        self.assertEqual(len(words), 15)
        for w in words:
            self.assertTrue(w.istitle())
            self.assertNotIn("sr", w.lower())
            self.assertNotIn("kp", w.lower())

    def test_generate_words_deterministic_seed(self) -> None:
        """Providing an identical integer seed reproduces the exact word list."""
        profile = {
            "name": "Valen",
            "consonants": ["p", "t", "k", "s", "m", "n", "l", "r"],
            "vowels": ["a", "e", "i", "o", "u"],
            "syllable_structures": ["CV", "CVC"],
            "forbidden_clusters": [],
        }
        words1 = generate_words(profile, count=10, seed=1234)
        words2 = generate_words(profile, count=10, seed=1234)
        self.assertEqual(words1, words2)

    def test_sound_change_intervocalic_voicing(self) -> None:
        """p > b between vowels (V_V) mutates apata to abata while preserving word-initial p."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k", "b", "d", "g", "s", "m", "n", "l", "r"]
        rules = ["p > b / V_V"]
        res = mutate_text("apata", rules, vowels, consonants)
        self.assertEqual(res, "abata")

        res2 = mutate_text("pata", rules, vowels, consonants)
        self.assertEqual(res2, "pata")

    def test_sound_change_palatalization(self) -> None:
        """k > ch before front vowels e/i (_[e,i]) mutates keli to cheli but keeps kora."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k", "ch", "b", "d", "s", "m", "n", "l", "r"]
        rules = ["k > ch / _[e,i]"]
        self.assertEqual(mutate_text("keli", rules, vowels, consonants), "cheli")
        self.assertEqual(mutate_text("kora", rules, vowels, consonants), "kora")

    def test_sound_change_word_initial(self) -> None:
        """s > h word-initially (#_) mutates solas to holas."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["s", "h", "p", "t", "k", "l", "m", "n"]
        rules = ["s > h / #_"]
        self.assertEqual(mutate_text("solas", rules, vowels, consonants), "holas")

    def test_sound_change_word_final_deletion(self) -> None:
        """e > 0 word-finally (_#) mutates mate to mat."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["s", "h", "p", "t", "k", "l", "m", "n"]
        rules = ["e > 0 / _#"]
        self.assertEqual(mutate_text("mate", rules, vowels, consonants), "mat")

    def test_sound_change_word_initial_with_following_vowel(self) -> None:
        """p > f word-initially before vowel (#_V) mutates pater to fater."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "f", "t", "k", "s", "m", "n"]
        rules = ["p > f / #_V"]
        self.assertEqual(mutate_text("pater", rules, vowels, consonants), "fater")
        self.assertEqual(mutate_text("apater", rules, vowels, consonants), "apater")

    def test_sound_change_whole_word(self) -> None:
        """e > a in single-character word (#_#) shifts isolated word."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k"]
        rules = ["e > a / #_#"]
        self.assertEqual(mutate_text("e", rules, vowels, consonants), "a")
        self.assertEqual(mutate_text("ee", rules, vowels, consonants), "ee")

    def test_sound_change_consonant_cluster_context(self) -> None:
        """p > f after consonant before end of word (C_#) shifts kasp to kasf."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "f", "s", "t", "k"]
        rules = ["p > f / C_#"]
        self.assertEqual(mutate_text("kasp", rules, vowels, consonants), "kasf")
        self.assertEqual(mutate_text("kap", rules, vowels, consonants), "kap")

    def test_lexicon_csv_export_and_filtering(self) -> None:
        """Lexicon entries can be filtered by query and written to standard CSV format."""
        (self.lang_dir / "Ancient.md").write_text("""---
name: "Ancient"
---
# Ancient
## 3. Essential Lexicon & Vocabulary
| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |
| :--- | :--- | :--- | :--- | :--- |
| *Sol* | Noun | /soʊl/ | Sun | Deity |
| *Luna* | Noun | /ˈluː.nə/ | Moon | Magic |
""", encoding="utf-8")

        profile = load_conlang_profile(self.world_dir, "Ancient")
        lex = profile["lexicon"]
        filtered = [e for e in lex if "sun" in e["translation"].lower()]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["word"], "Sol")

        csv_file = Path(self.temp_dir.name) / "lex.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["word", "pos", "ipa", "translation", "connotation"])
            writer.writeheader()
            writer.writerows(lex)

        self.assertTrue(csv_file.is_file())
        with open(csv_file, encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            self.assertEqual(len(reader), 2)
            self.assertEqual(reader[0]["word"], "Sol")

    def test_family_tree(self) -> None:
        (self.lang_dir / "Proto.md").write_text("""---
name: "Proto-Elven"
---
""", encoding="utf-8")
        (self.lang_dir / "High_Elven.md").write_text("""---
name: "High Elven"
proto_language: "Proto-Elven"
---
""", encoding="utf-8")

        from scripts.lib.conlang import load_all_conlangs
        langs = load_all_conlangs(self.world_dir)
        self.assertIn("Proto-Elven", langs)
        self.assertIn("High Elven", langs)
        self.assertEqual(langs["High Elven"]["proto_language"], "Proto-Elven")


if __name__ == "__main__":
    unittest.main()
