# Typography & Font Guide for Fiction Book Typesetting

Clean typography turns a raw manuscript into a professional, immersive reading experience. Typst and Pandoc utilize system-installed OpenType (`.otf`) and TrueType (`.ttf`) fonts.

---

## 1. Top Recommended Free & Open-Source Book Typefaces

| Font Family | Genre / Style | Typographic Characteristics | Debian/Mint Package |
| :--- | :--- | :--- | :--- |
| **Linux Libertine / Libertinus Serif** | Universal Fiction & Non-Fiction | Classical proportions, beautiful true italics, rich ligatures, excellent x-height. | `fonts-linuxlibertine` / `fonts-libertinus` |
| **EB Garamond** | Literary & Historical Fiction | Faithful revival of Claude Garamont's 1592 specimen. Timeless, elegant, soft humanist serifs. | `fonts-ebgaramond` |
| **Alegreya** | Fantasy, Adventure, Long-form | Dynamic rhythm designed specifically for long literature sessions. High legibility. | `fonts-alegreya` |
| **Cormorant Garamond** | Epic Fantasy / Historical / Poetry | High contrast, dramatic display titles, graceful swashes. | Font download (Google Fonts / GitHub) |
| **Bitter** | Modern Contemporary / Urban Fantasy | Slab-serif with robust structure designed for comfortable reading across screen and print. | `fonts-bitter` |
| **Charis SIL / Gentium Book Plus** | Linguistics / Conlang / Worldbuilding | Comprehensive Unicode support for International Phonetic Alphabet (IPA) and diacritics. | `fonts-sil-charis` / `fonts-sil-gentiumplus` |

---

## 2. Quick Font Installation on Linux

To install all standard high-quality book fonts in one command:
```bash
sudo apt update
sudo apt install -y \
  fonts-linuxlibertine \
  fonts-ebgaramond \
  fonts-alegreya \
  fonts-sil-charis \
  fonts-sil-gentiumplus \
  fonts-bitter \
  fonts-cmu
```

### Adding Custom Fonts (`.otf` / `.ttf`)
1. Create user font directory:
   ```bash
   mkdir -p ~/.local/share/fonts
   ```
2. Copy your font files into `~/.local/share/fonts/`.
3. Refresh the Linux font cache:
   ```bash
   fc-cache -f -v
   ```
4. Verify Typst detects the font:
   ```bash
   typst fonts | grep -i "Garamond"
   ```

---

## 3. Typst Typographic Standards for Novels
- **Standard Novel Trim Sizes**:
  - `5.5in x 8.5in` (Trade Paperback)
  - `6in x 9in` (Standard US Trade)
  - `5in x 8in` (Mass Market / Pocket)
- **Body Font Size**: 10.5pt to 11pt with `14pt` to `15pt` line leading.
- **First-Line Indent**: `1.25em` to `1.5em` (with `0pt` paragraph spacing).
- **First Paragraph of Chapter / Section Break**: `0pt` indent (flush left), optionally featuring a Drop Cap.
- **Margins**: Alternating inner (gutter) `0.75in` - `0.85in` and outer `0.65in` - `0.75in`.
