# AMBIENT — Focus Ambient & Binaural Soundscape Generator

> **Module**: `scripts/lib/ambient.py`  
> **CLI Command**: `arcanum ambient`  
> **Purpose**: Synthesizes stereo procedural soundscapes and binaural beats to aid focus during worldbuilding sessions, and generates standalone HTML5 WebAudio synthesizers for in-browser playback.

---

## Table of Contents

1. [Overview](#overview)
2. [CLI Usage](#cli-usage)
3. [Key API Reference](#key-api-reference)
4. [Built-In Profiles](#built-in-profiles)
5. [Noise Color Reference](#noise-color-reference)
6. [Binaural Beat Brain-Wave Types](#binaural-beat-brain-wave-types)
7. [Ambient Modes](#ambient-modes)
8. [Diagnostic Codes](#diagnostic-codes)
9. [Behavioral Notes](#behavioral-notes)
10. [Example Workflow](#example-workflow)

---

## Overview

The `ambient` module is the Ars Arcanum **soundscape engine**. It serves two distinct output modes:

| Mode | Description |
|---|---|
| **WAV synthesis** | Renders a `.wav` file encoded at 44100 Hz, 16-bit stereo with procedural noise and binaural-beat panning |
| **HTML synthesizer** | Generates a zero-dependency, standalone HTML5 file driven by the WebAudio API — no server required |

The module is particularly useful for:

- **Writing sessions** — long-duration ambient tracks customized to your cognitive goal (deep focus, creative brainstorm, meditation).
- **Worldbuilding presentations** — distributing the HTML synthesizer alongside a world document so readers can immerse themselves in the audio environment.
- **Playtesting tabletop sessions** — looping environment audio appropriate to a scene's setting.

The WAV synthesizer runs entirely offline using NumPy and SciPy; the HTML synthesizer is a self-contained document requiring no Python runtime for playback.

---

## CLI Usage

```
arcanum ambient [OPTIONS]
```

### Options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--profile PROFILE` | string | *(none)* | Load a named preset from `PROFILES` (overrides individual flags) |
| `--duration SEC` | int | `10` | Duration of the synthesized WAV in seconds |
| `--noise TYPE` | choice | `brown` | Noise colour: `white`, `pink`, or `brown` |
| `--beat HZ` | float | `10.0` | Binaural beat frequency in Hz |
| `--carrier HZ` | float | `216.0` | Carrier sine-wave frequency in Hz (base tone) |
| `--mode MODE` | choice | `rain` | Ambient environment mode (see [Ambient Modes](#ambient-modes)) |
| `--html` | flag | off | Emit a standalone HTML5 synthesizer instead of a WAV file |
| `-o OUTPUT` | path | `ambient_out.wav` | Destination file path |

### Quick Examples

```powershell
# Render a 60-second rainy-library WAV
arcanum ambient --profile rainy_library --duration 60 -o session.wav

# Render a deep-space HTML synthesizer for browser playback
arcanum ambient --profile deep_space --html -o deep_space.html

# Custom: pink noise, 6 Hz theta beat, 432 Hz carrier, 120 seconds
arcanum ambient --noise pink --beat 6.0 --carrier 432.0 --duration 120 -o theta_flow.wav

# Ocean mode, 40 Hz gamma beat for intensive editing
arcanum ambient --mode ocean --beat 40.0 --duration 180 -o gamma_ocean.wav
```

> [!TIP]
> Profiles are the fastest way to get started. Use `--profile` first; override individual knobs only when fine-tuning.

---

## Key API Reference

### `synthesize_wav`

```python
synthesize_wav(
    output_path: str | Path,
    duration_sec: int = 10,
    noise_type: str = "brown",
    binaural_beat: float = 10.0,
    carrier_freq: float = 216.0,
    ambient_mode: str = "rain"
) -> Path
```

Synthesizes a **stereo 16-bit 44100 Hz WAV** file and writes it to `output_path`.

| Parameter | Type | Description |
|---|---|---|
| `output_path` | `str \| Path` | Destination `.wav` file path |
| `duration_sec` | `int` | Length of audio in seconds |
| `noise_type` | `str` | `"white"`, `"pink"`, or `"brown"` |
| `binaural_beat` | `float` | Beat frequency in Hz; creates inter-aural frequency difference |
| `carrier_freq` | `float` | Carrier tone frequency in Hz |
| `ambient_mode` | `str` | Environment overlay: `"rain"`, `"ocean"`, `"wind"`, `"space"`, `"noise"` |

**Returns**: `Path` object pointing to the written WAV file.

**Stereo channel separation**: The left channel receives the carrier at `carrier_freq`; the right channel receives `carrier_freq + binaural_beat`. The brain perceives the arithmetic difference as a phantom beat frequency — the binaural effect.

---

### `generate_ambient_html_synthesizer`

```python
generate_ambient_html_synthesizer(output_path: str | Path) -> Path
```

Generates a **zero-dependency HTML5 document** containing a fully self-contained WebAudio synthesizer. No CDN links, no external stylesheets, no JavaScript libraries — the entire synthesizer is embedded inline.

| Parameter | Type | Description |
|---|---|---|
| `output_path` | `str \| Path` | Destination `.html` file path |

**Returns**: `Path` object of the written file.

The HTML synthesizer exposes the same knobs as the CLI: noise color, binaural beat frequency, carrier frequency, and ambient mode. Playback is controlled in real time from the browser.

---

### `PROFILES` Dictionary

```python
PROFILES: dict[str, dict]
```

A module-level dictionary of pre-tuned presets. Each entry is keyed by a profile name and contains the following fields:

| Field | Type | Description |
|---|---|---|
| `type` | `str` | Profile category label |
| `noise` | `str` | Noise colour (`white`, `pink`, `brown`) |
| `binaural` | `str` | Brain-wave band name (`alpha`, `theta`, `beta`, `gamma`) |
| `carrier` | `float` | Carrier frequency in Hz |
| `beat` | `float` | Binaural beat frequency in Hz |
| `desc` | `str` | Human-readable description of the profile's intended use |

---

## Built-In Profiles

| Profile Key | Noise | Beat Band | Beat (Hz) | Carrier (Hz) | Use Case |
|---|---|---|---|---|---|
| `rainy_library` | brown | alpha | 10.0 | 216.0 | Relaxed reading & note-taking |
| `deep_space` | white | theta | 6.0 | 144.0 | Deep meditative worldbuilding |
| `mountain_wind` | pink | alpha | 9.0 | 288.0 | Scenic description & prose drafting |
| `ocean_surf` | brown | theta | 5.5 | 180.0 | Emotional & introspective scenes |
| `pure_focus` | pink | beta | 18.0 | 256.0 | Analytical plot & structure work |

---

## Noise Color Reference

Noise colour controls the spectral distribution of the background noise layer.

| Colour | Spectrum | Character | Best For |
|---|---|---|---|
| **White** | Flat (all frequencies equal power) | Bright, hissy, clinical | Blocking sharp office noise; space ambience |
| **Pink** | 1/f rolloff (power ∝ 1/f) | Natural, balanced, airy | General writing; rainfall-like texture |
| **Brown / Red** | Brownian walk (power ∝ 1/f²) | Deep, warm, rumbling | Immersive long sessions; ocean/wind layers |

> [!NOTE]
> Brown noise is generated via a Brownian random walk: each sample is the previous sample plus a small Gaussian perturbation, then re-normalised. Pink noise uses a Voss–McCartney cascade filter.

---

## Binaural Beat Brain-Wave Types

Binaural beats require **headphones** for the effect to work — the two channels must reach each ear independently.

| Band | Range (Hz) | Cognitive State | Recommended Profile |
|---|---|---|---|
| **Alpha** | 8 – 12 Hz | Creative flow & relaxed focus | `rainy_library`, `mountain_wind` |
| **Theta** | 4 – 8 Hz | Deep meditation & dreaming | `deep_space`, `ocean_surf` |
| **Beta** | 13 – 30 Hz | High alertness & problem-solving | `pure_focus` |
| **Gamma** | ~40 Hz | Peak cognitive concentration | Custom `--beat 40.0` |

> [!IMPORTANT]
> Binaural beats are an **assistive focus aid**, not a medically validated treatment. Individual responses vary. If you experience discomfort, reduce the beat frequency or switch to a lower band.

---

## Ambient Modes

The ambient mode applies an **envelope or modulation layer** on top of the base noise.

| Mode | Behaviour | Spectral Character |
|---|---|---|
| `rain` | Steady broadband noise; mild high-frequency emphasis | Constant, uniform |
| `ocean` | 0.1 Hz amplitude swell modulation (slow wave rhythm) | Rolling, undulating |
| `wind` | Gust envelope: random amplitude bursts at irregular intervals | Dynamic, gusty |
| `space` | White-noise base with very low-frequency pulse; minimal modulation | Sparse, eerie |
| `noise` | Raw noise with no additional modulation layer | Neutral |

---

## Diagnostic Codes

| Code | Severity | Condition | Resolution |
|---|---|---|---|
| `AMB-001` | ERROR | `duration_sec` ≤ 0 | Provide a positive integer for `--duration` |
| `AMB-002` | ERROR | Unknown `noise_type` value | Must be one of `white`, `pink`, `brown` |
| `AMB-003` | ERROR | Unknown `ambient_mode` value | Must be one of `rain`, `ocean`, `wind`, `space`, `noise` |
| `AMB-004` | WARNING | `binaural_beat` > 80 Hz | Values above 80 Hz fall outside established brain-wave bands |
| `AMB-005` | ERROR | Output directory does not exist | Create the parent directory before running |
| `AMB-006` | ERROR | Unknown `--profile` name | Check `PROFILES` keys with `arcanum ambient --list-profiles` |

---

## Behavioral Notes

- **Sample rate**: Fixed at **44100 Hz**. This cannot be changed via CLI; use the Python API directly if you need a different rate.
- **Bit depth**: Fixed at **16-bit signed PCM**. The output is compatible with all standard media players.
- **Stereo field**: The left channel always carries `carrier_freq`; the right channel carries `carrier_freq + binaural_beat`. Swapping headphones will reverse the perceived beat direction but not affect efficacy.
- **WAV duration vs file size**: At 44100 Hz × 2 channels × 2 bytes = ~176 KB/second. A 60-minute session file is approximately 620 MB. For long sessions, the HTML synthesizer is preferable.
- **HTML synthesizer independence**: The generated HTML uses only native Web APIs (`AudioContext`, `OscillatorNode`, `BiquadFilterNode`). It can be opened on any modern desktop or mobile browser without an internet connection.
- **Profile overriding**: When `--profile` is combined with any individual flag (e.g., `--beat 20.0`), the individual flag **takes precedence** over the profile's default for that field.
- **NumPy dependency**: The WAV synthesizer requires `numpy` and `scipy` in the Python environment. The HTML synthesizer requires neither.

---

## Example Workflow

### Workflow 1: Long-Session Writing WAV

```powershell
# 2-hour deep-space session for intense worldbuilding
arcanum ambient --profile deep_space --duration 7200 -o world_session.wav
```

### Workflow 2: Browser Synthesizer for Portable Use

```powershell
# Generate HTML synthesizer — distribute alongside your world document
arcanum ambient --profile ocean_surf --html -o ocean_synthesizer.html
```

Open `ocean_synthesizer.html` in any browser. No internet required.

### Workflow 3: Custom Gamma Focus Track

```powershell
# 40 Hz gamma beat over pink noise for intensive editing sprint
arcanum ambient --noise pink --beat 40.0 --carrier 256.0 --mode noise --duration 3600 -o gamma_sprint.wav
```

### Workflow 4: Python API Integration

```python
from scripts.lib.ambient import synthesize_wav, PROFILES

# Pull settings from a built-in profile
profile = PROFILES["rainy_library"]

synthesize_wav(
    output_path="output/session.wav",
    duration_sec=3600,
    noise_type=profile["noise"],
    binaural_beat=profile["beat"],
    carrier_freq=profile["carrier"],
    ambient_mode="rain"
)

print(f"Profile: {profile['desc']}")
```

### Workflow 5: HTML Synthesizer from Python

```python
from scripts.lib.ambient import generate_ambient_html_synthesizer

path = generate_ambient_html_synthesizer("output/synth.html")
print(f"Synthesizer written to: {path}")
```

---

*Part of the **Ars Arcanum Scriptorium** craft engine. For platform-wide CLI reference, see `docs/CLI_REFERENCE.md`.*
