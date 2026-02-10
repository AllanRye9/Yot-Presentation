#!/usr/bin/env python3
"""
Standalone test script for v5.2 training data components
Tests core functionality without external dependencies
"""

import json
import sqlite3
import hashlib
import tarfile
import tempfile
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, List, Any

# ============================================================================
# Minimal versions of the classes for testing
# ============================================================================

@dataclass
class AudioTextRecord:
    """Single training example (text only)"""
    id: str
    text: str
    command_matched: str
    confidence: float
    timestamp: str
    source: str
    user_id: str = "default"
    
    @staticmethod
    def create(text: str, command: str, confidence: float, source: str = "google", 
               user_id: str = "default") -> 'AudioTextRecord':
        """Create a new record with auto-generated ID and timestamp"""
        import time
        record_id = hashlib.sha256(
            f"{text}{command}{time.time()}".encode()
        ).hexdigest()[:16]
        
        timestamp = datetime.now().isoformat()
        
        return AudioTextRecord(
            id=record_id,
            text=text,
            command_matched=command,
            confidence=confidence,
            timestamp=timestamp,
            source=source,
            user_id=user_id
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

class FallbackCache:
    """Local text-only cache for offline fallback"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.cache_file = data_dir / "fallback_cache.json"
        self.cache: Dict[str, str] = {}
        self._load()
    
    def _load(self):
        """Load cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}
    
    def _save(self):
        """Save cache to file"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2)
    
    def set(self, key: str, text: str):
        """Cache text"""
        self.cache[key] = text
        self._save()
    
    def get(self, key: str) -> Optional[str]:
        """Retrieve cached text"""
        return self.cache.get(key)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_size = 0
        if self.cache_file.exists():
            cache_size = self.cache_file.stat().st_size / 1024  # KB
        
        return {
            'items': len(self.cache),
            'size_kb': round(cache_size, 2)
        }

class LocalTrainingDataLogger:
    """Stores text records in SQLite + JSONL"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.db_file = data_dir / "training_data.db"
        self.jsonl_file = data_dir / "training_data.jsonl"
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                command_matched TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                user_id TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_command 
            ON training_data(command_matched)
        ''')
        
        conn.commit()
        conn.close()
    
    def log_text(self, record: AudioTextRecord):
        """Log a text record"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO training_data
                (id, text, command_matched, confidence, timestamp, source, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.id,
                record.text,
                record.command_matched,
                record.confidence,
                record.timestamp,
                record.source,
                record.user_id
            ))
            conn.commit()
        finally:
            conn.close()
        
        # JSONL storage
        with open(self.jsonl_file, 'a', encoding='utf-8') as f:
            f.write(record.to_json() + '\n')
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get training data statistics"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM training_data')
            total = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT command_matched, COUNT(*) 
                FROM training_data 
                GROUP BY command_matched
            ''')
            by_command = dict(cursor.fetchall())
            
            cursor.execute('''
                SELECT source, COUNT(*) 
                FROM training_data 
                GROUP BY source
            ''')
            by_source = dict(cursor.fetchall())
            
            cursor.execute('''
                SELECT AVG(confidence), MIN(confidence), MAX(confidence)
                FROM training_data
            ''')
            avg_conf, min_conf, max_conf = cursor.fetchone()
            
            db_size = 0
            if self.db_file.exists():
                db_size = self.db_file.stat().st_size / (1024 * 1024)
            
            return {
                'total_entries': total,
                'database_size_mb': round(db_size, 2),
                'by_command': by_command,
                'by_source': by_source,
                'confidence': {
                    'average': round(avg_conf or 0, 2),
                    'minimum': round(min_conf or 0, 2),
                    'maximum': round(max_conf or 0, 2)
                }
            }
        finally:
            conn.close()
    
    def export_training_set(self, output_path: Path, 
                           threshold: float = 0.80) -> Dict[str, Any]:
        """Export training dataset for ML"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT text, command_matched, confidence, timestamp, source
                FROM training_data
                WHERE confidence >= ?
                ORDER BY timestamp DESC
            ''', (threshold,))
            
            training_examples = []
            for row in cursor.fetchall():
                training_examples.append({
                    'text': row[0],
                    'label': row[1],
                    'confidence': row[2],
                    'timestamp': row[3],
                    'source': row[4]
                })
            
            export_data = {
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'total_examples': len(training_examples),
                    'confidence_threshold': threshold,
                    'version': '5.2'
                },
                'training_examples': training_examples
            }
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            return export_data
        finally:
            conn.close()

# ============================================================================
# Tests
# ============================================================================

def test_audio_text_record():
    """Test AudioTextRecord creation and serialization"""
    print("Testing AudioTextRecord...")
    
    record = AudioTextRecord.create("next slide", "next_slide", 0.95, "google")
    assert record.text == "next slide"
    assert record.command_matched == "next_slide"
    assert record.confidence == 0.95
    assert record.source == "google"
    
    record_dict = record.to_dict()
    assert record_dict['text'] == "next slide"
    
    record_json = record.to_json()
    assert "next slide" in record_json
    
    print("✅ AudioTextRecord tests passed")

def test_fallback_cache():
    """Test FallbackCache functionality"""
    print("\nTesting FallbackCache...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FallbackCache(Path(tmpdir))
        
        cache.set("test_key", "test text")
        text = cache.get("test_key")
        assert text == "test text"
        
        missing = cache.get("nonexistent")
        assert missing is None
        
        stats = cache.stats()
        assert stats['items'] == 1
        assert stats['size_kb'] >= 0
        
        print("✅ FallbackCache tests passed")

def test_local_training_data_logger():
    """Test LocalTrainingDataLogger functionality"""
    print("\nTesting LocalTrainingDataLogger...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = LocalTrainingDataLogger(Path(tmpdir))
        
        records = [
            AudioTextRecord.create("next slide", "next_slide", 0.95, "google"),
            AudioTextRecord.create("zoom in", "zoom_in", 0.88, "google"),
            AudioTextRecord.create("pen tool", "pen_tool", 0.92, "google"),
        ]
        
        for record in records:
            logger.log_text(record)
        
        stats = logger.get_statistics()
        assert stats['total_entries'] == 3
        assert stats['by_command']['next_slide'] == 1
        assert stats['by_command']['zoom_in'] == 1
        assert stats['by_source']['google'] == 3
        assert stats['confidence']['average'] > 0.85
        
        export_path = Path(tmpdir) / "export.json"
        export_data = logger.export_training_set(export_path, threshold=0.85)
        assert export_data['metadata']['total_examples'] == 3
        assert len(export_data['training_examples']) == 3
        
        assert export_path.exists()
        
        # Verify JSONL file
        jsonl_file = Path(tmpdir) / "training_data.jsonl"
        assert jsonl_file.exists()
        with open(jsonl_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3
        
        print("✅ LocalTrainingDataLogger tests passed")

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print(" 🧪 Running v5.2 Component Tests (Standalone)")
    print("="*60)
    
    try:
        test_audio_text_record()
        test_fallback_cache()
        test_local_training_data_logger()
        
        print("\n" + "="*60)
        print(" ✅ ALL TESTS PASSED!")
        print("="*60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
