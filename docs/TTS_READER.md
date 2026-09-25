# Offline Neural TTS & Audio Proofreader
> **Ars Arcanum Module**: `scripts/lib/tts_reader.py` | **CLI**: `arcanum tts` (alias: `proofread-audio`)

---

## 1. Overview & Craft Philosophy

Listening to a manuscript spoken aloud is one of the most effective techniques for detecting prose rhythm defects, awkward sentence phrasing, unintentional rhyme, repeated words, and dialogue cadence issues.

**Ars Arcanum's Offline Neural TTS & Audio Proofreader** provides a 100% offline, zero-dependency audio proofreading workstation:

- **Prose Sanitization**: Automatically strips YAML frontmatter, markdown header syntax, inline `@pov:`/`@location:` tags, and wikilink brackets `[[Target|Alias]]` to ensure seamless auditory continuity.
- **Phonetic Pronunciation Dictionary**: Replaces fantasy names, invented languages, and complex terms with phonetic guides (e.g. `Caelum` $\to$ `KAY-lum`).
- **Interactive HTML5 Speech Studio**: Generates a standalone, CSP-compliant HTML player utilizing the standard Web SpeechSynthesis API with real-time sentence-by-sentence karaoke highlighting, playback speed controls ($0.5\times$ to $2.5\times$), and keyboard shortcuts.
- **Native Host Toolchain Integration**: Discovers and orchestrates offline host synthesizers including `piper`, `espeak-ng`, `espeak`, `spd-say`, macOS `say`, and Windows SAPI.

---

## 2. CLI Usage Reference

### 2.1 Generating Interactive Audio Reader
```bash
# Generate standalone offline HTML5 karaoke audio proofreader
arcanum tts ~/Manuscripts/Novel/Book-01/Draft-01/01_Chapter.md --html dist/chapter1_audio.html

# Proofread an entire chapter using host speech synthesizer
arcanum tts ~/Manuscripts/Novel/Book-01/Draft-01/01_Chapter.md --speed 1.2

# Export cleaned spoken paragraphs as JSON
arcanum tts ~/Manuscripts/Novel/Book-01/Draft-01/01_Chapter.md --json
```

### 2.2 CLI Command Options

| Flag | Parameter | Default | Description |
| :--- | :--- | :--- | :--- |
| `--html` | `FILE` | `None` | Compile standalone interactive HTML5 audio proofreader. |
| `--speed` | `FLOAT` | `1.0` | Speech playback rate multiplier ($0.5$ to $2.5$). |
| `--voice` | `STRING` | `None` | Voice identifier or language model name. |
| `--json` | | `false` | Output cleaned paragraphs array as JSON to stdout. |
| `--dict` | `PATH` | `None` | Path to JSON pronunciation dictionary. |

---

## 3. Phonetic Pronunciation Dictionaries

To ensure consistent spoken names for speculative fiction entities, create a JSON pronunciation dictionary:

```json
{
  "Caelum": "KAY-lum",
  "Xylar": "ZY-lar",
  "Aeloria": "ay-LOR-ee-uh",
  "Aether": "EE-ther",
  "Mirella": "mi-REL-uh"
}
```

Pass the dictionary during generation:
```bash
arcanum tts Chapter_01.md --dict configs/pronunciations.json --html dist/player.html
```

---

## 4. Standalone HTML5 Audio Reader

The generated HTML5 player runs in any modern browser without network connectivity:

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';">
```

### Keyboard Shortcuts
- **Space**: Play / Pause toggle.
- **Left / Right Arrow**: Skip to previous / next sentence.
- **Up / Down Arrow**: Increase / decrease speech rate ($+0.1\times$).
- **R**: Restart playback from beginning.

---

## 5. Architectural Invariants

- **Zero-Pip Guarantee**: Standard library Python (`argparse`, `html`, `json`, `subprocess`, `re`, `shutil`).
- **Deterministic Audio Sanitization**: Dialogue punctuation (em-dashes, ellipses) translated into natural auditory pauses.
- **Offline Security**: Strict `default-src 'none'` Content Security Policy.
