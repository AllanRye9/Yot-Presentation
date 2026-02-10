#!/usr/bin/env python3
"""
Test script for v5.2 training data components
Tests all core functionality without requiring PowerPoint or microphone
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from powerpoint_voice_controller_v52 import (
    AudioTextRecord,
    LocalTrainingDataLogger,
    FallbackCache,
    TrainingDataManager,
    Config
)

def test_audio_text_record():
    """Test AudioTextRecord creation and serialization"""
    print("Testing AudioTextRecord...")
    
    record = AudioTextRecord.create("next slide", "next_slide", 0.95, "google")
    assert record.text == "next slide"
    assert record.command_matched == "next_slide"
    assert record.confidence == 0.95
    assert record.source == "google"
    
    # Test serialization
    record_dict = record.to_dict()
    assert record_dict['text'] == "next slide"
    
    record_json = record.to_json()
    assert "next slide" in record_json
    
    # Test deserialization
    record2 = AudioTextRecord.from_dict(record_dict)
    assert record2.text == record.text
    
    print("✅ AudioTextRecord tests passed")

def test_fallback_cache():
    """Test FallbackCache functionality"""
    print("\nTesting FallbackCache...")
    
    # Use temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FallbackCache(Path(tmpdir))
        
        # Test set/get
        cache.set("test_key", "test text")
        text = cache.get("test_key")
        assert text == "test text"
        
        # Test missing key
        missing = cache.get("nonexistent")
        assert missing is None
        
        # Test stats
        stats = cache.stats()
        assert stats['items'] == 1
        assert stats['size_kb'] >= 0
        
        print("✅ FallbackCache tests passed")

def test_local_training_data_logger():
    """Test LocalTrainingDataLogger functionality"""
    print("\nTesting LocalTrainingDataLogger...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = LocalTrainingDataLogger(Path(tmpdir))
        
        # Log some records
        records = [
            AudioTextRecord.create("next slide", "next_slide", 0.95, "google"),
            AudioTextRecord.create("zoom in", "zoom_in", 0.88, "google"),
            AudioTextRecord.create("pen tool", "pen_tool", 0.92, "google"),
        ]
        
        for record in records:
            logger.log_text(record)
        
        # Test statistics
        stats = logger.get_statistics()
        assert stats['total_entries'] == 3
        assert stats['by_command']['next_slide'] == 1
        assert stats['by_command']['zoom_in'] == 1
        assert stats['by_source']['google'] == 3
        assert stats['confidence']['average'] > 0.85
        
        # Test export
        export_path = Path(tmpdir) / "export.json"
        export_data = logger.export_training_set(export_path, threshold=0.85)
        assert export_data['metadata']['total_examples'] == 3
        assert len(export_data['training_examples']) == 3
        
        # Verify export file exists
        assert export_path.exists()
        
        # Test archive
        archive_path = logger.archive_data()
        assert archive_path.exists()
        assert archive_path.suffix == '.gz'
        
        print("✅ LocalTrainingDataLogger tests passed")

def test_training_data_manager():
    """Test TrainingDataManager high-level API"""
    print("\nTesting TrainingDataManager...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = TrainingDataManager(Path(tmpdir))
        
        # Log some texts
        manager.log_text("next slide", "next_slide", 0.95)
        manager.log_text("zoom in", "zoom_in", 0.88)
        manager.log_text("pen tool", "pen_tool", 0.92)
        manager.log_text("back", "prev_slide", 0.90)
        
        # Test statistics
        stats = manager.get_statistics()
        assert stats['training_data']['total_entries'] == 4
        assert stats['fallback_cache']['items'] == 0  # No cache items yet
        
        # Test batch creation
        batch = manager.create_batch(batch_size=2)
        assert len(batch) == 2
        assert 'input' in batch[0]
        assert 'label' in batch[0]
        assert 'confidence' in batch[0]
        
        # Test export
        export_path = Path(tmpdir) / "training_export.json"
        export_data = manager.export(export_path, threshold=0.85)
        assert export_data['metadata']['total_examples'] == 4
        
        # Test archive
        archive_path = manager.archive()
        assert archive_path.exists()
        
        print("✅ TrainingDataManager tests passed")

def test_config():
    """Test Config dataclass"""
    print("\nTesting Config...")
    
    config = Config()
    assert config.ENABLE_TRAINING
    assert config.LOG_CONFIDENCE_THRESHOLD == 0.70
    
    # High-precision logging only
    config2 = Config(
        ENABLE_TRAINING=False,
        TRAINING_DATA_DIR="custom_dir",
        FUZZY_THRESHOLD=85
    )
    assert not config2.ENABLE_TRAINING
    assert config2.TRAINING_DATA_DIR == Path("custom_dir")
    assert config2.FUZZY_THRESHOLD == 85
    
    print("✅ Config tests passed")

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print(" 🧪 Running v5.2 Component Tests")
    print("="*60)
    
    try:
        test_audio_text_record()
        test_fallback_cache()
        test_local_training_data_logger()
        test_training_data_manager()
        test_config()
        
        print("\n" + "="*60)
        print(" ✅ ALL TESTS PASSED!")
        print("="*60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
