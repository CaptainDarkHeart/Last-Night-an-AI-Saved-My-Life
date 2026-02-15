"""Journey arc planning using deep space house philosophy."""

from typing import List, Optional, Tuple
import random
from datetime import datetime

from .models import (
    TrackMetadata, JourneyArc, Playlist, Transition,
    MusicalKey, EnergyLevel, TextureType, JourneyPosition
)
from .library import TrackLibrary


class JourneyPlanner:
    """Plans DJ journey arcs based on deep space house philosophy."""

    def __init__(self, library: TrackLibrary):
        """
        Initialize journey planner.

        Args:
            library: Track library to select from
        """
        self.library = library

    def create_journey_arc(
        self,
        duration_minutes: int,
        key_center: Optional[MusicalKey] = None,
        bpm_range: Tuple[float, float] = (118, 124),
        energy_progression: str = "gradual_build",
        blend_duration: int = 60
    ) -> JourneyArc:
        """
        Create a journey arc template.

        Args:
            duration_minutes: Target duration in minutes
            key_center: Primary musical key (e.g., A Minor)
            bpm_range: Allowed BPM range
            energy_progression: Type of energy curve ("gradual_build", "peak_and_descent", "steady")
            blend_duration: Default blend duration in seconds

        Returns:
            JourneyArc template
        """
        # Calculate number of tracks needed
        # Assuming average track is 6 minutes, with overlaps
        avg_track_minutes = 6
        overlap_minutes = blend_duration / 60
        num_tracks = int(duration_minutes / (avg_track_minutes - overlap_minutes)) + 1

        # Generate energy curve based on progression type
        energy_curve = self._generate_energy_curve(num_tracks, energy_progression)

        # Deep space house texture requirements
        required_textures = [
            TextureType.ATMOSPHERIC,
            TextureType.HYPNOTIC,
            TextureType.DUB,
            TextureType.MINIMAL
        ]

        # Deep space house preferred labels (from LABEL_GUIDE.md)
        preferred_labels = [
            "Lucidflow",
            "Echocord",
            "Styrax",
            "MCDE",
            "Ostgut Ton",
            "Moodmusic"
        ]

        arc = JourneyArc(
            name=f"Deep Space Journey - {duration_minutes}min",
            description=f"A {energy_progression} journey through deep space house",
            duration_minutes=duration_minutes,
            key_center=key_center,
            bpm_range=bpm_range,
            energy_curve=energy_curve,
            num_tracks=num_tracks,
            required_textures=required_textures,
            preferred_labels=preferred_labels,
            blend_duration=blend_duration
        )

        return arc

    def _generate_energy_curve(self, num_tracks: int, progression: str) -> List[int]:
        """
        Generate energy progression curve (1-10 scale).

        Args:
            num_tracks: Number of tracks in the journey
            progression: Type of progression

        Returns:
            List of energy levels
        """
        if progression == "gradual_build":
            # Start low, build gradually to peak, gentle descent
            # Classic deep space house arc
            third = num_tracks // 3
            curve = []

            # Opening (2-4 energy)
            curve.extend([2 + i % 3 for i in range(third)])

            # Build (4-7 energy)
            for i in range(third):
                energy = 4 + int((i / third) * 3)
                curve.append(energy)

            # Peak and gentle descent (7-5 energy)
            for i in range(num_tracks - len(curve)):
                energy = 7 - int((i / (num_tracks - len(curve))) * 2)
                curve.append(max(energy, 5))

            return curve[:num_tracks]

        elif progression == "peak_and_descent":
            # Build to peak, then descend
            peak_at = int(num_tracks * 0.65)  # Peak at 65% through
            curve = []

            # Build to peak
            for i in range(peak_at):
                energy = 2 + int((i / peak_at) * 6)
                curve.append(energy)

            # Descent from peak
            for i in range(num_tracks - peak_at):
                energy = 8 - int((i / (num_tracks - peak_at)) * 5)
                curve.append(max(energy, 3))

            return curve[:num_tracks]

        elif progression == "steady":
            # Maintain steady energy throughout
            return [5 + (i % 2) for i in range(num_tracks)]

        else:
            # Default: moderate energy
            return [5] * num_tracks

    def generate_playlist(
        self,
        journey_arc: JourneyArc,
        strict_key: bool = False,
        prefer_labels: bool = True
    ) -> Playlist:
        """
        Generate a complete playlist following the journey arc.

        Args:
            journey_arc: Journey arc template to follow
            strict_key: Only use tracks in compatible keys
            prefer_labels: Prefer tracks from preferred labels

        Returns:
            Complete playlist with transitions
        """
        selected_tracks: List[TrackMetadata] = []
        transitions: List[Transition] = []

        # Start with opener
        first_track = self._select_opener(journey_arc, strict_key, prefer_labels)
        if not first_track:
            raise ValueError("No suitable opener found in library")

        selected_tracks.append(first_track)

        # Select subsequent tracks following energy curve
        current_track = first_track
        for i in range(1, journey_arc.num_tracks):
            target_energy = journey_arc.energy_curve[i] if i < len(journey_arc.energy_curve) else 5

            next_track = self._select_next_track(
                current_track=current_track,
                target_energy=target_energy,
                journey_arc=journey_arc,
                strict_key=strict_key,
                prefer_labels=prefer_labels,
                already_used=[t.file_path for t in selected_tracks]
            )

            if not next_track:
                print(f"Warning: Could not find suitable track {i+1}, stopping at {len(selected_tracks)} tracks")
                break

            # Create transition
            transition = self._create_transition(current_track, next_track, journey_arc.blend_duration)
            transitions.append(transition)

            selected_tracks.append(next_track)
            current_track = next_track

        # Create playlist
        playlist = Playlist(
            name=journey_arc.name,
            journey_arc=journey_arc,
            tracks=selected_tracks,
            transitions=transitions,
            created_at=datetime.now().isoformat()
        )

        playlist.calculate_duration()

        return playlist

    def _select_opener(
        self,
        journey_arc: JourneyArc,
        strict_key: bool,
        prefer_labels: bool
    ) -> Optional[TrackMetadata]:
        """Select an opening track for the journey."""
        target_energy = journey_arc.energy_curve[0] if journey_arc.energy_curve else 2

        # Find candidates
        candidates = self.library.find_tracks_by_bpm_range(*journey_arc.bpm_range)

        # Filter by energy
        candidates = [t for t in candidates if abs(t.energy_level - target_energy) <= 1]

        # Filter by key if strict
        if strict_key and journey_arc.key_center:
            candidates = [
                t for t in candidates
                if t.key and self.library.are_keys_compatible(t.key, journey_arc.key_center)
            ]

        # Prefer tracks marked as openers
        openers = [t for t in candidates if t.journey_position == JourneyPosition.OPENER]
        if openers:
            candidates = openers

        # Prefer atmospheric/minimal textures for opening
        atmospheric = [
            t for t in candidates
            if TextureType.ATMOSPHERIC in t.textures or TextureType.MINIMAL in t.textures
        ]
        if atmospheric:
            candidates = atmospheric

        # Prefer preferred labels
        if prefer_labels and journey_arc.preferred_labels:
            label_matches = [
                t for t in candidates
                if t.label and any(lbl in t.label for lbl in journey_arc.preferred_labels)
            ]
            if label_matches:
                candidates = label_matches

        return random.choice(candidates) if candidates else None

    def _select_next_track(
        self,
        current_track: TrackMetadata,
        target_energy: int,
        journey_arc: JourneyArc,
        strict_key: bool,
        prefer_labels: bool,
        already_used: List
    ) -> Optional[TrackMetadata]:
        """Select the next track in the journey."""
        # Find compatible tracks
        candidates = self.library.get_compatible_tracks(
            current_track,
            bpm_tolerance=6.0,
            key_compatible_only=strict_key
        )

        # Remove already used tracks
        candidates = [t for t in candidates if t.file_path not in already_used]

        # Filter by energy (±1 level tolerance)
        candidates = [t for t in candidates if abs(t.energy_level - target_energy) <= 1]

        # Filter by BPM range
        candidates = [
            t for t in candidates
            if journey_arc.bpm_range[0] <= t.bpm <= journey_arc.bpm_range[1]
        ]

        if not candidates:
            return None

        # Prefer key-compatible tracks
        if current_track.key:
            key_compatible = [
                t for t in candidates
                if t.key and self.library.are_keys_compatible(current_track.key, t.key)
            ]
            if key_compatible:
                candidates = key_compatible

        # Prefer preferred labels
        if prefer_labels and journey_arc.preferred_labels:
            label_matches = [
                t for t in candidates
                if t.label and any(lbl in t.label for lbl in journey_arc.preferred_labels)
            ]
            if label_matches:
                candidates = label_matches

        # Score candidates
        scored_candidates = []
        for track in candidates:
            score = self._score_track_compatibility(current_track, track, target_energy)
            scored_candidates.append((track, score))

        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Return top candidate with some randomness
        if len(scored_candidates) <= 3:
            return scored_candidates[0][0]
        else:
            # Pick from top 3 to add variety
            return random.choice([t for t, s in scored_candidates[:3]])

    def _score_track_compatibility(
        self,
        current: TrackMetadata,
        candidate: TrackMetadata,
        target_energy: int
    ) -> float:
        """
        Score how compatible a candidate track is.

        Returns a score from 0-100.
        """
        score = 50.0  # Base score

        # Energy match (+20 points for exact, -5 per level difference)
        energy_diff = abs(candidate.energy_level - target_energy)
        if energy_diff == 0:
            score += 20
        else:
            score -= energy_diff * 5

        # BPM similarity (+15 for very close BPM)
        bpm_diff = abs(current.bpm - candidate.bpm)
        if bpm_diff < 2:
            score += 15
        elif bpm_diff < 4:
            score += 10
        elif bpm_diff < 6:
            score += 5

        # Key compatibility (+25 points)
        if current.key and candidate.key:
            if self.library.are_keys_compatible(current.key, candidate.key):
                score += 25

        # Texture variety (+10 for different textures)
        if current.textures and candidate.textures:
            overlap = set(current.textures) & set(candidate.textures)
            if len(overlap) < len(current.textures):
                score += 10

        # Same artist penalty (avoid repetition)
        if current.artist == candidate.artist:
            score -= 15

        return max(0, score)

    def _create_transition(
        self,
        track_a: TrackMetadata,
        track_b: TrackMetadata,
        blend_duration: float
    ) -> Transition:
        """Create a transition between two tracks."""
        # Calculate transition timing
        # Use outro markers if available, otherwise use last blend_duration seconds
        if track_a.outro_start:
            start_time_a = track_a.outro_start
        else:
            start_time_a = max(0, track_a.duration - blend_duration)

        # Use intro markers if available, otherwise start from beginning
        start_time_b = track_b.intro_start if track_b.intro_start else 0.0

        # Check compatibility
        bpm_ratio = track_a.bpm / track_b.bpm
        bpm_compatible = 0.94 <= bpm_ratio <= 1.06 or 1.88 <= bpm_ratio <= 2.12

        key_compatible = True
        if track_a.key and track_b.key:
            key_compatible = self.library.are_keys_compatible(track_a.key, track_b.key)

        energy_compatible = abs(track_a.energy_level - track_b.energy_level) <= 2

        texture_compatible = True
        if track_a.textures and track_b.textures:
            overlap = set(track_a.textures) & set(track_b.textures)
            texture_compatible = len(overlap) > 0

        # Determine mixing strategy
        strategy = "extended_blend"  # Default for deep space house
        notes = f"Blend from {track_a.title} to {track_b.title} over {blend_duration}s"

        if not bpm_compatible:
            notes += " | BPM adjustment needed"

        if key_compatible:
            notes += " | Harmonic mix"

        transition = Transition(
            track_a=track_a,
            track_b=track_b,
            start_time_a=start_time_a,
            start_time_b=start_time_b,
            blend_duration=blend_duration,
            bpm_compatible=bpm_compatible,
            key_compatible=key_compatible,
            energy_compatible=energy_compatible,
            texture_compatible=texture_compatible,
            strategy=strategy,
            notes=notes
        )

        return transition
