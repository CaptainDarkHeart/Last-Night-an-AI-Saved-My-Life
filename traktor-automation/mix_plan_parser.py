#!/usr/bin/env python3
"""
Mix Plan Parser
Extracts structured mixing data from detailed DJ mix notes.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CuePoint:
    """Represents a cue point in a track."""
    name: str
    time: str  # Format: "M:SS" or "MM:SS"
    description: str


@dataclass
class TrackMixPlan:
    """Complete mixing plan for a single track."""
    track_number: int
    artist: str
    title: str
    remix: Optional[str]
    duration: str
    bpm: int
    key: Optional[str]
    label: str

    # Cue points
    cue_points: List[CuePoint]

    # Mixing metadata
    mix_in_point: str
    mix_out_point: str
    blend_duration_seconds: int

    # Transition info
    from_track_bpm: Optional[int]
    bpm_change: int
    from_track_key: Optional[str]
    tonal_relationship: str

    # Mixing notes
    transition_strategy: str
    textural_notes: str
    vibe_progression: str
    loop_opportunities: str
    critical_notes: str


class MixPlanParser:
    """Parses detailed DJ mix notes into structured data."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.tracks: List[TrackMixPlan] = []

    def parse(self) -> List[TrackMixPlan]:
        """Parse the entire mix plan file."""
        with open(self.filepath, 'r') as f:
            content = f.read()

        # Split by track sections
        track_sections = re.split(r'(?=TRACK \d+:|###TRACK \d+:)', content)

        for section in track_sections:
            if section.strip():
                track = self._parse_track_section(section)
                if track:
                    self.tracks.append(track)

        return self.tracks

    def _parse_track_section(self, section: str) -> Optional[TrackMixPlan]:
        """Parse a single track section."""
        lines = section.split('\n')

        # Extract track number and title
        title_match = re.match(r'(?:###)?TRACK (\d+):\s*(.+)', lines[0])
        if not title_match:
            return None

        track_number = int(title_match.group(1))
        full_title = title_match.group(2)

        # Parse artist, title, remix
        artist, title, remix = self._parse_title(full_title)

        # Extract metadata
        duration = self._extract_field(section, r'Duration:\s*([~\d:]+)')
        bpm_str = self._extract_field(section, r'BPM:\s*(\d+)')
        bpm = int(bpm_str) if bpm_str else 0
        key = self._extract_field(section, r'Key:\s*([A-G][#b]?\s*(?:Minor|Major|minor|major))')
        label = self._extract_field(section, r'Label:\s*(.+)')

        # Extract cue points
        cue_points = self._extract_cue_points(section)

        # Extract mixing points
        mix_in = self._extract_field(section, r'Mix-In Point:\s*(\d+:\d+)')
        mix_out = self._extract_field(section, r'Mix-Out Point:\s*(\d+:\d+)')

        # Extract blend duration
        blend_match = re.search(r'Blend Duration:\s*(\d+)', section)
        blend_duration = int(blend_match.group(1)) if blend_match else 75  # Default 75 seconds

        # Extract BPM change
        bpm_change_match = re.search(r'BPM Change:\s*(?:~)?(\d+)\s*→\s*(?:~)?(\d+)', section)
        if bpm_change_match:
            from_bpm = int(bpm_change_match.group(1))
            bpm_change = bpm - from_bpm
        else:
            from_bpm = None
            bpm_change = 0

        # Extract tonal relationship
        tonal_rel = self._extract_field(section, r'Tonal Relationship:\s*(.+)')
        from_key = None
        if tonal_rel and '→' in tonal_rel:
            keys = tonal_rel.split('→')
            from_key = keys[0].strip()

        # Extract mixing notes sections
        transition_strategy = self._extract_multiline(section, r'Transition Strategy:\s*(.+?)(?=Textural Notes:|Vibe Progression:|$)', re.DOTALL)
        textural_notes = self._extract_multiline(section, r'Textural Notes:\s*(.+?)(?=Vibe Progression:|Blend Duration:|$)', re.DOTALL)
        vibe_progression = self._extract_multiline(section, r'Vibe Progression:\s*(.+?)(?=Blend Duration:|Loop Opportunities:|$)', re.DOTALL)
        loop_opportunities = self._extract_multiline(section, r'Loop Opportunities:\s*(.+?)(?=Next Track Setup:|Critical Transition Notes:|$)', re.DOTALL)
        critical_notes = self._extract_multiline(section, r'Critical Transition Notes:\s*(.+?)(?=TRACK \d+:|###TRACK \d+:|$)', re.DOTALL)

        return TrackMixPlan(
            track_number=track_number,
            artist=artist,
            title=title,
            remix=remix,
            duration=duration or "unknown",
            bpm=bpm,
            key=key,
            label=label or "unknown",
            cue_points=cue_points,
            mix_in_point=mix_in or "1:30",
            mix_out_point=mix_out or "6:00",
            blend_duration_seconds=blend_duration,
            from_track_bpm=from_bpm,
            bpm_change=bpm_change,
            from_track_key=from_key,
            tonal_relationship=tonal_rel or "unknown",
            transition_strategy=transition_strategy.strip() if transition_strategy else "",
            textural_notes=textural_notes.strip() if textural_notes else "",
            vibe_progression=vibe_progression.strip() if vibe_progression else "",
            loop_opportunities=loop_opportunities.strip() if loop_opportunities else "",
            critical_notes=critical_notes.strip() if critical_notes else ""
        )

    def _parse_title(self, full_title: str) -> tuple:
        """Parse artist, title, and remix from full title string."""
        # Handle remixes in parentheses
        remix_match = re.search(r'\(([^)]+(?:Remix|remix|Mix|mix|Session|session))\)$', full_title)
        remix = remix_match.group(1) if remix_match else None

        # Remove remix part if found
        base_title = re.sub(r'\s*\([^)]+(?:Remix|remix|Mix|mix|Session|session)\)$', '', full_title)

        # Split artist and title
        if ' - ' in base_title:
            parts = base_title.split(' - ', 1)
            artist = parts[0].strip()
            title = parts[1].strip()
        else:
            artist = "Unknown"
            title = base_title.strip()

        return artist, title, remix

    def _extract_field(self, text: str, pattern: str) -> Optional[str]:
        """Extract a single field using regex."""
        match = re.search(pattern, text)
        return match.group(1).strip() if match else None

    def _extract_multiline(self, text: str, pattern: str, flags=0) -> Optional[str]:
        """Extract multiline field using regex."""
        match = re.search(pattern, text, flags)
        if match:
            content = match.group(1).strip()
            # Clean up extra whitespace
            content = re.sub(r'\s+', ' ', content)
            return content
        return None

    def _extract_cue_points(self, section: str) -> List[CuePoint]:
        """Extract all cue points from the section."""
        cue_points = []

        # Find the "Traktor Cue Points:" section
        cue_section_match = re.search(r'Traktor Cue Points:\s*(.+?)(?=Mixing Notes:|$)', section, re.DOTALL)
        if not cue_section_match:
            return cue_points

        cue_section = cue_section_match.group(1)

        # Extract individual cue points
        # Format: "Cue Name: M:SS (description)"
        cue_pattern = r'([^:\n]+):\s*(\d+:\d+)\s*(?:\(([^)]+)\))?'

        for match in re.finditer(cue_pattern, cue_section):
            name = match.group(1).strip()
            time = match.group(2).strip()
            description = match.group(3).strip() if match.group(3) else ""

            # Skip lines that are clearly not cue points
            if name and time and not name.startswith('From') and not name.startswith('BPM'):
                cue_points.append(CuePoint(name=name, time=time, description=description))

        return cue_points

    def get_track_by_number(self, track_number: int) -> Optional[TrackMixPlan]:
        """Get a specific track by number."""
        for track in self.tracks:
            if track.track_number == track_number:
                return track
        return None

    def get_transition_data(self, from_track: int, to_track: int) -> Optional[Dict]:
        """Get transition data between two tracks."""
        to_track_data = self.get_track_by_number(to_track)
        if not to_track_data:
            return None

        return {
            'from_track': from_track,
            'to_track': to_track,
            'start_blend_at': to_track_data.mix_out_point if from_track > 0 else "0:00",
            'bring_in_at': to_track_data.mix_in_point,
            'blend_duration': to_track_data.blend_duration_seconds,
            'bpm_change': to_track_data.bpm_change,
            'tonal_relationship': to_track_data.tonal_relationship,
            'strategy': to_track_data.transition_strategy,
            'critical_notes': to_track_data.critical_notes
        }


def main():
    """Test the parser."""
    parser = MixPlanParser('data/lucidflow_mix_plan.txt')
    tracks = parser.parse()

    print(f"Parsed {len(tracks)} tracks\n")
    print("="*70)

    for track in tracks[:3]:  # Show first 3 tracks
        print(f"\nTrack {track.track_number}: {track.artist} - {track.title}")
        if track.remix:
            print(f"  Remix: {track.remix}")
        print(f"  BPM: {track.bpm} | Key: {track.key} | Duration: {track.duration}")
        print(f"  Mix In: {track.mix_in_point} | Mix Out: {track.mix_out_point}")
        print(f"  Blend: {track.blend_duration_seconds}s | BPM Change: {track.bpm_change:+d}")
        print(f"  Cue Points: {len(track.cue_points)}")
        if track.critical_notes:
            print(f"  Critical: {track.critical_notes[:100]}...")
        print("-"*70)

    # Test transition data
    print("\n" + "="*70)
    print("Example Transition: Track 1 → Track 2")
    print("="*70)
    transition = parser.get_transition_data(1, 2)
    if transition:
        for key, value in transition.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
