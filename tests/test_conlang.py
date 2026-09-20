#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Conlang Phonotactics & Sound-Change Applier (scripts/lib/conlang.py).
Covers phonotactic word/name generation, cluster filtering, historical sound shift rules,
and lexicon management.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.conlang import (
    load_conlang_profile,
    generate_words,
    compile_sound_rule,
    mutate_text,
)


class TestConlangEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.lang_dir = self.world_dir / "Languages"
        self.lang_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_conlang_profile(self):
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

    def test_generate_words_phonotactics(self):
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

    def test_sound_change_intervocalic_voicing(self):
        # p > b between vowels (V_V)
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k", "b", "d", "g", "s", "m", "n", "l", "r"]
        rules = ["p > b / V_V"]
        res = mutate_text("apata", rules, vowels, consonants)
        self.assertEqual(res, "abata")

        # Initial p should remain p
        res2 = mutate_text("pata", rules, vowels, consonants)
        self.assertEqual(res2, "pata")

    def test_sound_change_palatalization(self):
        # k > ch before e or i (_[e,i])
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k", "ch", "b", "d", "s", "m", "n", "l", "r"]
        rules = ["k > ch / _[e,i]"]
        self.assertEqual(mutate_text("keli", rules, vowels, consonants), "cheli")
        self.assertEqual(mutate_text("kora", rules, vowels, consonants), "kora")

    def test_sound_change_word_initial(self):
        # s > h word initial (#_)
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["s", "h", "p", "t", "k", "l", "m", "n"]
        rules = ["s > h / #_"]
        self.assertEqual(mutate_text("solas", rules, vowels, consonants), "holas")

    def test_sound_change_word_final_deletion(self):
        # e > 0 word final (_#)
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["s", "h", "p", "t", "k", "l", "m", "n"]
        rules = ["e > 0 / _#"]
        self.assertEqual(mutate_text("mate", rules, vowels, consonants), "mat")

    def test_sound_change_word_initial_with_following_vowel(self):
        # p > f word initial before vowel (#_V)
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "f", "t", "k", "s", "m", "n"]
        rules = ["p > f / #_V"]
        self.assertEqual(mutate_text("pater", rules, vowels, consonants), "fater")
        self.assertEqual(mutate_text("apater", rules, vowels, consonants), "apater")

    def test_sound_change_whole_word(self):
        # e > a in single-character word (#_#)
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k"]
        rules = ["e > a / #_#"]
        self.assertEqual(mutate_text("e", rules, vowels, consonants), "a")
        self.assertEqual(mutate_text("ee", rules, vowels, consonants), "ee")

    def test_sound_change_consonant_cluster_context(self):
        # p > f after consonant before end of word (C_#)
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "f", "s", "t", "k"]
        rules = ["p > f / C_#"]
        self.assertEqual(mutate_text("kasp", rules, vowels, consonants), "kasf")
        self.assertEqual(mutate_text("kap", rules, vowels, consonants), "kap")


if __name__ == "__main__":
    unittest.main()
