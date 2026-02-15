"""Data models for track metadata and journey arcs."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict
import json


class EnergyLevel(Enum):
    """Energy level classification (1-10 scale)."""
    MINIMAL = 1      # Deep, atmospheric, beatless
    LOW = 2          # Subtle percussion, ambient
    BUILDING = 3     # Gradual introduction of elements
    MODERATE = 4     # Steady groove established
    WARM = 5         # Mid-set energy, engaging
    ENERGETIC = 6    # Increased intensity
    DRIVING = 7      # Strong momentum
    PEAK = 8         # High energy, peak moments
    INTENSE = 9      # Maximum drive
    CLIMAX = 10      # Absolute peak


class TextureType(Enum):
    """Texture classification for deep space house."""
    ATMOSPHERIC = "atmospheric"      # Spacey, ambient pads
    PERCUSSIVE = "percussive"       # Rhythm-focused
    VOCAL = "vocal"                 # Vocal elements
    MELODIC = "melodic"             # Strong melodic content
    MINIMAL = "minimal"             # Stripped back
    LAYERED = "layered"             # Complex, multi-textured
    DUB = "dub"                     # Dub techno influences
    TRIBAL = "tribal"               # Tribal percussion
    HYPNOTIC = "hypnotic"           # Repetitive, trance-inducing
    ORGANIC = "organic"             # Natural, warm sounds


class JourneyPosition(Enum):
    """Position in the DJ journey arc."""
    OPENER = "opener"               # Set opening (low energy)
    WARM_UP = "warm_up"             # Building atmosphere
    BUILDER = "builder"             # Energy escalation
    CORE = "core"                   # Main set body
    PEAK = "peak"                   # Peak energy moments
    BRIDGE = "bridge"               # Transition zones
    WIND_DOWN = "wind_down"         # Gentle descent
    CLOSER = "closer"               # Set closing


class MusicalKey(Enum):
    """Musical key using Camelot notation."""
    # Minor keys
    A_MINOR = "1A"
    E_MINOR = "2A"
    B_MINOR = "3A"
    F_SHARP_MINOR = "4A"
    D_FLAT_MINOR = "5A"
    A_FLAT_MINOR = "6A"
    E_FLAT_MINOR = "7A"
    B_FLAT_MINOR = "8A"
    F_MINOR = "9A"
    C_MINOR = "10A"
    G_MINOR = "11A"
    D_MINOR = "12A"

    # Major keys
    C_MAJOR = "1B"
    G_MAJOR = "2B"
    D_MAJOR = "3B"
    A_MAJOR = "4B"
    E_MAJOR = "5B"
    B_MAJOR = "6B"
    F_SHARP_MAJOR = "7B"
    D_FLAT_MAJOR = "8B"
    A_FLAT_MAJOR = "9B"
    E_FLAT_MAJOR = "10B"
    B_FLAT_MAJOR = "11B"
    F_MAJOR = "12B"


@dataclass
class CuePoint:
    """DJ cue point information."""
    time: float                      # Time in seconds
    label: str                       # Cue label (e.g., "Intro", "Drop", "Outro")
    color: Optional[str] = None      # Color code for Traktor
    confidence: float = 1.0          # AI detection confidence (0-1)


@dataclass
class TrackMetadata:
    """Complete track metadata for DJ analysis."""
    # File information
    file_path: Path
    title: str
    artist: str

    # Musical analysis
    bpm: float
    key: Optional[MusicalKey] = None
    duration: float = 0.0            # Duration in seconds

    # Energy and texture
    energy_level: int = 5            # 1-10 scale
    textures: List[TextureType] = field(default_factory=list)

    # Journey classification
    journey_position: Optional[JourneyPosition] = None

    # Label and style
    label: Optional[str] = None
    genre: List[str] = field(default_factory=list)

    # Cue points
    intro_start: Optional[float] = None
    intro_end: Optional[float] = None
    outro_start: Optional[float] = None
    outro_end: Optional[float] = None
    cue_points: List[CuePoint] = field(default_factory=list)

    # Beat information
    num_beats: Optional[int] = None
    downbeats: List[float] = field(default_factory=list)

    # Additional metadata
    year: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'file_path': str(self.file_path),
            'title': self.title,
            'artist': self.artist,
            'bpm': self.bpm,
            'key': self.key.value if self.key else None,
            'duration': self.duration,
            'energy_level': self.energy_level,
            'textures': [t.value for t in self.textures],
            'journey_position': self.journey_position.value if self.journey_position else None,
            'label': self.label,
            'genre': self.genre,
            'intro_start': self.intro_start,
            'intro_end': self.intro_end,
            'outro_start': self.outro_start,
            'outro_end': self.outro_end,
            'cue_points': [
                {'time': cp.time, 'label': cp.label, 'color': cp.color, 'confidence': cp.confidence}
                for cp in self.cue_points
            ],
            'num_beats': self.num_beats,
            'downbeats': self.downbeats,
            'year': self.year,
            'tags': self.tags,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TrackMetadata':
        """Create from dictionary."""
        return cls(
            file_path=Path(data['file_path']),
            title=data['title'],
            artist=data['artist'],
            bpm=data['bpm'],
            key=MusicalKey(data['key']) if data.get('key') else None,
            duration=data.get('duration', 0.0),
            energy_level=data.get('energy_level', 5),
            textures=[TextureType(t) for t in data.get('textures', [])],
            journey_position=JourneyPosition(data['journey_position']) if data.get('journey_position') else None,
            label=data.get('label'),
            genre=data.get('genre', []),
            intro_start=data.get('intro_start'),
            intro_end=data.get('intro_end'),
            outro_start=data.get('outro_start'),
            outro_end=data.get('outro_end'),
            cue_points=[
                CuePoint(**cp) for cp in data.get('cue_points', [])
            ],
            num_beats=data.get('num_beats'),
            downbeats=data.get('downbeats', []),
            year=data.get('year'),
            tags=data.get('tags', []),
            notes=data.get('notes', '')
        )


@dataclass
class JourneyArc:
    """Represents a complete DJ journey arc."""
    name: str
    description: str
    duration_minutes: int

    # Journey characteristics
    key_center: Optional[MusicalKey] = None  # Primary key (e.g., A Minor)
    bpm_range: tuple = (118, 124)            # BPM range for the journey
    energy_curve: List[int] = field(default_factory=list)  # Energy progression

    # Track requirements
    num_tracks: int = 0
    required_textures: List[TextureType] = field(default_factory=list)

    # Style preferences
    preferred_labels: List[str] = field(default_factory=list)
    blend_duration: int = 60                 # Default blend duration in seconds

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'key_center': self.key_center.value if self.key_center else None,
            'bpm_range': self.bpm_range,
            'energy_curve': self.energy_curve,
            'num_tracks': self.num_tracks,
            'required_textures': [t.value for t in self.required_textures],
            'preferred_labels': self.preferred_labels,
            'blend_duration': self.blend_duration
        }


@dataclass
class Transition:
    """Represents a transition between two tracks."""
    track_a: TrackMetadata
    track_b: TrackMetadata

    # Transition timing
    start_time_a: float              # When to start fading out Track A
    start_time_b: float              # When to start fading in Track B
    blend_duration: float            # Duration of the blend

    # Compatibility metrics
    bpm_compatible: bool = True
    key_compatible: bool = True
    energy_compatible: bool = True
    texture_compatible: bool = True

    # Mixing strategy
    strategy: str = "extended_blend"  # e.g., "extended_blend", "quick_cut", "bassline_swap"
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'track_a': self.track_a.to_dict(),
            'track_b': self.track_b.to_dict(),
            'start_time_a': self.start_time_a,
            'start_time_b': self.start_time_b,
            'blend_duration': self.blend_duration,
            'bpm_compatible': self.bpm_compatible,
            'key_compatible': self.key_compatible,
            'energy_compatible': self.energy_compatible,
            'texture_compatible': self.texture_compatible,
            'strategy': self.strategy,
            'notes': self.notes
        }


@dataclass
class Playlist:
    """Generated DJ playlist with transitions."""
    name: str
    journey_arc: JourneyArc
    tracks: List[TrackMetadata]
    transitions: List[Transition] = field(default_factory=list)

    # Playlist metadata
    total_duration: float = 0.0
    created_at: Optional[str] = None

    def calculate_duration(self) -> float:
        """Calculate total playlist duration including blends."""
        if not self.tracks:
            return 0.0

        total = self.tracks[0].duration
        for transition in self.transitions:
            # Add next track duration minus blend overlap
            total += transition.track_b.duration - transition.blend_duration

        self.total_duration = total
        return total

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'journey_arc': self.journey_arc.to_dict(),
            'tracks': [t.to_dict() for t in self.tracks],
            'transitions': [tr.to_dict() for tr in self.transitions],
            'total_duration': self.total_duration,
            'created_at': self.created_at
        }

    def to_json(self, file_path: Path) -> None:
        """Save playlist to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def to_m3u(self, file_path: Path) -> None:
        """Export playlist to M3U format for Mixxx/Traktor."""
        with open(file_path, 'w') as f:
            f.write("#EXTM3U\n")
            f.write(f"#PLAYLIST:{self.name}\n\n")

            for track in self.tracks:
                duration_int = int(track.duration)
                f.write(f"#EXTINF:{duration_int},{track.artist} - {track.title}\n")
                f.write(f"{track.file_path}\n")
