"""Enhanced directory scanner with multi-engine detection."""
from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Optional

from . import database
from .api_integration.malwarebazaar import MalwareBazaarClient
from .api_integration.virustotal import VirusTotalClient
from .behavior.sandbox import SandboxManager
from .config import config
from .heuristic.heuristic_engine import HeuristicEngine

logger = logging.getLogger(__name__)


@dataclass
class ScanFinding:
    """Enhanced scan finding with multi-engine detection results."""
    path: Path
    sha256: str
    file_size: int
    
    # Detection results
    signature_match: Optional[str] = None
    virustotal_result: Optional[dict] = None
    malwarebazaar_result: Optional[dict] = None
    heuristic_result: Optional[dict] = None
    sandbox_result: Optional[dict] = None
    
    # Threat assessment
    threat_level: str = "clean"  # clean, suspicious, malicious
    detection_methods: list[str] = field(default_factory=list)
    threat_names: list[str] = field(default_factory=list)
    
    @property
    def is_malicious(self) -> bool:
        """Check if file is detected as malicious by any method."""
        return self.threat_level in ["malicious", "suspicious"]
        
    @property
    def is_confirmed_malicious(self) -> bool:
        """Check if file is confirmed malicious (not just suspicious)."""
        return self.threat_level == "malicious"


class EnhancedScanner:
    """Enhanced scanner with multiple detection engines."""
    
    def __init__(self, db_path: Path = database.DB_PATH):
        self.db_path = db_path
        
        # Initialize detection engines
        self.vt_client = VirusTotalClient()
        self.mb_client = MalwareBazaarClient()
        self.heuristic_engine = HeuristicEngine()
        self.sandbox_manager = SandboxManager()
        
        # Configuration
        self.use_cloud = config.get('detection.cloud_lookup_enabled', True)
        self.use_heuristic = config.get('detection.heuristic_enabled', True)
        self.use_signature = config.get('detection.signature_enabled', True)
        self.use_sandbox = config.get('sandbox.enabled', False)
        
    def scan_file(self, file_path: Path) -> ScanFinding:
        """
        Scan a single file with all detection engines.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            ScanFinding with detection results
        """
        try:
            # Calculate hash
            file_hash = hash_file(file_path)
            file_size = file_path.stat().st_size
            
            finding = ScanFinding(
                path=file_path,
                sha256=file_hash,
                file_size=file_size,
            )
            
            # 1. Signature-based detection (local database)
            if self.use_signature:
                sig_match = database.lookup_signature(file_hash, db_path=self.db_path)
                if sig_match:
                    finding.signature_match = sig_match['name']
                    finding.detection_methods.append('signature')
                    finding.threat_names.append(sig_match['name'])
                    finding.threat_level = "malicious"
                    
            # 2. Cloud-based detection (VirusTotal)
            if self.use_cloud and self.vt_client.enabled:
                vt_result = self.vt_client.lookup_hash(file_hash)
                finding.virustotal_result = vt_result
                
                if vt_result and vt_result.get('found'):
                    malicious_count = vt_result.get('malicious', 0)
                    suspicious_count = vt_result.get('suspicious', 0)
                    
                    if malicious_count >= 3:  # At least 3 engines flagged it
                        finding.detection_methods.append('virustotal')
                        finding.threat_level = "malicious"
                        if vt_result.get('threat_names'):
                            finding.threat_names.extend(vt_result['threat_names'][:3])
                    elif malicious_count + suspicious_count >= 2:
                        if finding.threat_level == "clean":
                            finding.threat_level = "suspicious"
                        finding.detection_methods.append('virustotal')
                        
            # 3. MalwareBazaar lookup
            if self.use_cloud and self.mb_client.enabled:
                mb_result = self.mb_client.lookup_hash(file_hash)
                finding.malwarebazaar_result = mb_result
                
                if mb_result and mb_result.get('found'):
                    finding.detection_methods.append('malwarebazaar')
                    finding.threat_level = "malicious"
                    if mb_result.get('signature'):
                        finding.threat_names.append(mb_result['signature'])
                        
            # 4. Heuristic analysis
            if self.use_heuristic:
                heuristic_result = self.heuristic_engine.analyze_file(file_path)
                finding.heuristic_result = heuristic_result
                
                if heuristic_result.get('is_suspicious'):
                    finding.detection_methods.append('heuristic')
                    
                    # Heuristic only makes suspicious if not already confirmed malicious
                    if finding.threat_level == "clean":
                        if heuristic_result.get('threat_score', 0) >= 70:
                            finding.threat_level = "malicious"
                            finding.threat_names.append("Heuristic:Generic")
                        else:
                            finding.threat_level = "suspicious"
                            
            # 5. Sandbox analysis (if enabled and file looks suspicious)
            if self.use_sandbox and finding.threat_level != "clean":
                # Only sandbox files that are already flagged as suspicious/malicious
                # to save resources
                sandbox_result = self.sandbox_manager.analyze_file(file_path)
                
                finding.sandbox_result = {
                    'executed': sandbox_result.executed,
                    'suspicious_behaviors': sandbox_result.suspicious_behaviors,
                    'threat_score': sandbox_result.threat_score,
                    'is_malicious': sandbox_result.is_malicious,
                    'network_activity': len(sandbox_result.network_activity),
                    'file_operations': len(sandbox_result.file_operations),
                    'error': sandbox_result.error,
                }
                
                if sandbox_result.is_malicious:
                    finding.detection_methods.append('sandbox')
                    finding.threat_level = "malicious"
                    finding.threat_names.append("Sandbox:Behavioral")
                    
            return finding
            
        except OSError as e:
            logger.error(f"Error scanning {file_path}: {e}")
            return ScanFinding(
                path=file_path,
                sha256=f"error:{e}",
                file_size=0,
                threat_level="clean",
            )
            
    def scan_path(
        self,
        target: Path,
        recursive: bool = True,
        include_hidden: bool = False,
        progress_callback: Optional[callable] = None,
    ) -> list[ScanFinding]:
        """
        Scan a file or directory.
        
        Args:
            target: Path to scan
            recursive: Recurse into subdirectories
            include_hidden: Include hidden files
            progress_callback: Optional callback(current, total, file_path)
            
        Returns:
            List of scan findings
        """
        normalized = target.expanduser().resolve()
        if not normalized.exists():
            raise FileNotFoundError(f"Path not found: {normalized}")
            
        files_to_scan = list(_iter_files(normalized, recursive=recursive, include_hidden=include_hidden))
        findings: list[ScanFinding] = []
        
        total_files = len(files_to_scan)
        
        for idx, file_path in enumerate(files_to_scan, 1):
            if progress_callback:
                progress_callback(idx, total_files, file_path)
                
            finding = self.scan_file(file_path)
            findings.append(finding)
            
            # Log detections
            if finding.is_malicious:
                logger.warning(
                    f"Threat detected: {file_path} "
                    f"[{', '.join(finding.detection_methods)}] "
                    f"- {', '.join(finding.threat_names[:2])}"
                )
                
        return findings


def hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the lowercase SHA-256 hash of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_files(
    target: Path,
    recursive: bool,
    include_hidden: bool,
) -> Iterator[Path]:
    """Iterate over files in target path."""
    if target.is_file():
        yield target
        return

    iterator: Iterable[Path]
    if recursive:
        iterator = target.rglob("*")
    else:
        iterator = target.glob("*")

    for candidate in iterator:
        if candidate.is_dir():
            continue
        if not include_hidden and _is_hidden(candidate):
            continue
        yield candidate


def _is_hidden(path: Path) -> bool:
    """Check if a file is hidden."""
    name = path.name
    if name.startswith('.'):
        return True
    try:
        attrs = os.stat(path, follow_symlinks=False).st_file_attributes
    except AttributeError:
        return False
    # FILE_ATTRIBUTE_HIDDEN = 0x2
    return bool(attrs & 0x2)


# Legacy function for backward compatibility
def scan_path(
    target: Path,
    db_path: Path = database.DB_PATH,
    recursive: bool = True,
    include_hidden: bool = False,
) -> list:
    """Legacy scan function for backward compatibility."""
    scanner = EnhancedScanner(db_path=db_path)
    return scanner.scan_path(target, recursive=recursive, include_hidden=include_hidden)
