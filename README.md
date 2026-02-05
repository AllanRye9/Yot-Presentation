# Yot-Presentation

Voice-Controlled PowerPoint Presentation System

## Overview

Yot-Presentation is a voice-controlled system that creates a bridge between your microphone and Microsoft PowerPoint application. It runs a background thread that constantly monitors audio, parses it against a predefined list of commands, and uses the Windows API to simulate keypresses within PowerPoint.

## Features

- **Real-time Audio Monitoring**: Continuously listens to your microphone in a background thread
- **Voice Command Recognition**: Uses Google Speech Recognition to parse spoken commands
- **Windows API Integration**: Simulates keypresses to control PowerPoint presentations
- **Customizable Commands**: Easy-to-configure command mappings via JSON configuration
- **Hands-Free Presentation**: Navigate through slides without touching the keyboard

## Requirements

- Windows Operating System (required for Windows API keypress simulation)
- Python 3.7 or higher
- Microphone
- Internet connection (for Google Speech Recognition API)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AllanRye9/Yot-Presentation.git
cd Yot-Presentation
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Note: If you encounter issues installing PyAudio, you may need to install it using a precompiled wheel:
```bash
pip install pipwin
pipwin install pyaudio
```

## Usage

1. Ensure your microphone is connected and working
2. Open Microsoft PowerPoint (or have a presentation ready)
3. Run the application:
```bash
python yot_presentation.py
```

4. The system will calibrate for ambient noise and then start listening for commands
5. Speak the voice commands clearly to control your presentation
6. Press Ctrl+C to stop the system

## Available Commands

The following voice commands are available by default:

| Voice Command | Action | Key Simulated |
|---------------|--------|---------------|
| "next" or "next slide" | Go to next slide | Right Arrow |
| "previous" or "previous slide" or "back" | Go to previous slide | Left Arrow |
| "first" or "first slide" | Go to first slide | Home |
| "last" or "last slide" | Go to last slide | End |
| "start presentation" | Start slideshow | F5 |
| "end presentation" or "exit presentation" or "stop" | Exit slideshow | Escape |
| "black screen" | Toggle black screen | B |
| "white screen" | Toggle white screen | W |

## Configuration

You can customize the commands and recognition settings by editing the `config.json` file:

```json
{
  "commands": {
    "next": "Right",
    "custom command": "Space"
  },
  "recognition": {
    "energy_threshold": 4000,
    "pause_threshold": 0.8,
    "phrase_time_limit": 3
  }
}
```

### Configuration Options

- **commands**: Dictionary mapping voice commands to keyboard keys
- **energy_threshold**: Minimum audio energy to consider for recording (default: 4000)
- **pause_threshold**: Seconds of silence before a phrase is considered complete (default: 0.8)
- **phrase_time_limit**: Maximum seconds for a phrase (default: 3)

## How It Works

1. **Audio Monitoring**: A background thread continuously monitors your microphone for audio input
2. **Speech Recognition**: When audio is detected, it's sent to Google Speech Recognition API
3. **Command Parsing**: The recognized text is compared against the predefined command list
4. **Keypress Simulation**: If a match is found, the corresponding key is simulated using Windows API
5. **PowerPoint Control**: The simulated keypress controls PowerPoint as if you pressed the key manually

## Architecture

The system consists of three main components:

1. **VoiceControlledPowerPoint Class**: Main controller that manages the entire system
2. **Audio Monitoring Thread**: Background thread that continuously listens for voice input
3. **Windows API Integration**: Uses win32api to simulate keypresses

## Troubleshooting

### Microphone not detected
- Ensure your microphone is properly connected
- Check Windows sound settings to verify the microphone is set as the default recording device

### Commands not recognized
- Speak clearly and at a moderate pace
- Ensure you have an active internet connection
- Try adjusting the `energy_threshold` in config.json if the system is too sensitive or not sensitive enough

### PyAudio installation issues
- On Windows, use pipwin to install PyAudio: `pipwin install pyaudio`
- Alternatively, download a precompiled wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Uses [SpeechRecognition](https://github.com/Uberi/speech_recognition) library for voice recognition
- Uses [PyWin32](https://github.com/mhammond/pywin32) for Windows API integration
- Powered by Google Speech Recognition API