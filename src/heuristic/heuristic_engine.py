"""Unified heuristic detection engine."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import entropy_analyzer, pe_analyzer, string_analyzer
from ..config import config


class HeuristicEngine:
    """Unified heuristic detection engine."""
    
    def __init__(self):
        self.enabled = config.get('detection.heuristic_enabled', True)
        self.sensitivity = config.get('detection.sensitivity', 'medium')
        
        # Thresholds based on sensitivity
        self.thresholds = self._get_thresholds()
        
    def analyze_file(self, file_path: Path) -> dict:
        """
        Perform comprehensive heuristic analysis on a file.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Dictionary with analysis results and threat assessment
        """
        if not self.enabled:
            return {'enabled': False, 'is_suspicious': False}
            
        results = {
            'file_path': str(file_path),
            'is_suspicious': False,
            'threat_score': 0,
            'max_score': 100,
            'detections': [],
            'entropy': None,
            'pe_analysis': None,
            'string_analysis': None,
        }
        
        try:
            # Entropy analysis
            entropy_result = entropy_analyzer.analyze_file_entropy(file_path)
            results['entropy'] = entropy_result
            
            if entropy_result.get('suspicious'):
                results['threat_score'] += 15
                results['detections'].append({
                    'type': 'entropy',
                    'severity': 'medium',
                    'description': entropy_result.get('reason', 'High entropy detected'),
                })
                
            # PE analysis (if Windows executable)
            if pe_analyzer.check_pe_header(file_path):
                pe_result = pe_analyzer.analyze_pe_file(file_path)
                results['pe_analysis'] = pe_result
                
                if pe_result and pe_result.get('suspicious'):
                    results['threat_score'] += 25
                    
                    for warning in pe_result.get('warnings', []):
                        results['detections'].append({
                            'type': 'pe_structure',
                            'severity': 'high' if 'inject' in warning.lower() else 'medium',
                            'description': warning,
                        })
                        
                if pe_result and pe_result.get('is_packed'):
                    results['threat_score'] += 20
                    
            # String analysis
            string_result = string_analyzer.analyze_strings(file_path)
            results['string_analysis'] = string_result
            
            if string_result.get('suspicious'):
                results['threat_score'] += 20
                
                # Add findings
                for pattern_type, matches in string_result.get('findings', {}).items():
                    if matches:
                        results['detections'].append({
                            'type': 'suspicious_strings',
                            'severity': 'medium',
                            'description': f"Found {pattern_type}: {', '.join(matches[:3])}",
                        })
                        
                # Add keywords
                keywords = string_result.get('keywords_found', [])
                if keywords:
                    results['threat_score'] += len(keywords) * 5
                    results['detections'].append({
                        'type': 'suspicious_keywords',
                        'severity': 'high' if len(keywords) > 3 else 'medium',
                        'description': f"Suspicious keywords: {', '.join(keywords[:5])}",
                    })
                    
            # Check for obfuscation
            obfuscation = string_analyzer.check_obfuscation(file_path)
            if obfuscation.get('obfuscated'):
                results['threat_score'] += 15
                results['detections'].append({
                    'type': 'obfuscation',
                    'severity': 'medium',
                    'description': 'Possible string obfuscation detected',
                })
                
            # Determine if suspicious based on threshold
            threshold = self.thresholds[self.sensitivity]
            results['is_suspicious'] = results['threat_score'] >= threshold
            
            # Calculate confidence level
            if results['threat_score'] >= 70:
                results['confidence'] = 'high'
            elif results['threat_score'] >= 40:
                results['confidence'] = 'medium'
            elif results['threat_score'] >= threshold:
                results['confidence'] = 'low'
            else:
                results['confidence'] = 'none'
                
        except Exception as e:
            results['error'] = str(e)
            
        return results
        
    def _get_thresholds(self) -> dict[str, int]:
        """Get threat score thresholds based on sensitivity."""
        return {
            'low': 60,      # Only flag very suspicious files
            'medium': 40,   # Balanced detection
            'high': 25,     # Flag more potential threats
            'paranoid': 15, # Maximum sensitivity
        }
        
    def is_suspicious(self, file_path: Path) -> bool:
        """
        Quick check if file is suspicious.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is deemed suspicious
        """
        result = self.analyze_file(file_path)
        return result.get('is_suspicious', False)
