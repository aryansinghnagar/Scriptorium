#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum In-World Cipher & Phonetic Rune Engine (scripts/lib/cipher.py).
Covers Caesar, Atbash, Vigenère, Rail Fence, Columnar, Book Cipher, and Phonetic Runes SVG generation.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.cipher import (
    cipher_atbash,
    cipher_book_decode,
    cipher_book_encode,
    cipher_caesar,
    cipher_columnar,
    cipher_rail_fence,
    cipher_vigenere,
    generate_rune_svg,
    text_to_runes,
)


class TestCipherEngine(unittest.TestCase):

    def test_caesar_cipher_roundtrip(self) -> None:
        """Caesar cipher encodes and decodes accurately across letter case and punctuation."""
        plain = "The Dragon Awakens at Midnight!"
        shift = 7
        enc = cipher_caesar(plain, shift=shift, decode=False)
        dec = cipher_caesar(enc, shift=shift, decode=True)
        self.assertEqual(dec, plain)
        self.assertNotEqual(enc, plain)

    def test_caesar_cipher_non_alpha_preserved(self) -> None:
        """Digits, spaces, symbols, and punctuation are untouched by Caesar shift."""
        plain = "Room #404: 100% Secret!"
        enc = cipher_caesar(plain, shift=13)
        self.assertIn("#404: 100%", enc)
        self.assertEqual(cipher_caesar(enc, shift=13, decode=True), plain)

    def test_atbash_cipher_symmetry(self) -> None:
        """Atbash cipher is self-inverting (symmetric) across all uppercase and lowercase letters."""
        plain = "Secret Vault 101"
        enc = cipher_atbash(plain)
        dec = cipher_atbash(enc)
        self.assertEqual(dec, plain)
        self.assertEqual(cipher_atbash("ABCxyz"), "ZYXcba")

    def test_vigenere_cipher_roundtrip(self) -> None:
        """Vigenère polyalphabetic cipher correctly encodes and decodes with secret keyword."""
        plain = "DEFEND THE CITADEL OF VALORIA"
        key = "MITHRIL"
        enc = cipher_vigenere(plain, key=key, decode=False)
        dec = cipher_vigenere(enc, key=key, decode=True)
        self.assertEqual(dec, plain)
        self.assertNotEqual(enc, plain)

    def test_vigenere_cipher_empty_or_non_alpha_key(self) -> None:
        """Vigenère handles empty or non-alphabetic keys gracefully without crashing."""
        plain = "Arcane Secret"
        self.assertEqual(cipher_vigenere(plain, key=""), plain)
        self.assertEqual(cipher_vigenere(plain, key="12345!"), plain)

    def test_rail_fence_cipher_roundtrip(self) -> None:
        """Rail fence zigzag cipher performs correct geometric transposition and inversion."""
        plain = "ATTACK AT DAWN ON THE NORTH WALL"
        enc = cipher_rail_fence(plain, rails=4, decode=False)
        dec = cipher_rail_fence(enc, rails=4, decode=True)
        self.assertEqual(dec, plain)
        self.assertNotEqual(enc, plain)

    def test_rail_fence_edge_cases(self) -> None:
        """Rail fence returns identical string when text length <= rails or rails <= 1."""
        text = "SHORT"
        self.assertEqual(cipher_rail_fence(text, rails=10, decode=False), text)
        self.assertEqual(cipher_rail_fence(text, rails=1, decode=False), text)

    def test_columnar_cipher_roundtrip(self) -> None:
        """Columnar transposition cipher rearranges columns according to alphabetical key sort."""
        plain = "THE ARCHON HAS FALLEN TO SHADOW"
        key = "ZEPHYR"
        enc = cipher_columnar(plain, key=key, decode=False)
        dec = cipher_columnar(enc, key=key, decode=True)
        self.assertEqual(dec, plain)

    def test_book_cipher_roundtrip(self) -> None:
        """Book cipher encodes words into line.word coordinates and reconstructs plaintext."""
        book_text = """In the beginning the ancients carved the citadel into living stone.
The silent wardens guarded the gates against shadow and flame.
Only the true bearer shall awaken the hidden vault."""
        secret_msg = "ancients guarded the hidden vault"
        encoded = cipher_book_encode(secret_msg, book_text)
        self.assertIn("1.5", encoded)
        decoded = cipher_book_decode(encoded, book_text)
        self.assertEqual(decoded.lower(), secret_msg.lower())

    def test_book_cipher_missing_word_fallback(self) -> None:
        """Book cipher preserves missing words in bracketed notation `[word]`."""
        book_text = "The quick brown fox jumps over the lazy dog."
        encoded = cipher_book_encode("fox dragon jumps", book_text)
        self.assertIn("[dragon]", encoded)
        decoded = cipher_book_decode(encoded, book_text)
        self.assertIn("dragon", decoded)

    def test_phonetic_runes_elder_futhark_and_futhorc(self) -> None:
        """Phonetic rune translator converts latin letters and digraphs into Elder Futhark and Futhorc."""
        text = "Thor and Odin"
        futhark_runes = text_to_runes(text, alphabet="futhark")
        self.assertGreater(len(futhark_runes), 0)
        # Elder Futhark rune range starts around 0x16A0
        self.assertTrue(any(ord(c) >= 0x16A0 for c in futhark_runes))

        futhorc_runes = text_to_runes("King and Queen", alphabet="futhorc")
        self.assertGreater(len(futhorc_runes), 0)
        self.assertTrue(any(ord(c) >= 0x16A0 for c in futhorc_runes))

    def test_generate_rune_svg_card(self) -> None:
        """Rune SVG generator produces valid vector markup with styling and proper escaping."""
        rune_text = text_to_runes("Ancient Oath", alphabet="futhark")
        svg = generate_rune_svg(rune_text, title="Oath of the Vanguard & King")
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)
        self.assertIn("OATH OF THE VANGUARD &AMP; KING", svg)
        self.assertIn('viewBox="0 0 800 200"', svg)


if __name__ == "__main__":
    unittest.main()
