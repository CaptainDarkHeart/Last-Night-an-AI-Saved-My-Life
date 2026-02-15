"""Command-line interface for Track Selection Engine."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .library import TrackLibrary
from .journey_planner import JourneyPlanner
from .models import MusicalKey, TrackMetadata, TextureType, JourneyPosition


def create_library(args):
    """Create a new track library from a directory."""
    library_path = Path(args.library)
    music_dir = Path(args.directory)

    if not music_dir.exists():
        print(f"Error: Directory not found: {music_dir}")
        sys.exit(1)

    print(f"Scanning directory: {music_dir}")
    library = TrackLibrary()

    count = library.scan_directory(music_dir)
    print(f"✓ Added {count} tracks to library")

    library.library_path = library_path
    library.save()
    print(f"✓ Library saved to: {library_path}")

    # Show stats
    stats = library.stats()
    print(f"\nLibrary Statistics:")
    print(f"  Total tracks: {stats['total_tracks']}")
    print(f"  BPM range: {stats['bpm_range'][0]:.1f} - {stats['bpm_range'][1]:.1f}")
    print(f"  Average BPM: {stats['bpm_average']:.1f}")


def show_stats(args):
    """Show library statistics."""
    library_path = Path(args.library)

    if not library_path.exists():
        print(f"Error: Library not found: {library_path}")
        sys.exit(1)

    library = TrackLibrary(library_path)
    stats = library.stats()

    print(f"\nLibrary: {library_path}")
    print(f"{'='*60}")
    print(f"Total tracks: {stats['total_tracks']}")
    print(f"BPM range: {stats['bpm_range'][0]:.1f} - {stats['bpm_range'][1]:.1f}")
    print(f"Average BPM: {stats['bpm_average']:.1f}")
    print(f"Energy range: {stats['energy_range'][0]} - {stats['energy_range'][1]}")
    print(f"Average energy: {stats['energy_average']:.1f}")
    print(f"Keys represented: {stats['keys_represented']}")
    print(f"Labels: {stats['labels']}")


def generate_playlist(args):
    """Generate a journey arc playlist."""
    library_path = Path(args.library)

    if not library_path.exists():
        print(f"Error: Library not found: {library_path}")
        sys.exit(1)

    print(f"Loading library: {library_path}")
    library = TrackLibrary(library_path)
    print(f"✓ Loaded {len(library.tracks)} tracks")

    # Parse key center
    key_center = None
    if args.key:
        try:
            key_center = MusicalKey(args.key)
        except ValueError:
            print(f"Error: Invalid key: {args.key}")
            print(f"Valid keys: {', '.join([k.value for k in MusicalKey])}")
            sys.exit(1)

    # Create journey planner
    planner = JourneyPlanner(library)

    # Create journey arc
    print(f"\nCreating journey arc...")
    journey_arc = planner.create_journey_arc(
        duration_minutes=args.duration,
        key_center=key_center,
        bpm_range=(args.min_bpm, args.max_bpm),
        energy_progression=args.progression,
        blend_duration=args.blend
    )

    print(f"✓ Journey arc: {journey_arc.name}")
    print(f"  Duration: {journey_arc.duration_minutes} minutes")
    print(f"  Tracks needed: {journey_arc.num_tracks}")
    print(f"  Energy curve: {journey_arc.energy_curve}")

    # Generate playlist
    print(f"\nGenerating playlist...")
    try:
        playlist = planner.generate_playlist(
            journey_arc,
            strict_key=args.strict_key,
            prefer_labels=True
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"✓ Playlist generated: {len(playlist.tracks)} tracks")
    print(f"  Total duration: {playlist.total_duration / 60:.1f} minutes")

    # Show playlist
    print(f"\n{'='*80}")
    print(f"PLAYLIST: {playlist.name}")
    print(f"{'='*80}\n")

    for i, track in enumerate(playlist.tracks, 1):
        duration_min = int(track.duration // 60)
        duration_sec = int(track.duration % 60)
        key_str = track.key.value if track.key else "Unknown"
        energy_str = f"E{track.energy_level}"

        print(f"{i:2d}. {track.artist} - {track.title}")
        print(f"    {track.bpm:.1f} BPM | {key_str} | {energy_str} | {duration_min}:{duration_sec:02d}")

        if i < len(playlist.tracks):
            transition = playlist.transitions[i-1]
            print(f"    └─ Blend: {transition.blend_duration}s")
            if not transition.bpm_compatible:
                print(f"       ⚠ BPM adjustment needed")
        print()

    # Save playlist
    output_path = Path(args.output)

    # Save JSON
    json_path = output_path.with_suffix('.json')
    playlist.to_json(json_path)
    print(f"✓ Saved playlist to: {json_path}")

    # Save M3U
    if args.m3u:
        m3u_path = output_path.with_suffix('.m3u')
        playlist.to_m3u(m3u_path)
        print(f"✓ Saved M3U playlist to: {m3u_path}")


def list_tracks(args):
    """List tracks in the library."""
    library_path = Path(args.library)

    if not library_path.exists():
        print(f"Error: Library not found: {library_path}")
        sys.exit(1)

    library = TrackLibrary(library_path)

    # Apply filters
    tracks = library.tracks

    if args.bpm:
        min_bpm = args.bpm - 2
        max_bpm = args.bpm + 2
        tracks = [t for t in tracks if min_bpm <= t.bpm <= max_bpm]

    if args.key:
        try:
            key = MusicalKey(args.key)
            tracks = [t for t in tracks if t.key == key]
        except ValueError:
            print(f"Error: Invalid key: {args.key}")
            sys.exit(1)

    if args.energy:
        tracks = [t for t in tracks if abs(t.energy_level - args.energy) <= 1]

    # Show tracks
    print(f"\nFound {len(tracks)} tracks:\n")
    for track in tracks[:args.limit]:
        key_str = track.key.value if track.key else "?"
        print(f"{track.artist} - {track.title}")
        print(f"  {track.bpm:.1f} BPM | {key_str} | E{track.energy_level}")
        print(f"  {track.file_path}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Track Selection Engine - Intelligent DJ playlist generation"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Create library command
    create_parser = subparsers.add_parser('create', help='Create a new track library')
    create_parser.add_argument('directory', help='Directory to scan for audio files')
    create_parser.add_argument('-l', '--library', default='library.json', help='Library file path')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show library statistics')
    stats_parser.add_argument('-l', '--library', default='library.json', help='Library file path')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a journey arc playlist')
    gen_parser.add_argument('duration', type=int, help='Duration in minutes')
    gen_parser.add_argument('-l', '--library', default='library.json', help='Library file path')
    gen_parser.add_argument('-o', '--output', default='playlist', help='Output file path')
    gen_parser.add_argument('-k', '--key', help='Key center (e.g., 1A for A Minor)')
    gen_parser.add_argument('--min-bpm', type=float, default=118, help='Minimum BPM')
    gen_parser.add_argument('--max-bpm', type=float, default=124, help='Maximum BPM')
    gen_parser.add_argument('-p', '--progression', default='gradual_build',
                          choices=['gradual_build', 'peak_and_descent', 'steady'],
                          help='Energy progression type')
    gen_parser.add_argument('-b', '--blend', type=int, default=60, help='Blend duration in seconds')
    gen_parser.add_argument('--strict-key', action='store_true', help='Only use key-compatible tracks')
    gen_parser.add_argument('--m3u', action='store_true', help='Also save as M3U playlist')

    # List command
    list_parser = subparsers.add_parser('list', help='List tracks in library')
    list_parser.add_argument('-l', '--library', default='library.json', help='Library file path')
    list_parser.add_argument('--bpm', type=float, help='Filter by BPM (±2)')
    list_parser.add_argument('--key', help='Filter by key (e.g., 1A)')
    list_parser.add_argument('--energy', type=int, help='Filter by energy level (±1)')
    list_parser.add_argument('--limit', type=int, default=20, help='Max tracks to show')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == 'create':
        create_library(args)
    elif args.command == 'stats':
        show_stats(args)
    elif args.command == 'generate':
        generate_playlist(args)
    elif args.command == 'list':
        list_tracks(args)


if __name__ == '__main__':
    main()
