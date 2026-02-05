"""
Unit tests for Yot-Presentation Voice-Controlled PowerPoint System

Note: These tests focus on testing the structure and logic without requiring
actual microphone input or PowerPoint. Full integration tests would require
hardware and Windows environment.
"""

import unittest
import json
import sys
from unittest.mock import Mock, patch, mock_open, MagicMock

# Mock Windows modules for cross-platform testing
sys.modules['win32api'] = MagicMock()
sys.modules['win32con'] = MagicMock()

from yot_presentation import VoiceControlledPowerPoint, THREAD_SHUTDOWN_TIMEOUT_SECONDS


class TestVoiceControlledPowerPoint(unittest.TestCase):
    """Test cases for the VoiceControlledPowerPoint class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            "commands": {
                "next": "Right",
                "previous": "Left",
                "start presentation": "F5"
            },
            "recognition": {
                "energy_threshold": 4000,
                "pause_threshold": 0.8,
                "phrase_time_limit": 3
            }
        }
        self.config_content = json.dumps(self.test_config)

    @patch('yot_presentation.sr.Microphone')
    @patch('yot_presentation.sr.Recognizer')
    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_config_file_not_found(self, mock_file, mock_recognizer, mock_microphone):
        """Test that FileNotFoundError is raised with helpful message when config file is missing"""
        mock_file.side_effect = FileNotFoundError()
        
        with self.assertRaises(FileNotFoundError) as context:
            VoiceControlledPowerPoint("missing_config.json")
        
        self.assertIn("missing_config.json", str(context.exception))
        self.assertIn("not found", str(context.exception))

    @patch('yot_presentation.sr.Microphone')
    @patch('yot_presentation.sr.Recognizer')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json{')
    def test_invalid_json_config(self, mock_file, mock_recognizer, mock_microphone):
        """Test that ValueError is raised with helpful message when config file has invalid JSON"""
        
        with self.assertRaises(ValueError) as context:
            VoiceControlledPowerPoint("config.json")
        
        self.assertIn("Invalid JSON", str(context.exception))

    @patch('yot_presentation.sr.Microphone')
    @patch('yot_presentation.sr.Recognizer')
    @patch('builtins.open', new_callable=mock_open)
    def test_initialization_with_valid_config(self, mock_file, mock_recognizer, mock_microphone):
        """Test successful initialization with valid config"""
        mock_file.return_value.read.return_value = self.config_content
        mock_file.return_value.__enter__.return_value.read.return_value = self.config_content
        
        # Mock the microphone context manager
        mock_mic_instance = Mock()
        mock_microphone.return_value.__enter__ = Mock(return_value=mock_mic_instance)
        mock_microphone.return_value.__exit__ = Mock(return_value=False)
        
        # Mock recognizer
        mock_rec_instance = Mock()
        mock_rec_instance.energy_threshold = 4000
        mock_rec_instance.pause_threshold = 0.8
        mock_recognizer.return_value = mock_rec_instance
        
        with patch('builtins.open', mock_open(read_data=self.config_content)):
            controller = VoiceControlledPowerPoint("config.json")
        
        # Verify commands are loaded
        self.assertEqual(controller.commands["next"], "Right")
        self.assertEqual(controller.commands["previous"], "Left")
        self.assertEqual(controller.commands["start presentation"], "F5")

    @patch('yot_presentation.sr.Microphone')
    @patch('yot_presentation.sr.Recognizer')
    @patch('builtins.open', new_callable=mock_open)
    def test_process_command_with_valid_command(self, mock_file, mock_recognizer, mock_microphone):
        """Test that valid commands are processed correctly"""
        # Setup mocks
        mock_mic_instance = Mock()
        mock_microphone.return_value.__enter__ = Mock(return_value=mock_mic_instance)
        mock_microphone.return_value.__exit__ = Mock(return_value=False)
        
        mock_rec_instance = Mock()
        mock_recognizer.return_value = mock_rec_instance
        
        with patch('builtins.open', mock_open(read_data=self.config_content)):
            controller = VoiceControlledPowerPoint("config.json")
        
        # Mock simulate_keypress to avoid actual key simulation
        controller.simulate_keypress = Mock()
        
        # Test valid command
        result = controller.process_command("next")
        self.assertTrue(result)
        controller.simulate_keypress.assert_called_once_with("Right")

    @patch('yot_presentation.sr.Microphone')
    @patch('yot_presentation.sr.Recognizer')
    @patch('builtins.open', new_callable=mock_open)
    def test_process_command_with_invalid_command(self, mock_file, mock_recognizer, mock_microphone):
        """Test that invalid commands return False"""
        # Setup mocks
        mock_mic_instance = Mock()
        mock_microphone.return_value.__enter__ = Mock(return_value=mock_mic_instance)
        mock_microphone.return_value.__exit__ = Mock(return_value=False)
        
        mock_rec_instance = Mock()
        mock_recognizer.return_value = mock_rec_instance
        
        with patch('builtins.open', mock_open(read_data=self.config_content)):
            controller = VoiceControlledPowerPoint("config.json")
        
        # Mock simulate_keypress
        controller.simulate_keypress = Mock()
        
        # Test invalid command
        result = controller.process_command("invalid command")
        self.assertFalse(result)
        controller.simulate_keypress.assert_not_called()

    @patch('yot_presentation.sr.Microphone')
    @patch('yot_presentation.sr.Recognizer')
    @patch('builtins.open', new_callable=mock_open)
    def test_process_command_case_insensitive(self, mock_file, mock_recognizer, mock_microphone):
        """Test that command processing is case-insensitive"""
        # Setup mocks
        mock_mic_instance = Mock()
        mock_microphone.return_value.__enter__ = Mock(return_value=mock_mic_instance)
        mock_microphone.return_value.__exit__ = Mock(return_value=False)
        
        mock_rec_instance = Mock()
        mock_recognizer.return_value = mock_rec_instance
        
        with patch('builtins.open', mock_open(read_data=self.config_content)):
            controller = VoiceControlledPowerPoint("config.json")
        
        # Mock simulate_keypress
        controller.simulate_keypress = Mock()
        
        # Test with different cases
        result1 = controller.process_command("NEXT")
        result2 = controller.process_command("Next")
        result3 = controller.process_command("next")
        
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)

    def test_thread_shutdown_timeout_constant(self):
        """Test that thread shutdown timeout constant is defined"""
        self.assertIsInstance(THREAD_SHUTDOWN_TIMEOUT_SECONDS, int)
        self.assertGreater(THREAD_SHUTDOWN_TIMEOUT_SECONDS, 0)


if __name__ == '__main__':
    unittest.main()
