#!/usr/bin/env python3
"""
Quick test script for AI DJ MCP Server track analysis.

Usage:
    python test_track_analysis.py /path/to/audio/file.wav
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_dj_mcp.track import Track
from ai_dj_mcp.cue_detector import CuePointDetector, create_dummy_model, create_dummy_scaler


def test_track_analysis(audio_path: str):
    """Test basic track analysis."""
    print(f"\n{'='*60}")
    print(f"Testing Track Analysis: {Path(audio_path).name}")
    print(f"{'='*60}\n")

    # Create track
    track = Track(audio_path)

    # Load audio
    print("Loading audio...")
    track.load_audio()
    print(f"  ✓ Loaded: {track.duration:.2f} seconds")

    # Detect beats
    print("\nDetecting beats and tempo...")
    beats, tempo = track.detect_beats()
    print(f"  ✓ BPM: {tempo:.1f}")
    print(f"  ✓ Beats detected: {len(beats)}")

    # Detect downbeats
    print("\nDetecting downbeats...")
    downbeats = track.detect_downbeats()
    print(f"  ✓ Downbeats detected: {len(downbeats)}")

    # Extract features
    print("\nExtracting features...")
    features = track.extract_features_for_beats()
    print(f"  ✓ Feature shape: {features['beat_features'].shape}")

    # Test cue point detection (with dummy model)
    print("\nTesting cue point detection (dummy model)...")
    detector = CuePointDetector()
    detector.model = create_dummy_model()
    detector.scaler = create_dummy_scaler()

    cue_times, cue_indices, confidences = detector.predict_cue_points(
        features['beat_features'],
        beats,
        num_cues=8
    )

    print(f"  ✓ Detected {len(cue_times)} cue points:")
    for i, (time, conf) in enumerate(zip(cue_times, confidences)):
        minutes = int(time // 60)
        seconds = time % 60
        print(f"    Cue {i+1}: {minutes}:{seconds:05.2f} (confidence: {conf:.3f})")

    # Detect intro/outro
    intro_outro = detector.detect_intro_outro(cue_times, track.duration)
    print(f"\n  Intro/Outro markers:")
    print(f"    Intro Start: {intro_outro['intro_start']:.2f}s")
    print(f"    Intro End: {intro_outro['intro_end']:.2f}s")
    print(f"    Outro Start: {intro_outro['outro_start']:.2f}s")
    print(f"    Outro End: {intro_outro['outro_end']:.2f}s")

    print(f"\n{'='*60}")
    print("✓ All tests passed!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_track_analysis.py <audio_file.wav>")
        print("\nExample:")
        print("  python test_track_analysis.py /path/to/track.wav")
        sys.exit(1)

    audio_path = sys.argv[1]

    if not Path(audio_path).exists():
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    try:
        test_track_analysis(audio_path)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
