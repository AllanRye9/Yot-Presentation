"""
Yot-Presentation: Voice-Controlled PowerPoint System

This software creates a bridge between your microphone and Microsoft PowerPoint application.
It runs a background thread that constantly monitors audio, parses it against a predefined
list of commands, and uses the Windows API to simulate keypresses within PowerPoint.
"""

import speech_recognition as sr
import win32api
import win32con
import json
import threading
import time
from typing import Dict, Optional

# Configuration constants
THREAD_SHUTDOWN_TIMEOUT_SECONDS = 5  # Time to wait for monitoring thread to stop gracefully


class VoiceControlledPowerPoint:
    """
    Main class that manages the voice-controlled PowerPoint system.
    """

    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the voice-controlled PowerPoint system.

        Args:
            config_file: Path to the configuration file containing command mappings.
        """
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.running = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Load configuration
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file '{config_file}' not found. "
                "Please ensure config.json exists in the current directory."
            )
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in configuration file '{config_file}': {e}"
            )
        
        self.commands: Dict[str, str] = self.config.get("commands", {})
        
        # Configure recognizer settings
        recognition_config = self.config.get("recognition", {})
        self.recognizer.energy_threshold = recognition_config.get("energy_threshold", 4000)
        self.recognizer.pause_threshold = recognition_config.get("pause_threshold", 0.8)
        self.phrase_time_limit = recognition_config.get("phrase_time_limit", 3)
        
        # Adjust for ambient noise
        print("Adjusting for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready to receive voice commands.")

    def simulate_keypress(self, key: str) -> None:
        """
        Simulate a keypress using the Windows API.

        Args:
            key: The key to press (e.g., 'Right', 'Left', 'F5', etc.)
        """
        # Map key names to virtual key codes
        key_map = {
            'Right': win32con.VK_RIGHT,
            'Left': win32con.VK_LEFT,
            'Up': win32con.VK_UP,
            'Down': win32con.VK_DOWN,
            'Home': win32con.VK_HOME,
            'End': win32con.VK_END,
            'Escape': win32con.VK_ESCAPE,
            'F5': win32con.VK_F5,
            'Space': win32con.VK_SPACE,
            'Enter': win32con.VK_RETURN,
        }
        
        # Check if it's a mapped key
        if key in key_map:
            vk_code = key_map[key]
        # Check if it's a single character
        elif len(key) == 1:
            vk_code = ord(key.upper())
        else:
            print(f"Unknown key: {key}")
            return
        
        # Simulate key press and release
        win32api.keybd_event(vk_code, 0, 0, 0)  # Key down
        time.sleep(0.05)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
        
        print(f"Simulated keypress: {key}")

    def process_command(self, text: str) -> bool:
        """
        Process a recognized voice command.

        Args:
            text: The recognized text from speech recognition.

        Returns:
            True if a command was recognized and executed, False otherwise.
        """
        text = text.lower().strip()
        
        # Check if the text matches any predefined command
        if text in self.commands:
            key = self.commands[text]
            print(f"Command recognized: '{text}' -> {key}")
            self.simulate_keypress(key)
            return True
        
        return False

    def listen_and_execute(self) -> None:
        """
        Continuously listen for audio and execute commands.
        This method runs in a background thread.
        """
        print("Starting audio monitoring...")
        
        while self.running:
            try:
                # Listen for audio input
                with self.microphone as source:
                    print("Listening...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=1,
                        phrase_time_limit=self.phrase_time_limit
                    )
                
                # Recognize speech using Google Speech Recognition
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"Recognized: {text}")
                    self.process_command(text)
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    pass
                except sr.RequestError as e:
                    print(f"Could not request results from speech recognition service; {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                # No speech detected within timeout
                pass
            except Exception as e:
                print(f"Error in listen_and_execute: {e}")
                time.sleep(1)

    def start(self) -> None:
        """
        Start the voice-controlled PowerPoint system.
        Launches a background thread for audio monitoring.
        """
        if self.running:
            print("System is already running.")
            return
        
        self.running = True
        # Use daemon=False to ensure proper cleanup; stop() method handles thread termination
        self.monitoring_thread = threading.Thread(target=self.listen_and_execute, daemon=False)
        self.monitoring_thread.start()
        print("Voice-controlled PowerPoint system started.")

    def stop(self) -> None:
        """
        Stop the voice-controlled PowerPoint system.
        """
        if not self.running:
            print("System is not running.")
            return
        
        print("Stopping voice-controlled PowerPoint system...")
        self.running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=THREAD_SHUTDOWN_TIMEOUT_SECONDS)
            if self.monitoring_thread.is_alive():
                print("Warning: Monitoring thread did not stop within timeout period.")
        
        print("System stopped.")


def main():
    """
    Main entry point for the application.
    """
    print("=" * 60)
    print("Yot-Presentation: Voice-Controlled PowerPoint System")
    print("=" * 60)
    print()
    print("This software creates a bridge between your microphone and")
    print("Microsoft PowerPoint. It monitors audio and executes commands.")
    print()
    
    # Create and start the voice controller
    controller = VoiceControlledPowerPoint()
    controller.start()
    
    print()
    print("Available commands:")
    for cmd, key in controller.commands.items():
        print(f"  - '{cmd}' -> {key}")
    print()
    print("Press Ctrl+C to stop the system.")
    print()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        controller.stop()
        print("Goodbye!")


if __name__ == "__main__":
    main()
