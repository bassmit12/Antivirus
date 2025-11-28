"""Dashboard view showing system status and quick actions."""
from __future__ import annotations

import customtkinter as ctk
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from ..database import fetch_known_hashes
from ..quarantine import QuarantineManager

if TYPE_CHECKING:
    from .main_window import MainWindow


class Dashboard(ctk.CTkFrame):
    """Main dashboard view."""
    
    def __init__(self, parent, main_window: MainWindow):
        super().__init__(parent, fg_color="transparent")
        self.main_window = main_window
        
        # Configure grid
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Title with gradient effect
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 25))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(side="left")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="System Protection Overview",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60")
        )
        subtitle.pack(side="left", padx=(15, 0), pady=(8, 0))
        
        # Status cards
        self._create_status_cards()
        
        # Quick action buttons
        self._create_quick_actions()
        
        # Recent activity
        self._create_activity_panel()
        
    def _create_status_cards(self):
        """Create status information cards."""
        card_frame = ctk.CTkFrame(self)
        card_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        card_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Protection Status Card
        self.protection_card = self._create_card(
            card_frame,
            "🛡️ Protection Status",
            "Active",
            "#2ecc71",
            0
        )
        
        # Signatures Card
        sig_count = len(fetch_known_hashes())
        self.signatures_card = self._create_card(
            card_frame,
            "📝 Signature Database",
            f"{sig_count:,} signatures",
            "#3498db",
            1
        )
        
        # Quarantine Card
        qm = QuarantineManager()
        quarantine_count = len(qm.list_quarantined())
        self.quarantine_card = self._create_card(
            card_frame,
            "🗄️ Quarantined Files",
            f"{quarantine_count} files",
            "#e67e22",
            2
        )
        
    def _create_card(self, parent, title: str, value: str, color: str, column: int) -> ctk.CTkFrame:
        """Create a modern status card with shadow effect."""
        card = ctk.CTkFrame(
            parent, 
            fg_color=color, 
            corner_radius=15,
            border_width=0
        )
        card.grid(row=0, column=column, padx=12, pady=12, sticky="nsew")
        
        # Icon/Title section
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=20)
        
        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=13, weight="normal"),
            text_color=("white", "white"),
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        # Value section
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("white", "white"),
            anchor="w"
        )
        value_label.pack(anchor="w", pady=(0, 20), padx=20)
        
        # Add subtle hover effect
        card.bind("<Enter>", lambda e: card.configure(border_width=2, border_color="white"))
        card.bind("<Leave>", lambda e: card.configure(border_width=0))
        
        return card
        
    def _create_quick_actions(self):
        """Create enhanced quick action buttons."""
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=2, column=0, columnspan=3, sticky="new", pady=(15, 20))
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Define actions with colors
        actions = [
            ("⚡ Quick Scan", "Scan common locations", self._quick_scan, "#2ecc71", "#27ae60"),
            ("🔍 Full Scan", "Deep system scan", self._full_scan, "#3498db", "#2980b9"),
            ("📁 Custom Scan", "Choose files to scan", self._custom_scan, "#9b59b6", "#8e44ad"),
        ]
        
        for idx, (text, subtitle, command, color, hover) in enumerate(actions):
            btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=idx, padx=12, pady=0, sticky="ew")
            
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                font=ctk.CTkFont(size=16, weight="bold"),
                height=65,
                corner_radius=12,
                command=command,
                fg_color=color,
                hover_color=hover,
                border_width=0
            )
            btn.pack(fill="x")
            
            # Add subtitle
            subtitle_label = ctk.CTkLabel(
                btn_frame,
                text=subtitle,
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray60")
            )
            subtitle_label.pack(pady=(5, 0))
        
    def _create_activity_panel(self):
        """Create enhanced recent activity panel."""
        activity_frame = ctk.CTkFrame(self, corner_radius=15)
        activity_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(0, 0))
        activity_frame.grid_columnconfigure(0, weight=1)
        activity_frame.grid_rowconfigure(1, weight=1)
        
        # Header with icon
        header_frame = ctk.CTkFrame(activity_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        activity_title = ctk.CTkLabel(
            header_frame,
            text="📊 Recent Activity",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        activity_title.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            height=30,
            corner_radius=8,
            command=self._update_activity
        )
        refresh_btn.pack(side="right")
        
        # Activity list (scrollable) with better styling
        self.activity_text = ctk.CTkTextbox(
            activity_frame,
            height=250,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.activity_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Add some sample activity
        self._update_activity()
        
    def _update_activity(self):
        """Update activity log."""
        self.activity_text.delete("1.0", "end")
        
        # Get quarantine history
        qm = QuarantineManager()
        quarantined = qm.list_quarantined()
        
        if quarantined:
            self.activity_text.insert("end", "Recent Quarantined Files:\n\n", "header")
            
            for entry in quarantined[-10:]:  # Last 10 entries
                timestamp = datetime.fromisoformat(entry['quarantined_at']).strftime('%Y-%m-%d %H:%M')
                file_name = Path(entry['original_path']).name
                threat = entry['threat_name']
                
                self.activity_text.insert("end", f"[{timestamp}] ", "timestamp")
                self.activity_text.insert("end", f"{file_name}\n", "filename")
                self.activity_text.insert("end", f"  ⚠️ Threat: {threat}\n\n", "threat")
        else:
            self.activity_text.insert("end", "No recent threats detected.\nYour system is secure! ✅")
            
    def _quick_scan(self):
        """Start a quick scan."""
        self.main_window.show_view("Scan")
        # Trigger quick scan in scan view
        
    def _full_scan(self):
        """Start a full scan."""
        self.main_window.show_view("Scan")
        # Trigger full scan in scan view
        
    def _custom_scan(self):
        """Start a custom scan."""
        self.main_window.show_view("Scan")
        
    def on_show(self):
        """Called when view is shown."""
        # Refresh statistics
        sig_count = len(fetch_known_hashes())
        self.signatures_card.winfo_children()[1].configure(text=f"{sig_count:,} signatures")
        
        qm = QuarantineManager()
        quarantine_count = len(qm.list_quarantined())
        self.quarantine_card.winfo_children()[1].configure(text=f"{quarantine_count} files")
        
        # Refresh activity
        self._update_activity()
