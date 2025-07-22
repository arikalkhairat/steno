#!/usr/bin/env python3
"""
Test script to verify security integration in the steganography application
"""

def test_imports():
    """Test that all security-related imports work correctly"""
    try:
        # Test security utilities
        import security_utils
        print("✅ security_utils imported successfully")
        
        # Test enhanced qr_utils with security functions
        from qr_utils import generate_secure_qr, read_secure_qr, validate_qr_security
        print("✅ Enhanced qr_utils security functions imported successfully")
        
        # Test app imports
        import app
        print("✅ Flask app imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_security_functions():
    """Test basic security function functionality"""
    try:
        import security_utils
        import tempfile
        import os
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test document content")
            test_doc_path = f.name
        
        try:
            # Test document key generation
            key = security_utils.generate_document_key(test_doc_path)
            print(f"✅ Document key generated: {key[:10]}...")
            
            # Test encryption/decryption
            test_data = "Hello, secure world!"
            encrypted = security_utils.encrypt_qr_data(test_data, key)
            decrypted = security_utils.decrypt_qr_data(encrypted, key)
            
            if decrypted == test_data:
                print("✅ Encryption/Decryption working correctly")
            else:
                print("❌ Encryption/Decryption failed")
                return False
                
        finally:
            # Clean up temp file
            if os.path.exists(test_doc_path):
                os.unlink(test_doc_path)
            
        return True
    except Exception as e:
        print(f"❌ Security function error: {e}")
        return False

def test_qr_security():
    """Test secure QR code functionality"""
    try:
        from qr_utils import generate_secure_qr, read_secure_qr
        import security_utils
        import tempfile
        import os
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test document content")
            test_doc_path = f.name
        
        try:
            # Generate a secure QR code
            key = security_utils.generate_document_key(test_doc_path)
            test_text = "Secure QR Test Data"
            
            qr_path = generate_secure_qr(test_text, key, output_path="test_secure_qr.png")
            print(f"✅ Secure QR generated: {qr_path}")
            
            # Read the secure QR code
            decrypted_text = read_secure_qr(qr_path, key)
            
            if decrypted_text == test_text:
                print("✅ Secure QR read/write working correctly")
            else:
                print("❌ Secure QR read/write failed")
                return False
                
        finally:
            # Clean up temp files
            if os.path.exists(test_doc_path):
                os.unlink(test_doc_path)
            if os.path.exists("test_secure_qr.png"):
                os.unlink("test_secure_qr.png")
            
        return True
    except Exception as e:
        print(f"❌ Secure QR error: {e}")
        return False

def main():
    """Run all security tests"""
    print("🔒 Testing Security Integration for Steganography Application")
    print("=" * 60)
    
    # Test imports
    print("\n1. Testing Imports...")
    if not test_imports():
        return
    
    # Test security functions
    print("\n2. Testing Security Functions...")
    if not test_security_functions():
        return
    
    # Test QR security
    print("\n3. Testing Secure QR Functions...")
    if not test_qr_security():
        return
    
    print("\n" + "=" * 60)
    print("🎉 All security tests passed! Your application is ready.")
    print("\nSecurity Features Available:")
    print("• Document key generation and management")
    print("• AES encryption for QR code data")
    print("• Secure QR code generation and reading")
    print("• Digital signatures and validation")
    print("• CLI security commands")
    print("• Flask API security endpoints")
    print("\nAPI Endpoints Added:")
    print("• /generate_document_key - Generate secure document keys")
    print("• /generate_secure_qr - Create encrypted QR codes")
    print("• /validate_qr_security - Validate QR security status")
    print("• /get_document_hash - Get document hash for verification")
    print("• /embed_secure_document - Secure document embedding")

if __name__ == "__main__":
    main()
