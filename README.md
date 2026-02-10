# Yot_Presentation v5.3 🎙️

<div align="center">

**Intelligent Voice Control for PowerPoint Presentations**

*Navigate slides, jump to pages, and control presentations hands-free with natural language commands*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![PowerPoint](https://img.shields.io/badge/PowerPoint-2016+-orange.svg)](https://www.microsoft.com/microsoft-365/powerpoint)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Commands](#-voice-commands) • [Documentation](#-documentation)

</div>

---

## 📖 Overview

Yot_Presentation is a next-generation, hands-free presentation system that combines **intelligent speech recognition** with **fuzzy logic** to control Microsoft PowerPoint naturally. No need to memorize exact commands—just speak naturally and let the AI understand your intent.

### Why Yot_Presentation?

- 🗣️ **Natural Speech Recognition** - Speak conversationally, no rigid commands
- 🧠 **Fuzzy Logic Engine** - Understands intent even with mumbled or unclear speech
- 🎯 **High Accuracy** - Real-time confidence scoring for every command
- ⚡ **Zero Lag** - Asynchronous processing ensures smooth performance
- 📊 **Professional Logging** - Track all commands and confidence scores

---

## 📸 Application Gallery

<div align="center">

### Visual Demonstration

<table>
  <tr>
    <td align="center">
      <img src="a.jpeg" alt="Interface Screenshot A" width="300"/>
      <br />
      <b>Voice Control Interface</b>
    </td>
    <td align="center">
      <img src="b.jpeg" alt="Interface Screenshot B" width="300"/>
      <br />
      <b>Command Recognition System</b>
    </td>
    <td align="center">
      <img src="c.jpeg" alt="Interface Screenshot C" width="300"/>
      <br />
      <b>Presentation Control in Action</b>
    </td>
  </tr>
</table>

</div>

---

## 🆕 Latest Versions

### v5.2: LOCAL TRAINING DATA 🆕
**New in v5.2** - The training data update! This version introduces comprehensive training data collection for ML/LLM model training:

- 📊 **Text-Only Logging**: Logs all speech-to-text conversions (no audio files)
- 💾 **Local Storage**: SQLite database + JSONL files for portability
- 🤖 **ML Export**: Export training datasets in JSON format for TensorFlow, PyTorch, etc.
- 🔄 **Smart Fallback**: Works offline with cached text
- 🔒 **Privacy-First**: No cloud, no servers, complete data control

**[📖 Read the full v5.2 Documentation](V52_DOCUMENTATION.md)**

**Quick Start v5.2:**
```bash
python powerpoint_voice_controller_v52.py
```

### v5.3: The Human-First Upgrade

Yot_Presentation v5.3 continues the evolution of an intelligent assistant that understands *intent*, not just exact words. Building on the foundation established in v2.0, this version brings enhanced stability and performance improvements.

#### 🔧 Hybrid Matching Engine
- **Stage 1 (Regex)**: High-precision pattern matching for data-heavy commands
  - Examples: "Slide 5", "Jump to 12", "Go to page 7"
- **Stage 2 (Fuzzy Logic)**: AI-powered similarity scoring that recognizes:
  - Mumbled speech ("nex sli" → "next slide")
  - Natural phrasing ("go forward please" → "next slide")
  - Background noise interference
  - Accents and speech variations

#### 📊 Real-Time Confidence Scoring
Every command displays a match confidence percentage:
| Score | Meaning |
|-------|---------|
| **100%** | Exact match via regex |
| **85-99%** | Successfully rescued by fuzzy logic |
| **<85%** | Command not recognized |

#### 🚀 Enhanced Reliability
- **Force Focus Technology**: Keeps PowerPoint in the foreground
- **Asynchronous Processing**: Eliminates lag during voice processing
- **Smart Error Tolerance**: Powered by `thefuzz` library for robust NLP

---

## ✨ Features

### 🎯 Natural Language Processing
- Supports multiple conversational phrases for every action
- No need to memorize "magic words"—speak naturally
- Handles variations, synonyms, and casual phrasing

### 🧭 Smart Navigation
| Feature | Voice Commands |
|---------|----------------|
| **Direct Slide Jumping** | "Slide 5", "Go to page 10", "Jump to 3" |
| **Sequential Navigation** | "Next", "Previous", "Go back", "Advance" |
| **Presentation Control** | "Start", "Begin presenting", "End slideshow" |

### 🔍 Intelligent Mode Detection
- Automatically detects **Edit Mode** vs. **Slideshow Mode**
- Adjusts command execution based on current PowerPoint state
- Seamless transitions between modes

### 📝 Professional Logging
- Timestamped activity logs in `/logs` directory
- Confidence scores for debugging and optimization
- Full command history for post-presentation analysis

---

## 🚀 Installation

### Prerequisites

Before you begin, ensure you have:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Windows** | 10 or 11 | Required for COM automation |
| **PowerPoint** | 2016+ | Presentation software |
| **Python** | 3.8+ | Runtime environment |
| **Microphone** | Any | Voice input |

### Step-by-Step Setup

1️⃣ **Clone the repository**
```bash
git clone https://github.com/AllanRye9/Yot-Presentation.git
cd Yot-Presentation
```

2️⃣ **Install dependencies**
```bash
pip install pywin32 pyautogui SpeechRecognition PyAudio thefuzz
```

> **📌 Note**: If PyAudio installation fails, use:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

3️⃣ **Verify installation**
```bash
python --version  # Should be 3.8 or higher
```

---

## 💡 Usage

### Quick Start

1. **Open PowerPoint** with your presentation
2. **Run the controller**:
   ```bash
   python "yot presentation.py"
   ```
3. **Wait for calibration** (1 second background noise adjustment)
4. **Start speaking** when you see `[SYSTEM ONLINE]` 🟢

### Example Session

```
[SYSTEM ONLINE] 🟢 Listening for commands...

You: "Start the presentation"
✓ Confidence: 100% | Action: Slideshow started

You: "next slide"
✓ Confidence: 100% | Action: Advanced to slide 2

You: "go to slide 5"
✓ Confidence: 95% | Action: Jumped to slide 5

You: "end show"
✓ Confidence: 100% | Action: Exited slideshow
```

---

## 🎤 Voice Commands

### Navigation Commands

| Action | Example Commands |
|--------|------------------|
| **Next Slide** | "next", "next slide", "go forward", "advance" |
| **Previous Slide** | "previous", "back", "go back", "last slide" |
| **Jump to Slide** | "slide 5", "go to 10", "jump to page 3" |
| **First Slide** | "first slide", "go to start", "beginning" |
| **Last Slide** | "last slide", "go to end", "final slide" |

### Presentation Control

| Action | Example Commands |
|--------|------------------|
| **Start Slideshow** | "start", "begin", "start presentation" |
| **End Slideshow** | "end", "stop", "exit presentation" |
| **Pause** | "pause", "wait", "hold" |

### System Commands

| Action | Example Commands |
|--------|------------------|
| **Exit Program** | "quit", "exit", "close program" |
| **Help** | "help", "commands", "what can you do" |

> 💡 **Tip**: You can speak naturally! The fuzzy logic engine will understand variations of these commands.

---

## 📂 Project Structure

```
Yot-Presentation/
│
├── yot presentation.py    # Main application file
├── README.md              # This file
├── requirements.txt       # Python dependencies (optional)
└── logs/                  # Auto-generated logs directory
    └── session_*.log      # Timestamped session logs
```

---

## 🛠️ Technical Details

### Architecture

```
┌─────────────────┐
│  Microphone     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Speech Recognition     │
│  (Google Speech API)    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Hybrid Matcher         │
│  ├─ Regex (Stage 1)     │
│  └─ Fuzzy Logic (Stage 2)│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  PowerPoint Controller  │
│  (COM Automation)       │
└─────────────────────────┘
```

### Key Technologies

- **SpeechRecognition**: Google Web Speech API integration
- **pywin32**: Windows COM automation for PowerPoint control
- **thefuzz**: Fuzzy string matching with Levenshtein distance
- **PyAudio**: Real-time audio stream processing
- **pyautogui**: Keyboard simulation for slideshow control

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>PyAudio installation fails</b></summary>

**Solution**: Use pipwin to install the precompiled binary
```bash
pip install pipwin
pipwin install pyaudio
```
</details>

<details>
<summary><b>Microphone not detected</b></summary>

**Solution**: 
1. Check Windows sound settings
2. Ensure microphone is set as default recording device
3. Test microphone with Windows Voice Recorder
</details>

<details>
<summary><b>PowerPoint doesn't respond to commands</b></summary>

**Solution**:
1. Ensure PowerPoint is running
2. Check if presentation is open
3. Verify Force Focus Technology is working (check logs)
4. Try restarting the script
</details>

<details>
<summary><b>Low confidence scores (<85%)</b></summary>

**Solution**:
1. Speak more clearly and closer to microphone
2. Reduce background noise
3. Adjust microphone sensitivity in Windows settings
4. Check calibration during startup
</details>

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Average Response Time | <500ms |
| Command Recognition Rate | 95%+ |
| Fuzzy Match Accuracy | 85-100% |
| Supported Languages | English (expandable) |

---

## 📦 Version Comparison

### Which Version Should You Use?

| Feature | v5.2 | v5.3 |
|---------|------|------|
| **Voice Control** | ✅ | ✅ |
| **Fuzzy Matching** | ✅ | ✅ |
| **Training Data Logging** | **✅ NEW** | ❌ |
| **ML/LLM Export** | **✅ NEW** | ❌ |
| **Local Database** | **✅ SQLite** | ❌ |
| **Statistics Dashboard** | **✅ Comprehensive** | Basic |
| **Fallback Cache** | **✅ Smart** | Basic |
| **Privacy Features** | **✅ Enhanced** | Good |
| **File Size** | Larger | Smaller |
| **Best For** | ML Training, Data Collection | Simple Voice Control |

**Use v5.2 if you want:**
- To collect training data for ML models
- Comprehensive statistics and monitoring
- Smart offline fallback
- Export capabilities for AI training

**Use v5.3 if you want:**
- Simple, lightweight voice control
- No training data collection
- Minimal file structure

---

## 🗺️ Roadmap

- [x] Training data collection (v5.2)
- [x] ML/LLM export (v5.2)
- [ ] Multi-language support (Spanish, French, German)
- [ ] Custom command profiles
- [ ] Integration with Google Slides
- [ ] Mobile app remote control
- [ ] AI-powered presentation tips
- [ ] Cloud-based command history

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**AllanRye9**

- GitHub: [@AllanRye9](https://github.com/AllanRye9)
- Repository: [Yot-Presentation](https://github.com/AllanRye9/Yot-Presentation)

---

## 🌟 Acknowledgments

- Google Speech Recognition API for speech-to-text processing
- `thefuzz` library for fuzzy string matching
- Microsoft PowerPoint COM API documentation
- The open-source community for inspiration and support

---

<div align="center">

**Made with ❤️ for presenters who want to focus on their message, not their mouse**

⭐ Star this repository if you find it helpful!

</div>