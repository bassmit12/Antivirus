"""Test script for VirusTotal API integration."""
from src.api_integration.virustotal import VirusTotalClient

def test_virustotal():
    print("=" * 60)
    print("Testing VirusTotal API Integration")
    print("=" * 60)
    
    vt = VirusTotalClient()
    
    print(f"\nAPI Key configured: {vt.api_key is not None}")
    print(f"Enabled: {vt.enabled}")
    
    if not vt.enabled:
        print("\n❌ VirusTotal not enabled. Check your API key in .env file.")
        return
        
    # Test with EICAR test file hash (known malware test file)
    eicar_hash = "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
    
    print(f"\n🔍 Testing with EICAR test file hash...")
    print(f"Hash: {eicar_hash}")
    
    try:
        result = vt.lookup_hash(eicar_hash)
        
        if result:
            print(f"\n✅ Result received:")
            print(f"   Found in database: {result.get('found')}")
            print(f"   Malicious detections: {result.get('malicious', 0)}")
            print(f"   Suspicious detections: {result.get('suspicious', 0)}")
            print(f"   Harmless: {result.get('harmless', 0)}")
            print(f"   Total engines: {result.get('total_engines', 0)}")
            
            if result.get('threat_names'):
                print(f"\n   Threat names: {', '.join(result['threat_names'][:5])}")
                
            is_mal = vt.is_malicious(eicar_hash)
            print(f"\n   Is malicious (>=3 detections): {is_mal}")
        else:
            print("\n❌ No result returned")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_virustotal()
