"""Scan view for initiating and monitoring scans."""
from __future__ import annotations

import customtkinter as ctk
import threading
from pathlib import Path
from tkinter import filedialog
from typing import TYPE_CHECKING, Optional

from ..scanner_enhanced import EnhancedScanner
from ..quarantine import QuarantineManager
from ..config import config

if TYPE_CHECKING:
    from .main_window import MainWindow


class ScanView(ctk.CTkFrame):
    """Scan interface view."""
    
    def __init__(self, parent, main_window: MainWindow):
        super().__init__(parent, fg_color="transparent")
        self.main_window = main_window
        self.scanning = False
        self.scan_thread: Optional[threading.Thread] = None
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        # Title with icon
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", pady=(0, 25))
        
        title = ctk.CTkLabel(
            title_frame,
            text="🔍 File Scanner",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(side="left")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Multi-Engine Threat Detection",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60")
        )
        subtitle.pack(side="left", padx=(15, 0), pady=(8, 0))
        
        # Scan options
        self._create_scan_options()
        
        # Scan controls
        self._create_scan_controls()
        
        # Progress area
        self._create_progress_area()
        
        # Results area
        self._create_results_area()
        
    def _create_scan_options(self):
        """Create enhanced scan options panel."""
        options_frame = ctk.CTkFrame(self, corner_radius=15)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Path selection with modern styling
        path_label = ctk.CTkLabel(
            options_frame, 
            text="📂 Scan Target:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        path_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.path_entry = ctk.CTkEntry(
            options_frame, 
            placeholder_text="Select a file or folder to scan",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        self.path_entry.grid(row=0, column=1, padx=(0, 10), pady=20, sticky="ew")
        
        browse_btn = ctk.CTkButton(
            options_frame,
            text="Browse",
            width=100,
            height=40,
            corner_radius=10,
            command=self._browse_path
        )
        browse_btn.grid(row=0, column=2, padx=20, pady=20)
        
        # Quick scan shortcuts with icons
        shortcuts_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        shortcuts_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20))
        
        quick_label = ctk.CTkLabel(
            shortcuts_frame, 
            text="Quick Scan Locations:",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        quick_label.pack(side="left", padx=(0, 15))
        
        shortcuts = [
            ("📥 Downloads", Path.home() / "Downloads"),
            ("🖥️ Desktop", Path.home() / "Desktop"),
            ("📄 Documents", Path.home() / "Documents"),
        ]
        
        for text, path in shortcuts:
            btn = ctk.CTkButton(
                shortcuts_frame,
                text=text,
                width=130,
                height=35,
                corner_radius=8,
                fg_color=("gray85", "gray20"),
                hover_color=("gray75", "gray30"),
                command=lambda p=path: self._set_path(p)
            )
            btn.pack(side="left", padx=5)
        
    def _create_scan_controls(self):
        """Create enhanced scan control buttons."""
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        controls_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.scan_btn = ctk.CTkButton(
            controls_frame,
            text="▶️  Start Scan",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            corner_radius=12,
            command=self._start_scan,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.scan_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text="⏸️  Stop Scan",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            corner_radius=12,
            command=self._stop_scan,
            state="disabled",
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.stop_btn.grid(row=0, column=1, sticky="ew")
        
    def _create_progress_area(self):
        """Create enhanced progress display area."""
        progress_frame = ctk.CTkFrame(self, corner_radius=15)
        progress_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Status label with icon
        status_container = ctk.CTkFrame(progress_frame, fg_color="transparent")
        status_container.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.status_label = ctk.CTkLabel(
            status_container,
            text="⏱️  Ready to scan",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.status_label.pack(side="left")
        
        # Progress bar with better styling
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=20,
            corner_radius=10
        )
        self.progress_bar.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        
        # Progress details
        self.progress_detail = ctk.CTkLabel(
            progress_frame,
            text="0 / 0 files scanned",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60")
        )
        self.progress_detail.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
        
    def _create_results_area(self):
        """Create enhanced results display area."""
        results_frame = ctk.CTkFrame(self, corner_radius=15)
        results_frame.grid(row=4, column=0, sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        results_title = ctk.CTkLabel(
            header_frame,
            text="📋 Scan Results",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        results_title.pack(side="left")
        
        # Results textbox with better font
        self.results_text = ctk.CTkTextbox(
            results_frame,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.results_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
    def _browse_path(self):
        """Open file/folder browser."""
        path = filedialog.askdirectory(title="Select folder to scan")
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)
            
    def _set_path(self, path: Path):
        """Set scan path."""
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, str(path))
        
    def _start_scan(self):
        """Start scanning."""
        scan_path = self.path_entry.get().strip()
        
        if not scan_path:
            self.status_label.configure(text="❌ Please select a path to scan")
            return
            
        path = Path(scan_path)
        if not path.exists():
            self.status_label.configure(text="❌ Path does not exist")
            return
            
        # Disable controls
        self.scanning = True
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # Clear previous results
        self.results_text.delete("1.0", "end")
        
        # Start scan in background thread
        self.scan_thread = threading.Thread(target=self._run_scan, args=(path,), daemon=True)
        self.scan_thread.start()
        
    def _run_scan(self, path: Path):
        """Run scan in background thread."""
        try:
            scanner = EnhancedScanner()
            
            # Progress callback
            def progress_callback(current, total, file_path):
                if not self.scanning:
                    return
                    
                # Update UI (must use after to run in main thread)
                self.after(0, self._update_progress, current, total, file_path)
                
            # Run scan
            findings = scanner.scan_path(
                path,
                recursive=True,
                include_hidden=False,
                progress_callback=progress_callback
            )
            
            # Process results
            self.after(0, self._display_results, findings)
            
        except Exception as e:
            self.after(0, self._scan_error, str(e))
        finally:
            self.after(0, self._scan_complete)
            
    def _update_progress(self, current: int, total: int, file_path: Path):
        """Update progress display."""
        progress = current / total if total > 0 else 0
        self.progress_bar.set(progress)
        self.progress_detail.configure(text=f"{current} / {total} files scanned")
        self.status_label.configure(text=f"Scanning: {file_path.name}")
        
    def _display_results(self, findings):
        """Display scan results."""
        self.results_text.delete("1.0", "end")
        
        # Summary
        total = len(findings)
        malicious = sum(1 for f in findings if f.is_confirmed_malicious)
        suspicious = sum(1 for f in findings if f.threat_level == "suspicious")
        clean = total - malicious - suspicious
        
        self.results_text.insert("end", "=== SCAN SUMMARY ===\n\n", "header")
        self.results_text.insert("end", f"Total files scanned: {total}\n")
        self.results_text.insert("end", f"✅ Clean: {clean}\n", "clean")
        self.results_text.insert("end", f"⚠️  Suspicious: {suspicious}\n", "suspicious")
        self.results_text.insert("end", f"❌ Malicious: {malicious}\n\n", "malicious")
        
        # Detailed results for threats
        if malicious > 0 or suspicious > 0:
            self.results_text.insert("end", "\n=== DETECTED THREATS ===\n\n", "header")
            
            for finding in findings:
                if finding.is_malicious:
                    self.results_text.insert("end", f"\n📁 {finding.path}\n", "filename")
                    self.results_text.insert("end", f"   Hash: {finding.sha256[:16]}...\n")
                    self.results_text.insert("end", f"   Threat Level: {finding.threat_level.upper()}\n")
                    self.results_text.insert("end", f"   Detection: {', '.join(finding.detection_methods)}\n")
                    
                    if finding.threat_names:
                        self.results_text.insert("end", f"   Threat Names: {', '.join(finding.threat_names[:2])}\n")
                        
        else:
            self.results_text.insert("end", "\n✅ No threats detected! Your system is clean.\n", "success")
            
    def _scan_error(self, error: str):
        """Display scan error."""
        self.status_label.configure(text=f"❌ Scan error: {error}")
        self.results_text.insert("end", f"\n❌ Error: {error}\n")
        
    def _scan_complete(self):
        """Handle scan completion."""
        self.scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="✅ Scan complete")
        
    def _stop_scan(self):
        """Stop ongoing scan."""
        self.scanning = False
        self.status_label.configure(text="⏸️ Scan stopped")
        
    def on_show(self):
        """Called when view is shown."""
        pass
