# Mixxx AI DJ Controller - Installation Guide

Complete step-by-step installation for the automated DJ performance system.

---

## Prerequisites

### 1. Install Mixxx

**macOS:**
```bash
brew install --cask mixxx
```

Or download from: https://mixxx.org/download/

**Minimum version:** Mixxx 2.3 or higher

### 2. Verify Python

```bash
python3 --version
```

Should show Python 3.10 or higher.

---

## Step 1: Locate Mixxx Controllers Directory

### macOS
```bash
mkdir -p ~/Library/Application\ Support/Mixxx/controllers/
cd ~/Library/Application\ Support/Mixxx/controllers/
```

### Linux
```bash
mkdir -p ~/.mixxx/controllers/
cd ~/.mixxx/controllers/
```

### Windows
```cmd
mkdir %LOCALAPPDATA%\Mixxx\controllers
cd %LOCALAPPDATA%\Mixxx\controllers
```

---

## Step 2: Install Controller Files

### Copy Files to Mixxx

```bash
cp "/Users/dantaylor/Claude/Last Night an AI Saved My Life/mixxx-controller/AI_DJ_Controller.js" \
   ~/Library/Application\ Support/Mixxx/controllers/

cp "/Users/dantaylor/Claude/Last Night an AI Saved My Life/mixxx-controller/AI_DJ_Controller.midi.xml" \
   ~/Library/Application\ Support/Mixxx/controllers/
```

### Verify Installation

```bash
ls -la ~/Library/Application\ Support/Mixxx/controllers/AI_DJ*
```

You should see:
```
AI_DJ_Controller.js
AI_DJ_Controller.midi.xml
```

---

## Step 3: Enable in Mixxx

1. **Open Mixxx**

2. **Open Preferences**
   - macOS: `Mixxx > Preferences` or `Cmd+,`
   - Windows/Linux: `Options > Preferences`

3. **Go to Controllers**
   - Click **Controllers** in the left sidebar

4. **Enable AI DJ Controller**
   - Find **AI DJ Controller** in the list
   - Check the box to enable it
   - Click **OK**

5. **Restart Mixxx** (recommended)

---

## Step 4: Test the Controller

### Open Developer Console

- macOS: `Cmd+D`
- Windows/Linux: `Ctrl+D`

### Test Basic Functions

```javascript
// Check if controller is loaded
typeof AI_DJ_Controller

// Should output: "object"

// Check configuration
AI_DJ_Controller.config

// Should show configuration object
```

If you see `"object"`, the controller is installed correctly! ✅

---

## Step 5: Import Your Music

### Add Music to Mixxx Library

1. In Mixxx, go to **Library**
2. Click **Browse** in the sidebar
3. Navigate to `/Volumes/TRAKTOR/Traktor/Music`
4. Drag folders into the library

### Analyze Tracks

1. Select all tracks (Cmd+A / Ctrl+A)
2. Right-click > **Analyze**
3. Wait for BPM and beat grid analysis to complete

**Note:** This is important for beatmatching to work!

---

## Step 6: Generate Your First Playlist

### Using Track Selection Engine

```bash
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/track-selection-engine"

PYTHONPATH=src python3 -m track_selector.cli generate 60 \
  --library traktor-library-detailed.json \
  --output my-first-ai-set \
  --progression gradual_build \
  --blend 60 \
  --min-bpm 120 \
  --max-bpm 126
```

This creates `my-first-ai-set.json` (60-minute set)

---

## Step 7: Convert for Mixxx

```bash
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/mixxx-controller"

python3 playlist_loader.py ../track-selection-engine/my-first-ai-set.json
```

This creates:
- `my-first-ai-set.mixxx.js` - Playlist loader
- `my-first-ai-set.ai-dj.m3u` - M3U playlist

---

## Step 8: Load and Test

### Method A: Developer Console (Recommended for First Test)

1. Open Mixxx
2. Press **Cmd+D** (macOS) or **Ctrl+D** (Windows/Linux)
3. In console, type:

```javascript
load("/Users/dantaylor/Claude/Last Night an AI Saved My Life/mixxx-controller/my-first-ai-set.mixxx.js");
```

4. You should see:
```
Playlist loaded: my-first-ai-set
Total tracks: X
```

5. **Don't start yet!** First, manually load a few tracks to test.

### Method B: M3U Import

1. In Mixxx, right-click **Playlists**
2. Select **Import Playlist**
3. Choose `my-first-ai-set.ai-dj.m3u`
4. Tracks will appear in a new playlist

---

## Step 9: Manual Test

**Before running automated mode, test manually:**

1. Load first track from playlist on Deck 1
2. Load second track on Deck 2
3. Press **Sync** button on Deck 2
4. Start both decks playing
5. Use crossfader to mix between them

If this works smoothly, you're ready for automated mode!

---

## Step 10: Run Automated DJ

### Start Performance

In Mixxx developer console:

```javascript
// Start the AI DJ
AI_DJ_Controller.start();
```

### Monitor Performance

Watch the console for log messages:
```
[AI_DJ] Starting automated DJ performance...
[AI_DJ] Loading track 1/X
[AI_DJ] Artist: ...
[AI_DJ] Title: ...
```

### Stop if Needed

```javascript
AI_DJ_Controller.stop();
```

---

## Troubleshooting

### "Controller not found"

**Problem:** AI DJ Controller doesn't appear in Mixxx preferences

**Solution:**
1. Verify both `.js` and `.midi.xml` files are in controllers directory
2. Check filenames match exactly: `AI_DJ_Controller.js` and `AI_DJ_Controller.midi.xml`
3. Restart Mixxx completely

### "load() function not found"

**Problem:** `load()` command doesn't work in console

**Solution:**
- Use full path to file
- Or copy/paste the contents of `.mixxx.js` directly into console

### "Tracks not loading"

**Problem:** Tracks don't load during automated mode

**Solution:**
- Currently, you must pre-load tracks manually or import M3U playlist
- Ensure tracks are in Mixxx library
- Check that file paths in playlist JSON match actual files

### "Beatmatch not working"

**Problem:** Tracks play at different tempos

**Solution:**
1. Ensure tracks are analyzed in Mixxx (**Analyze** button)
2. Check beat grids are correct (visual waveform should align)
3. Verify BPM detection matches your playlist data
4. Try manual sync first to test

### "Crossfade too fast/slow"

**Problem:** Transitions feel rushed or dragged out

**Solution:**
```javascript
// Adjust blend duration (in seconds)
AI_DJ_Controller.config.blendDuration = 75;
```

Or regenerate playlist with different `--blend` parameter.

---

## Quick Reference

### Mixxx Controllers Directory

- **macOS:** `~/Library/Application Support/Mixxx/controllers/`
- **Linux:** `~/.mixxx/controllers/`
- **Windows:** `%LOCALAPPDATA%\Mixxx\controllers`

### Key Commands

```javascript
// Load playlist
load("/path/to/playlist.mixxx.js");

// Start AI DJ
AI_DJ_Controller.start();

// Stop AI DJ
AI_DJ_Controller.stop();

// Adjust blend duration
AI_DJ_Controller.config.blendDuration = 90;
```

---

## Next Steps

1. ✅ Install Mixxx
2. ✅ Copy controller files
3. ✅ Enable in Mixxx
4. ✅ Import music
5. ✅ Analyze tracks
6. ✅ Generate playlist
7. ✅ Convert for Mixxx
8. ✅ Test manually
9. ✅ Run automated!

---

**You're ready for your first automated DJ set!** 🎧🚀

Start with a short 30-60 minute playlist to test, then build up to full 3-hour journeys.
