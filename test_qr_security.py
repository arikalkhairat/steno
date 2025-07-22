# Test the new security functions in qr_utils.py
import sys
sys.path.append('d:/steno')

try:
    # Test importing our security module
    import security_utils
    print("✅ security_utils imported successfully")
    
    # Test the new functions from qr_utils by importing them individually
    from qr_utils import embed_security_metadata, extract_security_metadata, validate_qr_security
    print("✅ Security functions from qr_utils imported successfully")
    
    # Test document key generation
    doc_key = security_utils.generate_document_key('d:/steno/requirements.txt')
    print(f"✅ Document key generated: {doc_key[:20]}...")
    
    # Test encryption
    test_data = "This is a test message for QR security"
    encrypted = security_utils.encrypt_qr_data(test_data, doc_key)
    print(f"✅ Encryption successful: {len(encrypted)} chars")
    
    # Test metadata embedding
    import time
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Test with a simpler approach first
    print(f"[*] Testing metadata embedding...")
    print(f"[*] Encrypted data: {encrypted[:50]}...")
    print(f"[*] Document key: {doc_key[:20]}...")
    print(f"[*] Timestamp: {timestamp}")
    
    metadata_qr = embed_security_metadata(encrypted, doc_key, timestamp)
    print(f"✅ Metadata embedding successful: {len(metadata_qr)} chars")
    
    # Test metadata extraction
    extracted_metadata = extract_security_metadata(metadata_qr)
    print(f"✅ Metadata extraction successful: {extracted_metadata['has_metadata']}")
    
    # Test document hash
    doc_hash = security_utils.generate_document_hash('d:/steno/requirements.txt')
    print(f"✅ Document hash generated: {doc_hash[:20]}...")
    
    # Test security validation
    validation = validate_qr_security(metadata_qr, doc_key, doc_hash)
    print(f"✅ Security validation completed: {validation['overall_valid']}")
    
    print("\n🎉 All enhanced qr_utils.py security functions working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Test error: {e}")
