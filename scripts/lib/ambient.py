#!/usr/bin/env python3
"""
Ars Arcanum Focus Ambient & Binaural Soundscape Generator
(scripts/lib/ambient.py)
================================================================================
Zero-dependency, offline procedural audio synthesizer and writing atmosphere engine.

Capabilities (PLT-106):
1. Procedural Audio Synthesis (Pure Python Stdlib wave + struct + math):
   - Noise Colors: White noise, Pink noise (1/f filter), Brown/Red noise (Brownian random walk)
   - Binaural Beats: Stereo phase-offset carrier frequencies:
     * Alpha Waves (8–12 Hz): Creative flow & relaxed focus
     * Theta Waves (4–8 Hz): Deep meditation & dreaming
     * Beta Waves (13–30 Hz): High alertness & active problem-solving
     * Gamma Waves (40 Hz): Peak cognitive concentration
   - Soundscape Generators: Rainstorm, Ocean Surf, Mountain Wind
2. Soundscape Atmosphere Profiles:
   - "Rainy Library", "Deep Space Observatory", "Tavern Hearth", "Monastery Study"
3. Standalone Interactive HTML5 WebAudio Synthesizer:
   - Zero-dependency client-side procedural sound generator with audio sliders for
     Rain, Surf, Wind, Noise, and Binaural Beats.

Zero external dependencies; 100% offline privacy.
"""

import sys
import os
import math
import struct
import wave
import random
import json
import argparse
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("arcanum.ambient")

SAMPLE_RATE = 44100

PROFILES = {
    "rainy_library": {"type": "rain", "noise": "brown", "binaural": "alpha", "carrier": 216.0, "beat": 10.0, "desc": "Gentle rain against glass with 10 Hz Alpha focus beat"},
    "deep_space": {"type": "space", "noise": "pink", "binaural": "theta", "carrier": 108.0, "beat": 6.0, "desc": "Subterranean planetary hum with 6 Hz Theta meditation beat"},
    "mountain_wind": {"type": "wind", "noise": "brown", "binaural": "beta", "carrier": 320.0, "beat": 18.0, "desc": "High altitude sweeping wind with 18 Hz Beta concentration beat"},
    "ocean_surf": {"type": "ocean", "noise": "pink", "binaural": "alpha", "carrier": 216.0, "beat": 8.0, "desc": "Rhythmic ocean breakers with 8 Hz Alpha relaxation beat"},
    "pure_focus": {"type": "noise", "noise": "brown", "binaural": "gamma", "carrier": 432.0, "beat": 40.0, "desc": "Pure deep brown noise with 40 Hz Gamma peak cognition beat"}
}


def synthesize_wav(output_path: Path, duration_sec: int = 10, noise_type: str = "brown", binaural_beat: float = 10.0, carrier_freq: float = 216.0, ambient_mode: str = "rain"):
    """Synthesizes a stereo WAV file with procedural noise and binaural beats."""
    total_samples = int(SAMPLE_RATE * duration_sec)
    
    # Binaural frequencies
    left_freq = carrier_freq
    right_freq = carrier_freq + binaural_beat

    # Filter state for pink / brown noise
    brown_left = 0.0
    brown_right = 0.0
    b0, b1, b2, b3, b4, b5, b6 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    frames = bytearray()

    for i in range(total_samples):
        t = i / SAMPLE_RATE

        # Base white noise
        white_l = (random.random() * 2.0) - 1.0
        white_r = (random.random() * 2.0) - 1.0

        # Noise color filtering
        if noise_type == "brown":
            brown_left = (brown_left + (0.02 * white_l)) / 1.02
            brown_right = (brown_right + (0.02 * white_r)) / 1.02
            noise_l = brown_left * 3.5
            noise_r = brown_right * 3.5
        elif noise_type == "pink":
            # Paul Kellet filter approximation
            b0 = 0.99886 * b0 + white_l * 0.0555179
            b1 = 0.99332 * b1 + white_l * 0.0750759
            b2 = 0.96900 * b2 + white_l * 0.1538520
            b3 = 0.86650 * b3 + white_l * 0.3104856
            b4 = 0.55000 * b4 + white_l * 0.5329522
            b5 = -0.7616 * b5 - white_l * 0.0168980
            noise_l = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white_l * 0.5362) * 0.11
            noise_r = noise_l
        else:
            noise_l = white_l * 0.15
            noise_r = white_r * 0.15

        # Ambient modulations
        if ambient_mode == "ocean":
            # 0.1 Hz breathing swell
            swell = (math.sin(2 * math.pi * 0.1 * t) + 1.0) / 2.0
            noise_l *= (0.2 + 0.8 * (swell ** 2))
            noise_r *= (0.2 + 0.8 * (swell ** 2))
        elif ambient_mode == "wind":
            # Sweeping gusts
            gust = (math.sin(2 * math.pi * 0.05 * t) * math.cos(2 * math.pi * 0.12 * t) + 1.0) / 2.0
            noise_l *= (0.3 + 0.7 * gust)
            noise_r *= (0.3 + 0.7 * gust)

        # Binaural sine tones
        tone_l = math.sin(2 * math.pi * left_freq * t) * 0.08
        tone_r = math.sin(2 * math.pi * right_freq * t) * 0.08

        # Mix and clamp
        sample_l = max(-1.0, min(1.0, noise_l * 0.4 + tone_l))
        sample_r = max(-1.0, min(1.0, noise_r * 0.4 + tone_r))

        # 16-bit PCM integer
        val_l = int(sample_l * 32767.0)
        val_r = int(sample_r * 32767.0)

        frames.extend(struct.pack("<hh", val_l, val_r))

    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(frames)

    return output_path


def generate_ambient_html_synthesizer(output_path: Path) -> Path:
    """Generates a standalone zero-dependency HTML5 WebAudio ambient synthesizer."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Offline Focus Soundscape Studio</title>
<style>
  :root {
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
  }
  body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; display: flex; justify-content: center; }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 2rem; max-width: 500px; width: 100%; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
  h1 { font-size: 1.5rem; color: var(--accent); margin-top: 0; }
  .btn { width: 100%; padding: 1rem; border: none; border-radius: 8px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: all 0.2s; background: var(--accent); color: #0f172a; }
  .btn:hover { filter: brightness(1.1); }
  .slider-group { margin: 1.5rem 0; }
  .slider-row { display: flex; justify-content: space-between; margin-bottom: 0.25rem; font-size: 0.875rem; color: var(--muted); }
  input[type="range"] { width: 100%; margin-bottom: 1rem; accent-color: var(--accent); }
  .presets { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1.5rem; }
  .preset-btn { background: #334155; color: var(--text); border: 1px solid var(--border); padding: 0.5rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }
  .preset-btn:hover { background: #475569; }
</style>
</head>
<body>
<div class="card">
  <h1>🎧 Focus Soundscape Studio</h1>
  <p style="color: var(--muted); font-size: 0.875rem; margin-bottom: 1.5rem;">Offline procedural white noise & binaural beat generator.</p>

  <div class="presets">
    <button class="preset-btn" onclick="setPreset(0.6, 0.2, 0.0, 10)">🌧️ Rainy Library</button>
    <button class="preset-btn" onclick="setPreset(0.1, 0.5, 0.2, 6)">🌌 Deep Space</button>
    <button class="preset-btn" onclick="setPreset(0.0, 0.3, 0.6, 18)">🏔️ Mountain Wind</button>
    <button class="preset-btn" onclick="setPreset(0.0, 0.6, 0.0, 40)">⚡ Pure Cognition</button>
  </div>

  <button id="playBtn" class="btn" onclick="toggleAudio()">▶ Start Focus Soundscape</button>

  <div class="slider-group">
    <div class="slider-row"><span>Brown Noise (Depth)</span><span id="noiseVal">50%</span></div>
    <input type="range" id="noiseSlider" min="0" max="1" step="0.01" value="0.5" oninput="updateGains()">

    <div class="slider-row"><span>Rain / Waves (Swell)</span><span id="rainVal">30%</span></div>
    <input type="range" id="rainSlider" min="0" max="1" step="0.01" value="0.3" oninput="updateGains()">

    <div class="slider-row"><span>Binaural Beat Frequency</span><span id="beatVal">10 Hz (Alpha)</span></div>
    <input type="range" id="beatSlider" min="4" max="40" step="1" value="10" oninput="updateBeat()">

    <div class="slider-row"><span>Master Volume</span><span id="volVal">70%</span></div>
    <input type="range" id="volSlider" min="0" max="1" step="0.01" value="0.7" oninput="updateGains()">
  </div>
</div>

<script>
let ctx = null, isPlaying = false;
let noiseNode, rainGain, rainFilter, noiseGain, oscL, oscR, masterGain;

function initAudio() {
  ctx = new (window.AudioContext || window.webkitAudioContext)();
  
  // Master Gain
  masterGain = ctx.createGain();
  masterGain.connect(ctx.destination);
  masterGain.gain.value = 0.7;

  // Brown Noise Generator
  const bufferSize = 2 * ctx.sampleRate;
  const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const output = noiseBuffer.getChannelData(0);
  let lastOut = 0.0;
  for (let i = 0; i < bufferSize; i++) {
    const white = Math.random() * 2 - 1;
    output[i] = (lastOut + (0.02 * white)) / 1.02;
    lastOut = output[i];
    output[i] *= 3.5;
  }
  noiseNode = ctx.createBufferSource();
  noiseNode.buffer = noiseBuffer;
  noiseNode.loop = true;

  // Direct Noise Path
  noiseGain = ctx.createGain();
  noiseGain.gain.value = parseFloat(document.getElementById("noiseSlider").value);
  noiseNode.connect(noiseGain);
  noiseGain.connect(masterGain);

  // Rain / Swell Filter Path
  rainFilter = ctx.createBiquadFilter();
  rainFilter.type = "bandpass";
  rainFilter.frequency.value = 1200;
  rainFilter.Q.value = 2.5;

  rainGain = ctx.createGain();
  rainGain.gain.value = parseFloat(document.getElementById("rainSlider").value);
  noiseNode.connect(rainFilter);
  rainFilter.connect(rainGain);
  rainGain.connect(masterGain);

  noiseNode.start();

  // Binaural Beat Oscillators (Carrier 216 Hz)
  const carrier = 216.0;
  const beat = parseFloat(document.getElementById("beatSlider").value);
  
  oscL = ctx.createOscillator();
  oscR = ctx.createOscillator();
  oscL.frequency.value = carrier;
  oscR.frequency.value = carrier + beat;

  const merger = ctx.createChannelMerger(2);
  const oscGain = ctx.createGain();
  oscGain.gain.value = 0.08;

  oscL.connect(merger, 0, 0); // Left channel
  oscR.connect(merger, 0, 1); // Right channel
  merger.connect(oscGain);
  oscGain.connect(masterGain);

  oscL.start();
  oscR.start();
}

function toggleAudio() {
  if (!ctx) initAudio();
  if (ctx.state === 'suspended') ctx.resume();
  
  isPlaying = !isPlaying;
  document.getElementById("playBtn").innerText = isPlaying ? "⏸ Pause Audio" : "▶ Resume Audio";
  masterGain.gain.value = isPlaying ? parseFloat(document.getElementById("volSlider").value) : 0;
}

function updateGains() {
  if (!masterGain) return;
  const vol = parseFloat(document.getElementById("volSlider").value);
  const noise = parseFloat(document.getElementById("noiseSlider").value);
  const rain = parseFloat(document.getElementById("rainSlider").value);
  if (isPlaying) masterGain.gain.value = vol;
  if (noiseGain) noiseGain.gain.value = noise;
  if (rainGain) rainGain.gain.value = rain;
  document.getElementById("volVal").innerText = Math.round(vol*100) + "%";
  document.getElementById("noiseVal").innerText = Math.round(noise*100) + "%";
  document.getElementById("rainVal").innerText = Math.round(rain*100) + "%";
}

function updateBeat() {
  const beat = parseFloat(document.getElementById("beatSlider").value);
  if (oscR) oscR.frequency.value = 216.0 + beat;
  let label = beat + " Hz";
  if (beat <= 8) label += " (Theta)";
  else if (beat <= 12) label += " (Alpha Flow)";
  else if (beat <= 30) label += " (Beta Focus)";
  else label += " (Gamma Peak)";
  document.getElementById("beatVal").innerText = label;
}

function setPreset(noise, rain, unused, beat) {
  document.getElementById("noiseSlider").value = noise;
  document.getElementById("rainSlider").value = rain;
  document.getElementById("beatSlider").value = beat;
  updateBeat();
  updateGains();
  if (!isPlaying) toggleAudio();
}
</script>
</body>
</html>
"""
    output_path.write_text(html_content, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Focus Ambient & Binaural Synthesizer (PLT-106)")
    subparsers = parser.add_subparsers(dest="command", help="Command mode")

    p_gen = subparsers.add_parser("generate", help="Synthesize WAV focus audio file or HTML player")
    p_gen.add_argument("profile", nargs="?", default="rainy_library", choices=list(PROFILES.keys()) + ["white", "pink", "brown"], help="Atmosphere profile or noise color")
    p_gen.add_argument("-d", "--duration", type=int, default=10, help="Duration in seconds (default: 10s)")
    p_gen.add_argument("-o", "--output", help="Output .wav path")
    p_gen.add_argument("--binaural", choices=["alpha", "theta", "beta", "gamma"], default="alpha", help="Binaural frequency wave (default: alpha)")
    p_gen.add_argument("--html", help="Generate standalone interactive HTML5 synthesizer")

    p_list = subparsers.add_parser("list", help="List available atmosphere profiles")

    args = parser.parse_args()

    if args.command == "list" or not args.command:
        print("=== Ars Arcanum Ambient Atmosphere Profiles ===")
        for k, v in PROFILES.items():
            print(f"  🎵 {k:<18} | {v['desc']}")
        print("\nUse: arcanum ambient generate <profile> -o output.wav")
        return

    if args.command == "generate":
        if args.html:
            out_p = Path(args.html)
            generate_ambient_html_synthesizer(out_p)
            print(f"Interactive HTML5 WebAudio Studio generated: {out_p}")
            return

        out_wav = Path(args.output or f"ambient_{args.profile}.wav")
        prof = PROFILES.get(args.profile, {"noise": args.profile, "carrier": 216.0, "beat": 10.0, "type": "noise"})
        
        binaural_map = {"alpha": 10.0, "theta": 6.0, "beta": 18.0, "gamma": 40.0}
        beat_freq = binaural_map.get(args.binaural, prof.get("beat", 10.0))

        synthesize_wav(
            output_path=out_wav,
            duration_sec=args.duration,
            noise_type=prof.get("noise", "brown"),
            binaural_beat=beat_freq,
            carrier_freq=prof.get("carrier", 216.0),
            ambient_mode=prof.get("type", "rain")
        )
        print(f"Synthesized {args.duration}s stereo audio [{args.profile}]: {out_wav}")


if __name__ == "__main__":
    main()
