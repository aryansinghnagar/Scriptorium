#!/usr/bin/env python3
r"""
Ars Arcanum Inscriptions, In-World Ciphers & Phonetic Rune Engine (scripts/lib/cipher.py)
========================================================================================
Zero-dependency, offline cryptographic encoding/decoding suite and phonetic rune/glyph
generator for in-world manuscripts, secret factions, and arcane inscriptions.

Ciphers Supported:
1. Caesar / ROT-N Substitution: Shift-based monoalphabetic cipher.
2. Atbash Cipher: Reverse alphabet substitution ($A \leftrightarrow Z$).
3. Vigenère Cipher: Polyalphabetic substitution keyed with lore keywords (e.g. "MITHRIL").
4. Rail Fence Transposition: Zigzag transposition with N rails.
5. Columnar Transposition: Keyed permutation matrix.
6. Book Cipher: Coordinate encoding referencing source text paragraphs/words.
7. Phonetic Runes & Arcane Glyphs:
   - Elder Futhark, Anglo-Saxon Futhorc, and Cirth-inspired runes.
   - Standalone SVG inscription renderer.

Zero external dependencies; 100% offline privacy.
"""

import sys
import re
import json
import html
import argparse
import logging
from pathlib import Path

try:
    from lib.fs_utils import atomic_write
except ImportError:
    try:
        from fs_utils import atomic_write
    except ImportError:
        def atomic_write(path, data, encoding="utf-8"):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, (bytes, bytearray)):
                p.write_bytes(data)
            else:
                p.write_text(data, encoding=encoding)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.cipher")

# Phonetic Rune alphabets
ELDER_FUTHARK = {
    "f": "ᚠ", "u": "ᚢ", "th": "ᚦ", "a": "ᚨ", "r": "ᚱ", "k": "ᚲ", "c": "ᚲ",
    "g": "ᚷ", "w": "ᚹ", "v": "ᚹ", "h": "ᚺ", "n": "ᚾ", "i": "ᛁ", "j": "ᛃ",
    "y": "ᛃ", "ae": "ᛇ", "p": "ᛈ", "z": "ᛉ", "s": "ᛊ", "t": "ᛏ", "b": "ᛒ",
    "e": "ᛖ", "m": "ᛗ", "l": "ᛚ", "ng": "ᛜ", "d": "ᛞ", "o": "ᛟ", " ": " : "
}

ANGLO_SAXON_FUTHORC = {
    "f": "ᚠ", "u": "ᚢ", "th": "ᚦ", "o": "ᚩ", "r": "ᚱ", "c": "ᚳ", "k": "ᚳ",
    "g": "ᚷ", "w": "ᚹ", "h": "ᚻ", "n": "ᚾ", "i": "ᛁ", "j": "ᛄ", "eo": "ᛇ",
    "p": "ᛈ", "x": "ᛉ", "s": "ᛋ", "t": "ᛏ", "b": "ᛒ", "e": "ᛖ", "m": "ᛗ",
    "l": "ᛚ", "ng": "ᛝ", "d": "ᛞ", "oe": "ᛟ", "a": "ᚪ", "ae": "ᚫ", "y": "ᚣ",
    " ": " • "
}


def cipher_caesar(text: str, shift: int = 3, decode: bool = False) -> str:
    """Caesar cipher with configurable shift."""
    if decode:
        shift = -shift
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


def cipher_atbash(text: str) -> str:
    """Atbash cipher (A <-> Z, B <-> Y)."""
    result = []
    for ch in text:
        if ch.isalpha():
            if ch.isupper():
                result.append(chr(ord('Z') - (ord(ch) - ord('A'))))
            else:
                result.append(chr(ord('z') - (ord(ch) - ord('a'))))
        else:
            result.append(ch)
    return "".join(result)


def cipher_vigenere(text: str, key: str, decode: bool = False) -> str:
    """Vigenère polyalphabetic cipher."""
    if not key:
        return text
    clean_key = [ord(k.upper()) - ord('A') for k in key if k.isalpha()]
    if not clean_key:
        return text

    result = []
    key_idx = 0
    k_len = len(clean_key)

    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            shift = clean_key[key_idx % k_len]
            if decode:
                shift = -shift
            result.append(chr((ord(ch) - base + shift) % 26 + base))
            key_idx += 1
        else:
            result.append(ch)
    return "".join(result)


def cipher_rail_fence(text: str, rails: int = 3, decode: bool = False) -> str:
    """Rail fence zigzag transposition cipher."""
    if rails <= 1 or len(text) <= rails:
        return text

    if not decode:
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for ch in text:
            fence[rail].append(ch)
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        return "".join("".join(row) for row in fence)
    else:
        # Determine matrix positions
        pattern = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for _ in range(len(text)):
            pattern[rail].append(None)
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction

        # Fill with cipher characters
        idx = 0
        for r in range(rails):
            for c in range(len(pattern[r])):
                if idx < len(text):
                    pattern[r][c] = text[idx]
                    idx += 1

        # Read zigzag
        result = []
        rail = 0
        direction = 1
        col_indices = [0] * rails
        for _ in range(len(text)):
            result.append(pattern[rail][col_indices[rail]])
            col_indices[rail] += 1
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        return "".join(result)


def cipher_columnar(text: str, key: str, decode: bool = False) -> str:
    """Columnar transposition cipher."""
    if not key or len(key) <= 1:
        return text
    k_len = len(key)
    # Key order based on alphabetical sort of key chars
    sorted_key = sorted(list(enumerate(key)), key=lambda x: x[1])
    col_order = [x[0] for x in sorted_key]

    if not decode:
        # Pad text to multiple of k_len
        pad_len = (k_len - (len(text) % k_len)) % k_len
        padded = text + (" " * pad_len)
        num_rows = len(padded) // k_len

        cols = [""] * k_len
        for i, ch in enumerate(padded):
            cols[i % k_len] += ch

        return "".join(cols[c] for c in col_order)
    else:
        num_rows = len(text) // k_len
        if len(text) % k_len != 0:
            num_rows += 1
        # Reconstruct columns
        col_lengths = [len(text) // k_len] * k_len
        for i in range(len(text) % k_len):
            col_lengths[col_order[i]] += 1

        cols = {}
        idx = 0
        for c in col_order:
            col_len = col_lengths[c]
            cols[c] = text[idx:idx + col_len]
            idx += col_len

        result = []
        for r in range(num_rows):
            for c in range(k_len):
                if r < len(cols[c]):
                    result.append(cols[c][r])
        return "".join(result).rstrip()


def cipher_book_encode(text: str, book_text: str) -> str:
    """Encodes plaintext into word coordinates referencing book_text (line.word)."""
    book_lines = book_text.splitlines()
    word_map = {}
    for l_idx, line in enumerate(book_lines, start=1):
        words = [w.strip() for w in re.findall(r"\b\w+\b", line)]
        for w_idx, word in enumerate(words, start=1):
            w_norm = word.lower()
            if w_norm not in word_map:
                word_map[w_norm] = []
            word_map[w_norm].append(f"{l_idx}.{w_idx}")

    target_words = [w.strip() for w in re.findall(r"\b\w+\b", text)]
    encoded_coords = []
    for tw in target_words:
        tw_norm = tw.lower()
        if tw_norm in word_map:
            coords = word_map[tw_norm][0]
            encoded_coords.append(coords)
        else:
            encoded_coords.append(f"[{tw}]")
    return " ".join(encoded_coords)


def cipher_book_decode(cipher_coords: str, book_text: str) -> str:
    """Decodes coordinate string into plaintext using reference book_text."""
    book_lines = book_text.splitlines()
    line_words = {}
    for l_idx, line in enumerate(book_lines, start=1):
        line_words[l_idx] = [w.strip() for w in re.findall(r"\b\w+\b", line)]

    tokens = cipher_coords.split()
    decoded_words = []
    for token in tokens:
        if token.startswith("[") and token.endswith("]"):
            decoded_words.append(token[1:-1])
        elif "." in token:
            parts = token.split(".", 1)
            try:
                l_num = int(parts[0])
                w_num = int(parts[1])
                words_on_line = line_words.get(l_num, [])
                if 1 <= w_num <= len(words_on_line):
                    decoded_words.append(words_on_line[w_num - 1])
                else:
                    decoded_words.append("?")
            except ValueError:
                decoded_words.append(token)
        else:
            decoded_words.append(token)
    return " ".join(decoded_words)


def text_to_runes(text: str, alphabet: str = "futhark") -> str:
    """Translates latin text to phonetic rune characters."""
    rune_map = ANGLO_SAXON_FUTHORC if alphabet.lower() in ("futhorc", "anglo-saxon") else ELDER_FUTHARK
    text_lower = text.lower()
    
    result = []
    i = 0
    n = len(text_lower)
    while i < n:
        # Check two-character digraphs first (e.g. th, ng, ae, eo)
        if i + 1 < n and text_lower[i:i+2] in rune_map:
            result.append(rune_map[text_lower[i:i+2]])
            i += 2
        elif text_lower[i] in rune_map:
            result.append(rune_map[text_lower[i]])
            i += 1
        else:
            result.append(text_lower[i])
            i += 1
    return "".join(result)


def generate_rune_svg(rune_text: str, title: str = "Arcane Inscription") -> str:
    """Generates standalone SVG vector card for an in-world rune inscription."""
    escaped_runes = html.escape(rune_text)
    escaped_title = html.escape(title)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" width="100%" height="200" style="background:#0f172a; border-radius:8px; border:1px solid #334155;">
  <style>
    .title {{ font-family: 'Cinzel', 'Trajan Pro', Georgia, serif; font-size: 14px; fill: #94a3b8; letter-spacing: 2px; text-anchor: middle; }}
    .runes {{ font-family: 'Segoe UI Historic', 'Noto Sans Runic', sans-serif; font-size: 38px; fill: #38bdf8; text-anchor: middle; letter-spacing: 6px; filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.6)); }}
    .border-glow {{ stroke: #38bdf8; stroke-width: 1.5; fill: none; opacity: 0.4; }}
  </style>
  <rect x="20" y="20" width="760" height="160" rx="6" class="border-glow" />
  <text x="400" y="55" class="title">{escaped_title.upper()}</text>
  <text x="400" y="125" class="runes">{escaped_runes}</text>
</svg>"""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Inscriptions, Ciphers & Phonetic Rune Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Cipher subcommands")

    # 1. encode
    p_enc = subparsers.add_parser("encode", help="Encode plaintext into cipher")
    p_enc.add_argument("text", help="Plaintext to encode")
    p_enc.add_argument("--type", choices=["caesar", "atbash", "vigenere", "railfence", "columnar", "book"], default="caesar", help="Cipher algorithm")
    p_enc.add_argument("--shift", type=int, default=3, help="Shift for Caesar cipher (default 3)")
    p_enc.add_argument("--key", default="ARCANA", help="Key for Vigenère / Columnar ciphers (or reference text for Book cipher)")
    p_enc.add_argument("--book-file", help="Path to reference book/lore text file for Book cipher")
    p_enc.add_argument("--rails", type=int, default=3, help="Rails for Rail Fence cipher")
    p_enc.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 2. decode
    p_dec = subparsers.add_parser("decode", help="Decode ciphertext into plaintext")
    p_dec.add_argument("ciphertext", help="Ciphertext to decode")
    p_dec.add_argument("--type", choices=["caesar", "atbash", "vigenere", "railfence", "columnar", "book"], default="caesar", help="Cipher algorithm")
    p_dec.add_argument("--shift", type=int, default=3, help="Shift for Caesar cipher (default 3)")
    p_dec.add_argument("--key", default="ARCANA", help="Key for Vigenère / Columnar ciphers (or reference text for Book cipher)")
    p_dec.add_argument("--book-file", help="Path to reference book/lore text file for Book cipher")
    p_dec.add_argument("--rails", type=int, default=3, help="Rails for Rail Fence cipher")
    p_dec.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 3. runes
    p_runes = subparsers.add_parser("runes", help="Translate plaintext to phonetic runes and SVG")
    p_runes.add_argument("text", help="Text to translate to runes")
    p_runes.add_argument("--alphabet", choices=["futhark", "futhorc"], default="futhark", help="Rune alphabet")
    p_runes.add_argument("--svg", help="Export vector SVG inscription card to file")
    p_runes.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "encode":
        ctype = args.type
        txt = args.text
        if ctype == "caesar":
            encoded = cipher_caesar(txt, shift=args.shift, decode=False)
        elif ctype == "atbash":
            encoded = cipher_atbash(txt)
        elif ctype == "vigenere":
            encoded = cipher_vigenere(txt, key=args.key, decode=False)
        elif ctype == "railfence":
            encoded = cipher_rail_fence(txt, rails=args.rails, decode=False)
        elif ctype == "columnar":
            encoded = cipher_columnar(txt, key=args.key, decode=False)
        elif ctype == "book":
            book_txt = Path(args.book_file).read_text(encoding="utf-8", errors="ignore") if getattr(args, "book_file", None) else args.key
            encoded = cipher_book_encode(txt, book_txt)
        else:
            encoded = txt

        if args.json:
            print(json.dumps({"cipher": ctype, "plaintext": txt, "ciphertext": encoded}, indent=2))
        else:
            print(f"\n\033[1;36m=== In-World Cipher Encoding ({ctype.upper()}) ===\033[0m")
            print(f"Plaintext : {txt}")
            print(f"Ciphertext: \033[1;32m{encoded}\033[0m\n")
        sys.exit(0)

    elif args.subcommand == "decode":
        ctype = args.type
        ctxt = args.ciphertext
        if ctype == "caesar":
            decoded = cipher_caesar(ctxt, shift=args.shift, decode=True)
        elif ctype == "atbash":
            decoded = cipher_atbash(ctxt)
        elif ctype == "vigenere":
            decoded = cipher_vigenere(ctxt, key=args.key, decode=True)
        elif ctype == "railfence":
            decoded = cipher_rail_fence(ctxt, rails=args.rails, decode=True)
        elif ctype == "columnar":
            decoded = cipher_columnar(ctxt, key=args.key, decode=True)
        elif ctype == "book":
            book_txt = Path(args.book_file).read_text(encoding="utf-8", errors="ignore") if getattr(args, "book_file", None) else args.key
            decoded = cipher_book_decode(ctxt, book_txt)
        else:
            decoded = ctxt

        if args.json:
            print(json.dumps({"cipher": ctype, "ciphertext": ctxt, "plaintext": decoded}, indent=2))
        else:
            print(f"\n\033[1;36m=== In-World Cipher Decoding ({ctype.upper()}) ===\033[0m")
            print(f"Ciphertext: {ctxt}")
            print(f"Plaintext : \033[1;32m{decoded}\033[0m\n")
        sys.exit(0)

    elif args.subcommand == "runes":
        txt = args.text
        runes = text_to_runes(txt, alphabet=args.alphabet)

        if args.json:
            print(json.dumps({"alphabet": args.alphabet, "text": txt, "runes": runes}, indent=2))
        else:
            print(f"\n\033[1;35m=== Phonetic Rune Translation ({args.alphabet.upper()}) ===\033[0m")
            print(f"Text : {txt}")
            print(f"Runes: \033[1;36m{runes}\033[0m\n")

        if args.svg:
            svg_content = generate_rune_svg(runes, title=txt)
            atomic_write(Path(args.svg), svg_content)
            print(f"Rune SVG inscription written to: {args.svg}")
        sys.exit(0)


if __name__ == "__main__":
    main()
