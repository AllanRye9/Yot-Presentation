#!/usr/bin/env python3

import sys
import time
import datetime
import re
import threading
import queue
import logging
from pathlib import Path
import win32com.client
import pythoncom
import pyautogui
import speech_recognition as sr

# --- Dependency Check ---
REQUIRED = [
    ('win32com.client', 'pywin32'),
    ('pyautogui', 'pyautogui'), 
    ('speech_recognition', 'SpeechRecognition')
]

def check_deps():
    missing = []
    for mod, pkg in REQUIRED:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"CRITICAL: Missing packages: {', '.join(missing)}")
        print(f"Run: pip install {' '.join(missing)}")
        sys.exit(1)

check_deps()

# ============================================================================
# CONFIGURATION & COMMANDS
# ============================================================================

COMMANDS = {
    "next_slide": {"patterns": ["next", "forward", "advance", "right"], "key": "right"},
    "prev_slide": {"patterns": ["previous", "back", "left", "go back"], "key": "left"},
    "jump_slide": {"patterns": [r"slide (\d+)", r"page (\d+)", r"jump to (\d+)"], "key": None},
    "start_show": {"patterns": ["start", "present", "begin"], "key": "f5"},
    "end_show":   {"patterns": ["stop", "exit", "escape", "end presentation"], "key": "esc"},
    "blackout":   {"patterns": ["black screen", "darken", "black"], "key": "b"},
    "help":       {"patterns": ["help", "commands", "what can i say"], "key": None},
    "exit":       {"patterns": ["terminate program", "quit system", "shutdown controller"], "key": None}
}

# ============================================================================
# CORE ENGINE
# ============================================================================

class PPTController:
    def __init__(self):
        self.running = True
        self.command_queue = queue.Queue()
        self._setup_paths()
        self._init_logger()
        self._compile_regex()
        
        self.ppt_app = None
        self.presentation = None
        
        # Stats
        self.stats = {"total": 0, "success": 0}

    def _setup_paths(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"ppt_{datetime.datetime.now().strftime('%Y%m%d')}.log"

    def _init_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("PPTVoice")

    def _compile_regex(self):
        self.patterns = []
        for cmd, data in COMMANDS.items():
            for p in data['patterns']:
                self.patterns.append({
                    're': re.compile(p, re.IGNORECASE),
                    'cmd': cmd,
                    'is_regex': r'(\d+)' in p
                })

    def connect(self):
        """Connects to a running instance of PowerPoint."""
        try:
            pythoncom.CoInitialize()
            self.ppt_app = win32com.client.GetActiveObject("PowerPoint.Application")
            self.presentation = self.ppt_app.ActivePresentation
            self.logger.info(f"Connected to: {self.presentation.Name}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    def sync_state(self):
        """Refresh PPT state to ensure we aren't out of sync."""
        try:
            if self.ppt_app.SlideShowWindows.Count > 0:
                view = self.ppt_app.SlideShowWindows(1).View
                return view.Slide.SlideNumber, True
            return self.ppt_app.ActiveWindow.View.Slide.SlideNumber, False
        except:
            return 1, False

    def _focus_window(self):
        """Standardizes window focus before sending keys."""
        try:
            # Simple focus using AppActivate
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.AppActivate("PowerPoint")
            return True
        except:
            return False

    def listen_loop(self):
        """Threaded microphone listener."""
        recognizer = sr.Recognizer()
        # Adjust sensitivity for better performance
        recognizer.dynamic_energy_threshold = True
        
        while self.running:
            with sr.Microphone() as source:
                try:
                    # Short ambient adjustment
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    text = recognizer.recognize_google(audio).lower()
                    self.command_queue.put(text)
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    continue
                except Exception as e:
                    self.logger.debug(f"Mic error: {e}")

    def execute(self, text):
        """Logic for executing identified commands."""
        self.stats["total"] += 1
        found_cmd = None
        params = None

        for p in self.patterns:
            match = p['re'].search(text)
            if match:
                found_cmd = p['cmd']
                if p['is_regex']:
                    params = match.groups()[0]
                break

        if not found_cmd:
            return False

        self._focus_window()
        time.sleep(0.1)

        try:
            if found_cmd == "next_slide":
                pyautogui.press('right')
            elif found_cmd == "prev_slide":
                pyautogui.press('left')
            elif found_cmd == "start_show":
                pyautogui.press('f5')
            elif found_cmd == "end_show":
                pyautogui.press('esc')
            elif found_cmd == "blackout":
                pyautogui.press('b')
            elif found_cmd == "jump_slide" and params:
                # In SlideShow mode, typing number + enter jumps to slide
                pyautogui.write(params)
                pyautogui.press('enter')
            elif found_cmd == "exit":
                self.running = False
                return True
            
            self.logger.info(f"Executed: {found_cmd} ({text})")
            self.stats["success"] += 1
            return True
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            return False

    def run(self):
        if not self.connect():
            print("Please open PowerPoint and a presentation first!")
            return

        # Start listening thread
        threading.Thread(target=self.listen_loop, daemon=True).start()
        
        print("\n" + "="*50)
        print(" SYSTEM ONLINE - Listening for commands...")
        print(" (Say 'next', 'back', 'slide 5', or 'terminate program')")
        print("="*50 + "\n")

        try:
            while self.running:
                try:
                    text = self.command_queue.get(timeout=0.1)
                    print(f"🎤 Heard: '{text}'")
                    self.execute(text)
                except queue.Empty:
                    continue
        except KeyboardInterrupt:
            self.running = False
        
        print(f"\nSession Summary: {self.stats['success']}/{self.stats['total']} commands successful.")

if __name__ == "__main__":
    app = PPTController()
    app.run()