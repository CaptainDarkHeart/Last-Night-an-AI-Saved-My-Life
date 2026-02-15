# Track Selection Engine (Layer 3)

**Intelligent playlist generation for deep space house DJ sets using journey arc philosophy.**

---

## Overview

The Track Selection Engine is an AI-powered system that analyzes your music library and generates intelligent playlists following deep space house mixing philosophy:

- **60-90 second extended blends**
- **A Minor harmonic journeys**
- **Gradual energy progression**
- **Label-aware aesthetics** (Lucidflow, Echocord, etc.)
- **Texture and atmosphere focus**

---

## Features

### 🎯 Core Capabilities

1. **Track Library Management**
   - Scan music directories
   - Extract metadata (BPM, key, artist, title)
   - Index by key, BPM, energy, texture
   - Compatibility matching

2. **Journey Arc Planning**
   - Generate energy progression curves
   - Define musical key centers
   - Set BPM ranges and blend durations
   - Configure texture requirements

3. **Smart Playlist Generation**
   - Select tracks following energy curves
   - Maintain harmonic compatibility
   - Plan smooth transitions
   - Respect label aesthetics

4. **Transition Planning**
   - Calculate blend timing
   - Check BPM/key compatibility
   - Suggest mixing strategies
   - Generate transition notes

---

## Installation

```bash
cd track-selection-engine
pip install -e .
```

This installs the `track-selector` command-line tool.

---

## Quick Start

### 1. Create a Track Library

Scan your music directory:

```bash
track-selector create /path/to/your/music --library my-library.json
```

This will:
- Scan all audio files (WAV, AIFF, MP3, FLAC)
- Extract metadata
- Save to `my-library.json`

### 2. View Library Statistics

```bash
track-selector stats --library my-library.json
```

Shows:
- Total tracks
- BPM range and average
- Energy distribution
- Keys and labels

### 3. Generate a Playlist

Create a 3-hour deep space house journey:

```bash
track-selector generate 180 \
  --library my-library.json \
  --output my-journey \
  --key 1A \
  --progression gradual_build \
  --blend 75 \
  --m3u
```

This generates:
- `my-journey.json` - Full playlist with transitions
- `my-journey.m3u` - M3U playlist for Mixxx/Traktor

---

## Usage Guide

### Creating Libraries

**Basic scan:**
```bash
track-selector create /Music/Deep-House
```

**Custom library file:**
```bash
track-selector create /Music/Deep-House --library deep-house-lib.json
```

### Generating Playlists

**A Minor journey (gradual build):**
```bash
track-selector generate 120 \
  --key 1A \
  --progression gradual_build \
  --blend 60
```

**Peak and descent journey:**
```bash
track-selector generate 90 \
  --progression peak_and_descent \
  --min-bpm 120 \
  --max-bpm 124
```

**Strict harmonic mixing:**
```bash
track-selector generate 180 \
  --key 1A \
  --strict-key \
  --blend 90
```

### Listing Tracks

**Show all tracks:**
```bash
track-selector list
```

**Filter by BPM:**
```bash
track-selector list --bpm 122
```

**Filter by key:**
```bash
track-selector list --key 1A
```

**Filter by energy:**
```bash
track-selector list --energy 5
```

---

## Command Reference

### `create` - Create Library

```
track-selector create <directory> [options]

Arguments:
  directory              Directory to scan

Options:
  -l, --library FILE     Library file path (default: library.json)
```

### `stats` - Show Statistics

```
track-selector stats [options]

Options:
  -l, --library FILE     Library file path (default: library.json)
```

### `generate` - Generate Playlist

```
track-selector generate <duration> [options]

Arguments:
  duration               Duration in minutes

Options:
  -l, --library FILE     Library file path (default: library.json)
  -o, --output FILE      Output file path (default: playlist)
  -k, --key KEY          Key center (e.g., 1A for A Minor)
  --min-bpm BPM          Minimum BPM (default: 118)
  --max-bpm BPM          Maximum BPM (default: 124)
  -p, --progression TYPE Energy progression (default: gradual_build)
                         Choices: gradual_build, peak_and_descent, steady
  -b, --blend SECONDS    Blend duration (default: 60)
  --strict-key           Only use key-compatible tracks
  --m3u                  Also save as M3U playlist
```

### `list` - List Tracks

```
track-selector list [options]

Options:
  -l, --library FILE     Library file path (default: library.json)
  --bpm BPM              Filter by BPM (±2)
  --key KEY              Filter by key (e.g., 1A)
  --energy LEVEL         Filter by energy level (±1)
  --limit N              Max tracks to show (default: 20)
```

---

## Musical Key System (Camelot)

The engine uses the Camelot Wheel for harmonic mixing:

### Minor Keys (A)
- **1A** - A Minor
- **2A** - E Minor
- **3A** - B Minor
- **4A** - F# Minor
- **5A** - Db Minor
- **6A** - Ab Minor
- **7A** - Eb Minor
- **8A** - Bb Minor
- **9A** - F Minor
- **10A** - C Minor
- **11A** - G Minor
- **12A** - D Minor

### Major Keys (B)
- **1B** - C Major
- **2B** - G Major
- etc.

**Compatible mixes:**
- Same key (e.g., 1A → 1A)
- ±1 on the circle (e.g., 1A → 2A or 12A)
- Same number, different letter (e.g., 1A → 1B)

---

## Energy Progression Types

### Gradual Build (Default)
```
Deep space house classic arc:
2-3-4 (opening) → 4-5-6 (building) → 6-7-8 (peak) → 7-6-5 (descent)

Best for: Full DJ sets, warm-up to peak journey
```

### Peak and Descent
```
Build to climax, then wind down:
2-3-4-5-6-7-8 (build) → 7-6-5-4-3 (descent)

Best for: Opening or closing sets, dramatic arcs
```

### Steady
```
Maintain consistent energy:
5-6-5-6-5-6 (steady groove)

Best for: Mid-set sections, consistent vibe
```

---

## Output Formats

### JSON Playlist

Complete playlist with all metadata:

```json
{
  "name": "Deep Space Journey - 180min",
  "tracks": [
    {
      "title": "Una Pena",
      "artist": "Stimming",
      "bpm": 122.3,
      "key": "1A",
      "energy_level": 5
    }
  ],
  "transitions": [
    {
      "start_time_a": 301.5,
      "start_time_b": 0.0,
      "blend_duration": 60,
      "strategy": "extended_blend"
    }
  ]
}
```

### M3U Playlist

Standard format for DJ software:

```
#EXTM3U
#PLAYLIST:Deep Space Journey

#EXTINF:376,Stimming - Una Pena
/Music/Stimming - Una Pena.wav

#EXTINF:412,Sasha Carassi - Blurred
/Music/Sasha Carassi - Blurred.wav
```

---

## Integration

### With Mixxx DJ Software

1. Generate playlist with `--m3u` flag
2. Import M3U file into Mixxx
3. Use with AutoDJ or manual mixing

### With Traktor

1. Generate JSON playlist
2. Load tracks manually in Traktor
3. Use transition times to set cue points

### With AI DJ MCP Server (Layer 2)

Combine with the MCP server for enhanced analysis:

```python
# Example: Analyze tracks before adding to library
from track_selector.library import TrackLibrary
# Use MCP server to detect cue points, BPM, etc.
```

---

## Advanced Usage

### Python API

Use the engine programmatically:

```python
from track_selector.library import TrackLibrary
from track_selector.journey_planner import JourneyPlanner
from track_selector.models import MusicalKey

# Load library
library = TrackLibrary(Path("my-library.json"))

# Create planner
planner = JourneyPlanner(library)

# Create journey arc
journey = planner.create_journey_arc(
    duration_minutes=120,
    key_center=MusicalKey.A_MINOR,
    bpm_range=(120, 124),
    energy_progression="gradual_build",
    blend_duration=75
)

# Generate playlist
playlist = planner.generate_playlist(journey, strict_key=True)

# Save
playlist.to_json(Path("output.json"))
playlist.to_m3u(Path("output.m3u"))
```

---

## Deep Space House Philosophy

The engine implements your documented mixing approach:

### From EXAMPLE_JOURNEY_ARCS.md
- Gradual energy progression
- Extended blends (60-90s)
- Textural layering
- A Minor harmonic center

### From LABEL_GUIDE.md
- Lucidflow aesthetic preference
- Echocord dub influence
- MCDE atmospheric depth

### From TRANSITION_TECHNIQUES.md
- Bass/treble EQ swapping
- Phrase-aligned mixing
- Atmospheric layering

---

## Troubleshooting

### "No suitable opener found"
- Your library may not have low-energy tracks
- Try relaxing energy requirements
- Add more atmospheric/minimal tracks

### "Could not find suitable track"
- Library too small for the duration
- BPM/key constraints too strict
- Try `--strict-key false` or wider BPM range

### Empty library after scan
- Check audio file formats (WAV, AIFF, MP3, FLAC)
- Verify directory path
- Check file permissions

---

## Next Steps

1. **Scan your music library** - Create your first library
2. **Generate a test playlist** - Try a 60-minute journey
3. **Refine track metadata** - Add energy levels, textures, keys
4. **Combine with Layer 2** - Use MCP server for analysis
5. **Build Layer 4** - Create Mixxx controller integration

---

## Files Generated

- `*.json` - Full playlist with transitions
- `*.m3u` - M3U playlist for DJ software
- `library.json` - Track library database

---

**Built for deep space house DJs who understand the journey.** 🚀🎧
