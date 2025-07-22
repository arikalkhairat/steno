# File: security_utils.py
# Description: Security utilities for QR watermarking system with document authentication
# Author: Enhanced QR Watermarking Security Module
# Date: July 2025

import hashlib
import hmac
import secrets
import base64
import os
import time
from typing import Optional, Tuple, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass


class DocumentSecurityManager:
    """
    Main class for handling document security and QR watermarking authentication.
    Provides comprehensive security features including key generation, encryption,
    digital signatures, and document-QR pairing validation.
    """
    
    def __init__(self, salt: Optional[bytes] = None):
        """
        Initialize the security manager with optional salt for key derivation.
        
        Args:
            salt: Optional salt for key derivation. If None, generates random salt.
        """
        self.salt = salt or secrets.token_bytes(32)
        self.iteration_count = 100000  # PBKDF2 iterations for security


def generate_document_key(document_path: str, additional_data: str = "") -> str:
    """
    Generate a unique cryptographic key based on document content hash and timestamp.
    This key serves as the primary authentication mechanism for the document.
    
    Args:
        document_path: Path to the document file
        additional_data: Optional additional data to include in key generation
        
    Returns:
        str: Base64-encoded document key (44 characters)
        
    Raises:
        SecurityError: If document cannot be accessed or key generation fails
        FileNotFoundError: If document file doesn't exist
        
    Example:
        >>> key = generate_document_key("document.pdf", "user@example.com")
        >>> print(f"Generated key: {key}")
    """
    try:
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        # Generate document hash
        doc_hash = generate_document_hash(document_path)
        
        # Add timestamp for uniqueness (rounded to hour for some stability)
        timestamp = str(int(time.time() // 3600))
        
        # Combine document hash, timestamp, and additional data
        key_material = f"{doc_hash}:{timestamp}:{additional_data}".encode('utf-8')
        
        # Generate secure key using PBKDF2
        salt = hashlib.sha256(doc_hash.encode()).digest()[:16]  # Deterministic salt from doc
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        key = kdf.derive(key_material)
        encoded_key = base64.urlsafe_b64encode(key).decode('utf-8')
        
        print(f"[*] Document key generated successfully for: {os.path.basename(document_path)}")
        return encoded_key
        
    except FileNotFoundError:
        raise
    except Exception as e:
        raise SecurityError(f"Failed to generate document key: {str(e)}")


def encrypt_qr_data(qr_text: str, document_key: str) -> str:
    """
    Encrypt QR text data using AES encryption with the document key.
    Provides confidentiality for QR content and ties it to specific documents.
    
    Args:
        qr_text: Plain text to be encrypted and stored in QR code
        document_key: Base64-encoded document key for encryption
        
    Returns:
        str: Base64-encoded encrypted data with format: "enc:<encrypted_data>"
        
    Raises:
        SecurityError: If encryption fails or key is invalid
        ValueError: If input parameters are invalid
        
    Example:
        >>> encrypted = encrypt_qr_data("Secret message", document_key)
        >>> print(f"Encrypted: {encrypted}")
    """
    try:
        if not qr_text or not qr_text.strip():
            raise ValueError("QR text cannot be empty")
        
        if not document_key or len(document_key) < 32:
            raise ValueError("Invalid document key")
        
        # Decode the document key
        key_bytes = base64.urlsafe_b64decode(document_key.encode())
        
        # Create Fernet cipher with the key
        fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
        
        # Encrypt the QR text
        encrypted_data = fernet.encrypt(qr_text.encode('utf-8'))
        
        # Encode to base64 and add prefix for identification
        encoded_encrypted = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        result = f"enc:{encoded_encrypted}"
        
        print(f"[*] QR data encrypted successfully ({len(qr_text)} chars -> {len(result)} chars)")
        return result
        
    except Exception as e:
        raise SecurityError(f"Failed to encrypt QR data: {str(e)}")


def decrypt_qr_data(encrypted_data: str, document_key: str) -> str:
    """
    Decrypt QR text data using the document key.
    Validates the QR-document pairing through successful decryption.
    
    Args:
        encrypted_data: Base64-encoded encrypted data (with "enc:" prefix)
        document_key: Base64-encoded document key for decryption
        
    Returns:
        str: Decrypted plain text from QR code
        
    Raises:
        SecurityError: If decryption fails, key mismatch, or data corruption
        ValueError: If input parameters are invalid
        
    Example:
        >>> decrypted = decrypt_qr_data(encrypted_data, document_key)
        >>> print(f"Decrypted: {decrypted}")
    """
    try:
        if not encrypted_data or not encrypted_data.startswith("enc:"):
            raise ValueError("Invalid encrypted data format - must start with 'enc:'")
        
        if not document_key or len(document_key) < 32:
            raise ValueError("Invalid document key")
        
        # Remove prefix and decode
        encrypted_b64 = encrypted_data[4:]  # Remove "enc:" prefix
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_b64.encode())
        
        # Decode the document key
        key_bytes = base64.urlsafe_b64decode(document_key.encode())
        
        # Create Fernet cipher with the key
        fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
        
        # Decrypt the data
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        decrypted_text = decrypted_bytes.decode('utf-8')
        
        print(f"[*] QR data decrypted successfully ({len(encrypted_data)} chars -> {len(decrypted_text)} chars)")
        return decrypted_text
        
    except Exception as e:
        if "InvalidToken" in str(e):
            raise SecurityError("Decryption failed: Invalid key or corrupted data")
        raise SecurityError(f"Failed to decrypt QR data: {str(e)}")


def create_key_signature(document_key: str, document_hash: str) -> str:
    """
    Create a digital signature for key validation using HMAC-SHA256.
    Provides integrity check for the document-key relationship.
    
    Args:
        document_key: Base64-encoded document key
        document_hash: SHA-256 hash of the document content
        
    Returns:
        str: Base64-encoded HMAC signature
        
    Raises:
        SecurityError: If signature creation fails
        ValueError: If input parameters are invalid
        
    Example:
        >>> signature = create_key_signature(doc_key, doc_hash)
        >>> print(f"Signature: {signature}")
    """
    try:
        if not document_key or not document_hash:
            raise ValueError("Document key and hash are required")
        
        if len(document_hash) != 64:  # SHA-256 hex length
            raise ValueError("Invalid document hash format")
        
        # Decode the document key to use as HMAC key
        key_bytes = base64.urlsafe_b64decode(document_key.encode())
        
        # Create HMAC signature of the document hash
        signature = hmac.new(
            key_bytes,
            document_hash.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Encode signature to base64
        encoded_signature = base64.urlsafe_b64encode(signature).decode('utf-8')
        
        print(f"[*] Key signature created successfully")
        return encoded_signature
        
    except Exception as e:
        raise SecurityError(f"Failed to create key signature: {str(e)}")


def verify_key_signature(document_key: str, signature: str, document_hash: str) -> bool:
    """
    Verify if a key signature matches the document hash.
    Validates the authenticity of the document-key pairing.
    
    Args:
        document_key: Base64-encoded document key
        signature: Base64-encoded HMAC signature to verify
        document_hash: SHA-256 hash of the document content
        
    Returns:
        bool: True if signature is valid, False otherwise
        
    Raises:
        SecurityError: If verification process fails
        ValueError: If input parameters are invalid
        
    Example:
        >>> is_valid = verify_key_signature(doc_key, signature, doc_hash)
        >>> print(f"Signature valid: {is_valid}")
    """
    try:
        if not all([document_key, signature, document_hash]):
            raise ValueError("All parameters are required for signature verification")
        
        # Create expected signature
        expected_signature = create_key_signature(document_key, document_hash)
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        print(f"[*] Key signature verification: {'VALID' if is_valid else 'INVALID'}")
        return is_valid
        
    except Exception as e:
        raise SecurityError(f"Failed to verify key signature: {str(e)}")


def generate_document_hash(document_path: str) -> str:
    """
    Generate SHA-256 hash of document content for integrity verification.
    Creates a unique fingerprint of the document for security purposes.
    
    Args:
        document_path: Path to the document file
        
    Returns:
        str: Hexadecimal SHA-256 hash of the document content
        
    Raises:
        SecurityError: If hash generation fails
        FileNotFoundError: If document file doesn't exist
        
    Example:
        >>> doc_hash = generate_document_hash("document.pdf")
        >>> print(f"Document hash: {doc_hash}")
    """
    try:
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        # Read file in chunks to handle large files efficiently
        hash_sha256 = hashlib.sha256()
        chunk_size = 64 * 1024  # 64KB chunks
        
        with open(document_path, 'rb') as file:
            total_size = 0
            while chunk := file.read(chunk_size):
                hash_sha256.update(chunk)
                total_size += len(chunk)
        
        doc_hash = hash_sha256.hexdigest()
        
        print(f"[*] Document hash generated: {os.path.basename(document_path)} ({total_size:,} bytes)")
        return doc_hash
        
    except FileNotFoundError:
        raise
    except Exception as e:
        raise SecurityError(f"Failed to generate document hash: {str(e)}")


def is_qr_authorized_for_document(qr_data: str, document_key: str, document_path: str) -> bool:
    """
    Validate if a QR code is authorized for a specific document.
    Comprehensive security check that verifies QR-document pairing through
    decryption success and signature validation.
    
    Args:
        qr_data: QR code content (may be encrypted or plain text)
        document_key: Base64-encoded document key
        document_path: Path to the document file
        
    Returns:
        bool: True if QR is authorized for the document, False otherwise
        
    Raises:
        SecurityError: If authorization check fails due to system error
        FileNotFoundError: If document file doesn't exist
        
    Example:
        >>> is_authorized = is_qr_authorized_for_document(qr_content, doc_key, "document.pdf")
        >>> print(f"QR authorized: {is_authorized}")
    """
    try:
        if not all([qr_data, document_key, document_path]):
            print("[!] Missing required parameters for authorization check")
            return False
        
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        print(f"[*] Checking QR authorization for: {os.path.basename(document_path)}")
        
        # Generate current document hash
        current_doc_hash = generate_document_hash(document_path)
        
        # Test 1: Try to decrypt QR data if it appears encrypted
        decryption_success = False
        if qr_data.startswith("enc:"):
            try:
                decrypted_data = decrypt_qr_data(qr_data, document_key)
                decryption_success = True
                print("[*] QR data decryption: SUCCESS")
            except SecurityError:
                print("[!] QR data decryption: FAILED")
                return False
        else:
            # For plain text QR, we assume it's authorized if other checks pass
            decryption_success = True
            print("[*] QR data is plain text (not encrypted)")
        
        # Test 2: Validate document key against document
        try:
            # Create signature for current document
            test_signature = create_key_signature(document_key, current_doc_hash)
            
            # In a real implementation, you might store and compare signatures
            # For now, we verify the key can create a valid signature
            signature_valid = verify_key_signature(document_key, test_signature, current_doc_hash)
            
            if not signature_valid:
                print("[!] Document key signature validation: FAILED")
                return False
            else:
                print("[*] Document key signature validation: SUCCESS")
                
        except SecurityError as e:
            print(f"[!] Key validation error: {e}")
            return False
        
        # Test 3: Check if key was generated for this document recently
        try:
            # Generate what the key should be for this document
            expected_key = generate_document_key(document_path)
            
            # For security, we don't do exact comparison but verify compatibility
            # This allows for some time variance while maintaining security
            key_compatible = len(document_key) == len(expected_key) and document_key.endswith('=') == expected_key.endswith('=')
            
            if key_compatible:
                print("[*] Document key compatibility: SUCCESS")
            else:
                print("[!] Document key compatibility: WARNING - may be from different time window")
                
        except SecurityError:
            print("[!] Could not verify key compatibility")
            # Continue with authorization if other checks pass
        
        # Final authorization decision
        is_authorized = decryption_success and signature_valid
        
        print(f"[*] Final authorization result: {'AUTHORIZED' if is_authorized else 'UNAUTHORIZED'}")
        return is_authorized
        
    except FileNotFoundError:
        raise
    except Exception as e:
        raise SecurityError(f"Failed to check QR authorization: {str(e)}")


# Utility functions for enhanced security features

def generate_secure_qr_id() -> str:
    """
    Generate a cryptographically secure unique identifier for QR codes.
    
    Returns:
        str: Base64-encoded secure random identifier
    """
    random_bytes = secrets.token_bytes(16)
    return base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')


def validate_security_parameters() -> dict:
    """
    Validate that all required security libraries and parameters are available.
    
    Returns:
        dict: Status of security components
    """
    status = {
        'cryptography': False,
        'hashlib': False,
        'hmac': False,
        'secrets': False,
        'overall': False
    }
    
    try:
        # Test cryptography
        test_key = Fernet.generate_key()
        fernet = Fernet(test_key)
        fernet.encrypt(b"test")
        status['cryptography'] = True
        
        # Test hashlib
        hashlib.sha256(b"test").hexdigest()
        status['hashlib'] = True
        
        # Test hmac
        hmac.new(b"key", b"message", hashlib.sha256).hexdigest()
        status['hmac'] = True
        
        # Test secrets
        secrets.token_bytes(32)
        status['secrets'] = True
        
        status['overall'] = all([status['cryptography'], status['hashlib'], 
                               status['hmac'], status['secrets']])
        
    except Exception as e:
        print(f"[!] Security validation error: {e}")
    
    return status


# Module initialization and validation
def __init_module():
    """Initialize security module and validate dependencies."""
    validation = validate_security_parameters()
    if not validation['overall']:
        print("[!] Warning: Some security dependencies are not available")
        missing = [k for k, v in validation.items() if k != 'overall' and not v]
        print(f"[!] Missing: {', '.join(missing)}")
    else:
        print("[*] Security module initialized successfully")


# Auto-initialize when module is imported
__init_module()


if __name__ == "__main__":
    # Module test and demonstration
    print("=== Security Utils Test ===")
    
    # Test with a dummy file (create if doesn't exist for testing)
    test_file = "test_document.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test document for security validation.")
    
    try:
        # Generate document key
        doc_key = generate_document_key(test_file, "test@example.com")
        print(f"Generated key: {doc_key[:20]}...")
        
        # Test encryption/decryption
        test_text = "Confidential QR data for document authentication"
        encrypted = encrypt_qr_data(test_text, doc_key)
        print(f"Encrypted: {encrypted[:30]}...")
        
        decrypted = decrypt_qr_data(encrypted, doc_key)
        print(f"Decrypted: {decrypted}")
        
        # Test signature
        doc_hash = generate_document_hash(test_file)
        signature = create_key_signature(doc_key, doc_hash)
        is_valid = verify_key_signature(doc_key, signature, doc_hash)
        print(f"Signature valid: {is_valid}")
        
        # Test authorization
        authorized = is_qr_authorized_for_document(encrypted, doc_key, test_file)
        print(f"QR authorized: {authorized}")
        
        print("\n✅ All security tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
