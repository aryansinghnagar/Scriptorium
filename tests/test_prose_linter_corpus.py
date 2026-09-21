#!/usr/bin/env python3
"""
Labelled Fixture Corpus & Precision/Recall Benchmark for Prose Linters
(tests/test_prose_linter_corpus.py)
================================================================================
Validates precision and recall across labelled prose test corpora for:
- Dialogue mechanics: Said-bookisms, adverb-heavy tags, punctuation faults (PRO-101)
- Sliding-window word echoes (PRO-102)
- Readability rhythm and staccato cadences (PRO-105)
- Character voice profiles and voice bleed similarity (PRO-103)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.stylistics import (
    analyze_dialogue_mechanics,
    analyze_word_echoes,
    analyze_readability_rhythm,
)
from lib.voice import (
    extract_character_dialogue,
    compute_voice_profile,
    compute_voice_similarity,
)


class TestProseLinterCorpus(unittest.TestCase):

    # -------------------------------------------------------------------------
    # 1. Dialogue Mechanics: Said-Bookisms, Adverb Tags & Punctuation
    # -------------------------------------------------------------------------
    def test_said_bookisms_corpus_detection(self):
        """
        Corpus containing explicit positive examples of melodramatic said-bookisms
        and clean negative examples using standard said/asked/whispered.
        """
        test_text = """
        "We must hurry," gasped Elena as the roof began to cave in.
        "I know the way," said Marcus calmly.
        "You always think you know," pontificated the old archivist.
        "Quiet down," whispered Lyra.
        "Never!" ejaculated the haughty guard.
        "Follow me," Marcus replied.
        "Are you certain?" asked the novice.
        "Completely," opined the professor.
        """
        res = analyze_dialogue_mechanics(test_text)
        bookisms = [item["word"].lower() for item in res["said_bookisms"]]

        # High-severity said-bookisms should be flagged
        expected_bookisms = {"pontificated", "ejaculated", "opined", "gasped"}
        for exp in expected_bookisms:
            self.assertIn(exp, bookisms, f"Expected said-bookism '{exp}' to be detected")

        # Standard clean dialogue tags should NOT be flagged as said-bookisms
        clean_tags = ["said", "asked", "whispered", "replied"]
        for clean in clean_tags:
            self.assertNotIn(clean, bookisms, f"Clean tag '{clean}' should not be flagged as a said-bookism")

    def test_adverb_dialogue_tag_detection(self):
        """
        Corpus with adverb-modified dialogue tags vs clean action beats.
        """
        test_text = """
        "Drop your weapons," Elena said angrily.
        "Never," Marcus said fiercely.
        "Please stop fighting," Lyra whispered quietly.
        "The gate is open," Marcus said, drawing his sword.
        "Stay back," said proudly the knight.
        """
        res = analyze_dialogue_mechanics(test_text)
        adverbs = [item["adverb"].lower() for item in res["adverb_tags"]]

        self.assertIn("angrily", adverbs)
        self.assertIn("fiercely", adverbs)
        self.assertIn("quietly", adverbs)
        self.assertIn("proudly", adverbs)

    def test_dialogue_punctuation_and_capitalization_rules(self):
        """
        Corpus with intentional punctuation errors vs correct conventions.
        """
        test_text = """
        "We have to leave now." said the scout.
        "I am ready," He said.
        "Look over there!" shouted the captain.
        "Is that them?" asked the guard.
        "We are safe," said the mayor.
        """
        res = analyze_dialogue_mechanics(test_text)
        fault_types = [item["type"] for item in res["formatting_issues"]]

        # Line 1 has period before lowercase tag: "We have to leave now." said the scout.
        self.assertIn("period_before_tag", fault_types)
        # Line 2 has capitalized pronoun after comma: "I am ready," He said.
        self.assertIn("capitalized_tag_pronoun", fault_types)

    # -------------------------------------------------------------------------
    # 2. Word Echoes / Lexical Repetition Sliding Window
    # -------------------------------------------------------------------------
    def test_echo_detector_positive_and_negative(self):
        """
        Corpus with close repetition of non-stopword content words vs normal prose.
        """
        repetitive_prose = """
        The obsidian monolith stood in the center of the dark cavern.
        Marcus examined the obsidian carvings with great fascination.
        Suddenly, another obsidian shard detached from the cavern ceiling.
        """
        res = analyze_word_echoes(repetitive_prose, window_size=100)
        echo_stems = [e["stem"] for e in res["echoes"]]

        self.assertIn("obsidian", echo_stems)
        self.assertIn("cavern", echo_stems)

        # Common stopwords should NEVER be flagged as echoes
        for word in ["the", "in", "of", "and", "with", "from"]:
            self.assertNotIn(word, echo_stems)

    # -------------------------------------------------------------------------
    # 3. Readability Rhythm & Staccato Alerts
    # -------------------------------------------------------------------------
    def test_staccato_and_monotone_rhythm_detection(self):
        """
        Corpus with consecutive ultra-short sentences triggering staccato alert.
        """
        staccato_prose = """
        He ran. She stopped. Wind blew. Rain fell. Dark clouds gathered quickly.
        Lightning struck. Doors slammed. He fled. She hid. Fear grew.
        All around them the storm raged fiercely without any sign of stopping.
        """
        res = analyze_readability_rhythm(staccato_prose)
        self.assertGreater(len(res["staccato_clusters"]), 0)

    # -------------------------------------------------------------------------
    # 4. Character Voice Profiling & Voice Bleed Matrix
    # -------------------------------------------------------------------------
    def test_character_voice_fingerprint_and_bleed(self):
        """
        Corpus testing distinct character voices vs identical author voice bleed.
        """
        corpus = {
            "Elena_Formal": [
                "It is impermissible that we deviate from our solemn charter.",
                "We must not succumb to unwarranted panic or disorderly conduct.",
                "Shall we proceed with the ceremonial invocation forthwith?"
            ],
            "Marcus_Colloquial": [
                "Ain't no way I'm gonna let that slide, you know?",
                "Gotta run fast, buddy! Don't look back!",
                "What's up with you? Can't you hear 'em coming?"
            ],
            "Clone_Elena": [
                "It is strictly impermissible that we deviate from our sacred charter.",
                "We shall not succumb to unwarranted panic or unruly conduct.",
                "Shall we proceed with the formal ceremony forthwith?"
            ]
        }

        prof_formal = compute_voice_profile(corpus["Elena_Formal"], char_name="Elena_Formal")
        prof_colloquial = compute_voice_profile(corpus["Marcus_Colloquial"], char_name="Marcus_Colloquial")
        prof_clone = compute_voice_profile(corpus["Clone_Elena"], char_name="Clone_Elena")

        # Formal should have higher formality and lower contraction rate
        self.assertGreater(prof_formal["formality_score"], prof_colloquial["formality_score"])
        self.assertGreater(prof_colloquial["contraction_rate"], prof_formal["contraction_rate"])

        # Voice Bleed Similarity: Elena and Clone_Elena should have high similarity, Elena vs Marcus low
        sim_clones = compute_voice_similarity(prof_formal, prof_clone)
        sim_distinct = compute_voice_similarity(prof_formal, prof_colloquial)

        self.assertGreater(sim_clones, 0.90)
        self.assertGreater(sim_clones, sim_distinct)


if __name__ == "__main__":
    unittest.main()
