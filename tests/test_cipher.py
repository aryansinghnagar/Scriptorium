#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum In-World Cipher & Phonetic Rune Engine (scripts/lib/cipher.py).
"""

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.cipher import (
    cipher_caesar,
    cipher_atbash,
    cipher_vigenere,
    cipher_rail_fence,
    cipher_columnar,
    cipher_book_encode,
    cipher_book_decode,
    text_to_runes,
    generate_rune_svg,
)


class TestCipherEngine(unittest.TestCase):

    def test_caesar_cipher_roundtrip(self):
        plain = "The Dragon Awakens at Midnight!"
        shift = 7
        enc = cipher_caesar(plain, shift=shift, decode=False)
        dec = cipher_caesar(enc, shift=shift, decode=True)
        self.assertEqual(dec, plain)
        self.assertNotEqual(enc, plain)

    def test_atbash_cipher_symmetry(self):
        plain = "Secret Vault 101"
        enc = cipher_atbash(plain)
        dec = cipher_atbash(enc)
        self.assertEqual(dec, plain)

    def test_vigenere_cipher_roundtrip(self):
        plain = "DEFEND THE CITADEL OF VALORIA"
        key = "MITHRIL"
        enc = cipher_vigenere(plain, key=key, decode=False)
        dec = cipher_vigenere(enc, key=key, decode=True)
        self.assertEqual(dec, plain)
        self.assertNotEqual(enc, plain)

    def test_rail_fence_cipher_roundtrip(self):
        plain = "ATTACK AT DAWN ON THE NORTH WALL"
        enc = cipher_rail_fence(plain, rails=4, decode=False)
        dec = cipher_rail_fence(enc, rails=4, decode=True)
        self.assertEqual(dec, plain)

    def test_columnar_cipher_roundtrip(self):
        plain = "THE ARCHON HAS FALLEN TO SHADOW"
        key = "ZEPHYR"
        enc = cipher_columnar(plain, key=key, decode=False)
        dec = cipher_columnar(enc, key=key, decode=True)
        self.assertEqual(dec, plain)

    def test_book_cipher_roundtrip(self):
        book_text = """In the beginning the ancients carved the citadel into living stone.
The silent wardens guarded the gates against shadow and flame.
Only the true bearer shall awaken the hidden vault."""
        secret_msg = "ancients guarded the hidden vault"
        encoded = cipher_book_encode(secret_msg, book_text)
        self.assertIn("1.5", encoded)
        decoded = cipher_book_decode(encoded, book_text)
        self.assertEqual(decoded.lower(), secret_msg.lower())

    def test_phonetic_runes_and_svg(self):
        text = "Thor and Odin"
        runes = text_to_runes(text, alphabet="futhark")
        self.assertGreater(len(runes), 0)
        # Check Elder Futhark rune characters
        self.assertTrue(any(ord(c) >= 0x16A0 for c in runes))

        svg = generate_rune_svg(runes, title="Ancient Oath")
        self.assertIn("<svg", svg)
        self.assertIn("ANCIENT OATH", svg)


if __name__ == "__main__":
    unittest.main()
