"""PE (Portable Executable) file analysis for Windows executables."""
from __future__ import annotations

from pathlib import Path
from typing import Optional


def analyze_pe_file(file_path: Path) -> Optional[dict]:
    """
    Analyze a Windows PE file for suspicious characteristics.
    
    Args:
        file_path: Path to PE file
        
    Returns:
        Dictionary with PE analysis results or None if not a PE file
    """
    try:
        import pefile
        
        pe = pefile.PE(str(file_path))
        
        results = {
            'is_pe': True,
            'suspicious': False,
            'warnings': [],
            'imports': [],
            'sections': [],
            'is_packed': False,
            'is_signed': False,
        }
        
        # Check for suspicious imports
        suspicious_apis = {
            'VirtualAllocEx', 'WriteProcessMemory', 'CreateRemoteThread',
            'NtUnmapViewOfSection', 'SetWindowsHookEx', 'GetAsyncKeyState',
            'RegisterRawInputDevices', 'BitBlt', 'GetForegroundWindow',
        }
        
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll_name = entry.dll.decode('utf-8', errors='ignore') if entry.dll else 'unknown'
                for imp in entry.imports:
                    if imp.name:
                        func_name = imp.name.decode('utf-8', errors='ignore')
                        results['imports'].append(f"{dll_name}:{func_name}")
                        
                        if func_name in suspicious_apis:
                            results['suspicious'] = True
                            results['warnings'].append(f"Suspicious API: {func_name}")
                            
        # Check sections for suspicious characteristics
        suspicious_section_names = {'.upx', '.aspack', '.kkrunchy', '.mpress', '.petite'}
        
        for section in pe.sections:
            section_name = section.Name.decode('utf-8', errors='ignore').strip('\x00')
            results['sections'].append({
                'name': section_name,
                'virtual_size': section.Misc_VirtualSize,
                'raw_size': section.SizeOfRawData,
                'executable': bool(section.Characteristics & 0x20000000),
                'writable': bool(section.Characteristics & 0x80000000),
            })
            
            # Check for packer signatures
            if any(packer in section_name.lower() for packer in suspicious_section_names):
                results['is_packed'] = True
                results['suspicious'] = True
                results['warnings'].append(f"Packed with: {section_name}")
                
            # Writable and executable section (code injection technique)
            if (section.Characteristics & 0x20000000) and (section.Characteristics & 0x80000000):
                results['suspicious'] = True
                results['warnings'].append(f"Writable+Executable section: {section_name}")
                
        # Check for code signing
        if hasattr(pe, 'DIRECTORY_ENTRY_SECURITY'):
            results['is_signed'] = True
        else:
            results['warnings'].append("File is not digitally signed")
            
        # Check for suspicious entry point
        if hasattr(pe, 'OPTIONAL_HEADER'):
            entry_point = pe.OPTIONAL_HEADER.AddressOfEntryPoint
            
            # Entry point in non-standard section
            for section in pe.sections:
                if section.VirtualAddress <= entry_point < section.VirtualAddress + section.Misc_VirtualSize:
                    section_name = section.Name.decode('utf-8', errors='ignore').strip('\x00')
                    if section_name not in ['.text', 'CODE']:
                        results['suspicious'] = True
                        results['warnings'].append(f"Entry point in unusual section: {section_name}")
                    break
                    
        # Check for low number of imports (potential packer)
        if len(results['imports']) < 5 and not results['is_packed']:
            results['suspicious'] = True
            results['warnings'].append("Very few imports - possibly packed")
            results['is_packed'] = True
            
        return results
        
    except ImportError:
        return None
    except Exception as e:
        return {
            'is_pe': False,
            'error': str(e),
        }


def check_pe_header(file_path: Path) -> bool:
    """
    Quick check if file is a valid PE file.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file appears to be a PE file
    """
    try:
        with open(file_path, 'rb') as f:
            # Check for MZ header
            if f.read(2) != b'MZ':
                return False
                
            # Get PE header offset
            f.seek(0x3C)
            pe_offset = int.from_bytes(f.read(4), byteorder='little')
            
            # Check for PE signature
            f.seek(pe_offset)
            return f.read(4) == b'PE\x00\x00'
            
    except Exception:
        return False
