"""
Example usage of Yot-Presentation Voice-Controlled PowerPoint System

This script demonstrates how to use the VoiceControlledPowerPoint class
programmatically.
"""

from yot_presentation import VoiceControlledPowerPoint
import time


def main():
    print("Yot-Presentation Example")
    print("-" * 40)
    
    # Create an instance of the voice controller
    controller = VoiceControlledPowerPoint("config.json")
    
    # Start the voice control system
    controller.start()
    
    print("\nVoice control is now active!")
    print("Try saying commands like:")
    print("  - 'next slide'")
    print("  - 'previous slide'")
    print("  - 'start presentation'")
    print("\nThe system will run for 60 seconds as a demo.")
    print("Press Ctrl+C to stop earlier.\n")
    
    try:
        # Run for 60 seconds as a demo
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n\nStopping early...")
    
    # Stop the voice control system
    controller.stop()
    print("Demo complete!")


if __name__ == "__main__":
    main()
