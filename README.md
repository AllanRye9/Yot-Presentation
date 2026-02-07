# Yot_Presentation v2.0

🎙️ **AI-Powered Voice Control for PowerPoint Presentations**

A next-generation, hands-free presentation system that uses intelligent speech recognition and fuzzy logic to control Microsoft PowerPoint naturally. Speak conversationally—no need to memorize exact commands.

---

## 🆕 What's New in v2.0

### **The Human-First Upgrade**

Version 2.0 transforms Yot_Presentation from a rigid command parser into an intelligent assistant that understands *intent*, not just exact words.

#### **1. Hybrid Matching Engine**
- **Stage 1 (Regex)**: High-precision pattern matching for data-heavy commands like "Slide 5" or "Jump to 12"
- **Stage 2 (Fuzzy Logic)**: AI-powered similarity scoring that recognizes your intent even with:
  - Mumbled speech ("nex sli" → "next slide")
  - Natural phrasing ("go forward please" → "next slide")
  - Background noise interference
  - Accents and speech variations

#### **2. Real-Time Confidence Scoring**
Every command now displays a match confidence percentage:
- **100%**: Exact match via regex
- **85-99%**: Successfully rescued by fuzzy logic
- **<85%**: Command not recognized (adjust your speech or environment)

#### **3. Enhanced Reliability**
- **Force Focus Technology**: Aggressively brings PowerPoint to the foreground, preventing commands from "getting lost" to background windows
- **Asynchronous Processing**: Separated listening and execution threads eliminate lag and freezing during voice processing
- **Smart Error Tolerance**: Powered by the `thefuzz` library for robust natural language understanding

---

## ✨ Core Features

### **Natural Language Processing**
- Supports multiple conversational phrases for every action
- No need to memorize "magic words"—speak naturally
- Handles variations, synonyms, and casual phrasing

### **Smart Navigation**
- **Direct Slide Jumping**: "Slide 5", "Go to page 10", "Jump to 3"
- **Sequential Navigation**: "Next", "Previous", "Go back", "Advance"
- **Presentation Control**: "Start", "Begin presenting", "End slideshow"

### **Intelligent Mode Detection**
- Automatically detects Edit Mode vs. Slideshow Mode
- Adjusts command execution based on current PowerPoint state
- Seamless transitions between modes

### **Professional Logging**
- Timestamped activity logs in `/logs` directory
- Confidence scores for debugging and optimization
- Full command history for post-presentation analysis

---

## 🚦 Getting Started

### **Prerequisites**

- **Operating System**: Windows 10 or 11 (required for COM automation)
- **Software**: Microsoft PowerPoint 2016 or newer
- **Python**: 3.8 or higher
- **Hardware**: Working microphone

### **Installation**

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/yot_presentation.git
cd yot_presentation
```

2. **Install dependencies**:
```bash
pip install pywin32 pyautogui SpeechRecognition PyAudio thefuzz
```

**Note**: If PyAudio installation fails:
```bash
pip install pipwin
pipwin install pyaudio
```

### **Quick Start**

1. Open your PowerPoint presentation
2. Run the controller:
```bash
python yot_presentation.py
```
3. **Wait for calibration** (1 second background noise adjustment)
4. **Start speaking** when you see `[SYSTEM ONLINE]`

---

## 🎤 Voice Commands

### **Navigation Commands**

| Action | Spoken Examples |
|--------|----------------|
| **Next Slide** | "Next", "Forward", "Right", "Advance", "Go ahead" |
| **Previous Slide** | "Back", "Previous", "Left", "Go back", "Rewind" |
| **Jump to Slide** | "Slide 10", "Jump to 5", "Page 2", "Go to 15" |

### **Presentation Control**

| Action | Spoken Examples |
|--------|----------------|
| **Start Slideshow** | "Start presentation", "Begin", "Present", "Let's start" |
| **Exit Slideshow** | "Stop", "End", "Escape", "Finish" |
| **Black Screen** | "Black screen", "Blank screen", "Go dark" |
| **White Screen** | "White screen", "Blank white" |

### **System Commands**

| Action | Spoken Examples |
|--------|----------------|
| **Help** | "Help", "What can you do", "Commands" |
| **Status** | "Status", "Are you listening" |
| **Exit Program** | "Exit program", "Quit", "Shutdown" |

---

## ⚙️ Configuration

### **Sensitivity Tuning**

Adjust microphone sensitivity in `yot_presentation.py`:
```python
recognizer.energy_threshold = 600  # Higher = less sensitive to background noise
```

### **Fuzzy Match Threshold**

Customize the minimum confidence score for fuzzy matching:
```python
FUZZY_THRESHOLD = 85  # Minimum similarity percentage (0-100)
```

### **Adding Custom Commands**

Extend the command dictionary with your own voice triggers:
```python
COMMANDS = {
    "next_slide": {
        "patterns": ["next", "forward", "advance", "your custom phrase"],
        "action": "next_slide_function"
    }
}
```

---

## 📂 Project Structure
```
yot_presentation/
├── yot_presentation.py        # Main application
├── logs/                      # Auto-generated session logs
│   └── session_YYYYMMDD_HHMMSS.log
├── README.md                  # This documentation
└── requirements.txt           # Python dependencies
```

---

## 🔧 Troubleshooting

### **Commands Not Working**
- **Check Focus**: Click the PowerPoint window once to ensure it's the active application
- **Review Logs**: Check `/logs` for confidence scores—low scores indicate unclear speech
- **Adjust Sensitivity**: Lower `energy_threshold` if commands aren't being heard

### **High False Positive Rate**
- Increase `energy_threshold` to reduce sensitivity to background noise
- Raise `FUZZY_THRESHOLD` to require more exact matches

### **Internet Connection Issues**
- The default Google Speech Recognition engine requires active internet
- For offline use, consider switching to Sphinx (limited accuracy)

---

## ⚠️ Known Limitations

- **Internet Required**: Default speech recognition uses Google's cloud service
- **Windows Only**: COM automation is platform-specific
- **Focus Management**: Windows security may occasionally prevent automatic focus—manually click PowerPoint if needed
- **Multilingual Support**: Currently optimized for English commands

---

## 🛣️ Roadmap

- [ ] Offline speech recognition mode
- [ ] Multi-language support
- [ ] Custom wake word detection
- [ ] Integration with Google Slides and Keynote
- [ ] Voice-controlled annotations and laser pointer
- [ ] Mobile companion app for remote control

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 💡 Tips for Best Results

1. **Speak clearly** at a consistent volume
2. **Pause briefly** between commands
3. **Monitor confidence scores** in the console to optimize your speech patterns
4. **Use direct commands** for critical moments (e.g., "Slide 10" is more reliable than "go to that slide about revenue")
5. **Test your setup** before the actual presentation

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/AllanRye9/yot_presentation/issues)
- **Documentation**: [Wiki](https://github.com/AllanRye9/yot_presentation/wiki)
- **Discussions**: [Community Forum](https://github.com/AllanRye9/yot_presentation/discussions)

---

**Made with ❤️ for presenters who want to focus on their message, not their mouse.**
