"""AI DJ MCP Server - Provides DJ mixing tools via Model Context Protocol."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.types import Tool, TextContent, ErrorData, INTERNAL_ERROR

from .track import Track
from .cue_detector import CuePointDetector, create_dummy_model, create_dummy_scaler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-dj-mcp")

# Initialize MCP server
app = Server("ai-dj")

# Global cue detector instance
cue_detector: Optional[CuePointDetector] = None


def init_cue_detector():
    """Initialize the cue point detector with dummy model if no trained model available."""
    global cue_detector
    try:
        # Try to load pre-trained model (if available)
        # In production, these would point to actual trained model files
        model_path = Path(__file__).parent / "models" / "lstm_model.pth"
        scaler_path = Path(__file__).parent / "models" / "scaler.joblib"

        if model_path.exists() and scaler_path.exists():
            cue_detector = CuePointDetector(str(model_path), str(scaler_path))
            logger.info("Loaded pre-trained cue detection model")
        else:
            # Use dummy model for testing
            cue_detector = CuePointDetector()
            dummy_model = create_dummy_model()
            dummy_scaler = create_dummy_scaler()
            cue_detector.model = dummy_model
            cue_detector.scaler = dummy_scaler
            logger.warning("Using dummy cue detection model (no pre-trained model found)")

    except Exception as e:
        logger.error(f"Failed to initialize cue detector: {e}")
        cue_detector = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available DJ tools."""
    return [
        Tool(
            name="analyze_track",
            description=(
                "Comprehensive audio track analysis including BPM detection, beat detection, "
                "downbeat detection, and feature extraction. Returns detailed metadata about "
                "the track's rhythmic structure and musical characteristics."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "description": "Absolute path to audio file (WAV, AIFF, MP3, FLAC, etc.)"
                    },
                    "extract_features": {
                        "type": "boolean",
                        "description": "Extract 24-dimensional feature vectors at each beat (default: false)",
                        "default": False
                    }
                },
                "required": ["audio_path"]
            }
        ),
        Tool(
            name="detect_cue_points",
            description=(
                "AI-powered cue point detection using LSTM neural networks. Analyzes the track's "
                "features and suggests optimal cue points for DJ mixing, including intro/outro "
                "markers suitable for extended blends."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "description": "Absolute path to audio file"
                    },
                    "num_cues": {
                        "type": "integer",
                        "description": "Number of cue points to detect (default: 12)",
                        "default": 12
                    },
                    "align_to_phrase": {
                        "type": "boolean",
                        "description": "Align cues to 4-beat musical phrases (default: true)",
                        "default": True
                    }
                },
                "required": ["audio_path"]
            }
        ),
        Tool(
            name="suggest_transitions",
            description=(
                "Analyze two tracks and suggest optimal transition points based on BPM compatibility, "
                "energy matching, and cue point alignment. Useful for planning extended blends and "
                "seamless transitions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "track1_path": {
                        "type": "string",
                        "description": "Path to first (outgoing) track"
                    },
                    "track2_path": {
                        "type": "string",
                        "description": "Path to second (incoming) track"
                    },
                    "blend_duration": {
                        "type": "number",
                        "description": "Desired blend duration in seconds (default: 60)",
                        "default": 60
                    }
                },
                "required": ["track1_path", "track2_path"]
            }
        ),
        Tool(
            name="extract_features",
            description=(
                "Extract detailed 24-dimensional feature vectors from an audio track. "
                "Features include MFCC, spectral contrast, spectral centroid/rolloff/flux, "
                "and RMS energy at each beat. Useful for advanced analysis and ML applications."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "description": "Absolute path to audio file"
                    }
                },
                "required": ["audio_path"]
            }
        ),
        Tool(
            name="calculate_bpm_compatibility",
            description=(
                "Calculate BPM compatibility between two tracks, considering tempo ratios "
                "(1:1, 2:1, 1:2) and suggesting whether they can be mixed together. "
                "Essential for beatmatching and harmonic mixing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "bpm1": {
                        "type": "number",
                        "description": "BPM of first track"
                    },
                    "bpm2": {
                        "type": "number",
                        "description": "BPM of second track"
                    },
                    "tolerance": {
                        "type": "number",
                        "description": "BPM tolerance percentage (default: 6%)",
                        "default": 6.0
                    }
                },
                "required": ["bpm1", "bpm2"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "analyze_track":
            return await analyze_track(
                arguments["audio_path"],
                arguments.get("extract_features", False)
            )

        elif name == "detect_cue_points":
            return await detect_cue_points(
                arguments["audio_path"],
                arguments.get("num_cues", 12),
                arguments.get("align_to_phrase", True)
            )

        elif name == "suggest_transitions":
            return await suggest_transitions(
                arguments["track1_path"],
                arguments["track2_path"],
                arguments.get("blend_duration", 60)
            )

        elif name == "extract_features":
            return await extract_features_tool(arguments["audio_path"])

        elif name == "calculate_bpm_compatibility":
            return await calculate_bpm_compatibility(
                arguments["bpm1"],
                arguments["bpm2"],
                arguments.get("tolerance", 6.0)
            )

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error in {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def analyze_track(audio_path: str, extract_features: bool = False) -> list[TextContent]:
    """Analyze track: detect BPM, beats, downbeats, and optionally extract features."""
    track = Track(audio_path)

    # Load audio
    track.load_audio()

    # Detect beats and tempo
    beats, tempo = track.detect_beats()

    # Detect downbeats
    downbeats = track.detect_downbeats()

    # Extract features if requested
    if extract_features:
        track.extract_features_for_beats()

    # Build response
    analysis = track.to_dict()

    result = f"""Track Analysis: {track.name}

Duration: {analysis['duration']:.2f} seconds
BPM: {analysis['tempo']:.1f}
Beats detected: {analysis['num_beats']}
Downbeats detected: {analysis['num_downbeats']}

First 10 beats (seconds): {', '.join(f'{b:.2f}' for b in beats[:10])}
First 5 downbeats (seconds): {', '.join(f'{d:.2f}' for d in downbeats[:5])}
"""

    if extract_features:
        result += f"\nFeature vectors extracted: {track.features['beat_features'].shape}"

    return [TextContent(type="text", text=result)]


async def detect_cue_points(
    audio_path: str,
    num_cues: int = 12,
    align_to_phrase: bool = True
) -> list[TextContent]:
    """Detect optimal cue points using LSTM model."""
    if cue_detector is None:
        init_cue_detector()

    if cue_detector is None:
        raise ValueError("Cue detector not available")

    # Analyze track
    track = Track(audio_path)
    track.load_audio()
    track.detect_beats()
    track.extract_features_for_beats()

    # Predict cue points
    cue_times, cue_indices, confidences = cue_detector.predict_cue_points(
        track.features['beat_features'],
        track.beats,
        num_cues=num_cues,
        align_to_phrase=align_to_phrase
    )

    # Store in track
    track.cue_points = cue_times
    track.cue_points_indices = cue_indices

    # Detect intro/outro
    intro_outro = cue_detector.detect_intro_outro(cue_times, track.duration)

    # Build response
    result = f"""Cue Point Detection: {track.name}

Detected {len(cue_times)} optimal cue points:

"""

    for i, (time, conf) in enumerate(zip(cue_times, confidences)):
        minutes = int(time // 60)
        seconds = time % 60
        result += f"  Cue {i+1}: {minutes}:{seconds:05.2f} (confidence: {conf:.3f})\n"

    result += f"""
Suggested Intro/Outro Markers:
  Intro Start: {intro_outro['intro_start']:.2f}s
  Intro End: {intro_outro['intro_end']:.2f}s
  Outro Start: {intro_outro['outro_start']:.2f}s
  Outro End: {intro_outro['outro_end']:.2f}s

These markers are suitable for extended blends (60-90 seconds).
"""

    return [TextContent(type="text", text=result)]


async def suggest_transitions(
    track1_path: str,
    track2_path: str,
    blend_duration: float = 60
) -> list[TextContent]:
    """Suggest optimal transition between two tracks."""
    # Analyze both tracks
    track1 = Track(track1_path)
    track1.load_audio()
    track1.detect_beats()

    track2 = Track(track2_path)
    track2.load_audio()
    track2.detect_beats()

    # Calculate BPM compatibility
    bpm_ratio = track1.tempo / track2.tempo
    compatible = 0.94 <= bpm_ratio <= 1.06 or 1.88 <= bpm_ratio <= 2.12 or 0.47 <= bpm_ratio <= 0.53

    # Calculate transition points
    blend_start_track1 = track1.duration - blend_duration
    blend_start_track2 = 0

    result = f"""Transition Analysis

Track 1: {track1.name}
  BPM: {track1.tempo:.1f}
  Duration: {track1.duration:.2f}s

Track 2: {track2.name}
  BPM: {track2.tempo:.1f}
  Duration: {track2.duration:.2f}s

BPM Compatibility:
  Ratio: {bpm_ratio:.3f}
  Compatible: {"✓ Yes" if compatible else "✗ No - consider tempo adjustment"}

Suggested Transition ({blend_duration}s blend):
  Start fading out Track 1 at: {blend_start_track1:.2f}s ({blend_start_track1/60:.1f}min)
  Start fading in Track 2 at: {blend_start_track2:.2f}s (from beginning)

Mixing Strategy:
"""

    if compatible:
        if 0.94 <= bpm_ratio <= 1.06:
            result += "  - Beatmatch at 1:1 ratio\n"
        elif 1.88 <= bpm_ratio <= 2.12:
            result += "  - Beatmatch at 2:1 ratio (halftime mix)\n"
        else:
            result += "  - Beatmatch at 1:2 ratio (double-time mix)\n"

        result += f"  - Use extended blend ({blend_duration}s) for smooth textural transition\n"
        result += "  - Gradually swap EQ (bass out on Track 1, bass in on Track 2)\n"
        result += "  - Layer atmospheric elements during blend\n"
    else:
        result += "  - Consider tempo adjustment or quick cut\n"
        result += f"  - To match: adjust Track 2 to {track1.tempo:.1f} BPM\n"

    return [TextContent(type="text", text=result)]


async def extract_features_tool(audio_path: str) -> list[TextContent]:
    """Extract 24-dimensional feature vectors."""
    track = Track(audio_path)
    track.load_audio()
    track.detect_beats()
    features = track.extract_features_for_beats()

    feat_array = features['beat_features']

    result = f"""Feature Extraction: {track.name}

Extracted {feat_array.shape[0]} feature vectors (24 dimensions each)

Feature breakdown per beat:
  - 13 MFCC coefficients
  - 7 Spectral Contrast bands
  - 1 Spectral Centroid
  - 1 Spectral Rolloff
  - 1 Spectral Flux
  - 1 RMS Energy

Total shape: {feat_array.shape}

Sample features (first beat):
  MFCCs: {feat_array[0, :13]}
  Spectral Contrast: {feat_array[0, 13:20]}
  Other: {feat_array[0, 20:]}
"""

    return [TextContent(type="text", text=result)]


async def calculate_bpm_compatibility(
    bpm1: float,
    bpm2: float,
    tolerance: float = 6.0
) -> list[TextContent]:
    """Calculate BPM compatibility between two tracks."""
    ratio = bpm1 / bpm2
    tolerance_decimal = tolerance / 100.0

    # Check various ratios
    compatible_1_1 = abs(ratio - 1.0) <= tolerance_decimal
    compatible_2_1 = abs(ratio - 2.0) <= tolerance_decimal
    compatible_1_2 = abs(ratio - 0.5) <= tolerance_decimal

    result = f"""BPM Compatibility Analysis

Track 1 BPM: {bpm1:.1f}
Track 2 BPM: {bpm2:.1f}
Ratio: {ratio:.3f}
Tolerance: ±{tolerance}%

Compatibility:
"""

    if compatible_1_1:
        result += f"  ✓ 1:1 mixing (direct beatmatch)\n"
        result += f"    Tempo adjustment needed: {abs(bpm1 - bpm2):.1f} BPM\n"

    if compatible_2_1:
        result += f"  ✓ 2:1 mixing (halftime)\n"
        result += f"    Track 1 plays at double-time relative to Track 2\n"

    if compatible_1_2:
        result += f"  ✓ 1:2 mixing (double-time)\n"
        result += f"    Track 2 plays at double-time relative to Track 1\n"

    if not (compatible_1_1 or compatible_2_1 or compatible_1_2):
        result += f"  ✗ Not compatible within {tolerance}% tolerance\n"
        result += f"\nSuggestions:\n"
        result += f"  - Adjust Track 2 to {bpm1:.1f} BPM for 1:1 mix\n"
        result += f"  - Adjust Track 2 to {bpm1/2:.1f} BPM for 2:1 mix\n"
        result += f"  - Adjust Track 2 to {bpm1*2:.1f} BPM for 1:2 mix\n"

    return [TextContent(type="text", text=result)]


async def main():
    """Run the MCP server."""
    logger.info("Starting AI DJ MCP Server...")

    # Initialize cue detector
    init_cue_detector()

    # Run the server
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
