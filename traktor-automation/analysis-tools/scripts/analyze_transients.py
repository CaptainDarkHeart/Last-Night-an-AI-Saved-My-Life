#!/usr/bin/env python3
"""
Analyze Traktor transients files to understand beat detection data.

According to Native Instruments:
"The transient files contain beat information which is essential for
Beatgridding and Syncing your tracks."

This likely contains:
- Beat positions (timestamps)
- Beat strengths (confidence/amplitude)
- Tempo information
- Potentially downbeat markers
"""

import struct
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def parse_transients_file(data):
    """
    Parse the transients file to extract beat information.

    The file appears to contain floating-point data representing:
    - Beat timestamps
    - Beat strengths/confidence
    - Additional metadata
    """
    # Looking at the hexdump, the data appears to be structured as records
    # Each record might contain multiple float values

    # Try parsing as 32-bit floats (4 bytes each)
    # Format: '<f' = little-endian float

    num_floats = len(data) // 4
    floats = struct.unpack(f'<{num_floats}f', data[:num_floats * 4])

    # The pattern in the hexdump suggests records of varying length
    # Let's try to identify the structure

    # Looking at patterns like:
    # 05 e7 0f 00 00 00 00 00  e0 d7 bf aa 3f df d7 27
    # This could be: [timestamp][confidence][value1][value2]

    beats = []

    # Try interpreting as records with a specific structure
    # Based on the hex dump, there seem to be patterns every ~16-20 bytes

    # Let's try parsing as groups of 4-5 floats
    for i in range(0, len(floats) - 4, 5):
        # Potential structure:
        # float1: timestamp (increasing values suggest this)
        # float2: beat strength/confidence
        # float3: additional info
        # float4: additional info
        # float5: metadata

        beats.append({
            'timestamp': floats[i],
            'strength': floats[i+1],
            'value2': floats[i+2],
            'value3': floats[i+3],
            'value4': floats[i+4] if i+4 < len(floats) else 0
        })

    return beats


def analyze_beat_pattern(beats):
    """Analyze the beat pattern to understand tempo and structure."""
    if len(beats) < 2:
        return None

    # Calculate intervals between beats
    timestamps = [b['timestamp'] for b in beats if b['timestamp'] > 0]

    if len(timestamps) < 2:
        return None

    intervals = np.diff(timestamps)

    # Filter out outliers (very small or very large intervals)
    valid_intervals = intervals[(intervals > 0.1) & (intervals < 2.0)]

    if len(valid_intervals) == 0:
        return None

    avg_interval = np.mean(valid_intervals)
    std_interval = np.std(valid_intervals)

    # Convert to BPM
    bpm = 60.0 / avg_interval if avg_interval > 0 else 0

    return {
        'total_beats': len(timestamps),
        'avg_interval': avg_interval,
        'std_interval': std_interval,
        'estimated_bpm': bpm,
        'duration': timestamps[-1] if timestamps else 0
    }


def detect_downbeats(beats, beats_per_bar=4):
    """
    Detect potential downbeats (first beat of each bar).

    In electronic music, typically 4 beats per bar.
    Downbeats often have higher strength/energy.
    """
    if not beats or len(beats) < beats_per_bar:
        return []

    # Extract beat strengths
    strengths = [b['strength'] for b in beats]

    # Find local maxima that could be downbeats
    downbeats = []

    for i in range(0, len(beats) - beats_per_bar, beats_per_bar):
        # Look at each group of 4 beats and find the strongest
        group = beats[i:i+beats_per_bar]
        max_idx = max(range(len(group)), key=lambda j: group[j]['strength'])

        downbeats.append({
            'index': i + max_idx,
            'timestamp': group[max_idx]['timestamp'],
            'strength': group[max_idx]['strength']
        })

    return downbeats


def visualize_transients(beats, downbeats=None):
    """Visualize the beat information."""
    if not beats:
        print("No beats to visualize")
        return

    timestamps = [b['timestamp'] for b in beats]
    strengths = [b['strength'] for b in beats]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8))

    # Plot beat strengths over time
    ax1.scatter(timestamps, strengths, alpha=0.5, s=10, c='blue', label='Beats')

    if downbeats:
        db_times = [db['timestamp'] for db in downbeats]
        db_strengths = [db['strength'] for db in downbeats]
        ax1.scatter(db_times, db_strengths, alpha=0.8, s=50, c='red',
                   marker='^', label='Potential Downbeats', zorder=5)

    ax1.set_title('Beat Detection - Transient Strength Over Time')
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Beat Strength')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot beat intervals (tempo variations)
    if len(timestamps) > 1:
        intervals = np.diff(timestamps)
        interval_times = timestamps[1:]

        ax2.plot(interval_times, intervals, linewidth=0.5, alpha=0.7)
        ax2.set_title('Beat Intervals (Tempo Stability)')
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Interval (seconds)')
        ax2.grid(True, alpha=0.3)

        # Add average line
        avg_interval = np.mean(intervals)
        ax2.axhline(y=avg_interval, color='r', linestyle='--',
                   label=f'Average: {avg_interval:.3f}s ({60/avg_interval:.1f} BPM)')
        ax2.legend()

    plt.tight_layout()
    plt.savefig('/Users/dantaylor/Claude/Anima-in-Machina/analysis/transients_visualization.png', dpi=150)
    print("Visualization saved to analysis/transients_visualization.png")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_transients.py <path_to_transients_file>")
        print("\nExample:")
        print('  python analyze_transients.py "~/Documents/Native Instruments/Traktor 3.11.1/Transients/000/ABC123"')
        return

    transients_path = Path(sys.argv[1]).expanduser()

    if not transients_path.exists():
        print(f"Error: File not found: {transients_path}")
        return

    print(f"Analyzing transients file: {transients_path.name}")
    print(f"File size: {transients_path.stat().st_size} bytes")

    # Read the file
    with open(transients_path, 'rb') as f:
        data = f.read()

    # Parse beat information
    print("\n=== Parsing Beat Data ===")
    beats = parse_transients_file(data)
    print(f"Extracted {len(beats)} potential beat markers")

    if beats:
        # Analyze beat pattern
        print("\n=== Beat Pattern Analysis ===")
        analysis = analyze_beat_pattern(beats)

        if analysis:
            print(f"Total beats detected: {analysis['total_beats']}")
            print(f"Track duration: {analysis['duration']:.2f} seconds")
            print(f"Average beat interval: {analysis['avg_interval']:.3f} seconds")
            print(f"Interval std deviation: {analysis['std_interval']:.3f} seconds")
            print(f"Estimated BPM: {analysis['estimated_bpm']:.2f}")

            # Detect downbeats
            print("\n=== Downbeat Detection ===")
            downbeats = detect_downbeats(beats)
            print(f"Detected {len(downbeats)} potential downbeats")

            if downbeats:
                print(f"\nFirst 10 downbeat positions:")
                for i, db in enumerate(downbeats[:10]):
                    print(f"  {i+1}. Time: {db['timestamp']:.2f}s, Strength: {db['strength']:.3f}")

            # Create visualization
            print("\n=== Creating Visualization ===")
            Path('/Users/dantaylor/Claude/Anima-in-Machina/analysis').mkdir(exist_ok=True)
            visualize_transients(beats, downbeats)

            # Sample some beat data for inspection
            print("\n=== Sample Beat Data ===")
            print("First 5 beats:")
            for i, beat in enumerate(beats[:5]):
                print(f"  Beat {i+1}:")
                print(f"    Timestamp: {beat['timestamp']:.3f}s")
                print(f"    Strength: {beat['strength']:.3f}")
                print(f"    Value2: {beat['value2']:.3f}")
                print(f"    Value3: {beat['value3']:.3f}")


if __name__ == '__main__':
    main()
