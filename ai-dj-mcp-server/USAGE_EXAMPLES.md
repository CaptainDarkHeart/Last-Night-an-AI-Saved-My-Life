# AI DJ MCP Server - Usage Examples

Real-world examples of how to use the AI DJ tools with Claude.

---

## Basic Track Analysis

### Example 1: Analyze a Single Track

**You ask Claude:**
```
Analyze the track at /Users/dantaylor/Music/Stimming - Una Pena (Traktor Edit).wav
```

**Claude responds with:**
```
Track Analysis: Stimming - Una Pena (Traktor Edit)

Duration: 376.45 seconds
BPM: 122.3
Beats detected: 767
Downbeats detected: 192

First 10 beats (seconds): 0.52, 1.01, 1.50, 1.98, 2.47, 2.96, 3.44, 3.93, 4.42, 4.90
First 5 downbeats (seconds): 0.52, 2.47, 4.42, 6.37, 8.32
```

**What you can do with this:**
- Verify BPM detection matches your Traktor analysis
- Understand beat grid timing
- Check if downbeat detection aligns with musical structure

---

## Cue Point Detection

### Example 2: Find Optimal Mix Points

**You ask Claude:**
```
Detect cue points for /Users/dantaylor/Music/Sasha Carassi - Blurred (Original Mix).wav
```

**Claude responds with:**
```
Cue Point Detection: Sasha Carassi - Blurred (Original Mix)

Detected 12 optimal cue points:

  Cue 1: 0:08.12 (confidence: 0.876)
  Cue 2: 0:32.45 (confidence: 0.823)
  Cue 3: 1:04.78 (confidence: 0.891)
  Cue 4: 1:48.23 (confidence: 0.845)
  Cue 5: 2:16.56 (confidence: 0.901)
  Cue 6: 3:02.89 (confidence: 0.867)
  Cue 7: 3:35.12 (confidence: 0.778)
  Cue 8: 4:20.45 (confidence: 0.834)
  Cue 9: 4:52.78 (confidence: 0.812)
  Cue 10: 5:28.11 (confidence: 0.889)
  Cue 11: 6:04.44 (confidence: 0.856)
  Cue 12: 6:36.77 (confidence: 0.823)

Suggested Intro/Outro Markers:
  Intro Start: 8.12s
  Intro End: 32.45s
  Outro Start: 364.44s
  Outro End: 396.77s

These markers are suitable for extended blends (60-90 seconds).
```

**How to use these cues:**
1. Import track into Traktor
2. Set cue points at the suggested times
3. Use color coding: Red for intro, Green for outro
4. Plan your 60-90 second extended blends around these points

---

## Transition Planning

### Example 3: Plan a Mix Between Two Tracks

**You ask Claude:**
```
Suggest transitions between:
- /Music/Track1.wav (outgoing)
- /Music/Track2.wav (incoming)
with a 75 second blend
```

**Claude responds with:**
```
Transition Analysis

Track 1: Lucidflow - Atmospheric Journey
  BPM: 120.5
  Duration: 412.34s

Track 2: Echocord - Deep Pulse
  BPM: 121.8
  Duration: 389.67s

BPM Compatibility:
  Ratio: 0.989
  Compatible: ✓ Yes

Suggested Transition (75s blend):
  Start fading out Track 1 at: 337.34s (5.6min)
  Start fading in Track 2 at: 0.00s (from beginning)

Mixing Strategy:
  - Beatmatch at 1:1 ratio
  - Use extended blend (75s) for smooth textural transition
  - Gradually swap EQ (bass out on Track 1, bass in on Track 2)
  - Layer atmospheric elements during blend
```

**Your mixing workflow:**
1. Load Track 1 on Deck A
2. At 5:37 (337s), start loading Track 2 on Deck B
3. Begin your 75-second blend
4. Use EQ to gradually transition bass frequencies
5. Layer atmospheric elements for textural depth

---

## BPM Compatibility Checking

### Example 4: Check if Two Tracks Mix Well

**You ask Claude:**
```
Calculate BPM compatibility between 120 BPM and 122 BPM with 3% tolerance
```

**Claude responds with:**
```
BPM Compatibility Analysis

Track 1 BPM: 120.0
Track 2 BPM: 122.0
Ratio: 0.984
Tolerance: ±3%

Compatibility:
  ✓ 1:1 mixing (direct beatmatch)
    Tempo adjustment needed: 2.0 BPM
```

**Practical application:**
- These tracks CAN be mixed together
- Adjust Track 2 by -2 BPM to match Track 1
- Use Traktor's sync or manual tempo adjustment

---

## Advanced Workflows

### Example 5: Analyze an Entire Set

**You ask Claude:**
```
I'm planning a 3-hour deep space house set. Analyze these tracks and suggest the order:

1. /Music/Stimming - Una Pena.wav
2. /Music/Sasha Carassi - Blurred.wav
3. /Music/MCDE - Aurora.wav
4. /Music/Lucidflow - Atmospheric.wav
5. /Music/Echocord - Deep Pulse.wav
```

**Claude will:**
1. Analyze BPM and key for each track
2. Check compatibility between adjacent tracks
3. Suggest optimal ordering based on energy progression
4. Recommend transition points for each mix

---

### Example 6: Build a Journey Arc

**You ask Claude:**
```
Using my deep space house mixing philosophy (60-90 second blends, A Minor journeys,
gradual energy building), analyze these Lucidflow tracks and suggest a journey arc:

/Music/Lucidflow/Track1.wav (opener candidate)
/Music/Lucidflow/Track2.wav
/Music/Lucidflow/Track3.wav (peak candidate)
```

**Claude will:**
1. Analyze each track's energy curve
2. Detect cue points optimized for extended blends
3. Suggest BPM adjustments if needed
4. Map out a journey following your documented philosophy
5. Reference your EXAMPLE_JOURNEY_ARCS.md for style guidance

---

## Integration with Your Workflow

### Traktor Integration

Once you have cue points from Claude:

1. **Import to Traktor:**
   - Open track in Traktor
   - Set hot cues at detected times
   - Use your 6-color system (from TRAKTOR_SETUP_GUIDE.md)

2. **Verify Beat Grid:**
   - Compare detected BPM with Traktor's analysis
   - Adjust beat grid if needed
   - Set downbeat markers

3. **Mark Intro/Outro:**
   - Red cue at intro_start
   - Yellow cue at intro_end
   - Green cue at outro_start
   - Blue cue at outro_end

### Mixxx Integration

For use with Mixxx DJ software:

1. **Export Cue Points:**
   Ask Claude to format cue points for Mixxx import

2. **Create Playlists:**
   Use BPM compatibility to build smart playlists

3. **AutoDJ Configuration:**
   Set intro/outro markers for automatic mixing

---

## Feature Extraction for ML

### Example 7: Extract Features for Training

**You ask Claude:**
```
Extract features from /Music/training-set/track001.wav
```

**Claude responds with:**
```
Feature Extraction: track001

Extracted 512 feature vectors (24 dimensions each)

Feature breakdown per beat:
  - 13 MFCC coefficients
  - 7 Spectral Contrast bands
  - 1 Spectral Centroid
  - 1 Spectral Rolloff
  - 1 Spectral Flux
  - 1 RMS Energy

Total shape: (512, 24)
```

**Use cases:**
- Train custom cue detection models
- Analyze track similarity
- Build energy curve predictors
- Create genre classifiers

---

## Batch Processing

### Example 8: Analyze Multiple Tracks

**You ask Claude:**
```
Create a batch analysis script for all WAV files in /Music/New-Tracks/
```

**Claude can help you:**
1. Write a Python script using the Track class
2. Analyze all tracks in parallel
3. Export results to CSV or JSON
4. Generate compatibility matrix for your library

---

## Tips for Best Results

### Audio File Requirements

- **Supported formats:** WAV, AIFF, MP3, FLAC
- **Recommended:** WAV or AIFF (lossless)
- **Sample rate:** 44.1kHz or 48kHz
- **Bit depth:** 16-bit or 24-bit
- **Channels:** Mono or stereo (auto-converted to mono)

### Cue Point Detection Accuracy

- Works best with clear rhythmic structure
- Deep house, techno, and minimal are ideal genres
- Ambient or beatless sections may produce less accurate results
- Adjust `num_cues` based on track length (12 for 6-8 min tracks)

### BPM Detection

- Most accurate for tracks with consistent tempo
- May struggle with tracks that have tempo changes
- Compare with Traktor's BPM analysis for verification
- Use `align_to_phrase=True` for better musical alignment

---

## Next Steps

Now that you understand the tools:

1. **Analyze your top 100 tracks** - Build a database of BPM and cue points
2. **Create compatibility matrices** - Find tracks that mix well together
3. **Build journey arcs** - Use your deep space house philosophy
4. **Train custom models** - Use extracted features to train on your style

---

**Happy mixing!** 🎧🚀
