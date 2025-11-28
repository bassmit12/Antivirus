"""Quarantine management for infected files."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet

from .config import QUARANTINE_DIR, config

QUARANTINE_INDEX = QUARANTINE_DIR / "index.json"


class QuarantineManager:
    """Manages quarantined files."""
    
    def __init__(self, quarantine_dir: Path = QUARANTINE_DIR):
        self.quarantine_dir = quarantine_dir
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        self.encrypt_enabled = config.get('quarantine.encrypt', True)
        self._key = self._get_or_create_key()
        self._cipher = Fernet(self._key) if self.encrypt_enabled else None
        
    def quarantine_file(
        self,
        file_path: Path,
        threat_name: str,
        detection_method: str,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Move a file to quarantine with encryption.
        
        Args:
            file_path: Path to the file to quarantine
            threat_name: Name of the detected threat
            detection_method: Method used to detect (signature/heuristic/behavior)
            metadata: Additional metadata about the detection
            
        Returns:
            True if successfully quarantined
        """
        if not file_path.exists():
            return False
            
        try:
            # Generate unique quarantine ID
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            quarantine_id = f"{timestamp}_{hash(str(file_path)) % 10**8}"
            quarantine_path = self.quarantine_dir / quarantine_id
            
            # Read and optionally encrypt the file
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            if self.encrypt_enabled and self._cipher:
                file_data = self._cipher.encrypt(file_data)
                
            # Write to quarantine
            with open(quarantine_path, 'wb') as f:
                f.write(file_data)
                
            # Store metadata
            entry = {
                'id': quarantine_id,
                'original_path': str(file_path.absolute()),
                'threat_name': threat_name,
                'detection_method': detection_method,
                'quarantined_at': datetime.now(timezone.utc).isoformat(),
                'file_size': file_path.stat().st_size,
                'encrypted': self.encrypt_enabled,
                'metadata': metadata or {},
            }
            
            self._add_to_index(entry)
            
            # Delete original file
            file_path.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error quarantining file {file_path}: {e}")
            return False
            
    def restore_file(self, quarantine_id: str, restore_path: Optional[Path] = None) -> bool:
        """
        Restore a quarantined file.
        
        Args:
            quarantine_id: ID of the quarantined file
            restore_path: Optional custom restore path
            
        Returns:
            True if successfully restored
        """
        entry = self._get_entry(quarantine_id)
        if not entry:
            return False
            
        quarantine_path = self.quarantine_dir / quarantine_id
        if not quarantine_path.exists():
            return False
            
        try:
            # Read and decrypt if needed
            with open(quarantine_path, 'rb') as f:
                file_data = f.read()
                
            if entry.get('encrypted') and self._cipher:
                file_data = self._cipher.decrypt(file_data)
                
            # Determine restore location
            target_path = restore_path or Path(entry['original_path'])
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write restored file
            with open(target_path, 'wb') as f:
                f.write(file_data)
                
            # Remove from quarantine
            quarantine_path.unlink()
            self._remove_from_index(quarantine_id)
            
            return True
            
        except Exception as e:
            print(f"Error restoring file {quarantine_id}: {e}")
            return False
            
    def delete_permanently(self, quarantine_id: str) -> bool:
        """
        Permanently delete a quarantined file.
        
        Args:
            quarantine_id: ID of the quarantined file
            
        Returns:
            True if successfully deleted
        """
        quarantine_path = self.quarantine_dir / quarantine_id
        
        try:
            if quarantine_path.exists():
                quarantine_path.unlink()
            self._remove_from_index(quarantine_id)
            return True
        except Exception as e:
            print(f"Error deleting quarantined file {quarantine_id}: {e}")
            return False
            
    def list_quarantined(self) -> list[dict]:
        """Get list of all quarantined files."""
        return self._load_index()
        
    def get_quarantine_size(self) -> int:
        """Get total size of quarantine in bytes."""
        total = 0
        for file in self.quarantine_dir.glob('*'):
            if file.is_file() and file.name != 'index.json':
                total += file.stat().st_size
        return total
        
    def cleanup_old(self, days: int = 30) -> int:
        """
        Delete quarantined files older than specified days.
        
        Args:
            days: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        deleted = 0
        current_time = datetime.now(timezone.utc)
        
        for entry in self.list_quarantined():
            quarantined_at = datetime.fromisoformat(entry['quarantined_at'])
            age_days = (current_time - quarantined_at).days
            
            if age_days > days:
                if self.delete_permanently(entry['id']):
                    deleted += 1
                    
        return deleted
        
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key."""
        key_file = self.quarantine_dir / ".key"
        
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            # Hide the key file on Windows
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(key_file), 2)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
            return key
            
    def _load_index(self) -> list[dict]:
        """Load quarantine index."""
        if not QUARANTINE_INDEX.exists():
            return []
            
        try:
            with open(QUARANTINE_INDEX, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
            
    def _save_index(self, index: list[dict]) -> None:
        """Save quarantine index."""
        try:
            with open(QUARANTINE_INDEX, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2)
        except IOError:
            pass
            
    def _add_to_index(self, entry: dict) -> None:
        """Add entry to index."""
        index = self._load_index()
        index.append(entry)
        self._save_index(index)
        
    def _remove_from_index(self, quarantine_id: str) -> None:
        """Remove entry from index."""
        index = self._load_index()
        index = [e for e in index if e['id'] != quarantine_id]
        self._save_index(index)
        
    def _get_entry(self, quarantine_id: str) -> Optional[dict]:
        """Get entry by ID."""
        index = self._load_index()
        for entry in index:
            if entry['id'] == quarantine_id:
                return entry
        return None
