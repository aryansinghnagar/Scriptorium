#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Character Voice Profiler & Dialogue Fingerprint Engine
(scripts/lib/voice.py).
Validates:
- PRO-103: Character-attributed dialogue extraction.
- Character linguistic metrics (TTR, mean utterance length, contraction rate, formality).
- Voice bleed / character homogeneity alerts.
- Standalone HTML report generation.
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
    generate_voice_html_report
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

    def test_voice_bleed_similarity(self):
        utts1 = ["We must go now.", "I see the enemy approaching.", "Take the weapon quickly."]
        utts2 = ["We must move now.", "I see the foe approaching.", "Take the sword quickly."]
        p1 = compute_voice_profile(utts1)
        p2 = compute_voice_profile(utts2)
        sim = compute_voice_similarity(p1, p2)
        self.assertGreater(sim, 0.8)

    def test_scan_and_html_generation(self):
        chapter = self.target_dir / "01_Ch1.md"
        chapter.write_text("""# Ch 1\nElena: "We cannot fail."\nElena: "The kingdom depends on us."\nVance: "I'm ready when you are, Captain."\nVance: "Let's do this."\n""", encoding="utf-8")
        
        report = scan_manuscript_voices(self.target_dir)
        self.assertIn("Elena", report["profiles"])
        self.assertIn("Vance", report["profiles"])

        out_html = self.target_dir / "voice_report.html"
        generate_voice_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Character Voice Profiler", out_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
