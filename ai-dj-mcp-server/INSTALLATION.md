# AI DJ MCP Server - Installation Guide

Complete step-by-step guide to install and configure the AI DJ MCP Server for use with Claude Desktop.

---

## Prerequisites

### 1. System Requirements

- **Python 3.10 or higher**
- **macOS, Windows, or Linux**
- **At least 2GB of free RAM**
- **ffmpeg** (for audio processing)

### 2. Install Python Dependencies

First, verify Python version:

```bash
python3 --version
```

Should show Python 3.10 or higher.

### 3. Install ffmpeg

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

---

## Installation Steps

### Step 1: Navigate to Server Directory

```bash
cd /path/to/ai-dj-mcp-server
```

Replace `/path/to/` with the actual path to this directory.

### Step 2: Install the Package

```bash
pip install -e .
```

This installs the package in "editable" mode, allowing you to modify the code.

### Step 3: Verify Installation

Test that the server can be imported:

```bash
python3 -c "from ai_dj_mcp import server; print('Installation successful!')"
```

---

## Configure Claude Desktop

### Step 1: Find Configuration File

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Step 2: Edit Configuration

Open the configuration file and add the AI DJ server:

```json
{
  "mcpServers": {
    "ai-dj": {
      "command": "python3",
      "args": [
        "-m",
        "ai_dj_mcp.server"
      ],
      "cwd": "/absolute/path/to/ai-dj-mcp-server/src"
    }
  }
}
```

**Important:** Replace `/absolute/path/to/ai-dj-mcp-server/src` with the actual absolute path to the `src` directory.

**Example for macOS:**
```json
{
  "mcpServers": {
    "ai-dj": {
      "command": "python3",
      "args": [
        "-m",
        "ai_dj_mcp.server"
      ],
      "cwd": "/Users/dantaylor/Claude/Last Night an AI Saved My Life/ai-dj-mcp-server/src"
    }
  }
}
```

### Step 3: Get Absolute Path

To find the absolute path:

```bash
cd ai-dj-mcp-server/src
pwd
```

Copy the output and paste it into the `cwd` field.

### Step 4: Restart Claude Desktop

Completely quit and restart Claude Desktop for changes to take effect.

---

## Verify MCP Server is Running

After restarting Claude Desktop:

1. Open a new conversation with Claude
2. Ask: **"What MCP tools do you have available?"**
3. Claude should list the AI DJ tools:
   - `analyze_track`
   - `detect_cue_points`
   - `suggest_transitions`
   - `extract_features`
   - `calculate_bpm_compatibility`

---

## Test with Sample Audio

### Option A: Use Your Own Tracks

Ask Claude to analyze one of your tracks:

```
Analyze the track at /path/to/your/track.wav
```

### Option B: Download Sample Audio

Download a Creative Commons licensed track:

```bash
# Example: download a sample track
curl -o test-track.wav https://example.com/sample.wav
```

Then ask Claude:

```
Analyze the track at /absolute/path/to/test-track.wav
```

---

## Troubleshooting

### Issue: "Command not found: python3"

**Solution:** Use `python` instead of `python3` in the config:

```json
"command": "python",
```

### Issue: "Module 'ai_dj_mcp' not found"

**Solution:** Verify installation:

```bash
cd ai-dj-mcp-server
pip install -e .
```

Check that `cwd` points to the `src` directory (not the root).

### Issue: "librosa not installed"

**Solution:** Install missing dependencies:

```bash
pip install librosa soundfile numpy scipy torch scikit-learn pydub joblib
```

### Issue: Server not showing in Claude Desktop

**Solution:**

1. Check configuration file syntax (valid JSON)
2. Verify absolute paths (no `~` or relative paths)
3. Completely quit Claude Desktop (not just close window)
4. Check Claude Desktop logs:
   - **macOS:** `~/Library/Logs/Claude/`
   - **Windows:** `%APPDATA%\Claude\logs\`

### Issue: "No pre-trained model found" warning

**Expected behavior:** The server will use a dummy model for testing. This is normal and doesn't affect basic functionality. For production use, you would train and load a real LSTM model.

---

## Advanced Configuration

### Using a Custom Model

If you have a trained LSTM model:

1. Create `models` directory:
```bash
mkdir -p ai-dj-mcp-server/src/ai_dj_mcp/models
```

2. Place your files:
   - `lstm_model.pth` - PyTorch model weights
   - `scaler.joblib` - Feature scaler

3. Restart Claude Desktop

### Adjust Logging Level

Edit `src/ai_dj_mcp/server.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
# or
logging.basicConfig(level=logging.WARNING)  # Less verbose
```

---

## Next Steps

Once installed, you can:

1. **Analyze your track library** - Get BPM, beats, and cue points
2. **Plan transitions** - Find compatible tracks for mixing
3. **Extract features** - Use ML features for advanced analysis
4. **Build playlists** - Use compatibility data to create journey arcs

---

## Uninstallation

To remove the server:

1. Remove from Claude Desktop config:
   - Delete the `"ai-dj"` entry from `claude_desktop_config.json`

2. Uninstall Python package:
```bash
pip uninstall ai-dj-mcp-server
```

3. Delete directory:
```bash
rm -rf /path/to/ai-dj-mcp-server
```

---

## Support

For issues or questions:

- Check the main [README.md](README.md)
- Review error messages in Claude Desktop logs
- Verify all prerequisites are installed

---

**You're all set!** The AI DJ MCP Server is now ready to analyze tracks and help you build perfect DJ sets.
