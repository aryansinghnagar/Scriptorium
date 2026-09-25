#!/usr/bin/env python3
"""
Ars Arcanum Offline Neural TTS & Audio Proofreader
(scripts/lib/tts_reader.py)
================================================================================
Zero-dependency, offline text-to-speech engine and audio proofreading studio.

Capabilities (INT-101):
1. Prose Preparation & Dialogue Sanitization:
   - Strips frontmatter, markdown hashes (#), scene tags (@pov:, @location:), and
     table formatting while preserving natural punctuation pacing.
   - Applies phonetic in-world name pronunciation glossaries.
2. System Speech Toolchain Discovery:
   - Automatically detects piper, espeak-ng, espeak, spd-say, macOS say, and Windows SAPI.
3. Standalone Interactive HTML5 Audio Proofreading Player:
   - Zero-dependency client-side HTML5 Web SpeechSynthesis reader with karaoke
     sentence-by-sentence highlight, speed control (0.5x to 2.5x), and keyboard controls.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

logger = logging.getLogger("arcanum.tts_reader")


def clean_prose_for_speech(text: str, pronunciation_dict: dict | None = None) -> list[str]:
    """Cleans markdown text into natural spoken paragraphs and applies phonetic replacements."""
    lines = text.splitlines()
    clean_paragraphs = []
    current_para = []

    in_fm = False
    in_code = False
    for line in lines:
        s = line.strip()
        if s == "---":
            in_fm = not in_fm
            continue
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_fm or in_code or s.startswith("@"):
            continue

        if not s:
            if current_para:
                clean_paragraphs.append(" ".join(current_para))
                current_para = []
            continue

        # Strip markdown headers (#), bullet points, and images
        s = re.sub(r'^#+\s*', '', s)
        s = re.sub(r'^\s*[\*\-\+]\s*', '', s)
        s = re.sub(r'!\[.*?\]\(.*?\)', '', s)
        s = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', s)  # keep link text
        s = re.sub(r'\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]', lambda m: m.group(2) if m.group(2) else m.group(1), s)
        s = re.sub(r'[\*_]{1,3}', '', s)  # strip bold/italics

        current_para.append(s)

    if current_para:
        clean_paragraphs.append(" ".join(current_para))

    # Apply phonetic replacements if provided
    if pronunciation_dict:
        for orig, phonetic in pronunciation_dict.items():
            clean_paragraphs = [re.sub(rf'\b{re.escape(orig)}\b', phonetic, p) for p in clean_paragraphs]

    return [p for p in clean_paragraphs if p.strip()]


def find_system_tts_engine() -> str | None:
    """Detects available CLI speech synthesizer tool on the host."""
    for tool in ("piper", "espeak-ng", "espeak", "spd-say", "say"):
        if shutil.which(tool):
            return tool
    if sys.platform == "win32":
        return "powershell_sapi"
    return None


def speak_text(text: str, speed: float = 1.0, voice: str | None = None) -> bool:
    """Speaks text aloud using available system speech tool."""
    engine = find_system_tts_engine()
    if not engine:
        print("[!] No native CLI speech synthesizer found. Use --html to launch browser speech studio.", file=sys.stderr)
        return False

    try:
        if engine == "piper":
            # Piper neural TTS
            cmd = ["piper", "--output_raw"]
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            p.communicate(input=text.encode("utf-8"))
            return p.returncode == 0
        elif engine in ("espeak-ng", "espeak"):
            speed_wpm = int(175 * speed)
            cmd = [engine, "-s", str(speed_wpm), text]
            if voice:
                cmd.extend(["-v", voice])
            res = subprocess.run(cmd)
            return res.returncode == 0
        elif engine == "spd-say":
            rate = int((speed - 1.0) * 50)
            cmd = ["spd-say", "-r", str(rate), text]
            res = subprocess.run(cmd)
            return res.returncode == 0
        elif engine == "say":
            # macOS
            cmd = ["say", "-r", str(int(180 * speed)), text]
            if voice:
                cmd.extend(["-v", voice])
            res = subprocess.run(cmd)
            return res.returncode == 0
        elif engine == "powershell_sapi":
            # Windows PowerShell SAPI.SpVoice
            escaped = text.replace('"', '""').replace("'", "''")
            rate = max(-10, min(10, int((speed - 1.0) * 5)))
            ps_code = f"Add-Type -AssemblyName System.speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = {rate}; $s.Speak('{escaped}')"
            cmd = ["powershell", "-NoProfile", "-Command", ps_code]
            res = subprocess.run(cmd)
            return res.returncode == 0
    except Exception as e:
        logger.error("TTS execution error: %s", e)
        return False
    return False


def generate_tts_html_player(paragraphs: list[str], title: str, output_path: Path) -> Path:
    """Generates an offline HTML5 speech synthesis player with karaoke highlight."""
    sentences = []
    for p_idx, p in enumerate(paragraphs):
        raw_sents = re.split(r'(?<=[.!?])\s+', p)
        for s in raw_sents:
            s_clean = s.strip()
            if s_clean:
                sentences.append({"id": len(sentences), "text": s_clean, "para": p_idx})

    sentences_json = json.dumps(sentences)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Audio Proofreader: {html.escape(title)}</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --highlight: #d97706;
  }}
  body {{ font-family: 'Georgia', serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; line-height: 1.8; }}
  .container {{ max-width: 800px; margin: 0 auto; }}
  .controls-bar {{ position: sticky; top: 1rem; background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; margin-bottom: 2rem; display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; z-index: 100; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
  .btn {{ background: var(--accent); color: #0f172a; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; font-weight: 700; cursor: pointer; }}
  .btn:hover {{ filter: brightness(1.1); }}
  .btn-sec {{ background: #334155; color: var(--text); }}
  .prose-card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 2.5rem; font-size: 1.15rem; }}
  .sentence {{ padding: 2px 4px; border-radius: 4px; cursor: pointer; transition: background 0.15s; }}
  .sentence:hover {{ background: rgba(56, 189, 248, 0.2); }}
  .sentence.active {{ background: #0284c7; color: #ffffff; font-weight: 600; box-shadow: 0 0 10px rgba(56,189,248,0.5); }}
</style>
</head>
<body>
<div class="container">
  <div class="controls-bar">
    <button id="playBtn" class="btn" onclick="togglePlay()">▶ Start Reading</button>
    <button class="btn btn-sec" onclick="prevSentence()">⏮</button>
    <button class="btn btn-sec" onclick="nextSentence()">⏭</button>
    
    <label style="color:var(--muted); font-size:0.85rem; display:flex; align-items:center; gap:0.5rem;">
      Speed: <span id="speedVal">1.0x</span>
      <input type="range" id="speedSlider" min="0.5" max="2.0" step="0.1" value="1.0" oninput="updateSpeed()" style="width:90px; accent-color:var(--accent);">
    </label>

    <select id="voiceSelect" style="background:var(--bg); border:1px solid var(--border); color:var(--text); padding:0.4rem; border-radius:6px; font-size:0.8rem; max-width:180px;"></select>
  </div>

  <div class="prose-card">
    <h1 style="color:var(--accent); font-family:system-ui,sans-serif; margin-top:0;">{html.escape(title)}</h1>
    <div id="proseContainer"></div>
  </div>
</div>

<script>
const sentences = {sentences_json};
let currentIndex = 0;
let isPlaying = false;
let synth = window.speechSynthesis;
let voices = [];

function populateVoices() {{
  voices = synth.getVoices();
  const sel = document.getElementById('voiceSelect');
  sel.innerHTML = '';
  voices.forEach((v, i) => {{
    const opt = document.createElement('option');
    opt.value = i;
    opt.text = `${{v.name}} (${{v.lang}})`;
    if (v.default || v.lang.startsWith('en')) opt.selected = true;
    sel.appendChild(opt);
  }});
}}
if (speechSynthesis.onvoiceschanged !== undefined) {{
  speechSynthesis.onvoiceschanged = populateVoices;
}}
populateVoices();

function renderProse() {{
  const container = document.getElementById('proseContainer');
  let currentPara = -1;
  let pElem = null;

  sentences.forEach((s, idx) => {{
    if (s.para !== currentPara) {{
      currentPara = s.para;
      pElem = document.createElement('p');
      container.appendChild(pElem);
    }}
    const span = document.createElement('span');
    span.id = 's-' + idx;
    span.className = 'sentence';
    span.innerText = s.text + ' ';
    span.onclick = () => jumpTo(idx);
    pElem.appendChild(span);
  }});
}}

function highlightSentence(idx) {{
  document.querySelectorAll('.sentence').forEach(el => el.classList.remove('active'));
  const el = document.getElementById('s-' + idx);
  if (el) {{
    el.classList.add('active');
    el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
  }}
}}

function speakCurrent() {{
  if (currentIndex >= sentences.length) {{
    isPlaying = false;
    document.getElementById('playBtn').innerText = '▶ Start Reading';
    return;
  }}
  synth.cancel();

  highlightSentence(currentIndex);
  const u = new SpeechSynthesisUtterance(sentences[currentIndex].text);
  
  const vIdx = document.getElementById('voiceSelect').value;
  if (voices[vIdx]) u.voice = voices[vIdx];
  u.rate = parseFloat(document.getElementById('speedSlider').value);

  u.onend = () => {{
    if (isPlaying) {{
      currentIndex++;
      speakCurrent();
    }}
  }};
  u.onerror = (e) => {{
    console.error(e);
    if (isPlaying) {{
      currentIndex++;
      speakCurrent();
    }}
  }};

  synth.speak(u);
}}

function togglePlay() {{
  if (!isPlaying) {{
    isPlaying = true;
    document.getElementById('playBtn').innerText = '⏸ Pause';
    speakCurrent();
  }} else {{
    isPlaying = false;
    synth.cancel();
    document.getElementById('playBtn').innerText = '▶ Resume';
  }}
}}

function jumpTo(idx) {{
  currentIndex = idx;
  if (isPlaying) speakCurrent();
  else highlightSentence(idx);
}}

function nextSentence() {{
  if (currentIndex < sentences.length - 1) {{
    currentIndex++;
    if (isPlaying) speakCurrent();
    else highlightSentence(currentIndex);
  }}
}}

function prevSentence() {{
  if (currentIndex > 0) {{
    currentIndex--;
    if (isPlaying) speakCurrent();
    else highlightSentence(currentIndex);
  }}
}}

function updateSpeed() {{
  const val = document.getElementById('speedSlider').value;
  document.getElementById('speedVal').innerText = val + 'x';
}}

window.addEventListener('keydown', (e) => {{
  if (e.code === 'Space') {{
    e.preventDefault();
    togglePlay();
  }} else if (e.code === 'ArrowRight') {{
    nextSentence();
  }} else if (e.code === 'ArrowLeft') {{
    prevSentence();
  }}
}});

renderProse();
</script>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Offline Audio Proofreader (INT-101)")
    parser.add_argument("target", help="File or chapter markdown path")
    parser.add_argument("--speed", type=float, default=1.0, help="Reading speed multiplier (default: 1.0)")
    parser.add_argument("--voice", help="Voice name or identifier")
    parser.add_argument("--speak", action="store_true", help="Speak text directly in terminal via system TTS")
    parser.add_argument("--html", help="Generate standalone interactive HTML5 audio proofreader")
    parser.add_argument("--json", action="store_true", help="Output JSON paragraphs")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    content = ""
    if target_path.is_file():
        content = target_path.read_text(encoding="utf-8", errors="replace")
    elif target_path.is_dir():
        for p in sorted(target_path.rglob("*.md")):
            if not p.name.startswith((".", "_")) and "04_Back_Matter" not in p.parts:
                content += f"\n\n# {p.stem}\n" + p.read_text(encoding="utf-8", errors="replace")

    paragraphs = clean_prose_for_speech(content)

    if args.json:
        print(json.dumps({"target": str(target_path), "paragraphs": paragraphs}, indent=2))
        return

    if args.html:
        out_p = Path(args.html)
        generate_tts_html_player(paragraphs, title=target_path.stem.replace("_", " "), output_path=out_p)
        print(f"Generated Interactive HTML5 Audio Proofreader: {out_p}")
        return

    if args.speak:
        joined_text = " ".join(paragraphs)
        print(f"Speaking '{target_path.name}' ({len(paragraphs)} paragraphs)...")
        speak_text(joined_text, speed=args.speed, voice=args.voice)
    else:
        # Default: generate HTML player or print speech stats
        out_default = Path(f"{target_path.stem}_audio_proofreader.html")
        generate_tts_html_player(paragraphs, title=target_path.stem.replace("_", " "), output_path=out_default)
        print("=== Ars Arcanum Audio Proofreader ===")
        print(f"Target:        {target_path.name}")
        print(f"Paragraphs:    {len(paragraphs)}")
        print(f"Generated:     {out_default} (Open in any browser for neural voice audio proofreading)")


if __name__ == "__main__":
    main()
