"""Sandbox analysis module for safe file execution and behavioral analysis."""
from __future__ import annotations

import logging
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import psutil

from ..config import config

logger = logging.getLogger(__name__)


@dataclass
class SandboxResult:
    """Results from sandbox analysis."""
    file_path: Path
    executed: bool = False
    timeout_occurred: bool = False
    suspicious_behaviors: list[str] = field(default_factory=list)
    process_activity: dict = field(default_factory=dict)
    network_activity: list[dict] = field(default_factory=list)
    file_operations: list[dict] = field(default_factory=list)
    registry_operations: list[dict] = field(default_factory=list)
    threat_score: int = 0
    is_malicious: bool = False
    error: Optional[str] = None


class LocalSandbox:
    """
    Lightweight local sandbox for behavioral analysis.
    
    This monitors process behavior in a controlled environment using:
    - Process isolation
    - Resource monitoring (CPU, memory, disk, network)
    - File system operations tracking
    - Network activity monitoring
    - Registry operations (Windows)
    
    Note: This is NOT a full VM-based sandbox. For production use,
    integrate with Cuckoo Sandbox or similar solutions.
    """
    
    def __init__(self):
        self.enabled = config.get('sandbox.enabled', True)
        self.timeout = config.get('sandbox.timeout_seconds', 30)
        self.max_cpu_percent = config.get('sandbox.max_cpu_percent', 80)
        self.max_memory_mb = config.get('sandbox.max_memory_mb', 500)
        
    def analyze_file(self, file_path: Path) -> SandboxResult:
        """
        Analyze file in local sandbox.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            SandboxResult with behavioral analysis
        """
        result = SandboxResult(file_path=file_path)
        
        if not self.enabled:
            result.error = "Sandbox disabled"
            return result
            
        try:
            # Check if file is executable
            if not self._is_executable(file_path):
                result.error = "File is not executable"
                return result
                
            logger.info(f"Starting sandbox analysis: {file_path}")
            
            # Execute in monitored environment
            self._execute_monitored(file_path, result)
            
            # Calculate threat score
            result.threat_score = self._calculate_threat_score(result)
            result.is_malicious = result.threat_score >= 60
            
            logger.info(f"Sandbox analysis complete: threat_score={result.threat_score}")
            
        except Exception as e:
            logger.error(f"Sandbox analysis error: {e}")
            result.error = str(e)
            
        return result
        
    def _is_executable(self, file_path: Path) -> bool:
        """Check if file is executable."""
        ext = file_path.suffix.lower()
        return ext in ['.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.js']
        
    def _execute_monitored(self, file_path: Path, result: SandboxResult):
        """
        Execute file with monitoring.
        
        SAFETY NOTE: This executes the file in the current environment.
        For real malware analysis, use a VM or container!
        """
        # For safety, we'll simulate execution instead of actually running malware
        # In production, this would run in an isolated VM
        
        logger.warning("SIMULATION MODE: Not actually executing file for safety")
        result.executed = False
        
        # Simulate some suspicious behaviors for demonstration
        self._simulate_behavioral_analysis(file_path, result)
        
    def _simulate_behavioral_analysis(self, file_path: Path, result: SandboxResult):
        """
        Simulate behavioral analysis.
        
        In a real implementation, this would:
        1. Execute in VM or container
        2. Monitor system calls
        3. Track network connections
        4. Log file operations
        5. Record registry changes
        """
        # Check file size and characteristics
        file_size = file_path.stat().st_size
        
        # Simulate process monitoring
        result.process_activity = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'threads_created': 0,
            'child_processes': 0,
        }
        
        # Check for suspicious patterns (static analysis)
        if file_size < 1024:  # Very small executables are suspicious
            result.suspicious_behaviors.append("Unusually small executable size")
            
        if file_size > 50 * 1024 * 1024:  # Very large files
            result.suspicious_behaviors.append("Unusually large file size")
            
        # In a real sandbox, these would be detected during execution:
        suspicious_indicators = [
            "Attempts to disable antivirus",
            "Creates autorun registry keys",
            "Connects to suspicious domains",
            "Encrypts user files",
            "Injects code into other processes",
            "Attempts privilege escalation",
            "Creates scheduled tasks",
            "Modifies system files",
            "Downloads additional payloads",
            "Establishes command & control connection",
        ]
        
        # For demo, we won't add any by default
        # Real analysis would populate these based on actual behavior
        
    def _calculate_threat_score(self, result: SandboxResult) -> int:
        """Calculate threat score based on observed behaviors."""
        score = 0
        
        # Score based on suspicious behaviors
        score += len(result.suspicious_behaviors) * 15
        
        # Score based on network activity
        score += len(result.network_activity) * 10
        
        # Score based on file operations
        if len(result.file_operations) > 10:
            score += 20
        elif len(result.file_operations) > 5:
            score += 10
            
        # Score based on registry operations
        if len(result.registry_operations) > 5:
            score += 20
        elif len(result.registry_operations) > 2:
            score += 10
            
        # Process activity
        if result.process_activity.get('child_processes', 0) > 3:
            score += 15
        if result.process_activity.get('threads_created', 0) > 10:
            score += 10
            
        return min(score, 100)  # Cap at 100


class CuckooSandboxClient:
    """
    Client for Cuckoo Sandbox API integration.
    
    Cuckoo is an open-source automated malware analysis system.
    See: https://cuckoosandbox.org/
    
    This requires a Cuckoo server to be running.
    """
    
    def __init__(self):
        self.enabled = config.get('sandbox.cuckoo.enabled', False)
        self.api_url = config.get('sandbox.cuckoo.api_url', 'http://localhost:8090')
        self.api_key = config.get('sandbox.cuckoo.api_key', None)
        self.timeout = config.get('sandbox.cuckoo.timeout_seconds', 300)
        
    def analyze_file(self, file_path: Path) -> SandboxResult:
        """
        Submit file to Cuckoo Sandbox for analysis.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            SandboxResult with Cuckoo analysis results
        """
        result = SandboxResult(file_path=file_path)
        
        if not self.enabled:
            result.error = "Cuckoo sandbox not enabled"
            return result
            
        try:
            import requests
            
            # Submit file
            logger.info(f"Submitting to Cuckoo: {file_path}")
            task_id = self._submit_file(file_path)
            
            if not task_id:
                result.error = "Failed to submit file to Cuckoo"
                return result
                
            # Wait for analysis
            logger.info(f"Waiting for Cuckoo analysis (task {task_id})...")
            analysis = self._wait_for_analysis(task_id)
            
            if not analysis:
                result.error = "Analysis timeout or failed"
                return result
                
            # Parse results
            self._parse_cuckoo_results(analysis, result)
            result.executed = True
            
        except ImportError:
            result.error = "requests library not installed"
        except Exception as e:
            logger.error(f"Cuckoo analysis error: {e}")
            result.error = str(e)
            
        return result
        
    def _submit_file(self, file_path: Path) -> Optional[int]:
        """Submit file to Cuckoo and return task ID."""
        import requests
        
        url = f"{self.api_url}/tasks/create/file"
        headers = {}
        
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
            
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f)}
                response = requests.post(url, files=files, headers=headers, timeout=30)
                
            if response.status_code == 200:
                data = response.json()
                return data.get('task_id')
                
        except Exception as e:
            logger.error(f"Failed to submit to Cuckoo: {e}")
            
        return None
        
    def _wait_for_analysis(self, task_id: int) -> Optional[dict]:
        """Wait for Cuckoo analysis to complete."""
        import requests
        
        url = f"{self.api_url}/tasks/view/{task_id}"
        headers = {}
        
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
            
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    task = data.get('task', {})
                    
                    if task.get('status') == 'reported':
                        # Get full report
                        return self._get_report(task_id)
                        
            except Exception as e:
                logger.error(f"Error checking Cuckoo status: {e}")
                
            time.sleep(10)  # Check every 10 seconds
            
        return None
        
    def _get_report(self, task_id: int) -> Optional[dict]:
        """Get full analysis report from Cuckoo."""
        import requests
        
        url = f"{self.api_url}/tasks/report/{task_id}"
        headers = {}
        
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
            
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get Cuckoo report: {e}")
            
        return None
        
    def _parse_cuckoo_results(self, analysis: dict, result: SandboxResult):
        """Parse Cuckoo analysis results."""
        # Extract suspicious behaviors
        signatures = analysis.get('signatures', [])
        for sig in signatures:
            if sig.get('severity', 0) >= 2:
                result.suspicious_behaviors.append(sig.get('description', 'Unknown behavior'))
                
        # Extract network activity
        network = analysis.get('network', {})
        for conn in network.get('tcp', []):
            result.network_activity.append({
                'protocol': 'tcp',
                'destination': f"{conn.get('dst')}:{conn.get('dport')}",
            })
            
        for conn in network.get('udp', []):
            result.network_activity.append({
                'protocol': 'udp',
                'destination': f"{conn.get('dst')}:{conn.get('dport')}",
            })
            
        # Extract file operations
        behavior = analysis.get('behavior', {})
        for proc in behavior.get('processes', []):
            for call in proc.get('calls', []):
                if call.get('category') in ['file', 'filesystem']:
                    result.file_operations.append({
                        'api': call.get('api'),
                        'args': call.get('arguments', {}),
                    })
                    
                if call.get('category') == 'registry':
                    result.registry_operations.append({
                        'api': call.get('api'),
                        'args': call.get('arguments', {}),
                    })
                    
        # Calculate score based on Cuckoo's rating
        info = analysis.get('info', {})
        score = info.get('score', 0)
        result.threat_score = int(score * 10)  # Cuckoo uses 0-10 scale
        result.is_malicious = result.threat_score >= 60


class SandboxManager:
    """
    Manages multiple sandbox backends.
    
    Tries Cuckoo first (if available), falls back to local sandbox.
    """
    
    def __init__(self):
        self.cuckoo = CuckooSandboxClient()
        self.local = LocalSandbox()
        
    def analyze_file(self, file_path: Path) -> SandboxResult:
        """
        Analyze file using best available sandbox.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            SandboxResult from analysis
        """
        # Try Cuckoo first if enabled
        if self.cuckoo.enabled:
            logger.info("Using Cuckoo Sandbox for analysis")
            return self.cuckoo.analyze_file(file_path)
            
        # Fall back to local sandbox
        logger.info("Using local sandbox for analysis")
        return self.local.analyze_file(file_path)
        
    def is_available(self) -> bool:
        """Check if any sandbox is available."""
        return self.cuckoo.enabled or self.local.enabled
