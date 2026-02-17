#!/usr/bin/env python3
"""
Use Traktor stripes files to suggest intelligent cue point placement.

This script:
1. Parses a stripes file to extract frequency/amplitude data
2. Detects structural changes in the track (breakdowns, build-ups, drops)
3. Suggests cue point positions based on the analysis
4. Optionally updates the Traktor collection.nml file
"""

import struct
import sys
from pathlib import Path
import numpy as np
from typing import List, Dict, Tuple
import xml.etree.ElementTree as ET


class StripesAnalyzer:
    """Analyze Traktor stripes files for track structure."""

    def __init__(self, stripes_path: Path):
        self.stripes_path = stripes_path
        self.samples = []
        self.track_duration = 0

    def parse_file(self) -> List[Dict]:
        """Parse the stripes file and extract waveform samples."""
        with open(self.stripes_path, 'rb') as f:
            data = f.read()

        # Skip header (first 16 bytes contain PRTS signature and metadata)
        waveform_data = data[16:]

        # Parse as triplets (appears to be low/mid/high frequency data)
        for i in range(0, len(waveform_data) - 2, 3):
            self.samples.append({
                'low': waveform_data[i],
                'mid': waveform_data[i+1],
                'high': waveform_data[i+2],
            })

        return self.samples

    def set_track_duration(self, duration_seconds: float):
        """Set the track duration to convert sample indices to time positions."""
        self.track_duration = duration_seconds

    def sample_to_time(self, sample_index: int) -> float:
        """Convert a sample index to time position in seconds."""
        if self.track_duration > 0 and len(self.samples) > 0:
            return (sample_index / len(self.samples)) * self.track_duration
        return 0.0

    def detect_breakdowns(self, low_threshold=0.5, min_duration_samples=200, min_separation=1000) -> List[int]:
        """
        Detect breakdown sections where bass/low frequencies drop significantly.

        Args:
            low_threshold: Multiplier of average low freq (e.g., 0.5 = 50% of average)
            min_duration_samples: Minimum number of consecutive low samples
            min_separation: Minimum samples between detected breakdowns

        Returns:
            List of sample indices where breakdowns start
        """
        if not self.samples:
            return []

        low_freqs = np.array([s['low'] for s in self.samples])
        avg_low = np.mean(low_freqs)
        threshold_value = avg_low * low_threshold

        # Find regions below threshold
        below_threshold = low_freqs < threshold_value

        # Find start of breakdown regions
        breakdowns = []
        in_breakdown = False
        breakdown_start = 0
        breakdown_length = 0

        for i, is_low in enumerate(below_threshold):
            if is_low and not in_breakdown:
                # Start of a new breakdown
                in_breakdown = True
                breakdown_start = i
                breakdown_length = 1
            elif is_low and in_breakdown:
                # Continuing breakdown
                breakdown_length += 1
            elif not is_low and in_breakdown:
                # End of breakdown - check if it's significant and separated
                if breakdown_length >= min_duration_samples:
                    # Check separation from previous breakdown
                    if not breakdowns or (breakdown_start - breakdowns[-1]) > min_separation:
                        breakdowns.append(breakdown_start)
                in_breakdown = False
                breakdown_length = 0

        return breakdowns

    def detect_buildups(self, window_size=80, increase_threshold=1.6, min_separation=800) -> List[int]:
        """
        Detect build-up sections where energy gradually increases.

        Args:
            window_size: Number of samples to analyze for trend
            increase_threshold: Multiplier for energy increase
            min_separation: Minimum samples between detected buildups

        Returns:
            List of sample indices where build-ups start
        """
        if not self.samples or len(self.samples) < window_size * 2:
            return []

        # Calculate total energy
        energy = np.array([s['low'] + s['mid'] + s['high'] for s in self.samples])

        buildups = []

        for i in range(window_size, len(energy) - window_size, 20):  # Skip by 20 for efficiency
            # Compare energy in current window vs previous window
            prev_window = np.mean(energy[i-window_size:i])
            curr_window = np.mean(energy[i:i+window_size])

            if curr_window > prev_window * increase_threshold:
                # Check if it's not too close to the last buildup
                if not buildups or (i - buildups[-1]) > min_separation:
                    buildups.append(i)

        return buildups

    def detect_drops(self, window_size=50, drop_threshold=1.6, min_separation=500) -> List[int]:
        """
        Detect drop sections where energy suddenly increases (typical EDM drop).

        Args:
            window_size: Number of samples to compare
            drop_threshold: Multiplier for sudden energy increase
            min_separation: Minimum samples between detected drops

        Returns:
            List of sample indices where drops occur
        """
        if not self.samples or len(self.samples) < window_size * 2:
            return []

        energy = np.array([s['low'] + s['mid'] + s['high'] for s in self.samples])
        drops = []

        for i in range(window_size, len(energy) - window_size, 10):  # Skip by 10 for efficiency
            # Look for sudden energy increase
            before = np.mean(energy[i-window_size:i])
            after = np.mean(energy[i:i+window_size])

            # Also check that bass/low freq increases (not just high freq)
            low_before = np.mean([self.samples[j]['low'] for j in range(i-window_size, i)])
            low_after = np.mean([self.samples[j]['low'] for j in range(i, min(i+window_size, len(self.samples)))])

            if after > before * drop_threshold and low_after > low_before * 1.3:
                # Ensure minimum separation from previous drops
                if not drops or (i - drops[-1]) > min_separation:
                    drops.append(i)

        return drops

    def suggest_cue_points(self) -> List[Dict]:
        """
        Suggest cue points based on track structure analysis.

        Returns:
            List of dictionaries containing cue point information
        """
        if not self.samples:
            return []

        cue_points = []

        # Track start (always useful)
        cue_points.append({
            'type': 'load',
            'sample_idx': 0,
            'time': 0.0,
            'name': 'Load',
            'description': 'Track start'
        })

        # Detect breakdowns
        breakdowns = self.detect_breakdowns()
        for i, bd_idx in enumerate(breakdowns[:4]):  # Limit to 4 breakdowns
            cue_points.append({
                'type': 'breakdown',
                'sample_idx': bd_idx,
                'time': self.sample_to_time(bd_idx),
                'name': f'Breakdown {i+1}',
                'description': 'Low frequency drop - potential breakdown section'
            })

        # Detect build-ups
        buildups = self.detect_buildups()
        for i, bu_idx in enumerate(buildups[:3]):  # Limit to 3 build-ups
            cue_points.append({
                'type': 'buildup',
                'sample_idx': bu_idx,
                'time': self.sample_to_time(bu_idx),
                'name': f'Build {i+1}',
                'description': 'Energy increase - potential build-up section'
            })

        # Detect drops
        drops = self.detect_drops()
        for i, drop_idx in enumerate(drops[:3]):  # Limit to 3 drops
            cue_points.append({
                'type': 'drop',
                'sample_idx': drop_idx,
                'time': self.sample_to_time(drop_idx),
                'name': f'Drop {i+1}',
                'description': 'Sudden energy increase - potential drop section'
            })

        # Sort by time
        cue_points.sort(key=lambda x: x['sample_idx'])

        return cue_points


def main():
    if len(sys.argv) < 2:
        print("Usage: python stripes_to_cuepoints.py <path_to_stripes_file> [track_duration_seconds]")
        print("\nExample:")
        print('  python stripes_to_cuepoints.py "~/Documents/.../Stripes/000/ABC123" 360')
        return

    stripes_path = Path(sys.argv[1]).expanduser()

    if not stripes_path.exists():
        print(f"Error: File not found: {stripes_path}")
        return

    # Optional track duration
    track_duration = float(sys.argv[2]) if len(sys.argv) > 2 else 0

    print(f"Analyzing: {stripes_path.name}")
    print(f"File size: {stripes_path.stat().st_size} bytes")

    # Parse stripes file
    analyzer = StripesAnalyzer(stripes_path)
    samples = analyzer.parse_file()
    print(f"Extracted {len(samples)} samples")

    if track_duration > 0:
        analyzer.set_track_duration(track_duration)
        print(f"Track duration: {track_duration} seconds")

    # Suggest cue points
    print("\n=== Suggested Cue Points ===")
    cue_points = analyzer.suggest_cue_points()

    for cue in cue_points:
        time_str = f"{cue['time']:.2f}s" if track_duration > 0 else "N/A"
        print(f"\n{cue['name']} ({cue['type']})")
        print(f"  Position: Sample {cue['sample_idx']:,} | Time: {time_str}")
        print(f"  {cue['description']}")

    print(f"\n\nTotal cue points suggested: {len(cue_points)}")

    # Save to file
    output_file = Path('/Users/dantaylor/Claude/Anima-in-Machina/analysis/suggested_cuepoints.txt')
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(f"Suggested Cue Points for: {stripes_path.name}\n")
        f.write(f"Track duration: {track_duration}s\n\n")

        for cue in cue_points:
            time_str = f"{cue['time']:.2f}s" if track_duration > 0 else "N/A"
            f.write(f"{cue['name']} ({cue['type']})\n")
            f.write(f"  Sample: {cue['sample_idx']:,} | Time: {time_str}\n")
            f.write(f"  {cue['description']}\n\n")

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
