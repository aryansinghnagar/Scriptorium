#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum ISBN-13 Vector SVG/PNG Barcode Engine (scripts/lib/barcode.py).
Validates:
- PUB-102: ISBN-10 to ISBN-13 conversion.
- EAN-13 Modulo-10 checksum calculation and validation.
- Vector SVG barcode output.
- Binary PNG barcode generation (zero-dependency pure python zlib).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.barcode import (
    calculate_isbn13_checksum,
    isbn10_to_isbn13,
    validate_and_normalize_isbn,
    generate_svg_barcode,
    generate_png_barcode,
    export_barcode
)


class TestBarcodeEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_isbn13_checksum_calculation(self):
        # 978-0-345-39180-3 -> check digit is 3
        core = "978034539180"
        check = calculate_isbn13_checksum(core)
        self.assertEqual(check, 3)

    def test_isbn10_to_isbn13_conversion(self):
        # 0-345-39180-2 -> 978-0345391803
        converted = isbn10_to_isbn13("0-345-39180-2")
        self.assertEqual(converted, "9780345391803")

    def test_invalid_isbn_raises_error(self):
        with self.assertRaises(ValueError):
            validate_and_normalize_isbn("978-0-345-39180-9")  # bad checksum

    def test_generate_svg_barcode(self):
        svg = generate_svg_barcode("9780345391803")
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("</svg>", svg)
        self.assertIn("978-0-3453-9180-3", svg)

    def test_generate_svg_barcode_979(self):
        # 979-10-90636-07-1
        svg = generate_svg_barcode("9791090636071")
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("ISBN 979-1-0906-3607-1", svg)

    def test_generate_png_barcode(self):
        png_bytes = generate_png_barcode("9780345391803")
        # Check standard PNG header
        self.assertTrue(png_bytes.startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertIn(b'IHDR', png_bytes)
        self.assertIn(b'IDAT', png_bytes)
        self.assertIn(b'IEND', png_bytes)

    def test_export_barcode_files(self):
        svg_file = self.target_dir / "test.svg"
        png_file = self.target_dir / "test.png"

        export_barcode("9780345391803", svg_file)
        export_barcode("9780345391803", png_file)

        self.assertTrue(svg_file.is_file())
        self.assertTrue(png_file.is_file())
        self.assertGreater(svg_file.stat().st_size, 500)
        self.assertGreater(png_file.stat().st_size, 500)

    def test_barcode_cli_json(self):
        import subprocess
        import json
        res = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "lib" / "barcode.py"), "9780306406157", "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(res.stdout)
        self.assertTrue(data.get("valid"))
        self.assertEqual(data.get("normalized_isbn13"), "9780306406157")
        self.assertEqual(data.get("checksum"), 7)


if __name__ == "__main__":
    unittest.main()
