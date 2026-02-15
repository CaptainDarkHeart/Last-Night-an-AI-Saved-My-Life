"""Track library management and analysis."""

import json
from pathlib import Path
from typing import List, Optional, Dict
import pandas as pd
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.aiff import AIFF

from .models import TrackMetadata, MusicalKey, TextureType, JourneyPosition


class TrackLibrary:
    """Manages a collection of tracks with metadata."""

    def __init__(self, library_path: Optional[Path] = None):
        """
        Initialize track library.

        Args:
            library_path: Path to library database (JSON file)
        """
        self.library_path = library_path
        self.tracks: List[TrackMetadata] = []
        self.tracks_by_key: Dict[MusicalKey, List[TrackMetadata]] = {}
        self.tracks_by_bpm: Dict[int, List[TrackMetadata]] = {}

        if library_path and library_path.exists():
            self.load()

    def add_track(self, track: TrackMetadata) -> None:
        """Add a track to the library."""
        self.tracks.append(track)

        # Index by key
        if track.key:
            if track.key not in self.tracks_by_key:
                self.tracks_by_key[track.key] = []
            self.tracks_by_key[track.key].append(track)

        # Index by BPM
        bpm_int = int(track.bpm)
        if bpm_int not in self.tracks_by_bpm:
            self.tracks_by_bpm[bpm_int] = []
        self.tracks_by_bpm[bpm_int].append(track)

    def scan_directory(
        self,
        directory: Path,
        extensions: List[str] = ['.wav', '.aiff', '.mp3', '.flac']
    ) -> int:
        """
        Scan a directory for audio files and extract basic metadata.

        Args:
            directory: Directory to scan
            extensions: Audio file extensions to include

        Returns:
            Number of tracks added
        """
        count = 0
        for ext in extensions:
            for file_path in directory.rglob(f'*{ext}'):
                try:
                    track = self.extract_metadata(file_path)
                    if track:
                        self.add_track(track)
                        count += 1
                except Exception as e:
                    print(f"Warning: Failed to process {file_path}: {e}")

        return count

    def extract_metadata(self, file_path: Path) -> Optional[TrackMetadata]:
        """
        Extract metadata from audio file.

        Args:
            file_path: Path to audio file

        Returns:
            TrackMetadata or None if extraction fails
        """
        try:
            audio = MutagenFile(file_path, easy=True)

            if audio is None:
                return None

            # Extract basic info
            title = audio.get('title', [file_path.stem])[0]
            artist = audio.get('artist', ['Unknown'])[0]

            # Get duration
            duration = getattr(audio.info, 'length', 0.0)

            # Try to extract BPM from tags
            bpm = 120.0  # Default BPM
            if hasattr(audio, 'tags') and audio.tags:
                # Try various BPM tag names
                for bpm_tag in ['BPM', 'bpm', 'TBPM']:
                    if bpm_tag in audio.tags:
                        try:
                            bpm = float(str(audio.tags[bpm_tag][0]))
                            break
                        except (ValueError, IndexError):
                            pass

            # Extract genre
            genre = audio.get('genre', [])
            if isinstance(genre, str):
                genre = [genre]

            # Extract year
            year = None
            date = audio.get('date', [None])[0]
            if date:
                try:
                    year = int(str(date)[:4])
                except (ValueError, TypeError):
                    pass

            # Create track metadata
            track = TrackMetadata(
                file_path=file_path,
                title=title,
                artist=artist,
                bpm=bpm,
                duration=duration,
                genre=genre,
                year=year
            )

            return track

        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return None

    def find_tracks_by_key(self, key: MusicalKey) -> List[TrackMetadata]:
        """Find all tracks in a specific key."""
        return self.tracks_by_key.get(key, [])

    def find_tracks_by_bpm_range(self, min_bpm: float, max_bpm: float) -> List[TrackMetadata]:
        """Find tracks within a BPM range."""
        return [t for t in self.tracks if min_bpm <= t.bpm <= max_bpm]

    def find_tracks_by_energy(self, energy_level: int, tolerance: int = 1) -> List[TrackMetadata]:
        """Find tracks with specific energy level (±tolerance)."""
        return [
            t for t in self.tracks
            if abs(t.energy_level - energy_level) <= tolerance
        ]

    def find_tracks_by_texture(self, texture: TextureType) -> List[TrackMetadata]:
        """Find tracks with specific texture."""
        return [t for t in self.tracks if texture in t.textures]

    def find_tracks_by_label(self, label: str) -> List[TrackMetadata]:
        """Find tracks from a specific label."""
        return [t for t in self.tracks if t.label and label.lower() in t.label.lower()]

    def find_tracks_by_journey_position(self, position: JourneyPosition) -> List[TrackMetadata]:
        """Find tracks suitable for a specific journey position."""
        return [t for t in self.tracks if t.journey_position == position]

    def get_compatible_tracks(
        self,
        reference_track: TrackMetadata,
        bpm_tolerance: float = 6.0,
        key_compatible_only: bool = False
    ) -> List[TrackMetadata]:
        """
        Find tracks compatible with a reference track.

        Args:
            reference_track: Track to find compatible matches for
            bpm_tolerance: BPM tolerance percentage (default: 6%)
            key_compatible_only: Only return tracks in compatible keys

        Returns:
            List of compatible tracks
        """
        compatible = []

        for track in self.tracks:
            if track == reference_track:
                continue

            # Check BPM compatibility
            bpm_ratio = track.bpm / reference_track.bpm
            bpm_ok = (
                abs(bpm_ratio - 1.0) <= bpm_tolerance / 100.0 or
                abs(bpm_ratio - 2.0) <= bpm_tolerance / 100.0 or
                abs(bpm_ratio - 0.5) <= bpm_tolerance / 100.0
            )

            if not bpm_ok:
                continue

            # Check key compatibility if required
            if key_compatible_only and reference_track.key and track.key:
                if not self.are_keys_compatible(reference_track.key, track.key):
                    continue

            compatible.append(track)

        return compatible

    @staticmethod
    def are_keys_compatible(key1: MusicalKey, key2: MusicalKey) -> bool:
        """
        Check if two keys are compatible for mixing (Camelot system).

        Compatible keys:
        - Same key
        - Adjacent keys (±1 on the circle)
        - Same number, different letter (relative major/minor)
        """
        if key1 == key2:
            return True

        # Extract Camelot number and letter
        num1 = int(key1.value[:-1])
        letter1 = key1.value[-1]
        num2 = int(key2.value[:-1])
        letter2 = key2.value[-1]

        # Same number, different letter (relative major/minor)
        if num1 == num2:
            return True

        # Adjacent on the circle (same letter)
        if letter1 == letter2:
            diff = abs(num1 - num2)
            return diff == 1 or diff == 11  # Adjacent or wrapping around

        return False

    def to_dataframe(self) -> pd.DataFrame:
        """Convert library to pandas DataFrame for analysis."""
        data = [track.to_dict() for track in self.tracks]
        return pd.DataFrame(data)

    def save(self, file_path: Optional[Path] = None) -> None:
        """Save library to JSON file."""
        path = file_path or self.library_path
        if not path:
            raise ValueError("No library path specified")

        data = {
            'tracks': [track.to_dict() for track in self.tracks],
            'version': '0.1.0'
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, file_path: Optional[Path] = None) -> None:
        """Load library from JSON file."""
        path = file_path or self.library_path
        if not path or not path.exists():
            raise ValueError(f"Library file not found: {path}")

        with open(path, 'r') as f:
            data = json.load(f)

        self.tracks = [TrackMetadata.from_dict(t) for t in data['tracks']]

        # Rebuild indices
        self.tracks_by_key = {}
        self.tracks_by_bpm = {}
        for track in self.tracks:
            if track.key:
                if track.key not in self.tracks_by_key:
                    self.tracks_by_key[track.key] = []
                self.tracks_by_key[track.key].append(track)

            bpm_int = int(track.bpm)
            if bpm_int not in self.tracks_by_bpm:
                self.tracks_by_bpm[bpm_int] = []
            self.tracks_by_bpm[bpm_int].append(track)

    def stats(self) -> Dict:
        """Get library statistics."""
        if not self.tracks:
            return {'total_tracks': 0}

        bpms = [t.bpm for t in self.tracks]
        energies = [t.energy_level for t in self.tracks]

        return {
            'total_tracks': len(self.tracks),
            'bpm_range': (min(bpms), max(bpms)),
            'bpm_average': sum(bpms) / len(bpms),
            'energy_range': (min(energies), max(energies)),
            'energy_average': sum(energies) / len(energies),
            'keys_represented': len(self.tracks_by_key),
            'labels': len(set(t.label for t in self.tracks if t.label))
        }
