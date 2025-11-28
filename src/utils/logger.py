"""Logging configuration for the antivirus application."""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ..config import LOGS_DIR, config


def setup_logging() -> None:
    """Configure logging for the application."""
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get configuration
    log_level = config.get('logging.level', 'INFO')
    log_file = LOGS_DIR / "antivirus.log"
    max_bytes = config.get('logging.max_size_mb', 50) * 1024 * 1024
    backup_count = config.get('logging.backup_count', 5)
    console_output = config.get('logging.console_output', True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(logging.WARNING)  # Only warnings and above to console
        root_logger.addHandler(console_handler)
        
    # Log startup
    logging.info("=" * 60)
    logging.info(f"{config.get('app.name', 'Antivirus')} v{config.get('app.version', '2.0.0')} starting")
    logging.info("=" * 60)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
