# Traktor Analysis Tools

Intelligent cue point detection by combining Traktor's native analysis files with advanced audio analysis.

## Overview

This toolkit provides:

1. **Stripes Parser** - Decode Traktor's frequency visualization files
2. **Transients Explorer** - Research into beat detection files (WIP)
3. **Hybrid Analyzer** - Combine Stripes + Librosa for intelligent cue points ⭐

## Quick Start

### Prerequisites

```bash
pip install librosa numpy scipy
```

### Analyze a Track (Hybrid Mode)

```bash
python scripts/hybrid_analyzer.py \
  "/path/to/track.mp3" \
  "~/Documents/Native Instruments/Traktor 3.11.1/Stripes/000/ABC123"
```

**Output**: Beat-precise cue points combining structural analysis (stripes) with beat detection (librosa).

## Tools

### 🎯 hybrid_analyzer.py (Recommended)

**What it does**: Combines the best of both worlds
- Structural detection from Traktor Stripes (breakdowns, builds, drops)
- Beat-precise timing from Librosa
- Automatic alignment of structure to beats

**When to use**: When you want intelligent, beat-perfect cue points

**Docs**: [Hybrid Integration Guide](docs/hybrid-integration.md)

### 🎨 stripes_to_cuepoints.py

**What it does**: Analyzes Traktor's stripes files for track structure
- Detects breakdowns (bass drops)
- Detects build-ups (energy increases)
- Detects drops (energy returns)

**When to use**: When you only have stripes files and want quick structural analysis

**Docs**: [Stripes Analysis](docs/stripes-analysis.md)

### 🔬 analyze_stripes.py

**What it does**: Low-level stripes file exploration
- Parses binary format
- Extracts frequency data
- Generates visualizations

**When to use**: Research or visualization purposes

### 🧪 analyze_transients.py (v1, v2, v3)

**What it does**: Experimental transients file parsers
- Attempting to decode beat detection files
- Work in progress

**Status**: ❌ Not fully functional (binary format not decoded)

**Docs**: [Transients Exploration](docs/transients-exploration.md)

## Directory Structure

```
analysis-tools/
├── scripts/
│   ├── hybrid_analyzer.py           ⭐ Main tool (Stripes + Librosa)
│   ├── stripes_to_cuepoints.py      📊 Stripes-only analysis
│   ├── analyze_stripes.py           🔬 Low-level stripes parser
│   ├── analyze_transients.py        🧪 Experimental
│   ├── analyze_transients_v2.py     🧪 Experimental
│   └── analyze_transients_v3.py     🧪 Experimental
│
└── docs/
    ├── hybrid-integration.md         📖 Complete integration guide
    ├── stripes-analysis.md           📖 Stripes file format + analysis
    ├── traktor-analysis-files-summary.md  📖 Overview of all file types
    └── transients-exploration.md     📖 Transients research notes
```

## Workflow Comparison

### Option 1: Hybrid Analysis (Recommended) ⭐

```bash
# One command for everything
python scripts/hybrid_analyzer.py track.mp3 stripes_file

# Result: Beat-precise cue points with structural understanding
```

**Pros**:
- ✅ Best accuracy (structure + beat precision)
- ✅ Traktor-ready cue points
- ✅ Single command

**Cons**:
- ⚠️ Requires audio file (~30s to analyze)
- ⚠️ Need both audio + stripes

### Option 2: Stripes Only

```bash
# Quick structural analysis
python scripts/stripes_to_cuepoints.py stripes_file 360

# Result: Approximate cue points (not beat-aligned)
```

**Pros**:
- ✅ Very fast (<1 second)
- ✅ No audio file needed
- ✅ Good structural detection

**Cons**:
- ⚠️ Timing not beat-precise
- ⚠️ May place cues between beats

### Option 3: Librosa Only (Not in this toolkit)

See `../../audio_analyzer.py` for pure Librosa analysis.

**Pros**:
- ✅ Beat-precise
- ✅ Works without stripes

**Cons**:
- ⚠️ Limited structural understanding
- ⚠️ Slow (~30s per track)

## How It Works

### The Hybrid Approach

```
┌─────────────────┐         ┌─────────────────┐
│  Traktor Stripes│         │     Librosa     │
│                 │         │                 │
│  "Breakdown at  │         │  "Beats at:     │
│   ~93 seconds"  │         │   92.87s,       │
│                 │         │   93.37s, ..."  │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │    ┌───────────────────┐  │
         └───►│ Hybrid Analyzer   │◄─┘
              │                   │
              │ 1. Get structure  │
              │ 2. Get beats      │
              │ 3. Align them     │
              └─────────┬─────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  Intelligent    │
              │  Cue Points     │
              │                 │
              │ "Breakdown at   │
              │  92.87s         │
              │  (Beat #187)"   │
              └─────────────────┘
```

**Key Innovation**: We snap structural features to the nearest beat:
- Stripes says: "Breakdown around 93.0 seconds"
- Librosa says: "Beat #187 is at 92.87 seconds"
- Result: "Breakdown at beat #187 (92.87s)" ← Perfect for DJing!

## Use Cases

### 1. Prepare a Single Track

```bash
# Analyze and save cue points
python scripts/hybrid_analyzer.py track.mp3 stripes_file

# Result: track_analysis.json with all cue points
```

### 2. Batch Process Library

```python
from hybrid_analyzer import HybridAnalyzer

for track in library:
    analyzer = HybridAnalyzer(track.audio, track.stripes)
    results = analyzer.analyze()
    cues = analyzer.export_traktor_cues()
    # TODO: Write to NML file
```

### 3. Research Track Structure

```bash
# Visualize frequency distribution
python scripts/analyze_stripes.py stripes_file

# Result: visualization showing bass/mid/high frequency changes
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Stripes parsing | <0.1s | Very fast |
| Librosa analysis | ~30s | Depends on track length |
| Hybrid analysis | ~30s | Librosa is the bottleneck |
| Batch (100 tracks) | ~50min | Can parallelize |

**Tip**: Use hybrid analysis for final cue points, stripes-only for quick previews.

## Output Formats

### JSON Analysis File

```json
{
  "file": "/path/to/track.mp3",
  "duration": 360.0,
  "tempo": 120.4,
  "total_beats": 721,
  "cue_points": [
    {
      "type": "breakdown",
      "name": "Breakdown 1",
      "beat_time": 92.87,
      "beat_number": 187,
      "description": "Low frequency drop"
    }
  ],
  "summary": {
    "total_cue_points": 8,
    "breakdowns": 2,
    "buildups": 3,
    "drops": 2
  }
}
```

### Traktor-Ready Cues

```json
[
  {
    "name": "Breakdown 1",
    "time": 92.87,
    "type": 0,
    "color": 1,
    "description": "Low frequency drop"
  }
]
```

## Next Steps

### Current Status

- ✅ Stripes parsing complete
- ✅ Structural detection working
- ✅ Librosa integration complete
- ✅ Hybrid alignment algorithm implemented
- ⬜ NML file integration (pending)
- ⬜ Batch processing script (pending)

### Roadmap

1. **NML Integration** - Write cue points directly to Traktor's collection.nml
2. **Batch Processor** - Analyze entire music library automatically
3. **GUI Tool** - Visual interface for reviewing/editing cue points
4. **Genre Tuning** - Optimize detection parameters per genre

## Troubleshooting

### Can't find stripes file

Stripes files are in: `~/Documents/Native Instruments/Traktor 3.11.1/Stripes/`

They're organized in numbered subdirectories (000, 001, etc.) with hash-based filenames.

**Solution**: You need to map audio files to stripes files using Traktor's collection.nml file.

### Librosa is slow

Yes, audio analysis takes time. For faster results:
- Use stripes-only mode for previews
- Batch process overnight
- Use a faster machine
- Consider using Traktor's beatgrid instead (coming soon)

### Cue points aren't accurate

**Structural detection**:
- Adjust detection thresholds in `stripes_to_cuepoints.py`
- Some tracks may not have clear breakdowns/builds

**Beat alignment**:
- Check if the track has tempo changes
- Verify audio file matches the stripes file
- Consider using Traktor's beatgrid for better accuracy

## Documentation

- **[Hybrid Integration Guide](docs/hybrid-integration.md)** - Complete guide to hybrid analysis
- **[Stripes Analysis](docs/stripes-analysis.md)** - Deep dive into stripes files
- **[Analysis Files Summary](docs/traktor-analysis-files-summary.md)** - Overview of all Traktor analysis files
- **[Transients Exploration](docs/transients-exploration.md)** - Transients research (WIP)

## Contributing

This toolkit is part of the **Anima-in-Machina** project. Contributions welcome!

Areas for improvement:
- Better alignment algorithms
- NML integration code
- Genre-specific detection parameters
- Performance optimizations
- Transients file decoding

## License

Part of Anima-in-Machina, shared under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).

---

**Status**: ✅ Core functionality complete
**Created**: February 2026
**Last Updated**: February 2026
