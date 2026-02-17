#!/usr/bin/env python3
"""
Improved Traktor transients file parser.

Based on pattern analysis, the file appears to have a record-based structure
where each record contains beat timing and metadata information.
"""

import struct
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def parse_transients_structured(data):
    """
    Parse transients file with record-based structure.

    Pattern observed:
    - Groups of bytes that seem to represent individual beat markers
    - Likely format: timestamp, confidence/strength, and metadata
    """

    # The pattern shows regular 0x43, 0x42, 0x41 bytes (67, 66, 65 in decimal)
    # These could be format markers or type indicators

    # Try parsing as 20-byte records
    record_size = 20  # bytes
    num_records = len(data) // record_size

    beats = []

    for i in range(num_records):
        offset = i * record_size
        record_data = data[offset:offset + record_size]

        if len(record_data) < record_size:
            break

        # Try unpacking as: [uint32, uint32, float, float, float]
        try:
            parts = struct.unpack('<IIf  f f', record_data)

            # The uint32 values might be a timestamp in a different format
            # The floats might be position, strength, confidence

            beat_record = {
                'value1': parts[0],
                'value2': parts[1],
                'float1': parts[2],
                'float2': parts[3],
                'float3': parts[4]
            }

            # Check if this looks like valid data
            # (floats should be reasonable values, not huge numbers)
            if abs(parts[2]) < 1000 and abs(parts[3]) < 1000:
                beats.append(beat_record)

        except struct.error:
            continue

    return beats


def analyze_beat_values(beats):
    """Analyze the beat data to understand what each field represents."""
    if not beats:
        return None

    # Check if value1 increases monotonically (timestamp candidate)
    value1_vals = [b['value1'] for b in beats]
    value1_diffs = np.diff(value1_vals)
    value1_increasing = np.all(value1_diffs >= 0)

    # Check ranges of each field
    float1_range = (min(b['float1'] for b in beats), max(b['float1'] for b in beats))
    float2_range = (min(b['float2'] for b in beats), max(b['float2'] for b in beats))
    float3_range = (min(b['float3'] for b in beats), max(b['float3'] for b in beats))

    return {
        'total_beats': len(beats),
        'value1_increasing': value1_increasing,
        'value1_range': (min(value1_vals), max(value1_vals)),
        'float1_range': float1_range,
        'float2_range': float2_range,
        'float3_range': float3_range,
    }


def visualize_beat_data(beats):
    """Visualize the different fields to understand their meaning."""
    if not beats or len(beats) < 10:
        print("Not enough beat data to visualize")
        return

    indices = list(range(len(beats)))
    float1_vals = [b['float1'] for b in beats]
    float2_vals = [b['float2'] for b in beats]
    float3_vals = [b['float3'] for b in beats]

    fig, axes = plt.subplots(3, 1, figsize=(15, 10))

    axes[0].plot(indices, float1_vals, linewidth=0.5, alpha=0.7)
    axes[0].set_title('Float1 Values Over Beat Sequence')
    axes[0].set_xlabel('Beat Index')
    axes[0].set_ylabel('Float1')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(indices, float2_vals, linewidth=0.5, alpha=0.7, color='orange')
    axes[1].set_title('Float2 Values Over Beat Sequence')
    axes[1].set_xlabel('Beat Index')
    axes[1].set_ylabel('Float2')
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(indices, float3_vals, linewidth=0.5, alpha=0.7, color='green')
    axes[2].set_title('Float3 Values Over Beat Sequence')
    axes[2].set_xlabel('Beat Index')
    axes[2].set_ylabel('Float3')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/Users/dantaylor/Claude/Anima-in-Machina/analysis/transients_fields.png', dpi=150)
    print("Visualization saved to analysis/transients_fields.png")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_transients_v2.py <path_to_transients_file>")
        return

    transients_path = Path(sys.argv[1]).expanduser()

    if not transients_path.exists():
        print(f"Error: File not found: {transients_path}")
        return

    print(f"Analyzing transients file: {transients_path.name}")
    print(f"File size: {transients_path.stat().st_size} bytes")

    with open(transients_path, 'rb') as f:
        data = f.read()

    # Parse with structured approach
    print("\n=== Parsing as Structured Records ===")
    beats = parse_transients_structured(data)
    print(f"Extracted {len(beats)} beat records")

    if beats:
        print("\n=== Field Analysis ===")
        analysis = analyze_beat_values(beats)

        if analysis:
            print(f"Total beats: {analysis['total_beats']}")
            print(f"Value1 monotonically increasing: {analysis['value1_increasing']}")
            print(f"Value1 range: {analysis['value1_range']}")
            print(f"Float1 range: {analysis['float1_range']}")
            print(f"Float2 range: {analysis['float2_range']}")
            print(f"Float3 range: {analysis['float3_range']}")

        print("\n=== Sample Records (first 10) ===")
        for i, beat in enumerate(beats[:10]):
            print(f"Beat {i+1}:")
            print(f"  Value1: {beat['value1']:12d} (0x{beat['value1']:08x})")
            print(f"  Value2: {beat['value2']:12d}")
            print(f"  Float1: {beat['float1']:12.6f}")
            print(f"  Float2: {beat['float2']:12.6f}")
            print(f"  Float3: {beat['float3']:12.6f}")

        # Visualize
        print("\n=== Creating Visualization ===")
        Path('/Users/dantaylor/Claude/Anima-in-Machina/analysis').mkdir(exist_ok=True)
        visualize_beat_data(beats)


if __name__ == '__main__':
    main()
