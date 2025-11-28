"""String analysis for suspicious patterns."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


# Suspicious string patterns
SUSPICIOUS_PATTERNS = {
    'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'url': r'https?://[^\s]+',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'registry_key': r'HKEY_[A-Z_]+\\[^\s]+',
    'bitcoin_address': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
    'file_path': r'[A-Za-z]:\\[^:*?"<>|\r\n]+',
    'discord_webhook': r'https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+',
}

# Suspicious keywords
SUSPICIOUS_KEYWORDS = {
    'keylog', 'password', 'credential', 'token', 'cookie',
    'wallet', 'bitcoin', 'crypto', 'ransom', 'encrypt',
    'payload', 'shellcode', 'inject', 'hook', 'rootkit',
    'backdoor', 'trojan', 'rat', 'stealer', 'miner',
}


def extract_strings(file_path: Path, min_length: int = 4, max_strings: int = 1000) -> list[str]:
    """
    Extract ASCII strings from a binary file.
    
    Args:
        file_path: Path to file
        min_length: Minimum string length
        max_strings: Maximum number of strings to extract
        
    Returns:
        List of extracted strings
    """
    strings = []
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read(10 * 1024 * 1024)  # Read first 10MB
            
        # Find ASCII strings
        pattern = re.compile(b'[ -~]{%d,}' % min_length)
        matches = pattern.findall(data)
        
        for match in matches[:max_strings]:
            try:
                strings.append(match.decode('ascii'))
            except UnicodeDecodeError:
                continue
                
    except Exception:
        pass
        
    return strings


def analyze_strings(file_path: Path) -> dict:
    """
    Analyze strings in a file for suspicious patterns.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with string analysis results
    """
    strings = extract_strings(file_path)
    
    results = {
        'total_strings': len(strings),
        'suspicious': False,
        'findings': {},
        'keywords_found': [],
    }
    
    if not strings:
        return results
        
    # Search for suspicious patterns
    for pattern_name, pattern in SUSPICIOUS_PATTERNS.items():
        matches = []
        for string in strings:
            found = re.findall(pattern, string, re.IGNORECASE)
            matches.extend(found)
            
        if matches:
            # Remove duplicates and limit results
            unique_matches = list(set(matches))[:10]
            results['findings'][pattern_name] = unique_matches
            results['suspicious'] = True
            
    # Search for suspicious keywords
    string_lower = ' '.join(strings).lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in string_lower:
            results['keywords_found'].append(keyword)
            results['suspicious'] = True
            
    return results


def check_obfuscation(file_path: Path) -> dict:
    """
    Check for signs of string obfuscation.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with obfuscation analysis
    """
    strings = extract_strings(file_path, min_length=8)
    
    if not strings:
        return {'obfuscated': False}
        
    # Calculate average string length
    avg_length = sum(len(s) for s in strings) / len(strings)
    
    # Count random-looking strings (high proportion of mixed case)
    random_count = 0
    for string in strings[:100]:  # Sample first 100 strings
        if _is_random_looking(string):
            random_count += 1
            
    random_ratio = random_count / min(len(strings), 100)
    
    is_obfuscated = random_ratio > 0.5 or avg_length < 6
    
    return {
        'obfuscated': is_obfuscated,
        'avg_string_length': round(avg_length, 2),
        'random_ratio': round(random_ratio, 2),
    }


def _is_random_looking(string: str) -> bool:
    """Check if a string looks random (potential obfuscation)."""
    if len(string) < 8:
        return False
        
    # Count uppercase, lowercase, digits
    upper = sum(1 for c in string if c.isupper())
    lower = sum(1 for c in string if c.islower())
    digits = sum(1 for c in string if c.isdigit())
    
    # Random if has mix of all three or mostly non-alphanumeric
    has_mix = upper > 0 and lower > 0 and digits > 0
    non_alnum = sum(1 for c in string if not c.isalnum())
    
    return has_mix or (non_alnum / len(string) > 0.3)
