"""Quarantine view for managing quarantined files."""
from __future__ import annotations

import customtkinter as ctk
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from tkinter import messagebox

from ..quarantine import QuarantineManager

if TYPE_CHECKING:
    from .main_window import MainWindow


class QuarantineView(ctk.CTkFrame):
    """Quarantine management view."""
    
    def __init__(self, parent, main_window: MainWindow):
        super().__init__(parent, fg_color="transparent")
        self.main_window = main_window
        self.qm = QuarantineManager()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="Quarantine Manager",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Stats frame
        self._create_stats_frame()
        
        # Quarantine list
        self._create_quarantine_list()
        
        # Action buttons
        self._create_action_buttons()
        
    def _create_stats_frame(self):
        """Create statistics frame."""
        stats_frame = ctk.CTkFrame(self)
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total files
        files_count = len(self.qm.list_quarantined())
        files_card = self._create_stat_card(stats_frame, "📦 Total Files", str(files_count), 0)
        
        # Total size
        total_size = self.qm.get_quarantine_size()
        size_mb = total_size / (1024 * 1024)
        size_card = self._create_stat_card(stats_frame, "💾 Total Size", f"{size_mb:.2f} MB", 1)
        
        # Storage location
        location_card = self._create_stat_card(stats_frame, "📁 Location", "data/quarantine", 2)
        
    def _create_stat_card(self, parent, title: str, value: str, column: int):
        """Create a statistics card."""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="ew")
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
        )
        title_label.pack(pady=(10, 5), padx=10)
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        value_label.pack(pady=(0, 10), padx=10)
        
        return card
        
    def _create_quarantine_list(self):
        """Create quarantine files list."""
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        list_title = ctk.CTkLabel(
            list_frame,
            text="🗄️ Quarantined Files",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        list_title.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Scrollable frame for files
        self.files_textbox = ctk.CTkTextbox(list_frame, corner_radius=10)
        self.files_textbox.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        self._refresh_list()
        
    def _create_action_buttons(self):
        """Create action buttons."""
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="ew")
        
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh",
            height=40,
            command=self._refresh_list
        )
        refresh_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        cleanup_btn = ctk.CTkButton(
            actions_frame,
            text="🧹 Cleanup Old Files",
            height=40,
            command=self._cleanup_old,
            fg_color="#e67e22",
            hover_color="#d35400"
        )
        cleanup_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        delete_all_btn = ctk.CTkButton(
            actions_frame,
            text="❌ Delete All",
            height=40,
            command=self._delete_all,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        delete_all_btn.pack(side="left", fill="x", expand=True)
        
    def _refresh_list(self):
        """Refresh the quarantine list."""
        self.files_textbox.delete("1.0", "end")
        
        quarantined = self.qm.list_quarantined()
        
        if not quarantined:
            self.files_textbox.insert("end", "No files in quarantine.\n\n")
            self.files_textbox.insert("end", "✅ Your system is clean!")
            return
            
        for entry in quarantined:
            timestamp = datetime.fromisoformat(entry['quarantined_at']).strftime('%Y-%m-%d %H:%M:%S')
            file_path = Path(entry['original_path'])
            file_name = file_path.name
            threat = entry['threat_name']
            method = entry['detection_method']
            size_kb = entry['file_size'] / 1024
            
            self.files_textbox.insert("end", f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            self.files_textbox.insert("end", f"📄 {file_name}\n", "filename")
            self.files_textbox.insert("end", f"   Path: {entry['original_path']}\n")
            self.files_textbox.insert("end", f"   ⚠️  Threat: {threat}\n")
            self.files_textbox.insert("end", f"   Detection: {method}\n")
            self.files_textbox.insert("end", f"   Size: {size_kb:.2f} KB\n")
            self.files_textbox.insert("end", f"   Quarantined: {timestamp}\n")
            self.files_textbox.insert("end", f"   ID: {entry['id']}\n")
            self.files_textbox.insert("end", "\n")
            
    def _cleanup_old(self):
        """Cleanup old quarantined files."""
        days = 30
        
        result = messagebox.askyesno(
            "Cleanup Confirmation",
            f"Delete quarantined files older than {days} days?",
            parent=self
        )
        
        if result:
            deleted = self.qm.cleanup_old(days=days)
            messagebox.showinfo(
                "Cleanup Complete",
                f"Deleted {deleted} old file(s) from quarantine.",
                parent=self
            )
            self._refresh_list()
            self.on_show()  # Refresh stats
            
    def _delete_all(self):
        """Delete all quarantined files."""
        quarantined = self.qm.list_quarantined()
        
        if not quarantined:
            messagebox.showinfo("Quarantine Empty", "No files to delete.", parent=self)
            return
            
        result = messagebox.askyesno(
            "Delete All Confirmation",
            f"Permanently delete all {len(quarantined)} quarantined file(s)?",
            parent=self
        )
        
        if result:
            deleted = 0
            for entry in quarantined:
                if self.qm.delete_permanently(entry['id']):
                    deleted += 1
                    
            messagebox.showinfo(
                "Delete Complete",
                f"Deleted {deleted} file(s) from quarantine.",
                parent=self
            )
            self._refresh_list()
            self.on_show()  # Refresh stats
            
    def on_show(self):
        """Called when view is shown."""
        # Refresh stats
        files_count = len(self.qm.list_quarantined())
        total_size = self.qm.get_quarantine_size()
        size_mb = total_size / (1024 * 1024)
        
        # Update stats (recreate stats frame)
        for widget in self.grid_slaves(row=1):
            widget.destroy()
        self._create_stats_frame()
        
        # Refresh list
        self._refresh_list()
