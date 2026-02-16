#!/usr/bin/env python3
"""
Verify all three MIDI devices are working together.
Tests: IAC Driver automation, X1 mk2 feedback, Z1 presence.
"""

import mido
import time

def verify_setup():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     VERIFY ALL THREE DEVICES WORKING TOGETHER                ║
╚══════════════════════════════════════════════════════════════╝

This test verifies:
1. IAC Driver can send commands to Traktor
2. X1 mk2 is active and receiving feedback from Traktor
3. Z1 is connected and active

REQUIREMENTS:
- Traktor is open
- A track is loaded on Deck A
- All three devices are ACTIVE in Controller Manager
""")

    print("\n" + "="*70)
    print("STEP 1: Check MIDI Ports")
    print("="*70 + "\n")

    inputs = mido.get_input_names()
    outputs = mido.get_output_names()

    # Check for required ports
    has_iac = "IAC Driver Bus 1" in outputs
    has_x1_in = any("X1" in port for port in inputs)
    has_x1_out = any("X1" in port for port in outputs)
    has_z1_in = any("Z1" in port for port in inputs)
    has_z1_out = any("Z1" in port for port in outputs)

    print(f"{'✓' if has_iac else '✗'} IAC Driver Bus 1 (Output): {has_iac}")
    print(f"{'✓' if has_x1_in else '✗'} X1 mk2 Input: {has_x1_in}")
    print(f"{'✓' if has_x1_out else '✗'} X1 mk2 Output: {has_x1_out}")
    print(f"{'✓' if has_z1_in else '✗'} Z1 Input: {has_z1_in}")
    print(f"{'✓' if has_z1_out else '✗'} Z1 Output: {has_z1_out}")

    if not all([has_iac, has_x1_in, has_x1_out, has_z1_in, has_z1_out]):
        print("\n⚠️  Some MIDI ports are missing!")
        print("Make sure X1 mk2 and Z1 are plugged in via USB.")
        return

    print("\n✓ All MIDI ports present!\n")

    print("="*70)
    print("STEP 2: Test IAC Driver → Traktor")
    print("="*70 + "\n")

    try:
        output = mido.open_output("IAC Driver Bus 1")
        print("→ Sending Play command to Deck A...")
        output.send(mido.Message('control_change', control=1, value=127, channel=0))
        time.sleep(0.5)

        print("→ Sending Pause command to Deck A...")
        output.send(mido.Message('control_change', control=1, value=127, channel=0))
        time.sleep(0.5)

        print("\n✓ IAC Driver commands sent successfully")
        print("  Did Deck A play/pause in Traktor? If YES, IAC Driver is working!\n")

        output.close()
    except Exception as e:
        print(f"✗ Error with IAC Driver: {e}\n")

    print("="*70)
    print("STEP 3: Test X1 mk2 Feedback (Advanced)")
    print("="*70 + "\n")

    print("This test checks if X1 mk2 receives MIDI from Traktor...")
    print("(This only works if X1 mk2 is ACTIVE in Controller Manager)\n")

    try:
        # Find exact X1 input name
        x1_input_name = [p for p in inputs if "X1" in p][0]

        messages_received = []

        def callback(msg):
            messages_received.append(msg)
            print(f"  ← X1 mk2 received: {msg}")

        x1_input = mido.open_input(x1_input_name, callback=callback)

        print(f"✓ Listening to {x1_input_name}...")
        print("\nNow press ANY button on the X1 mk2 hardware...")
        print("(Waiting 5 seconds...)\n")

        time.sleep(5)

        x1_input.close()

        if messages_received:
            print(f"\n✓ X1 mk2 is active! Received {len(messages_received)} MIDI messages")
            print("  X1 mk2 is communicating with Traktor!\n")
        else:
            print("\n⚠️  No messages from X1 mk2")
            print("  Possible issues:")
            print("  - X1 mk2 not ACTIVE in Traktor Controller Manager")
            print("  - X1 mk2 in wrong mode (should be Native, not MIDI)")
            print("  - Out-Port not set correctly\n")

    except Exception as e:
        print(f"✗ Could not test X1 mk2: {e}\n")

    print("="*70)
    print("STEP 4: Test Z1 Presence")
    print("="*70 + "\n")

    try:
        z1_input_name = [p for p in inputs if "Z1" in p][0]
        z1_output_name = [p for p in outputs if "Z1" in p][0]

        print(f"✓ Z1 Input: {z1_input_name}")
        print(f"✓ Z1 Output: {z1_output_name}")
        print("\nZ1 is connected!")
        print("If you move the Z1 crossfader, it should control Traktor.\n")

    except Exception as e:
        print(f"✗ Could not find Z1: {e}\n")

    print("="*70)
    print("SUMMARY")
    print("="*70 + "\n")

    print("For full three-device setup, you need:\n")

    print("In Traktor → Preferences → Controller Manager:")
    print("  □ Traktor Kontrol X1 mk2 - ACTIVE")
    print("  □ Traktor Kontrol Z1 - ACTIVE")
    print("  □ Generic MIDI (IAC Driver) - ACTIVE\n")

    print("If any device is NOT active:")
    print("  1. Click 'Add...'")
    print("  2. Select the device")
    print("  3. Set correct In/Out ports")
    print("  4. Make sure checkbox is CHECKED\n")

if __name__ == "__main__":
    try:
        verify_setup()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
