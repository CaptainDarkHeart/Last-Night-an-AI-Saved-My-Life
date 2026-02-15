# AI DJ MCP Server

A Model Context Protocol (MCP) server that provides AI-powered DJ mixing capabilities to Claude and other AI assistants.

## Features

### Core Tools

- **`analyze_track`** - Comprehensive audio analysis including BPM, beats, downbeats, and musical features
- **`detect_cue_points`** - AI-powered cue point detection using LSTM neural networks
- **`suggest_transitions`** - Intelligent transition suggestions between tracks based on BPM, key, and energy
- **`extract_features`** - Extract 24-dimensional feature vectors (MFCC, spectral analysis)
- **`normalize_tempo`** - Pitch-preserving time stretching to match BPM across tracks

### Planned Tools

- **`generate_mix`** - Automated mix generation from multiple tracks
- **`detect_energy_curve`** - Analyze energy progression throughout a track
- **`find_compatible_tracks`** - Search for tracks compatible with a given track

## Installation

### Prerequisites

- Python 3.10 or higher
- ffmpeg (for audio processing)

### Setup

1. Clone this repository or navigate to the `ai-dj-mcp-server` directory

2. Install dependencies:
```bash
pip install -e .
```

3. For development:
```bash
pip install -e ".[dev]"
```

### Install as MCP Server in Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ai-dj": {
      "command": "python",
      "args": [
        "-m",
        "ai_dj_mcp.server"
      ],
      "cwd": "/path/to/ai-dj-mcp-server/src"
    }
  }
}
```

Replace `/path/to/ai-dj-mcp-server/src` with the actual absolute path.

## Usage

Once installed, Claude can use the tools to analyze tracks:

```
Analyze the BPM and cue points for my-track.wav
```

Claude will use the MCP tools to:
1. Load the audio file
2. Detect beats and downbeats
3. Calculate BPM
4. Extract features
5. Use LSTM model to predict optimal cue points
6. Return analysis results

## Architecture

Built on top of AI-DJ-Mix-Generator algorithms:
- **Beat Detection**: madmom library (neural network-based)
- **Feature Extraction**: librosa (MFCC, spectral analysis)
- **Cue Point Detection**: LSTM neural network
- **Tempo Normalization**: pyrubberband (pitch-preserving)
- **MCP Integration**: mcp Python SDK

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## Credits

Based on research from:
- [AI-DJ-Mix-Generator](https://github.com/sycomix/AI-DJ-Mix-Generator)
- [madmom](https://github.com/CPJKU/madmom) - Beat detection library

## License

MIT License
