#!/usr/bin/env python3
"""
EQ + Mixer FX Mapping Test
===========================

Verifies all 8 EQ/MixerFX MIDI mappings are working in Traktor.
Run with Traktor open and IAC Driver active.

Usage:
    python3 test_eq_mapping.py
"""

import mido
import time

PORT = "IAC Driver Bus 1"

# CC map — mirrors traktor_ai_dj.py
CC = {
    'deck_a_eq_high': 50,
    'deck_a_eq_mid':  51,
    'deck_a_eq_low':  52,
    'deck_b_eq_high': 53,
    'deck_b_eq_mid':  54,
    'deck_b_eq_low':  55,
    'deck_a_mixer_fx': 56,
    'deck_b_mixer_fx': 57,
}

CENTER = 64   # 0 dB / neutral
CUT    = 0    # Full cut
PAUSE  = 1.5  # Seconds between each test step


def send(port, cc, value):
    port.send(mido.Message('control_change', control=cc, value=value))


def test_band(port, label, cc):
    """Cut → restore a single band so you can see it move in Traktor."""
    print(f"  {label:22s} (CC {cc}): ", end="", flush=True)

    # Start at centre
    send(port, cc, CENTER)
    time.sleep(0.3)

    # Cut to zero
    send(port, cc, CUT)
    print("CUT → ", end="", flush=True)
    time.sleep(PAUSE)

    # Restore to centre
    send(port, cc, CENTER)
    print("RESTORED")
    time.sleep(0.5)


def test_bass_swap(port):
    """Simulate a deep-house bass swap over 10 seconds (shortened for testing)."""
    print("\n--- Bass swap simulation (10s) ---")
    print("  Watch Deck A Low cut while Deck B Low rises...\n")

    steps = 50
    duration = 10.0
    dt = duration / steps

    # Set both decks to known state
    send(port, CC['deck_a_eq_low'], CENTER)
    send(port, CC['deck_b_eq_low'], CUT)
    time.sleep(0.5)

    # Phase 1: cut Deck A bass
    for i in range(steps // 2):
        p = i / (steps // 2 - 1)
        smooth = p * p * (3 - 2 * p)  # S-curve
        send(port, CC['deck_a_eq_low'], int(CENTER * (1.0 - smooth)))
        time.sleep(dt)

    # Phase 2: bring in Deck B bass
    for i in range(steps // 2):
        p = i / (steps // 2 - 1)
        smooth = p * p * (3 - 2 * p)
        send(port, CC['deck_b_eq_low'], int(CENTER * smooth))
        time.sleep(dt)

    # Snap to final state
    send(port, CC['deck_a_eq_low'], CUT)
    send(port, CC['deck_b_eq_low'], CENTER)
    print("  Bass swap complete.")


def test_mixer_fx(port):
    """Sweep Mixer FX Adjust up and back on both decks."""
    print("\n--- Mixer FX Adjust sweep ---")
    print("  Deck A: sweeping up then back...")

    steps = 30
    duration = 3.0
    dt = duration / steps

    send(port, CC['deck_a_mixer_fx'], CENTER)
    time.sleep(0.3)

    for i in range(steps):
        p = i / (steps - 1)
        send(port, CC['deck_a_mixer_fx'], int(CENTER + p * (127 - CENTER)))
        time.sleep(dt)

    for i in range(steps):
        p = i / (steps - 1)
        send(port, CC['deck_a_mixer_fx'], int(127 - p * (127 - CENTER)))
        time.sleep(dt)

    print("  Deck A MixerFX restored.")

    print("  Deck B: sweeping up then back...")
    send(port, CC['deck_b_mixer_fx'], CENTER)
    time.sleep(0.3)

    for i in range(steps):
        p = i / (steps - 1)
        send(port, CC['deck_b_mixer_fx'], int(CENTER + p * (127 - CENTER)))
        time.sleep(dt)

    for i in range(steps):
        p = i / (steps - 1)
        send(port, CC['deck_b_mixer_fx'], int(127 - p * (127 - CENTER)))
        time.sleep(dt)

    print("  Deck B MixerFX restored.")


def reset_all(port):
    print("\n  Resetting all bands to centre...")
    for cc in CC.values():
        send(port, cc, CENTER)
    time.sleep(0.2)


def main():
    print("""
╔══════════════════════════════════════════╗
║     EQ + Mixer FX Mapping Test          ║
║     Traktor AI DJ — Z1 Integration      ║
╚══════════════════════════════════════════╝

Each band will cut to zero then restore to centre.
Watch the corresponding knob move in Traktor.
""")

    try:
        port = mido.open_output(PORT)
    except Exception as e:
        print(f"✗ Could not open '{PORT}': {e}")
        print("  Make sure IAC Driver Bus 1 is online (Audio MIDI Setup).")
        return

    print(f"✓ Connected to {PORT}\n")

    print("=== Individual band tests ===\n")
    print("[ Deck A ]")
    test_band(port, "EQ High",    CC['deck_a_eq_high'])
    test_band(port, "EQ Mid",     CC['deck_a_eq_mid'])
    test_band(port, "EQ Low",     CC['deck_a_eq_low'])
    test_band(port, "Mixer FX",   CC['deck_a_mixer_fx'])

    print("\n[ Deck B ]")
    test_band(port, "EQ High",    CC['deck_b_eq_high'])
    test_band(port, "EQ Mid",     CC['deck_b_eq_mid'])
    test_band(port, "EQ Low",     CC['deck_b_eq_low'])
    test_band(port, "Mixer FX",   CC['deck_b_mixer_fx'])

    test_bass_swap(port)
    test_mixer_fx(port)
    reset_all(port)

    port.close()
    print("\n✓ All tests complete. If any knob didn't move, check its mapping in")
    print("  Traktor → Preferences → Controller Manager → Generic MIDI (IAC Driver).")


if __name__ == "__main__":
    main()
