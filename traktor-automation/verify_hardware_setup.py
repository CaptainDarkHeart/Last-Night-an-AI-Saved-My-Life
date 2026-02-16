#!/usr/bin/env python3
"""
Hardware Setup Verification
Checks if X1 mk2 and Z1 controllers are connected and ready.
"""

import mido
import subprocess

def check_usb_devices():
    """Check for connected NI controllers via USB."""
    print("="*70)
    print("CHECKING USB DEVICES")
    print("="*70 + "\n")

    try:
        result = subprocess.run(
            ['system_profiler', 'SPUSBDataType'],
            capture_output=True,
            text=True
        )

        lines = result.stdout.split('\n')
        found_ni = False

        for i, line in enumerate(lines):
            if 'Native Instruments' in line or 'Kontrol' in line or 'Traktor' in line:
                found_ni = True
                # Print context around the match
                start = max(0, i-2)
                end = min(len(lines), i+5)
                print('\n'.join(lines[start:end]))
                print('-'*70)

        if not found_ni:
            print("⚠️  No Native Instruments controllers found via USB")
            print("   Make sure X1 mk2 and Z1 are plugged in\n")
        else:
            print("✓ Found Native Instruments devices\n")

    except Exception as e:
        print(f"Error checking USB: {e}\n")


def check_midi_devices():
    """Check for MIDI devices."""
    print("="*70)
    print("CHECKING MIDI DEVICES")
    print("="*70 + "\n")

    print("MIDI Inputs:")
    inputs = mido.get_input_names()
    if inputs:
        for port in inputs:
            if 'Traktor' in port or 'Kontrol' in port or 'IAC' in port:
                print(f"  ✓ {port}")
            else:
                print(f"    {port}")
    else:
        print("  (none)")

    print("\nMIDI Outputs:")
    outputs = mido.get_output_names()
    if outputs:
        for port in outputs:
            if 'Traktor' in port or 'Kontrol' in port or 'IAC' in port:
                print(f"  ✓ {port}")
            else:
                print(f"    {port}")
    else:
        print("  (none)")

    print()


def check_traktor_requirements():
    """Verify what should be configured in Traktor."""
    print("="*70)
    print("TRAKTOR CONTROLLER MANAGER CHECKLIST")
    print("="*70 + "\n")

    print("You should have THREE devices in Traktor Controller Manager:\n")

    print("1. ✓ Traktor Kontrol X1 mk2 (Native Mode)")
    print("   - Device Type: Traktor Kontrol X1 mk2")
    print("   - In-Port: Traktor Kontrol X1 Mk2 Input")
    print("   - Out-Port: Traktor Kontrol X1 Mk2 Output")
    print("   - Deck: Left → A, Right → B")
    print("   - Active: ✓\n")

    print("2. ✓ Traktor Kontrol Z1 (Native Mode)")
    print("   - Device Type: Traktor Kontrol Z1")
    print("   - In-Port: Traktor Kontrol Z1 Input")
    print("   - Out-Port: Traktor Kontrol Z1 Output")
    print("   - Deck: A+B")
    print("   - Active: ✓\n")

    print("3. ✓ Generic MIDI (AI DJ Automation)")
    print("   - Device Type: Generic MIDI")
    print("   - In-Port: IAC Driver Bus 1")
    print("   - Out-Port: IAC Driver Bus 1")
    print("   - Custom mapping (18 commands)")
    print("   - Active: ✓\n")

    print("="*70)
    print("AUDIO SETUP (if using Z1 as audio interface)")
    print("="*70 + "\n")

    print("Traktor Preferences → Audio Setup:")
    print("  - Audio Device: Traktor Kontrol Z1")
    print("  - Output Routing:")
    print("    - Master: Traktor Kontrol Z1 (Main Out)")
    print("    - Monitor: Traktor Kontrol Z1 (Cue Out)")
    print("  - Channel Setup: Dual (Stereo)\n")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         X1 MK2 + Z1 HARDWARE SETUP VERIFICATION              ║
╚══════════════════════════════════════════════════════════════╝

This script checks if your hardware is connected and ready.
""")

    check_usb_devices()
    check_midi_devices()
    check_traktor_requirements()

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70 + "\n")

    print("1. Plug in X1 mk2 and Z1 via USB (if not already)")
    print("2. Make sure both are in NATIVE mode (not MIDI mode)")
    print("3. Open Traktor → Preferences → Controller Manager")
    print("4. Verify all three devices are listed and ACTIVE")
    print("5. Set Z1 as audio device (Preferences → Audio Setup)")
    print("6. Run the AI DJ automation:\n")
    print("   cd '/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation'")
    print("   python3 traktor_ai_dj.py\n")
    print("7. Watch the X1 mk2 LEDs respond to automation!")
    print("8. Use Z1 crossfader for manual control\n")

    print("See HARDWARE_MIDI_SETUP.md for complete setup guide.\n")


if __name__ == "__main__":
    main()
