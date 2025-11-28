"""Main application window."""
from __future__ import annotations

import customtkinter as ctk
from typing import Optional

from .dashboard import Dashboard
from .scan_view import ScanView
from .threats_view import ThreatsView
from .quarantine_view import QuarantineView
from .settings_view import SettingsView
from ..config import config


class MainWindow(ctk.CTk):
    """Main application window with navigation."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(f"{config.get('app.name', 'SecureGuard Antivirus')} v{config.get('app.version', '2.0.0')}")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create navigation frame with gradient-like appearance
        self.nav_frame = ctk.CTkFrame(
            self, 
            width=240, 
            corner_radius=0,
            fg_color=("#f0f0f0", "#1a1a1a")
        )
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(7, weight=1)
        
        # Logo/Title with better styling
        self.logo_frame = ctk.CTkFrame(
            self.nav_frame,
            fg_color="transparent"
        )
        self.logo_frame.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="ew")
        
        self.logo_label = ctk.CTkLabel(
            self.logo_frame,
            text="🛡️",
            font=ctk.CTkFont(size=48)
        )
        self.logo_label.pack()
        
        self.app_name = ctk.CTkLabel(
            self.logo_frame,
            text="SecureGuard",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.app_name.pack()
        
        self.app_tagline = ctk.CTkLabel(
            self.logo_frame,
            text="Multi-Engine Protection",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        )
        self.app_tagline.pack(pady=(5, 0))
        
        # Divider line
        divider = ctk.CTkFrame(
            self.nav_frame,
            height=2,
            fg_color=("gray80", "gray25")
        )
        divider.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 20))
        
        # Navigation buttons with modern styling
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "🏠", 2, "Your system overview"),
            ("Scan", "🔍", 3, "Scan files & folders"),
            ("Threats", "⚠️", 4, "Detected threats"),
            ("Quarantine", "🗄️", 5, "Isolated files"),
            ("Settings", "⚙️", 6, "Configure protection"),
        ]
        
        for name, icon, row, tooltip in nav_items:
            btn_frame = ctk.CTkFrame(
                self.nav_frame,
                fg_color="transparent"
            )
            btn_frame.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
            
            btn = ctk.CTkButton(
                btn_frame,
                text=f"{icon}  {name}",
                width=210,
                height=45,
                corner_radius=10,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("#e0e0e0", "#2a2a2a"),
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda n=name: self.show_view(n)
            )
            btn.pack(side="left", fill="x", expand=True)
            self.nav_buttons[name] = btn
            
        # Footer in navigation
        footer_frame = ctk.CTkFrame(
            self.nav_frame,
            fg_color="transparent"
        )
        footer_frame.grid(row=8, column=0, padx=20, pady=20, sticky="s")
        
        version_label = ctk.CTkLabel(
            footer_frame,
            text=f"Version {config.get('app.version', '2.0.0')}",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        )
        version_label.pack()
        
        # Main content frame with shadow effect
        self.content_frame = ctk.CTkFrame(
            self, 
            corner_radius=0,
            fg_color=("#ffffff", "#1a1a1a")
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize views
        self.views: dict[str, ctk.CTkFrame] = {}
        self.current_view: Optional[str] = None
        
        # Create all views
        self._create_views()
        
        # Show dashboard by default
        self.show_view("Dashboard")
        
    def _create_views(self):
        """Create all view instances."""
        self.views["Dashboard"] = Dashboard(self.content_frame, self)
        self.views["Scan"] = ScanView(self.content_frame, self)
        self.views["Threats"] = ThreatsView(self.content_frame, self)
        self.views["Quarantine"] = QuarantineView(self.content_frame, self)
        self.views["Settings"] = SettingsView(self.content_frame, self)
        
    def show_view(self, view_name: str):
        """Switch to a different view with smooth transition."""
        # Hide current view
        if self.current_view and self.current_view in self.views:
            self.views[self.current_view].grid_forget()
            # Reset button style
            self.nav_buttons[self.current_view].configure(
                fg_color="transparent",
                text_color=("gray10", "gray90")
            )
            
        # Show new view
        if view_name in self.views:
            self.views[view_name].grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
            self.current_view = view_name
            
            # Highlight active button with accent color
            self.nav_buttons[view_name].configure(
                fg_color=("#2b7de9", "#1f538d"),
                text_color=("white", "white")
            )
            
            # Refresh view if it has a refresh method
            if hasattr(self.views[view_name], 'on_show'):
                self.views[view_name].on_show()
