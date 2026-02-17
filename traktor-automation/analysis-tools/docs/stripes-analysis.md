# Traktor Stripes File Analysis

## Overview

Traktor generates **stripes files** during track analysis. These files contain waveform visualization data that shows frequency distribution across the entire track. According to Native Instruments documentation:

- **Brighter color shades** represent higher frequencies
- **Darker color shades** represent lower frequencies

This frequency distribution data is incredibly valuable for automated cue point detection because it reveals the track's structure.

## Why Stripes Files Matter for Cue Points

### 1. Breakdown Detection

When low frequencies (bass) drop out, it typically indicates a **breakdown** section:
- Vocals-only sections
- Atmospheric interludes
- Build-up preparation
- Tension building moments

These are ideal places for DJs to:
- Mix in a new track
- Apply effects
- Build energy before a drop

### 2. Build-Up Detection

Gradual energy increases across frequency bands indicate **build-ups**:
- Rising tension
- Filter sweeps
- Adding layers
- Preparing for a drop

### 3. Drop Detection

Sudden energy increases, especially in low frequencies, indicate **drops**:
- The "payoff" moment
- Full frequency spectrum return
- Maximum energy
- Dance floor peak moments

## Stripes File Format

### File Location
```
~/Documents/Native Instruments/Traktor 3.11.1/Stripes/
```

### Directory Structure
```
Stripes/
├── 000/
│   ├── A25QIFCHTIEFTCB04LEZBPVKMIOC
│   ├── A2ODYSAZ0WSBEBBVFNHUBQ5QHMCD
│   └── ...
├── 001/
└── ...
```

The filenames are hash identifiers that correspond to tracks in the collection.nml file.

### Binary Format

The stripes files use a proprietary binary format:

```
Offset | Size | Description
-------|------|------------
0x00   | 4    | Signature: "PRTS" (or partial)
0x04   | 1    | Version or flag byte
0x05   | 8    | Metadata (purpose unclear)
0x0D   | 3    | Start of waveform data
...    | ...  | Continues as triplets
```

### Waveform Data Structure

The waveform data appears to be organized as **triplets of bytes**:

```python
[byte1, byte2, byte3, byte1, byte2, byte3, ...]
```

Each triplet likely represents:
- `byte1`: Low frequency amplitude (bass)
- `byte2`: Mid frequency amplitude
- `byte3`: High frequency amplitude

## Scripts

### 1. `analyze_stripes.py`

Basic stripes file analyzer that:
- Parses the binary format
- Extracts frequency data
- Generates visualizations
- Detects potential breakdown points

**Usage:**
```bash
python3 scripts/analyze_stripes.py "<path_to_stripes_file>"
```

**Output:**
- Console statistics
- Visualization image: `analysis/stripes_visualization.png`

### 2. `stripes_to_cuepoints.py`

Advanced cue point suggestion system that:
- Analyzes track structure from stripes data
- Detects breakdowns, build-ups, and drops
- Suggests optimal cue point positions
- Outputs detailed recommendations

**Usage:**
```bash
python3 scripts/stripes_to_cuepoints.py "<stripes_file>" <duration_seconds>
```

**Example:**
```bash
python3 scripts/stripes_to_cuepoints.py \
  "~/Documents/Native Instruments/Traktor 3.11.1/Stripes/000/ABC123" \
  360
```

**Output:**
- Console listing of suggested cue points
- Text file: `analysis/suggested_cuepoints.txt`

## Detection Algorithms

### Breakdown Detection

```python
def detect_breakdowns(samples, threshold=0.5, min_duration=200):
    """
    Detect sections where bass drops below 50% of average.
    Requires minimum duration to avoid false positives.
    """
```

**Parameters:**
- `threshold`: 0.5 = bass must drop to 50% of average or below
- `min_duration_samples`: 200 = must last ~2 seconds minimum
- `min_separation`: 1000 = breakdowns must be ~10 seconds apart

### Build-Up Detection

```python
def detect_buildups(samples, window_size=80, threshold=1.6):
    """
    Detect gradual energy increases.
    Compare sliding windows for rising trend.
    """
```

**Parameters:**
- `window_size`: 80 samples to compare
- `increase_threshold`: 1.6 = energy must increase 60%
- `min_separation`: 800 = build-ups must be ~8 seconds apart

### Drop Detection

```python
def detect_drops(samples, window_size=50, threshold=1.6):
    """
    Detect sudden energy increases with bass return.
    """
```

**Parameters:**
- `window_size`: 50 samples to compare before/after
- `drop_threshold`: 1.6 = energy must jump 60%
- `bass_threshold`: 1.3 = bass specifically must increase 30%
- `min_separation`: 500 = drops must be ~5 seconds apart

## Integration with Existing System

The stripes-based analysis **complements** the existing librosa-based system:

### Librosa Analysis (existing)
- Beat detection
- Tempo analysis
- Onset detection
- Spectral analysis

### Stripes Analysis (new)
- Uses Traktor's native analysis
- Faster (pre-computed)
- Matches Traktor's visual display
- Proven track structure understanding

### Combined Approach

```python
# 1. Load stripes data
stripes = StripesAnalyzer(stripes_path)
structure_cues = stripes.suggest_cue_points()

# 2. Load librosa analysis
beats = librosa.beat.beat_track(y, sr=sample_rate)
onsets = librosa.onset.onset_detect(y, sr=sample_rate)

# 3. Align and merge
cue_points = merge_analyses(structure_cues, beats, onsets)

# 4. Update NML
update_traktor_nml(track_id, cue_points)
```

## Finding the Corresponding Track

To map a stripes file to its track in `collection.nml`:

1. The stripes filename is likely a hash of the file path
2. Search the NML file for references to this hash
3. Alternatively, analyze all tracks and match by duration

**Future enhancement:** Create a lookup table mapping stripes files to NML entries.

## Benefits Over Pure Librosa Analysis

1. **Pre-computed**: No need to re-analyze (saves time)
2. **Traktor-aligned**: Uses same analysis as Traktor's own display
3. **Optimized**: Native Instruments' algorithms are tuned for DJ use
4. **Visual consistency**: Matches what DJs see in Traktor
5. **Lightweight**: Binary format is compact and fast to parse

## Next Steps

1. ✅ Parse stripes file format
2. ✅ Extract frequency data
3. ✅ Detect breakdowns, build-ups, drops
4. ✅ Generate cue point suggestions
5. ⬜ Map stripes files to NML track entries
6. ⬜ Integrate with existing cue point system
7. ⬜ Batch process entire library
8. ⬜ Compare accuracy vs. librosa-only approach
9. ⬜ Fine-tune detection parameters per genre

## References

- [DJ TechTools: Read traktor stripe files](https://forum.djtechtools.com/showthread.php?t=22289)
- [DJ TechTools: Stripes and Transients](https://forum.djtechtools.com/showthread.php?t=15892)
- [Decoding the TRAKTOR4 field](https://hellricer.github.io/2021/05/05/decoding-traktor4-field.html)
- [Native Instruments: What Files Does TRAKTOR Install](https://support.native-instruments.com/hc/en-us/articles/210274225)

## Conclusion

The stripes files provide a **goldmine of structural information** that was previously untapped. By analyzing the frequency distribution data, we can automatically detect:

- Where breakdowns occur (perfect for mixing in/out)
- Where build-ups happen (prepare the crowd)
- Where drops hit (maximize impact)

This significantly improves automated cue point placement compared to beat-only detection.
