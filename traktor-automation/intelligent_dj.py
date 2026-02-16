#!/usr/bin/env python3
"""
Intelligent DJ - Enhanced AI DJ with Mix Plan Intelligence
Uses structured mix planning data to make informed mixing decisions.
"""

from traktor_ai_dj import TraktorAIDJ
from mix_plan_parser import MixPlanParser
import time


class IntelligentDJ(TraktorAIDJ):
    """Enhanced AI DJ that uses mix plan intelligence."""

    def __init__(self, mix_plan_file: str, virtual_midi_port: str = "IAC Driver Bus 1"):
        """
        Initialize intelligent DJ with mix plan.

        Args:
            mix_plan_file: Path to mix plan text file
            virtual_midi_port: MIDI port name
        """
        super().__init__(virtual_midi_port)

        # Load mix plan
        self.log("📚 Loading mix plan intelligence...")
        self.parser = MixPlanParser(mix_plan_file)
        self.tracks = self.parser.parse()
        self.log(f"✓ Loaded {len(self.tracks)} tracks with mixing data")

        # Current mix state
        self.current_track_number = 0
        self.next_track_number = 1

    def get_current_track_plan(self):
        """Get mix plan for current track."""
        return self.parser.get_track_by_number(self.current_track_number)

    def get_next_track_plan(self):
        """Get mix plan for next track."""
        return self.parser.get_track_by_number(self.next_track_number)

    def time_to_seconds(self, time_str: str) -> int:
        """Convert time string (M:SS or MM:SS) to seconds."""
        parts = time_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0

    def should_start_transition(self, current_position_seconds: int) -> bool:
        """
        Determine if it's time to start transitioning to next track.

        Args:
            current_position_seconds: Current playback position in seconds

        Returns:
            True if transition should begin
        """
        track_plan = self.get_current_track_plan()
        if not track_plan:
            # Fallback to basic timing
            return current_position_seconds >= 300  # 5 minutes

        # Use mix-out point from plan
        mix_out_seconds = self.time_to_seconds(track_plan.mix_out_point)

        return current_position_seconds >= mix_out_seconds

    def execute_intelligent_blend(self):
        """Execute blend using mix plan intelligence."""
        transition = self.parser.get_transition_data(
            self.current_track_number,
            self.next_track_number
        )

        if not transition:
            self.log("⚠️ No transition data, using default blend")
            self.execute_crossfade(75, self.active_deck, self.next_deck)
            return

        # Extract transition intelligence
        blend_duration = transition['blend_duration']
        bpm_change = transition['bpm_change']
        strategy = transition['strategy']

        # Log intelligent mixing decision
        self.log("🧠 INTELLIGENT TRANSITION")
        self.log(f"   BPM Change: {bpm_change:+d}")
        self.log(f"   Blend: {blend_duration}s")
        self.log(f"   Strategy: {strategy[:80]}...")

        # Execute blend with plan-specific duration
        self.execute_crossfade(blend_duration, self.active_deck, self.next_deck)

    def load_next_track_intelligent(self):
        """Load next track using mix plan data."""
        next_plan = self.get_next_track_plan()

        if not next_plan:
            self.log("⚠️ No plan for next track")
            return

        # Log what we're loading
        track_info = f"{next_plan.artist} - {next_plan.title}"
        if next_plan.remix:
            track_info += f" ({next_plan.remix})"

        self.log(f"📀 Loading: {track_info}")
        self.log(f"   BPM: {next_plan.bpm} | Key: {next_plan.key}")
        self.log(f"   Mix In: {next_plan.mix_in_point}")

        # Navigate to track in browser
        # TODO: Implement intelligent track search/navigation

        # Load to next deck
        self.load_track_to_deck(self.next_track_number - 1, self.next_deck)

    def show_mix_overview(self):
        """Display overview of the entire mix plan."""
        self.log("\n" + "="*70)
        self.log("MIX PLAN OVERVIEW")
        self.log("="*70)

        for i, track in enumerate(self.tracks, 1):
            track_info = f"{track.artist} - {track.title}"
            if track.remix:
                track_info += f" ({track.remix[:30]}...)"

            bpm_indicator = f"{track.bpm_change:+d}" if track.bpm_change != 0 else "→"

            self.log(f"  {i:2d}. {track_info[:50]:<50} | {track.bpm:3d} BPM {bpm_indicator:4s} | {track.key or 'Unknown'}")

        self.log("="*70 + "\n")

    def run_intelligent_mix(self):
        """Run the full mix with intelligence."""
        self.log("\n🎧 INTELLIGENT DJ STARTING...")

        # Show mix overview
        self.show_mix_overview()

        # Connect MIDI
        self.connect_midi()

        # Load first track
        self.log("\n🎬 LOADING OPENING TRACK...")
        self.current_track_number = 1
        self.next_track_number = 2

        first_track = self.get_current_track_plan()
        if first_track:
            self.log(f"Opening: {first_track.artist} - {first_track.title}")
            self.log(f"  {first_track.critical_notes[:100]}...")

        # Load and play first track
        self.load_track_to_deck(0, self.active_deck)
        time.sleep(1)

        self.enable_sync(self.active_deck)
        self.play_deck(self.active_deck)

        self.log(f"\n▶️ DECK {self.active_deck} PLAYING - Mix has begun!")
        self.log("\nPress Ctrl+C to stop\n")

        # Main mixing loop
        try:
            track_start_time = time.time()

            while True:
                current_position = int(time.time() - track_start_time)

                # Check if it's time to transition
                if self.should_start_transition(current_position):
                    self.log(f"\n⏰ Transition point reached at {current_position}s")

                    # Prepare next track
                    self.log("🔄 PREPARING NEXT TRACK...")
                    self.load_next_track_intelligent()
                    time.sleep(1)

                    # Enable sync on next deck
                    self.enable_sync(self.next_deck)

                    # Start playing next deck
                    self.play_deck(self.next_deck)
                    time.sleep(1)

                    # Execute intelligent blend
                    self.execute_intelligent_blend()

                    # Swap decks
                    self.active_deck, self.next_deck = self.next_deck, self.active_deck

                    # Move to next tracks
                    self.current_track_number += 1
                    self.next_track_number += 1

                    # Reset timer
                    track_start_time = time.time()

                    # Check if mix is complete
                    if self.current_track_number > len(self.tracks):
                        self.log("\n🎉 MIX COMPLETE!")
                        break

                    next_plan = self.get_current_track_plan()
                    if next_plan:
                        self.log(f"\n▶️ NOW PLAYING: {next_plan.artist} - {next_plan.title}")

                # Status update every 30 seconds
                if current_position % 30 == 0 and current_position > 0:
                    track_plan = self.get_current_track_plan()
                    if track_plan:
                        remaining = self.time_to_seconds(track_plan.duration.replace('~', '')) - current_position
                        self.log(f"⏱️ Position: {current_position}s | Remaining: ~{remaining}s")

                time.sleep(1)

        except KeyboardInterrupt:
            self.log("\n\n🛑 Mix stopped by user")

        finally:
            self.disconnect_midi()
            self.log("👋 Intelligent DJ session ended\n")


def main():
    """Main entry point."""
    try:
        dj = IntelligentDJ('data/lucidflow_mix_plan.txt')
        dj.run_intelligent_mix()
    except FileNotFoundError:
        print("❌ Mix plan file not found: data/lucidflow_mix_plan.txt")
        print("   Make sure the file exists in the data/ directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
