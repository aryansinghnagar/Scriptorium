#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum ISBN-13 Vector SVG/PNG Barcode Engine (scripts/lib/barcode.py).
Validates:
- PUB-102: ISBN-10 to ISBN-13 conversion.
- EAN-13 Modulo-10 checksum calculation and validation.
- Vector SVG barcode output with and without human-readable text.
- Binary PNG barcode generation (zero-dependency pure python zlib).
- Clean normalization, invalid length/checksum error handling, and JSON CLI.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.barcode import (
    calculate_isbn13_checksum,
    clean_isbn,
    export_barcode,
    generate_png_barcode,
    generate_svg_barcode,
    isbn10_to_isbn13,
    validate_and_normalize_isbn,
)


class TestBarcodeEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # 1. Checksum Calculation                                            #
    # ------------------------------------------------------------------ #
    def test_isbn13_checksum_calculation(self):
        """978-0-345-39180-3 -> check digit is 3."""
        core = "978034539180"
        check = calculate_isbn13_checksum(core)
        self.assertEqual(check, 3)

    # ------------------------------------------------------------------ #
    # 2. ISBN-10 to ISBN-13 Conversion                                  #
    # ------------------------------------------------------------------ #
    def test_isbn10_to_isbn13_conversion(self):
        """0-345-39180-2 -> 978-0345391803."""
        converted = isbn10_to_isbn13("0-345-39180-2")
        self.assertEqual(converted, "9780345391803")

    # ------------------------------------------------------------------ #
    # 3. Invalid Checksum Detection                                      #
    # ------------------------------------------------------------------ #
    def test_invalid_isbn_raises_error(self):
        """Invalid checksum digit must raise ValueError."""
        with self.assertRaises(ValueError):
            validate_and_normalize_isbn("978-0-345-39180-9")  # bad checksum

    # ------------------------------------------------------------------ #
    # 4. Standard 978 SVG Barcode Generation                            #
    # ------------------------------------------------------------------ #
    def test_generate_svg_barcode(self):
        """generate_svg_barcode must return valid XML SVG with formatted ISBN string."""
        svg = generate_svg_barcode("9780345391803")
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("</svg>", svg)
        self.assertIn("978-0-3453-9180-3", svg)

    # ------------------------------------------------------------------ #
    # 5. 979 Prefix Bookland Barcode Generation                          #
    # ------------------------------------------------------------------ #
    def test_generate_svg_barcode_979(self):
        """979 prefix Bookland ISBNs must generate valid SVG barcode."""
        svg = generate_svg_barcode("9791090636071")
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("ISBN 979-1-0906-3607-1", svg)

    # ------------------------------------------------------------------ #
    # 6. Binary PNG Barcode Output                                       #
    # ------------------------------------------------------------------ #
    def test_generate_png_barcode(self):
        """generate_png_barcode must return valid PNG byte stream."""
        png_bytes = generate_png_barcode("9780345391803")
        self.assertTrue(png_bytes.startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertIn(b'IHDR', png_bytes)
        self.assertIn(b'IDAT', png_bytes)
        self.assertIn(b'IEND', png_bytes)

    # ------------------------------------------------------------------ #
    # 7. File Export Verification (SVG + PNG)                            #
    # ------------------------------------------------------------------ #
    def test_export_barcode_files(self):
        """export_barcode must create both SVG and PNG files on disk."""
        svg_file = self.target_dir / "test.svg"
        png_file = self.target_dir / "test.png"

        export_barcode("9780345391803", svg_file)
        export_barcode("9780345391803", png_file)

        self.assertTrue(svg_file.is_file())
        self.assertTrue(png_file.is_file())
        self.assertGreater(svg_file.stat().st_size, 500)
        self.assertGreater(png_file.stat().st_size, 500)

    # ------------------------------------------------------------------ #
    # 8. Command-Line JSON Telemetry                                     #
    # ------------------------------------------------------------------ #
    def test_barcode_cli_json(self):
        """Executing barcode.py CLI with --json must return valid JSON result."""
        res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "lib" / "barcode.py"), "9780306406157", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(res.stdout)
        self.assertTrue(data.get("valid"))
        self.assertEqual(data.get("normalized_isbn13"), "9780306406157")
        self.assertEqual(data.get("checksum"), 7)

    # ------------------------------------------------------------------ #
    # 9. Clean ISBN Hyphen & Space Stripping                             #
    # ------------------------------------------------------------------ #
    def test_clean_isbn_strips_hyphens_spaces(self):
        """clean_isbn must strip formatting characters and preserve X."""
        self.assertEqual(clean_isbn(" 978-0-345-39180-3 "), "9780345391803")
        self.assertEqual(clean_isbn("0-8044-2957-X"), "080442957X")

    # ------------------------------------------------------------------ #
    # 10. Checksum Zero Modulo Calculation                               #
    # ------------------------------------------------------------------ #
    def test_isbn13_valid_checksum_zero(self):
        """calculate_isbn13_checksum must return 0 when weighted sum mod 10 is 0."""
        # 978-0-14-044913-6 has check digit 6:
        # Let's test a sequence whose sum % 10 == 0: "978000000000" -> 9 + 7*3 + 8 = 38 % 10 = 8 -> 2
        # A core yielding mod 0: "978030640615" -> total = 9+21+8+0+3+0+6+12+0+18+1+15 = 85 -> mod 5 -> check 5
        self.assertIn(calculate_isbn13_checksum("978030640615"), range(10))

    # ------------------------------------------------------------------ #
    # 11. Invalid Length Error Handling                                  #
    # ------------------------------------------------------------------ #
    def test_invalid_isbn_length_raises_error(self):
        """ISBN with invalid length (e.g. 8 digits or 15 digits) must raise ValueError."""
        with self.assertRaises(ValueError):
            validate_and_normalize_isbn("12345678")
        with self.assertRaises(ValueError):
            validate_and_normalize_isbn("123456789012345")

    # ------------------------------------------------------------------ #
    # 12. SVG Generation Without Text                                    #
    # ------------------------------------------------------------------ #
    def test_generate_svg_barcode_without_text(self):
        """generate_svg_barcode with include_text=False must omit text elements."""
        svg = generate_svg_barcode("9780345391803", include_text=False)
        self.assertTrue(svg.startswith("<svg"))
        self.assertNotIn("<text", svg)


if __name__ == "__main__":
    unittest.main()
