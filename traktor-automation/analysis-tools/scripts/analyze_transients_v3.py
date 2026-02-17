#!/usr/bin/env python3
"""
Traktor transients parser - Pattern-based approach.

Based on observation:
- 0x43 bytes appear regularly, often followed by 00 00 00
- These might be record markers
- The 8 bytes before 0x43 might be two floats representing beat info
"""

import struct
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def find_beat_markers(data):
    """Find positions of potential beat record markers."""
    # Look for 0x43 00 00 00 pattern
    markers = []

    for i in range(len(data) - 3):
        if data[i] == 0x43 and data[i+1] == 0x00 and data[i+2] == 0x00 and data[i+3] == 0x00:
            markers.append(i)

    return markers


def parse_beats_from_markers(data, markers):
    """Parse beat data based on identified markers."""
    beats = []

    for i, marker_pos in enumerate(markers):
        # The 8 bytes before the marker might be two floats
        if marker_pos >= 8:
            try:
                # Extract the 8 bytes before 0x43 00 00 00
                beat_data = data[marker_pos-8:marker_pos]

                # Parse as two 32-bit floats
                float1, float2 = struct.unpack('<ff', beat_data)

                # Basic sanity check - beat positions should be reasonable
                if 0 <= float1 <= 10000 and -10 <= float2 <= 10:
                    beats.append({
                        'position': float1,
                        'strength': float2,
                        'marker_offset': marker_pos
                    })

            except struct.error:
                continue

    return beats


def analyze_beats(beats):
    """Analyze the parsed beat data."""
    if len(beats) < 2:
        return None

    positions = [b['position'] for b in beats]
    strengths = [b['strength'] for b in beats]

    # Calculate intervals between beats
    intervals = np.diff(positions)
    valid_intervals = intervals[(intervals > 0.1) & (intervals < 2.0)]

    if len(valid_intervals) > 0:
        avg_interval = np.mean(valid_intervals)
        bpm = 60.0 / avg_interval if avg_interval > 0 else 0
    else:
        avg_interval = 0
        bpm = 0

    return {
        'total_beats': len(beats),
        'duration': positions[-1] if positions else 0,
        'avg_interval': avg_interval,
        'estimated_bpm': bpm,
        'position_range': (min(positions), max(positions)),
        'strength_range': (min(strengths), max(strengths))
    }


def find_downbeats(beats, beats_per_bar=4):
    """Identify potential downbeats (first beat of each bar)."""
    if len(beats) < beats_per_bar:
        return []

    downbeats = []

    # Group beats by bars and find strongest in each group
    for i in range(0, len(beats), beats_per_bar):
        bar_beats = beats[i:i+beats_per_bar]
        if bar_beats:
            # Find the beat with highest strength in this bar
            strongest = max(bar_beats, key=lambda b: b['strength'])
            downbeats.append(strongest)

    return downbeats


def suggest_cue_points_from_beats(beats, track_duration=None):
    """Suggest cue points based on beat positions."""
    if not beats:
        return []

    cue_points = []

    # First beat (track start / load point)
    if beats:
        cue_points.append({
            'name': 'First Beat',
            'position': beats[0]['position'],
            'type': 'load',
            'description': 'First detected beat - good load point'
        })

    # Find potential phrase starts (every 16 or 32 beats)
    phrase_lengths = [16, 32]

    for phrase_len in phrase_lengths:
        for i in range(0, len(beats), phrase_len):
            if i > 0 and i < len(beats):  # Skip first beat (already added)
                cue_points.append({
                    'name': f'{phrase_len}-beat phrase',
                    'position': beats[i]['position'],
                    'type': 'phrase',
                    'description': f'Start of {phrase_len}-beat phrase'
                })

    # Find strong beats (potential downbeats or accents)
    strengths = [b['strength'] for b in beats]
    mean_strength = np.mean(strengths)
    std_strength = np.std(strengths)
    strong_threshold = mean_strength + 1.5 * std_strength

    for beat in beats:
        if beat['strength'] > strong_threshold:
            cue_points.append({
                'name': 'Strong Beat',
                'position': beat['position'],
                'type': 'accent',
                'description': f'High-strength beat (strength: {beat["strength"]:.3f})'
            })

    # Sort by position and limit to avoid too many cue points
    cue_points.sort(key=lambda x: x['position'])

    # Limit to reasonable number
    return cue_points[:20]


def visualize_beats(beats, downbeats=None):
    """Visualize beat timing and strength."""
    if not beats:
        print("No beats to visualize")
        return

    positions = [b['position'] for b in beats]
    strengths = [b['strength'] for b in beats]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8))

    # Plot beat strengths
    ax1.scatter(positions, strengths, alpha=0.5, s=10, c='blue', label='Beats')

    if downbeats:
        db_positions = [db['position'] for db in downbeats]
        db_strengths = [db['strength'] for db in downbeats]
        ax1.scatter(db_positions, db_strengths, alpha=0.8, s=50, c='red',
                   marker='^', label='Downbeats', zorder=5)

    ax1.set_title('Beat Detection - Strength Over Time')
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Beat Strength')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot beat intervals (tempo stability)
    if len(positions) > 1:
        intervals = np.diff(positions)

        ax2.plot(positions[1:], intervals, linewidth=0.5, alpha=0.7)
        ax2.set_title('Beat Intervals (Tempo Stability)')
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Interval (seconds)')
        ax2.grid(True, alpha=0.3)

        # Add average line
        valid_intervals = intervals[(intervals > 0.1) & (intervals < 2.0)]
        if len(valid_intervals) > 0:
            avg_interval = np.mean(valid_intervals)
            ax2.axhline(y=avg_interval, color='r', linestyle='--',
                       label=f'Average: {avg_interval:.3f}s ({60/avg_interval:.1f} BPM)')
            ax2.legend()

    plt.tight_layout()
    plt.savefig('/Users/dantaylor/Claude/Anima-in-Machina/analysis/transients_beats.png', dpi=150)
    print("Visualization saved to analysis/transients_beats.png")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_transients_v3.py <path_to_transients_file>")
        return

    transients_path = Path(sys.argv[1]).expanduser()

    if not transients_path.exists():
        print(f"Error: File not found: {transients_path}")
        return

    print(f"Analyzing transients file: {transients_path.name}")
    print(f"File size: {transients_path.stat().st_size} bytes")

    with open(transients_path, 'rb') as f:
        data = f.read()

    # Find beat markers
    print("\n=== Finding Beat Markers ===")
    markers = find_beat_markers(data)
    print(f"Found {len(markers)} potential beat markers")

    # Parse beats
    print("\n=== Parsing Beat Data ===")
    beats = parse_beats_from_markers(data, markers)
    print(f"Extracted {len(beats)} beats")

    if beats:
        # Analyze
        print("\n=== Beat Analysis ===")
        analysis = analyze_beats(beats)

        if analysis:
            print(f"Total beats: {analysis['total_beats']}")
            print(f"Duration: {analysis['duration']:.2f} seconds")
            print(f"Average interval: {analysis['avg_interval']:.3f} seconds")
            print(f"Estimated BPM: {analysis['estimated_bpm']:.2f}")
            print(f"Position range: {analysis['position_range'][0]:.2f}s - {analysis['position_range'][1]:.2f}s")
            print(f"Strength range: {analysis['strength_range'][0]:.3f} - {analysis['strength_range'][1]:.3f}")

        # Find downbeats
        print("\n=== Downbeat Detection ===")
        downbeats = find_downbeats(beats)
        print(f"Identified {len(downbeats)} potential downbeats")

        # Show samples
        print("\n=== Sample Beat Data (first 10) ===")
        for i, beat in enumerate(beats[:10]):
            print(f"Beat {i+1}: Position={beat['position']:.3f}s, Strength={beat['strength']:.3f}")

        # Suggest cue points
        print("\n=== Suggested Cue Points ===")
        cue_points = suggest_cue_points_from_beats(beats)
        for cue in cue_points[:10]:  # Show first 10
            print(f"{cue['name']:20s} @ {cue['position']:7.2f}s - {cue['description']}")

        # Visualize
        print("\n=== Creating Visualization ===")
        Path('/Users/dantaylor/Claude/Anima-in-Machina/analysis').mkdir(exist_ok=True)
        visualize_beats(beats, downbeats)

        # Save results
        output_file = Path('/Users/dantaylor/Claude/Anima-in-Machina/analysis/transients_beats.txt')
        with open(output_file, 'w') as f:
            f.write(f"Transients Analysis for: {transients_path.name}\n\n")
            f.write(f"Total beats: {len(beats)}\n")
            f.write(f"Duration: {analysis['duration']:.2f}s\n")
            f.write(f"Estimated BPM: {analysis['estimated_bpm']:.2f}\n\n")

            f.write("Beat Positions (first 50):\n")
            for i, beat in enumerate(beats[:50]):
                f.write(f"{i+1:4d}. {beat['position']:7.2f}s (strength: {beat['strength']:.3f})\n")

        print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
