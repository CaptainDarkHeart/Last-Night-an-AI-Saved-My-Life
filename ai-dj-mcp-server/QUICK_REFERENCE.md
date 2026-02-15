# AI DJ MCP Server - Quick Reference

Fast reference for using the AI DJ tools with Claude.

---

## Installation (One-Time Setup)

```bash
cd ai-dj-mcp-server
pip install -e .
```

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ai-dj": {
      "command": "python3",
      "args": ["-m", "ai_dj_mcp.server"],
      "cwd": "/FULL/PATH/TO/ai-dj-mcp-server/src"
    }
  }
}
```

Restart Claude Desktop.

---

## Quick Commands

### Analyze a Track
```
Analyze the track at /path/to/track.wav
```

### Find Cue Points
```
Detect cue points for /path/to/track.wav
```

### Plan a Transition
```
Suggest transitions between /path/to/track1.wav and /path/to/track2.wav
```

### Check BPM Compatibility
```
Calculate BPM compatibility between 120 and 122
```

### Extract Features
```
Extract features from /path/to/track.wav
```

---

## Tool Reference

| Tool | What It Does | Inputs |
|------|--------------|--------|
| `analyze_track` | BPM, beats, duration | audio_path |
| `detect_cue_points` | AI cue point detection | audio_path, num_cues (12) |
| `suggest_transitions` | Transition planning | track1_path, track2_path, blend_duration (60) |
| `extract_features` | 24-D feature vectors | audio_path |
| `calculate_bpm_compatibility` | BPM ratio check | bpm1, bpm2, tolerance (6%) |

---

## Common Workflows

### 1. Prepare Track for Traktor
```
Detect cue points for /Music/new-track.wav
```
→ Copy cue times to Traktor hot cues

### 2. Build a DJ Set
```
Analyze these tracks and suggest mix order:
- /Music/track1.wav
- /Music/track2.wav
- /Music/track3.wav
```

### 3. Check Track Compatibility
```
Calculate BPM compatibility between 118.5 and 122.3
```

---

## File Path Tips

- Use **absolute paths** (not relative)
- macOS example: `/Users/dantaylor/Music/track.wav`
- Windows example: `C:\Users\Dan\Music\track.wav`
- Drag & drop file into Terminal to get path

---

## Supported Audio Formats

✅ WAV, AIFF, MP3, FLAC
❌ Streaming URLs (Spotify, SoundCloud)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Tool not found" | Restart Claude Desktop |
| "File not found" | Use absolute path |
| "Module not found" | Run `pip install -e .` |
| Slow analysis | Normal for long tracks (5-10 min) |

---

## Output Interpretation

### BPM Detection
- Compare with Traktor/Mixxx
- ±1 BPM difference is normal
- Re-analyze if >5 BPM off

### Cue Points
- Higher confidence = better cue
- Use 0.8+ confidence cues
- Verify aligned with music

### Compatibility
- ✓ = Can mix directly
- ✗ = Needs tempo adjustment
- Shows adjustment amount

---

## Next Steps

1. **Test:** Analyze 5 favorite tracks
2. **Compare:** Match against your manual cues
3. **Plan:** Build a 1-hour mix using transitions
4. **Execute:** Load into Traktor/Mixxx

---

**Questions?** See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for detailed examples.
