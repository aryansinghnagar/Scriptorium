#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Focus Ambient & Binaural Soundscape Generator (scripts/lib/ambient.py).
Validates:
- PLT-106: Procedural audio synthesis (wave + struct stdlib).
- Multi-noise colors (white, pink, brown) and binaural beat frequencies.
- WAV header and audio format compliance.
- Atmosphere profile schema completeness.
- Interactive HTML5 WebAudio synthesizer generation and CSP compliance.
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
    PROFILES,
    SAMPLE_RATE,
)


class TestAmbientEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # WAV Synthesis Tests                                                  #
    # ------------------------------------------------------------------ #

    def test_synthesize_wav_format_and_header(self):
        """WAV file must be stereo, 16-bit, 44100 Hz, with correct frame count."""
        out_wav = self.target_dir / "test_ambient.wav"
        synthesize_wav(
            output_path=out_wav,
            duration_sec=1,
            noise_type="brown",
            binaural_beat=10.0,
            carrier_freq=216.0,
            ambient_mode="rain",
        )
        self.assertTrue(out_wav.is_file())
        self.assertGreater(out_wav.stat().st_size, 1000)

        with wave.open(str(out_wav), "rb") as wf:
            self.assertEqual(wf.getnchannels(), 2)
            self.assertEqual(wf.getsampwidth(), 2)  # 16-bit
            self.assertEqual(wf.getframerate(), 44100)
            self.assertEqual(wf.getnframes(), 44100)

    def test_synthesize_wav_creates_file(self):
        """synthesize_wav must create the output file and return the output path."""
        out_wav = self.target_dir / "brown_ambient.wav"
        result = synthesize_wav(output_path=out_wav, duration_sec=1, noise_type="brown")
        self.assertTrue(out_wav.is_file())
        self.assertEqual(result, out_wav)

    def test_synthesize_brown_noise_wav(self):
        """Brown noise WAV must produce non-trivial file size (> 80 KB for 1 second stereo)."""
        out_wav = self.target_dir / "brown.wav"
        synthesize_wav(output_path=out_wav, duration_sec=1, noise_type="brown")
        self.assertGreater(out_wav.stat().st_size, 80_000)

    def test_synthesize_pink_noise_wav(self):
        """Pink noise WAV must complete without error and produce a valid file."""
        out_wav = self.target_dir / "pink.wav"
        synthesize_wav(output_path=out_wav, duration_sec=1, noise_type="pink", ambient_mode="ocean")
        self.assertTrue(out_wav.is_file())
        with wave.open(str(out_wav), "rb") as wf:
            self.assertEqual(wf.getnchannels(), 2)

    def test_synthesize_white_noise_wav(self):
        """White noise (non-brown/pink fallback) must produce a valid stereo WAV."""
        out_wav = self.target_dir / "white.wav"
        synthesize_wav(output_path=out_wav, duration_sec=1, noise_type="white", ambient_mode="wind")
        self.assertTrue(out_wav.is_file())
        with wave.open(str(out_wav), "rb") as wf:
            self.assertEqual(wf.getframerate(), 44100)

    def test_synthesize_wav_duration_proportional(self):
        """A 2-second WAV must contain exactly 2 * SAMPLE_RATE frames."""
        out_wav = self.target_dir / "two_seconds.wav"
        synthesize_wav(output_path=out_wav, duration_sec=2, noise_type="brown")
        with wave.open(str(out_wav), "rb") as wf:
            self.assertEqual(wf.getnframes(), 2 * SAMPLE_RATE)

    def test_binaural_beat_separation_in_profiles(self):
        """For each profile, right_freq = carrier + beat must be > carrier (positive separation)."""
        for name, p in PROFILES.items():
            carrier = float(p["carrier"])
            beat = float(p["beat"])
            self.assertGreater(
                carrier + beat,
                carrier,
                msg=f"Profile '{name}' has non-positive binaural separation",
            )

    # ------------------------------------------------------------------ #
    # PROFILES Schema Tests                                                #
    # ------------------------------------------------------------------ #

    def test_profiles_dict_has_five_entries(self):
        """PROFILES must contain at least 5 named atmosphere profiles."""
        self.assertGreaterEqual(len(PROFILES), 5)

    def test_profile_keys_schema(self):
        """Each profile must have type, noise, binaural, carrier, beat, and desc keys."""
        required_keys = {"type", "noise", "binaural", "carrier", "beat", "desc"}
        for name, p in PROFILES.items():
            missing = required_keys - p.keys()
            self.assertEqual(
                missing,
                set(),
                msg=f"Profile '{name}' is missing keys: {missing}",
            )

    def test_atmosphere_profiles_valid(self):
        """Legacy test: each profile has noise, carrier, and beat keys."""
        for _name, p in PROFILES.items():
            self.assertIn("noise", p)
            self.assertIn("carrier", p)
            self.assertIn("beat", p)

    # ------------------------------------------------------------------ #
    # HTML Synthesizer Tests                                               #
    # ------------------------------------------------------------------ #

    def test_html_synthesizer_generation(self):
        """HTML synthesizer file must be created and contain AudioContext reference."""
        out_html = self.target_dir / "synthesizer.html"
        generate_ambient_html_synthesizer(out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Focus Soundscape Studio", content)
        self.assertIn("AudioContext", content)

    def test_html_synthesizer_csp_compliant(self):
        """HTML synthesizer must declare a Content-Security-Policy meta tag."""
        out_html = self.target_dir / "csp_check.html"
        generate_ambient_html_synthesizer(out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn(
            "default-src",
            content,
            msg="HTML synthesizer is missing Content-Security-Policy meta tag",
        )

    def test_html_synthesizer_contains_webaudio(self):
        """HTML synthesizer must reference AudioContext (WebAudio API)."""
        out_html = self.target_dir / "webaudio_check.html"
        generate_ambient_html_synthesizer(out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertTrue(
            "AudioContext" in content or "webkitAudioContext" in content,
            msg="HTML synthesizer must reference AudioContext or webkitAudioContext",
        )

    def test_html_synthesizer_contains_profile_names(self):
        """HTML synthesizer must mention at least 3 of the 5 PROFILES by name or description."""
        out_html = self.target_dir / "profiles_check.html"
        generate_ambient_html_synthesizer(out_html)
        content = out_html.read_text(encoding="utf-8").lower()
        # Check for at least 3 profile type names: rain, ocean, wind, space, noise/focus
        type_words = ["rain", "ocean", "wind", "space", "focus", "binaural", "noise"]
        matches = sum(1 for w in type_words if w in content)
        self.assertGreaterEqual(
            matches,
            3,
            msg=f"HTML synthesizer only mentions {matches} of expected profile type words",
        )


if __name__ == "__main__":
    unittest.main()
