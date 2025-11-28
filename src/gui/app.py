"""Main GUI application entry point."""
from __future__ import annotations

import customtkinter as ctk
import sys
from pathlib import Path

from .main_window import MainWindow
from ..utils.logger import setup_logging


def main():
    """Launch the GUI application."""
    # Setup logging
    setup_logging()
    
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
    
    # Create and run application
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
