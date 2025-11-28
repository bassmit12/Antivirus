"""Threats view for managing detected threats."""
from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main_window import MainWindow


class ThreatsView(ctk.CTkFrame):
    """Threats management view."""
    
    def __init__(self, parent, main_window: MainWindow):
        super().__init__(parent, fg_color="transparent")
        self.main_window = main_window
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="Threat History",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Info frame
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=1, column=0, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(0, weight=1)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="🛡️ Threat History\n\nThis view will display all detected threats\nand their detection history.\n\nRun a scan to detect threats!",
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        info_label.grid(row=0, column=0, padx=20, pady=20)
        
    def on_show(self):
        """Called when view is shown."""
        pass
