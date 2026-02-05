# Yot-Presentation
🎙️ PowerPoint Voice Control System
A robust, hands-free solution for presenters. This Python-based utility uses real-time speech recognition to control Microsoft PowerPoint, allowing speakers to navigate slides, jump to specific pages, and manage presentation modes using only their voice.

## ✨ Features

- **Natural Language Processing**: Supports multiple phrases for a single action (e.g., "next," "advance," or "forward").
- **Direct Slide Jumping**: Say "Slide 5" to jump immediately to that page.
- **Smart State Sync**: Automatically detects if you are in "Edit Mode" or "Slideshow Mode" and adjusts command execution accordingly.
- **Automatic Focus**: Attempts to bring the PowerPoint window to the foreground before executing commands.
- **Robust Logging**: Keeps a timestamped log of all recognized phrases and executed actions in the `/logs` directory.

## 🚦 Getting Started

### Prerequisites

- **Operating System**: Windows 10 or 11 (Required for COM automation).
- **Software**: Microsoft PowerPoint (2016 or newer recommended).
- **Python**: 3.8 or higher.
- **Hardware**: A working microphone.

### Installation

1. Clone or download this repository to your local machine.

2. Install dependencies using pip:

```bash
pip install pywin32 pyautogui SpeechRecognition PyAudio
```

**Note**: If PyAudio fails to install, try using `pip install pipwin` followed by `pipwin install pyaudio`.

## 🛠️ Usage

1. Launch PowerPoint and open the presentation you wish to use.

2. Run the controller:

```bash
python ppt_voice_control.py
```

3. **Wait for Calibration**: The system will spend 1 second calibrating for background noise.

4. **Speak Clearly**: Once you see the `[SYSTEM ONLINE]` message, speak your commands.

### Voice Commands

| Action | Spoken Command (Examples) |
|--------|---------------------------|
| Next Slide | "Next", "Forward", "Right", "Advance" |
| Previous Slide | "Back", "Previous", "Left", "Go back" |
| Jump to Slide | "Slide 10", "Jump to 5", "Page 2" |
| Presentation Mode | "Start presentation", "Begin", "Present" |
| Exit Slideshow | "Stop", "End", "Escape" |
| Screen Control | "Black screen", "White screen" |
| System | "Help", "Status", "Exit program" |

## ⚙️ Configuration

You can customize the command patterns or the sensitivity in the code:

- **Sensitivity**: Adjust `recognizer.energy_threshold` in the script. A higher value (e.g., 600) makes the mic less sensitive to background chatter.
- **New Commands**: Add entries to the `COMMANDS` dictionary to map new phrases to keyboard shortcuts.

## 📂 Project Structure

- `ppt_voice_control.py`: The main application script.
- `/logs`: Automatically generated directory containing session logs.
- `README.md`: This documentation.

## ⚠️ Known Limitations

- **Internet Access**: The default engine uses Google Speech Recognition, which requires an active internet connection.
- **Focus Issues**: Windows security may occasionally prevent the script from "stealing focus." If commands aren't working, click on the PowerPoint window once to ensure it is the active application.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
