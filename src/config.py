"""Configuration management for the antivirus application."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ROOT_PATH = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_PATH / "config.yaml"
DB_PATH = ROOT_PATH / "signature_antivirus.db"
LOGS_DIR = ROOT_PATH / "logs"
QUARANTINE_DIR = ROOT_PATH / "data" / "quarantine"
ML_MODELS_DIR = ROOT_PATH / "data" / "ml_models"


class Config:
    """Application configuration manager."""
    
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self._config: dict[str, Any] = {}
        self.load()
        
    def load(self) -> None:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = self._get_defaults()
            
    def save(self) -> None:
        """Save configuration to YAML file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False)
            
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        Example: config.get('scanning.threads', 4)
        """
        keys = key_path.split('.')
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value
        
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        Example: config.set('scanning.threads', 8)
        """
        keys = key_path.split('.')
        config = self._config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        
    @staticmethod
    def _get_defaults() -> dict[str, Any]:
        """Get default configuration."""
        return {
            'app': {
                'name': 'SecureGuard Antivirus',
                'version': '2.0.0',
            },
            'scanning': {
                'default_recursive': True,
                'include_hidden': False,
                'max_file_size_mb': 500,
                'threads': 4,
            },
            'detection': {
                'signature_enabled': True,
                'heuristic_enabled': True,
                'behavior_enabled': False,
                'cloud_lookup_enabled': True,
                'sensitivity': 'medium',
            },
        }
        
    @property
    def vt_api_key(self) -> str | None:
        """Get VirusTotal API key from environment."""
        return os.getenv('VT_API_KEY')
        
    @property
    def malwarebazaar_api_key(self) -> str | None:
        """Get MalwareBazaar API key from environment."""
        return os.getenv('MALWAREBAZAAR_API_KEY')


# Global configuration instance
config = Config()


def ensure_directories() -> None:
    """Ensure required directories exist."""
    directories = [
        LOGS_DIR,
        QUARANTINE_DIR,
        ML_MODELS_DIR,
        ROOT_PATH / "data" / "seeds",
        ROOT_PATH / "data" / "heuristic_rules",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Ensure directories on module import
ensure_directories()
