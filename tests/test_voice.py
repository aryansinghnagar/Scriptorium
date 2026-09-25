#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Character Voice Profiler & Dialogue Fingerprint Engine
(scripts/lib/voice.py).
Validates:
- PRO-103: Character-attributed dialogue extraction.
- Character linguistic metrics (TTR, mean utterance length, contraction rate, formality).
- Voice bleed / character homogeneity alerts.
- Standalone HTML report generation with Content Security Policy.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.voice import (
    extract_character_dialogue,
    compute_voice_profile,
    compute_voice_similarity,
    scan_manuscript_voices,
    generate_voice_html_report,
)


class TestVoiceProfilerEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_character_dialogue_script_format(self):
        text = """
        Elena: "We must find the star sapphire before dawn."
        Vance: "I don't think that's wise, Elena. It's too dangerous."
        Elena: "Do you have a better idea?"
        """
        extracted = extract_character_dialogue(text)
        self.assertIn("Elena", extracted)
        self.assertIn("Vance", extracted)
        self.assertEqual(len(extracted["Elena"]), 2)
        self.assertEqual(len(extracted["Vance"]), 1)

    def test_extract_character_dialogue_tags(self):
        text = """
        "We have reached the perimeter," said Kaelen.
        "Hold your fire until they enter the canyon," whispered Lyra.
        """
        extracted = extract_character_dialogue(text)
        self.assertIn("Kaelen", extracted)
        self.assertIn("Lyra", extracted)

    def test_extract_character_dialogue_pre_quote(self):
        text = """
        Kaelen shouted, "Hold the inner gate at all costs!"
        Lyra whispered, "The runes are failing."
        """
        extracted = extract_character_dialogue(text)
        self.assertIn("Kaelen", extracted)
        self.assertIn("Lyra", extracted)
        self.assertEqual(extracted["Kaelen"][0], "Hold the inner gate at all costs!")

    def test_voice_profile_metrics_formal_vs_colloquial(self):
        # Formal character: no contractions, long sentences
        formal_utts = [
            "We cannot permit these insolent trespassers to violate our sacred boundary.",
            "It is imperative that we maintain absolute vigilance throughout the nocturnal watches.",
            "Shall we proceed to the inner sanctum to consult the grand archivist?"
        ]
        prof_formal = compute_voice_profile(formal_utts, char_name="Archon")
        self.assertEqual(prof_formal["contraction_rate"], 0.0)
        self.assertGreater(prof_formal["formality_score"], 50.0)
        self.assertGreater(prof_formal["mean_length"], 8.0)

        # Colloquial character: heavy contractions, short sentences
        colloquial_utts = [
            "I don't know, it's gotta be around here somewhere, right?",
            "Can't we just grab it and run? Won't that be easier?",
            "I'm gonna check behind that rock!"
        ]
        prof_colloquial = compute_voice_profile(colloquial_utts, char_name="Rogue")
        self.assertGreater(prof_colloquial["contraction_rate"], 10.0)
        self.assertLess(prof_colloquial["formality_score"], prof_formal["formality_score"])

    def test_voice_profile_punctuation_cadence(self):
        utts = [
            "Is anyone there? Where are they?",
            "Look out! Behind you!",
            "I thought... maybe we could wait...",
            "Wait—don't open that door!"
        ]
        prof = compute_voice_profile(utts, char_name="CadenceTest")
        self.assertGreater(prof["question_ratio"], 0.0)
        self.assertGreater(prof["exclamation_ratio"], 0.0)
        self.assertGreater(prof["ellipsis_ratio"], 0.0)
        self.assertGreater(prof["interruption_ratio"], 0.0)

    def test_voice_profile_empty_utterances(self):
        prof = compute_voice_profile([], char_name="Empty")
        self.assertEqual(prof["utterance_count"], 0)
        self.assertEqual(prof["total_words"], 0)
        self.assertEqual(prof["formality_score"], 50.0)

    def test_voice_profile_distinctive_vocabulary(self):
        corpus = {
            "Mage": [
                "The arcane resonance illuminates the celestial vortex.",
                "Arcane conduits channel the celestial vortex through ancient stones."
            ],
            "Warrior": [
                "Sharpen the heavy iron sword and polish the heavy shield.",
                "The iron shield withstood the enemy blow with great force."
            ]
        }
        prof = compute_voice_profile(corpus["Mage"], all_characters_corpus=corpus, char_name="Mage")
        words = [d["word"] for d in prof["distinctive_words"]]
        self.assertTrue("arcane" in words or "celestial" in words or "vortex" in words)

    def test_voice_bleed_similarity(self):
        utts1 = ["We must go now.", "I see the enemy approaching.", "Take the weapon quickly."]
        utts2 = ["We must move now.", "I see the foe approaching.", "Take the sword quickly."]
        p1 = compute_voice_profile(utts1)
        p2 = compute_voice_profile(utts2)
        sim = compute_voice_similarity(p1, p2)
        self.assertGreater(sim, 0.8)

    def test_voice_dissimilarity(self):
        formal = ["We shall respectfully decline your generous proposal.", "It is of paramount importance that decorum is preserved."]
        informal = ["Nah, no way man! Ain't doing that, get outta here!"]
        p1 = compute_voice_profile(formal)
        p2 = compute_voice_profile(informal)
        sim = compute_voice_similarity(p1, p2)
        self.assertLess(sim, 0.8)

    def test_voice_profile_sample_size_warning(self):
        short_utts = ["Hello there."]
        prof = compute_voice_profile(short_utts, char_name="Short")
        self.assertIsNotNone(prof["sample_size_warning"])

    def test_scan_manuscript_voices_multiple_chapters(self):
        (self.target_dir / "01_Ch1.md").write_text("""# Ch 1
Elena: "We cannot fail this quest."
Elena: "The realm depends on our courage."
Vance: "I'm ready when you are."
Vance: "Let us move silently through the shadows."
""", encoding="utf-8")
        (self.target_dir / "02_Ch2.md").write_text("""# Ch 2
Elena: "The celestial alignment begins."
Kaelen: "My blade is yours to command."
Kaelen: "We strike at midnight."
""", encoding="utf-8")
        report = scan_manuscript_voices(self.target_dir)
        self.assertIn("Elena", report["profiles"])
        self.assertIn("Vance", report["profiles"])
        self.assertIn("Kaelen", report["profiles"])

    def test_generate_voice_html_report_csp(self):
        chapter = self.target_dir / "01_Ch1.md"
        chapter.write_text("""# Ch 1\nElena: "We cannot fail."\nElena: "The kingdom depends on us."\nVance: "I'm ready when you are, Captain."\nVance: "Let's do this."\n""", encoding="utf-8")
        report = scan_manuscript_voices(self.target_dir)
        out_html = self.target_dir / "voice_report.html"
        generate_voice_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Character Voice Profiler", content)
        self.assertIn("Content-Security-Policy", content)


if __name__ == "__main__":
    unittest.main()
