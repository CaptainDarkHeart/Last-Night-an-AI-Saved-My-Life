#!/usr/bin/env python3
"""
Playlist Loader for Mixxx AI DJ Controller

Converts Track Selection Engine playlists to Mixxx-compatible format
and provides utilities for loading them into the AI DJ Controller.
"""

import json
import sys
from pathlib import Path


def load_playlist(playlist_path: Path) -> dict:
    """Load playlist JSON from Track Selection Engine."""
    with open(playlist_path, 'r') as f:
        return json.load(f)


def convert_to_mixxx_format(playlist: dict) -> dict:
    """Convert playlist to format expected by Mixxx controller."""
    mixxx_playlist = {
        'name': playlist['name'],
        'tracks': [],
        'transitions': []
    }

    # Convert tracks
    for track in playlist['tracks']:
        mixxx_track = {
            'artist': track['artist'],
            'title': track['title'],
            'bpm': track['bpm'],
            'duration': track['duration'],
            'energy_level': track['energy_level'],
            'file_path': track['file_path']
        }
        mixxx_playlist['tracks'].append(mixxx_track)

    # Convert transitions
    for transition in playlist['transitions']:
        mixxx_transition = {
            'blend_duration': transition['blend_duration'],
            'strategy': transition['strategy'],
            'bpm_compatible': transition['bpm_compatible'],
            'key_compatible': transition['key_compatible']
        }
        mixxx_playlist['transitions'].append(mixxx_transition)

    return mixxx_playlist


def generate_mixxx_script(playlist: dict, output_path: Path):
    """Generate JavaScript code to load playlist into Mixxx."""
    mixxx_playlist = convert_to_mixxx_format(playlist)

    script = f"""// Auto-generated playlist loader
// Generated from: {playlist['name']}

var playlist = {json.dumps(mixxx_playlist, indent=2)};

// Load into AI DJ Controller
if (typeof AI_DJ_Controller !== 'undefined') {{
    AI_DJ_Controller.loadPlaylist(playlist);
    print("Playlist loaded: {playlist['name']}");
    print("Total tracks: " + playlist.tracks.length);
}} else {{
    print("ERROR: AI DJ Controller not found!");
}}
"""

    with open(output_path, 'w') as f:
        f.write(script)

    print(f"✓ Generated Mixxx script: {output_path}")


def create_m3u_with_metadata(playlist: dict, output_path: Path):
    """Create M3U playlist with metadata comments for Mixxx."""
    with open(output_path, 'w') as f:
        f.write("#EXTM3U\n")
        f.write(f"#PLAYLIST:{playlist['name']}\n")
        f.write(f"#AI_DJ_PLAYLIST:TRUE\n\n")

        for i, track in enumerate(playlist['tracks']):
            duration_int = int(track['duration'])

            # Add metadata as comments
            f.write(f"#TRACK_INDEX:{i}\n")
            f.write(f"#BPM:{track['bpm']}\n")
            f.write(f"#ENERGY:{track['energy_level']}\n")

            # Add blend duration if transition exists
            if i < len(playlist['transitions']):
                blend = playlist['transitions'][i]['blend_duration']
                f.write(f"#BLEND_DURATION:{blend}\n")

            # Standard M3U entry
            f.write(f"#EXTINF:{duration_int},{track['artist']} - {track['title']}\n")
            f.write(f"{track['file_path']}\n\n")

    print(f"✓ Created M3U with metadata: {output_path}")


def main():
    """Main CLI for playlist conversion."""
    if len(sys.argv) < 2:
        print("Usage: python playlist_loader.py <playlist.json>")
        print("\nExample:")
        print("  python playlist_loader.py deep-space-journey.json")
        sys.exit(1)

    playlist_path = Path(sys.argv[1])

    if not playlist_path.exists():
        print(f"Error: Playlist not found: {playlist_path}")
        sys.exit(1)

    print(f"Loading playlist: {playlist_path}")
    playlist = load_playlist(playlist_path)

    print(f"\nPlaylist: {playlist['name']}")
    print(f"Tracks: {len(playlist['tracks'])}")
    print(f"Duration: {playlist.get('total_duration', 0) / 60:.1f} minutes")

    # Generate Mixxx loader script
    script_output = playlist_path.with_suffix('.mixxx.js')
    generate_mixxx_script(playlist, script_output)

    # Generate enhanced M3U
    m3u_output = playlist_path.with_suffix('.ai-dj.m3u')
    create_m3u_with_metadata(playlist, m3u_output)

    print(f"\n✓ Conversion complete!")
    print(f"\nNext steps:")
    print(f"1. Copy AI_DJ_Controller.js and AI_DJ_Controller.midi.xml to Mixxx controllers folder")
    print(f"2. Open Mixxx and enable AI DJ Controller in Preferences > Controllers")
    print(f"3. Load {script_output.name} in Mixxx developer console to load playlist")
    print(f"4. Call AI_DJ_Controller.start() to begin automated performance")


if __name__ == '__main__':
    main()
