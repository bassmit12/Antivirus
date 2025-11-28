"""Settings view for configuring the antivirus."""
from __future__ import annotations

import customtkinter as ctk
from typing import TYPE_CHECKING

from ..config import config

if TYPE_CHECKING:
    from .main_window import MainWindow


class SettingsView(ctk.CTkFrame):
    """Settings configuration view."""
    
    def __init__(self, parent, main_window: MainWindow):
        super().__init__(parent, fg_color="transparent")
        self.main_window = main_window
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Settings container (scrollable)
        self.settings_container = ctk.CTkScrollableFrame(self)
        self.settings_container.grid(row=1, column=0, sticky="nsew")
        self.settings_container.grid_columnconfigure(0, weight=1)
        
        # Create settings sections
        self._create_detection_settings()
        self._create_scanning_settings()
        self._create_appearance_settings()
        self._create_api_settings()
        
    def _create_section(self, title: str, row: int) -> ctk.CTkFrame:
        """Create a settings section."""
        section_frame = ctk.CTkFrame(self.settings_container)
        section_frame.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        section_frame.grid_columnconfigure(0, weight=1)
        
        section_title = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        return section_frame
        
    def _create_detection_settings(self):
        """Create detection settings section."""
        section = self._create_section("🔍 Detection Settings", 0)
        
        content_frame = ctk.CTkFrame(section, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Signature detection
        sig_label = ctk.CTkLabel(content_frame, text="Signature Detection:", anchor="w")
        sig_label.grid(row=0, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.sig_switch = ctk.CTkSwitch(
            content_frame,
            text="",
            command=self._toggle_signature
        )
        self.sig_switch.grid(row=0, column=1, sticky="e", pady=10)
        if config.get('detection.signature_enabled', True):
            self.sig_switch.select()
            
        # Heuristic detection
        heur_label = ctk.CTkLabel(content_frame, text="Heuristic Detection:", anchor="w")
        heur_label.grid(row=1, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.heur_switch = ctk.CTkSwitch(
            content_frame,
            text="",
            command=self._toggle_heuristic
        )
        self.heur_switch.grid(row=1, column=1, sticky="e", pady=10)
        if config.get('detection.heuristic_enabled', True):
            self.heur_switch.select()
            
        # Cloud lookup
        cloud_label = ctk.CTkLabel(content_frame, text="Cloud Lookup (VirusTotal):", anchor="w")
        cloud_label.grid(row=2, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.cloud_switch = ctk.CTkSwitch(
            content_frame,
            text="",
            command=self._toggle_cloud
        )
        self.cloud_switch.grid(row=2, column=1, sticky="e", pady=10)
        if config.get('detection.cloud_lookup_enabled', True):
            self.cloud_switch.select()
            
        # Sensitivity
        sens_label = ctk.CTkLabel(content_frame, text="Detection Sensitivity:", anchor="w")
        sens_label.grid(row=3, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.sensitivity_menu = ctk.CTkOptionMenu(
            content_frame,
            values=["low", "medium", "high", "paranoid"],
            command=self._change_sensitivity
        )
        self.sensitivity_menu.grid(row=3, column=1, sticky="e", pady=10)
        self.sensitivity_menu.set(config.get('detection.sensitivity', 'medium'))
        
    def _create_scanning_settings(self):
        """Create scanning settings section."""
        section = self._create_section("⚙️ Scanning Settings", 1)
        
        content_frame = ctk.CTkFrame(section, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Recursive scan
        recursive_label = ctk.CTkLabel(content_frame, text="Recursive Scanning:", anchor="w")
        recursive_label.grid(row=0, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.recursive_switch = ctk.CTkSwitch(content_frame, text="")
        self.recursive_switch.grid(row=0, column=1, sticky="e", pady=10)
        if config.get('scanning.default_recursive', True):
            self.recursive_switch.select()
            
        # Include hidden files
        hidden_label = ctk.CTkLabel(content_frame, text="Scan Hidden Files:", anchor="w")
        hidden_label.grid(row=1, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.hidden_switch = ctk.CTkSwitch(content_frame, text="")
        self.hidden_switch.grid(row=1, column=1, sticky="e", pady=10)
        if config.get('scanning.include_hidden', False):
            self.hidden_switch.select()
            
        # Thread count
        threads_label = ctk.CTkLabel(content_frame, text="Scan Threads:", anchor="w")
        threads_label.grid(row=2, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.threads_entry = ctk.CTkEntry(content_frame, width=100)
        self.threads_entry.grid(row=2, column=1, sticky="e", pady=10)
        self.threads_entry.insert(0, str(config.get('scanning.threads', 4)))
        
    def _create_appearance_settings(self):
        """Create appearance settings section."""
        section = self._create_section("🎨 Appearance", 2)
        
        content_frame = ctk.CTkFrame(section, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Theme
        theme_label = ctk.CTkLabel(content_frame, text="Theme:", anchor="w")
        theme_label.grid(row=0, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.theme_menu = ctk.CTkOptionMenu(
            content_frame,
            values=["System", "Dark", "Light"],
            command=self._change_theme
        )
        self.theme_menu.grid(row=0, column=1, sticky="e", pady=10)
        self.theme_menu.set("Dark")
        
    def _create_api_settings(self):
        """Create API settings section."""
        section = self._create_section("🔑 API Configuration", 3)
        
        content_frame = ctk.CTkFrame(section, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        content_frame.grid_columnconfigure(1, weight=1)
        
        # VirusTotal API Key
        vt_label = ctk.CTkLabel(content_frame, text="VirusTotal API Key:", anchor="w")
        vt_label.grid(row=0, column=0, sticky="w", pady=10, padx=(0, 20))
        
        api_key = config.vt_api_key or ""
        masked_key = f"{api_key[:8]}...{api_key[-8:]}" if len(api_key) > 16 else "Not configured"
        
        vt_value = ctk.CTkLabel(
            content_frame,
            text=masked_key,
            text_color="gray",
            anchor="e"
        )
        vt_value.grid(row=0, column=1, sticky="e", pady=10)
        
        # Info label
        info_label = ctk.CTkLabel(
            content_frame,
            text="ℹ️  API keys are configured via .env file",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        info_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 10))
        
    def _toggle_signature(self):
        """Toggle signature detection."""
        enabled = self.sig_switch.get() == 1
        config.set('detection.signature_enabled', enabled)
        config.save()
        
    def _toggle_heuristic(self):
        """Toggle heuristic detection."""
        enabled = self.heur_switch.get() == 1
        config.set('detection.heuristic_enabled', enabled)
        config.save()
        
    def _toggle_cloud(self):
        """Toggle cloud lookup."""
        enabled = self.cloud_switch.get() == 1
        config.set('detection.cloud_lookup_enabled', enabled)
        config.save()
        
    def _change_sensitivity(self, value: str):
        """Change detection sensitivity."""
        config.set('detection.sensitivity', value)
        config.save()
        
    def _change_theme(self, value: str):
        """Change appearance theme."""
        ctk.set_appearance_mode(value)
        
    def on_show(self):
        """Called when view is shown."""
        pass
