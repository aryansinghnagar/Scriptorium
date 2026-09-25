#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Offline Neural TTS & Audio Proofreader
(scripts/lib/tts_reader.py)
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.tts_reader import (
    clean_prose_for_speech,
    find_system_tts_engine,
    generate_tts_html_player,
    main as tts_main,
    speak_text,
)


class TestTTSReader(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_prose_basic(self):
        sample_md = """---
title: Chapter 1
author: Scriptor
---
@pov: Alden
@location: High Spire

# Act I: The Awakening

The ancient bell tolled three times. **Danger** approached swiftly.

*Alden* gripped his blade, eyes fixed on [[The Sunken Citadel|Sunken Citadel]].
He whispered to [[Kaelen]]: "Wait here."

```python
# ignored code
```

- Watch the shadows
- Do not make a sound
"""
        paragraphs = clean_prose_for_speech(sample_md)
        self.assertEqual(len(paragraphs), 4)
        self.assertEqual(paragraphs[0], "Act I: The Awakening")
        self.assertIn("The ancient bell tolled three times. Danger approached swiftly.", paragraphs[1])
        self.assertIn("Alden gripped his blade, eyes fixed on Sunken Citadel.", paragraphs[2])
        self.assertIn("He whispered to Kaelen: \"Wait here.\"", paragraphs[2])
        self.assertIn("Watch the shadows Do not make a sound", paragraphs[3])
        # Verify markdown headers hashes, frontmatter, and code blocks were omitted
        for p in paragraphs:
            self.assertNotIn("Chapter 1", p)
            self.assertNotIn("#", p)
            self.assertNotIn("@pov:", p)
            self.assertNotIn("ignored code", p)

    def test_clean_prose_pronunciation_dictionary(self):
        sample_md = "Caelum channeled his aether while approaching the city of Xylar."
        pron_dict = {
            "Caelum": "KAY-lum",
            "Xylar": "ZY-lar",
            "aether": "EE-ther"
        }
        cleaned = clean_prose_for_speech(sample_md, pronunciation_dict=pron_dict)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0], "KAY-lum channeled his EE-ther while approaching the city of ZY-lar.")

    def test_clean_prose_wikilink_variations(self):
        sample_md = "Visiting [[Aethelgard]] and [[Morvath Prime|the dark citadel]]."
        cleaned = clean_prose_for_speech(sample_md)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0], "Visiting Aethelgard and the dark citadel.")

    def test_generate_tts_html_player(self):
        paragraphs = [
            "The sky turned dark as midnight fell upon the city. Lightning flashed across the spires.",
            "Alden stood silent. He knew what had to be done."
        ]
        out_file = self.test_dir / "test_player.html"
        generated = generate_tts_html_player(paragraphs, title="Chapter One", output_path=out_file)

        self.assertTrue(generated.exists())
        content = generated.read_text(encoding="utf-8")

        self.assertIn("Ars Arcanum — Audio Proofreader: Chapter One", content)
        self.assertIn("window.speechSynthesis", content)
        self.assertIn("The sky turned dark as midnight fell upon the city.", content)
        self.assertIn("Lightning flashed across the spires.", content)
        self.assertIn("togglePlay", content)
        self.assertIn("speedSlider", content)

    @patch("shutil.which")
    def test_find_system_tts_engine(self, mock_which):
        # Case 1: piper available
        mock_which.side_effect = lambda tool: "/usr/bin/piper" if tool == "piper" else None
        self.assertEqual(find_system_tts_engine(), "piper")

        # Case 2: espeak available
        mock_which.side_effect = lambda tool: "/usr/bin/espeak" if tool == "espeak" else None
        self.assertEqual(find_system_tts_engine(), "espeak")

        # Case 3: none found on linux
        mock_which.side_effect = None
        mock_which.return_value = None
        with patch("sys.platform", "linux"):
            self.assertIsNone(find_system_tts_engine())

        # Case 4: none found on windows -> powershell_sapi
        with patch("sys.platform", "win32"):
            self.assertEqual(find_system_tts_engine(), "powershell_sapi")

    @patch("lib.tts_reader.find_system_tts_engine")
    @patch("subprocess.run")
    def test_speak_text(self, mock_run, mock_find):
        mock_find.return_value = "espeak"
        mock_run.return_value = MagicMock(returncode=0)

        result = speak_text("Hello world", speed=1.2, voice="en-us")
        self.assertTrue(result)
        mock_run.assert_called_once()
        args, _kwargs = mock_run.call_args
        cmd = args[0]
        self.assertEqual(cmd[0], "espeak")
        self.assertIn("-s", cmd)
        self.assertIn("-v", cmd)
        self.assertIn("en-us", cmd)

    def test_cli_json_export(self):
        doc = self.test_dir / "chapter.md"
        doc.write_text("# Chapter\n\nFirst paragraph here.\n\nSecond paragraph here.", encoding="utf-8")

        with patch("sys.argv", ["tts_reader.py", str(doc), "--json"]), patch("builtins.print") as mock_print:
            tts_main()
            mock_print.assert_called()
            printed_str = mock_print.call_args[0][0]
            data = json.loads(printed_str)
            self.assertEqual(len(data["paragraphs"]), 3)
            self.assertEqual(data["paragraphs"][0], "Chapter")
            self.assertEqual(data["paragraphs"][1], "First paragraph here.")

    def test_clean_prose_empty_and_whitespace(self):
        """Verifies empty strings and whitespace-only documents produce empty list."""
        self.assertEqual(clean_prose_for_speech(""), [])
        self.assertEqual(clean_prose_for_speech("   \n\n   \t  "), [])
        self.assertEqual(clean_prose_for_speech("---\ntitle: Only Frontmatter\n---\n"), [])

    def test_clean_prose_multiple_paragraphs_spacing(self):
        """Verifies distinct paragraphs are parsed with proper boundaries."""
        text = "First paragraph here.\n\nSecond paragraph with multiple sentences. Another sentence.\n\nThird paragraph."
        paragraphs = clean_prose_for_speech(text)
        self.assertEqual(len(paragraphs), 3)
        self.assertEqual(paragraphs[0], "First paragraph here.")
        self.assertEqual(paragraphs[2], "Third paragraph.")

    def test_generate_tts_html_player_csp_meta(self):
        """Verifies CSP meta tag and offline compliance in audio player HTML."""
        out_file = self.test_dir / "player_csp.html"
        generate_tts_html_player(["Paragraph 1", "Paragraph 2"], title="Proofreader", output_path=out_file)
        self.assertTrue(out_file.exists())
        content = out_file.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)

    @patch("lib.tts_reader.find_system_tts_engine")
    def test_speak_text_no_engine_returns_false(self, mock_find):
        """Verifies speak_text returns False when no system TTS engine is available."""
        mock_find.return_value = None
        res = speak_text("Test voice output")
        self.assertFalse(res)

    def test_cli_execution_with_html_export(self):
        """Verifies CLI execution with --html output file creation."""
        doc = self.test_dir / "story.md"
        doc.write_text("# Chapter One\n\nThe hero embarked on the journey.", encoding="utf-8")
        out_html = self.test_dir / "story_audio.html"

        with patch("sys.argv", ["tts_reader.py", str(doc), "--html", str(out_html)]):
            tts_main()
            self.assertTrue(out_html.exists())
            content = out_html.read_text(encoding="utf-8")
            self.assertIn("The hero embarked on the journey.", content)


if __name__ == "__main__":
    unittest.main()
