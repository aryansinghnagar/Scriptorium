#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Focus Ambient & Binaural Soundscape Generator (scripts/lib/ambient.py).
Validates:
- PLT-106: Procedural audio synthesis (wave + struct stdlib).
- Multi-noise colors (white, pink, brown) and binaural beat frequencies.
- WAV header and audio format compliance.
- Interactive HTML5 WebAudio synthesizer generation.
"""

import tempfile
import unittest
import wave
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.ambient import (
    synthesize_wav,
    generate_ambient_html_synthesizer,
    PROFILES
)


class TestAmbientEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_synthesize_wav_format_and_header(self):
        out_wav = self.target_dir / "test_ambient.wav"
        synthesize_wav(
            output_path=out_wav,
            duration_sec=1,
            noise_type="brown",
            binaural_beat=10.0,
            carrier_freq=216.0,
            ambient_mode="rain"
        )
        self.assertTrue(out_wav.is_file())
        self.assertGreater(out_wav.stat().st_size, 1000)

        # Validate with stdlib wave
        with wave.open(str(out_wav), "rb") as wf:
            self.assertEqual(wf.getnchannels(), 2)
            self.assertEqual(wf.getsampwidth(), 2)  # 16-bit
            self.assertEqual(wf.getframerate(), 44100)
            self.assertEqual(wf.getnframes(), 44100)

    def test_atmosphere_profiles_valid(self):
        for _name, p in PROFILES.items():
            self.assertIn("noise", p)
            self.assertIn("carrier", p)
            self.assertIn("beat", p)

    def test_html_synthesizer_generation(self):
        out_html = self.target_dir / "synthesizer.html"
        generate_ambient_html_synthesizer(out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Focus Soundscape Studio", content)
        self.assertIn("AudioContext", content)


if __name__ == "__main__":
    unittest.main()
