#!/usr/bin/env python3
"""Import detailed music list with artist, title, BPM, and duration."""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from track_selector.library import TrackLibrary
from track_selector.models import TrackMetadata


def parse_duration(duration_str: str) -> float:
    """Parse duration string like '6:43' to seconds."""
    try:
        parts = duration_str.split(':')
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return hours * 3600 + minutes * 60 + seconds
    except:
        pass
    return 360.0  # Default 6 minutes


def parse_detailed_list(file_path: Path, music_root: Path) -> list[TrackMetadata]:
    """Parse the detailed music list."""
    tracks = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Format: Artist - Title | BPM: 123 | Key: N/A | Duration: 6:43
        # Split by |
        parts = [p.strip() for p in line.split('|')]

        if len(parts) < 4:
            continue

        # Parse artist and title
        artist_title = parts[0]
        if ' - ' not in artist_title:
            continue

        # Remove leading dots and numbers
        artist_title = re.sub(r'^[\.\s\d]+', '', artist_title)

        artist, title = artist_title.split(' - ', 1)
        artist = artist.strip()
        title = title.strip()

        # Parse BPM
        bpm_str = parts[1].replace('BPM:', '').strip()
        try:
            bpm = float(bpm_str)
        except ValueError:
            continue

        # Skip invalid BPMs
        if bpm < 60 or bpm > 200:
            continue

        # Parse duration
        duration_str = parts[3].replace('Duration:', '').strip()
        duration = parse_duration(duration_str)

        # Estimate energy level from BPM
        if bpm < 115:
            energy = 2
        elif bpm < 120:
            energy = 3
        elif bpm < 123:
            energy = 4
        elif bpm < 126:
            energy = 5
        elif bpm < 128:
            energy = 6
        elif bpm < 130:
            energy = 7
        else:
            energy = 8

        # Create track metadata
        # Use sanitized filename as placeholder
        safe_filename = f"{artist} - {title}".replace('/', '_')
        track = TrackMetadata(
            file_path=music_root / f"{safe_filename}.wav",
            title=title,
            artist=artist,
            bpm=bpm,
            duration=duration,
            energy_level=energy
        )

        tracks.append(track)

    return tracks


def main():
    """Main import function."""
    detailed_list_file = Path("/Users/dantaylor/Claude/Last Night an AI Saved My Life/Detailed_Music_List.md")
    music_root = Path("/Volumes/TRAKTOR/Traktor/Music")
    output_file = Path("traktor-library-detailed.json")

    if not detailed_list_file.exists():
        print(f"Error: Detailed list not found at {detailed_list_file}")
        sys.exit(1)

    print(f"Reading detailed music list from: {detailed_list_file}")
    tracks = parse_detailed_list(detailed_list_file, music_root)

    print(f"Parsed {len(tracks)} tracks")

    # Create library
    library = TrackLibrary()

    for track in tracks:
        library.add_track(track)

    # Save library
    library.library_path = output_file
    library.save()

    print(f"✓ Library saved to: {output_file}")

    # Show stats
    stats = library.stats()
    print(f"\nLibrary Statistics:")
    print(f"  Total tracks: {stats['total_tracks']}")
    print(f"  BPM range: {stats['bpm_range'][0]:.1f} - {stats['bpm_range'][1]:.1f}")
    print(f"  Average BPM: {stats['bpm_average']:.1f}")
    print(f"  Energy range: {stats['energy_range'][0]} - {stats['energy_range'][1]}")
    print(f"  Average energy: {stats['energy_average']:.1f}")

    # Show BPM distribution
    print(f"\nBPM Distribution:")
    bpm_counts = {}
    for track in tracks:
        bpm_int = int(track.bpm)
        bpm_counts[bpm_int] = bpm_counts.get(bpm_int, 0) + 1

    # Show top 10 most common BPMs
    top_bpms = sorted(bpm_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for bpm, count in top_bpms:
        print(f"  {bpm} BPM: {count} tracks")

    # Show some sample tracks
    print(f"\nSample tracks:")
    for track in tracks[:5]:
        print(f"  {track.artist} - {track.title}")
        print(f"    {track.bpm:.1f} BPM | E{track.energy_level} | {track.duration/60:.1f} min")


if __name__ == '__main__':
    main()
