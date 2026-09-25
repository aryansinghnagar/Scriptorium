# Ars Arcanum — In-World Ciphers & Phonetic Rune Engine Guide
> **Engine**: `scripts/lib/cipher.py` | **CLI**: `arcanum cipher`

---

## 1. Overview & Purpose

The **In-World Ciphers & Phonetic Rune Engine** equips authors and narrative designers with offline cryptographic transformations and arcane inscription generators. It creates in-universe coded missives, secret faction cyphers, temple riddles, and authentic phonetic runic carvings (Elder Futhark, Anglo-Saxon Futhorc) with standalone SVG vector export.

### Core Capabilities
- **Classical Monoalphabetic Ciphers**: Caesar / ROT-N substitution and Atbash reverse alphabet mapping.
- **Polyalphabetic & Transposition Ciphers**: Vigenère keyed substitution, Rail Fence zigzag transposition, and Columnar matrix transposition.
- **Historical Book Ciphers**: Coordinates `line.word` referencing in-world manuscripts, holy scriptures, or lore documents.
- **Phonetic Rune Translation**: Context-aware transliteration of latin text into historic Germanic runes with digraph recognition (`th`, `ng`, `ae`, `eo`).
- **Vector Inscription Cards**: Generates self-contained, publication-ready SVG artifact cards.

---

## 2. Supported Ciphers & Algorithms

| Cipher Type | Key / Parameter | Description |
| :--- | :--- | :--- |
| **Caesar / ROT-N** | `--shift <int>` | Rotates letters by $N$ positions while preserving casing and punctuation. |
| **Atbash** | *None* | Symmetric mirror cipher ($A \leftrightarrow Z, B \leftrightarrow Y$). |
| **Vigenère** | `--key <word>` | Polyalphabetic stream cipher keyed by a lore phrase or faction passphrase. |
| **Rail Fence** | `--rails <int>` | Transposition cipher writing text along a zigzag pattern across $N$ rails. |
| **Columnar** | `--key <word>` | Permutation transposition rearranging columns based on key alphabetical order. |
| **Book Cipher** | `--book-file <path>` | Encodes plaintext into `line.word` numerical coordinates from a target text. |
| **Phonetic Runes** | `--alphabet futhark\|futhorc` | Phonetic transcription into Elder Futhark or Anglo-Saxon Futhorc runes. |

---

## 3. CLI Command Reference

### Encoding Plaintext into In-World Cipher
```bash
# Caesar Cipher (ROT-7)
arcanum cipher encode "The Dragon Awakens at Midnight" --type caesar --shift 7

# Vigenère Cipher with Secret Key
arcanum cipher encode "DEFEND THE CITADEL" --type vigenere --key "MITHRIL"

# Rail Fence Transposition
arcanum cipher encode "ATTACK AT DAWN ON THE NORTH WALL" --type railfence --rails 4

# Book Cipher using World Lore Book
arcanum cipher encode "ancients guarded the hidden vault" --type book --book-file World/Cosmology/Old_Scripture.md
```

### Decoding In-World Cipher
```bash
# Decode Vigenère Cipher
arcanum cipher decode "PMLMVL BPA KPBILMT" --type vigenere --key "MITHRIL"
```

### Generating Phonetic Runes & SVG Inscription Cards
```bash
# Transliterate to Elder Futhark
arcanum cipher runes "Thor and Odin" --alphabet futhark

# Export vector SVG graphic card
arcanum cipher runes "Oath of the Iron Vanguard" --alphabet futhorc --svg exports/iron_oath.svg
```

---

## 4. Architectural Invariants

- **Zero External Dependencies**: Pure Python standard library (`html`, `json`, `re`, `pathlib`).
- **Atomic Writing**: SVG artifacts written via `atomic_write()` from `lib._bootstrap.py`.
- **Offline & Deterministic**: Zero network telemetry; identical plaintext, keys, and seeds produce reproducible ciphertexts.
