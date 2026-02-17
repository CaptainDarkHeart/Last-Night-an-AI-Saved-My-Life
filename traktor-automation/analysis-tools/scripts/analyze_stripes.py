#!/usr/bin/env python3
"""
Analyze Traktor stripes files to understand the binary format.
The stripes file contains waveform visualization data showing frequency distribution.
"""

import struct
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def parse_stripes_header(data):
    """Parse the header of a stripes file."""
    # First 4 bytes appear to be "PRTS" signature
    signature = data[:4].decode('ascii', errors='ignore')

    # Next bytes might contain metadata
    # Based on hexdump: 06 50 52 54 53 02 00 00 00 00 00 60 40
    header_info = {
        'signature': signature,
        'version_or_flag': data[4],
        'bytes_5_12': data[5:13].hex(),
        'potential_length': struct.unpack('>I', data[8:12])[0],  # Big-endian int
    }

    return header_info


def analyze_waveform_data(data, skip_header=16):
    """
    Analyze the waveform data in the stripes file.
    Based on the documentation, brighter shades = high freq, darker = low freq.

    Looking at the hexdump pattern more carefully:
    The data appears to be structured as waveform samples where each sample
    might represent different frequency bands or amplitude values.
    """
    # Skip header and analyze the rest as waveform data
    waveform_data = data[skip_header:]

    samples = []

    # After examining the data, it appears to be sequential bytes
    # Each byte might represent amplitude at that time slice
    # Let's try a different approach: interpret the data as a stream of amplitude values
    # and look for patterns

    # Try reading as individual bytes first to see the pattern
    for i in range(0, len(waveform_data), 3):
        if i + 2 < len(waveform_data):
            # These might be interleaved frequency bands
            byte1 = waveform_data[i]
            byte2 = waveform_data[i+1]
            byte3 = waveform_data[i+2]

            # Based on hexdump observation: 0d 1e 2a (13, 30, 42)
            # These could be: low, mid, high frequencies
            # Or they could be: min, avg, max amplitudes
            samples.append({
                'low': byte1,      # Typically lowest value
                'mid': byte2,      # Middle value
                'high': byte3,     # Typically highest value
                'total': byte1 + byte2 + byte3
            })

    return samples


def detect_breakdowns(samples, threshold=0.3):
    """
    Detect potential breakdown sections where low frequencies drop significantly.

    Args:
        samples: List of frequency samples
        threshold: Percentage drop in low frequencies to consider a breakdown

    Returns:
        List of sample indices where breakdowns might occur
    """
    if not samples:
        return []

    breakdown_points = []

    # Calculate rolling average of low frequencies
    window_size = 10
    low_freqs = np.array([s['low'] for s in samples])

    if len(low_freqs) < window_size:
        return []

    # Calculate moving average
    moving_avg = np.convolve(low_freqs, np.ones(window_size)/window_size, mode='valid')

    # Find points where low freq drops below threshold of the average
    avg_low = np.mean(low_freqs)

    for i, (sample, avg) in enumerate(zip(low_freqs[window_size-1:], moving_avg)):
        if sample < avg_low * threshold:
            breakdown_points.append(i + window_size - 1)

    return breakdown_points


def visualize_stripes(samples, breakdown_points=None):
    """Visualize the waveform data similar to Traktor's stripe view."""
    if not samples:
        print("No samples to visualize")
        return

    indices = range(len(samples))
    low_freqs = [s['low'] for s in samples]
    mid_freqs = [s['mid'] for s in samples]
    high_freqs = [s['high'] for s in samples]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8))

    # Plot frequency bands
    ax1.fill_between(indices, low_freqs, alpha=0.3, label='Low Freq (Bass)', color='darkblue')
    ax1.fill_between(indices, mid_freqs, alpha=0.3, label='Mid Freq', color='green')
    ax1.fill_between(indices, high_freqs, alpha=0.3, label='High Freq', color='yellow')

    if breakdown_points:
        for bp in breakdown_points[::50]:  # Plot every 50th point to avoid clutter
            ax1.axvline(x=bp, color='red', alpha=0.5, linestyle='--')

    ax1.set_title('Traktor Stripes - Frequency Distribution')
    ax1.set_xlabel('Sample Index')
    ax1.set_ylabel('Amplitude')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot total energy
    total_energy = [s['total'] for s in samples]
    ax2.plot(indices, total_energy, color='purple', linewidth=0.5)
    ax2.fill_between(indices, total_energy, alpha=0.3, color='purple')
    ax2.set_title('Total Energy')
    ax2.set_xlabel('Sample Index')
    ax2.set_ylabel('Energy')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/Users/dantaylor/Claude/Anima-in-Machina/analysis/stripes_visualization.png', dpi=150)
    print("Visualization saved to analysis/stripes_visualization.png")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_stripes.py <path_to_stripes_file>")
        print("\nExample:")
        print('  python analyze_stripes.py "~/Documents/Native Instruments/Traktor 3.11.1/Stripes/000/A25QIFCHTIEFTCB04LEZBPVKMIOC"')
        return

    stripes_path = Path(sys.argv[1]).expanduser()

    if not stripes_path.exists():
        print(f"Error: File not found: {stripes_path}")
        return

    print(f"Analyzing stripes file: {stripes_path}")
    print(f"File size: {stripes_path.stat().st_size} bytes")

    # Read the file
    with open(stripes_path, 'rb') as f:
        data = f.read()

    # Parse header
    print("\n=== Header Information ===")
    header = parse_stripes_header(data)
    for key, value in header.items():
        print(f"{key}: {value}")

    # Analyze waveform data
    print("\n=== Analyzing Waveform Data ===")
    samples = analyze_waveform_data(data)
    print(f"Extracted {len(samples)} samples")

    if samples:
        # Show some statistics
        low_avg = np.mean([s['low'] for s in samples])
        mid_avg = np.mean([s['mid'] for s in samples])
        high_avg = np.mean([s['high'] for s in samples])

        print(f"\nAverage amplitudes:")
        print(f"  Low freq:  {low_avg:.2f}")
        print(f"  Mid freq:  {mid_avg:.2f}")
        print(f"  High freq: {high_avg:.2f}")

        # Detect potential breakdowns
        print("\n=== Detecting Breakdowns ===")
        breakdown_points = detect_breakdowns(samples, threshold=0.3)
        print(f"Found {len(breakdown_points)} potential breakdown points")

        if breakdown_points:
            print(f"\nFirst 10 breakdown points (sample indices): {breakdown_points[:10]}")

            # Convert sample indices to approximate time positions
            # Assuming each sample represents a small time slice
            total_samples = len(samples)
            print(f"\nBreakdown distribution:")
            print(f"  Early (0-33%): {sum(1 for bp in breakdown_points if bp < total_samples/3)}")
            print(f"  Middle (33-66%): {sum(1 for bp in breakdown_points if total_samples/3 <= bp < 2*total_samples/3)}")
            print(f"  Late (66-100%): {sum(1 for bp in breakdown_points if bp >= 2*total_samples/3)}")

        # Create visualization
        print("\n=== Creating Visualization ===")
        Path('/Users/dantaylor/Claude/Anima-in-Machina/analysis').mkdir(exist_ok=True)
        visualize_stripes(samples, breakdown_points)


if __name__ == '__main__':
    main()
