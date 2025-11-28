"""Entropy-based malware detection."""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path


def calculate_entropy(data: bytes) -> float:
    """
    Calculate Shannon entropy of data.
    
    High entropy (>7.0) often indicates compression or encryption,
    common in packed malware.
    
    Args:
        data: Bytes to analyze
        
    Returns:
        Entropy value (0.0 to 8.0)
    """
    if not data:
        return 0.0
        
    # Count byte frequencies
    counter = Counter(data)
    length = len(data)
    
    # Calculate entropy
    entropy = 0.0
    for count in counter.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
        
    return entropy


def analyze_file_entropy(file_path: Path, chunk_size: int = 1024 * 1024) -> dict:
    """
    Analyze entropy of a file.
    
    Args:
        file_path: Path to file to analyze
        chunk_size: Size of chunks to analyze
        
    Returns:
        Dictionary with entropy analysis results
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read(chunk_size * 10)  # Analyze first 10MB max
            
        if not data:
            return {
                'entropy': 0.0,
                'suspicious': False,
                'reason': 'Empty file',
            }
            
        entropy = calculate_entropy(data)
        
        # High entropy is suspicious (packed/encrypted malware)
        is_suspicious = entropy > 7.2
        
        reason = None
        if entropy > 7.8:
            reason = "Very high entropy - likely encrypted or compressed"
        elif entropy > 7.2:
            reason = "High entropy - possibly packed"
        elif entropy < 1.0:
            reason = "Very low entropy - unusual pattern"
            is_suspicious = True
            
        return {
            'entropy': round(entropy, 2),
            'suspicious': is_suspicious,
            'reason': reason,
        }
        
    except Exception as e:
        return {
            'entropy': 0.0,
            'suspicious': False,
            'reason': f'Error analyzing entropy: {e}',
        }


def analyze_section_entropy(file_path: Path) -> list[dict]:
    """
    Analyze entropy of file sections (for PE files).
    
    Args:
        file_path: Path to PE file
        
    Returns:
        List of section entropy analysis results
    """
    try:
        import pefile
        
        pe = pefile.PE(str(file_path))
        sections = []
        
        for section in pe.sections:
            section_data = section.get_data()
            entropy = calculate_entropy(section_data)
            
            sections.append({
                'name': section.Name.decode('utf-8', errors='ignore').strip('\x00'),
                'entropy': round(entropy, 2),
                'size': len(section_data),
                'suspicious': entropy > 7.2,
            })
            
        return sections
        
    except ImportError:
        return []
    except Exception:
        return []
