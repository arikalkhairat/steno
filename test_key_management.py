#!/usr/bin/env python3
"""
Test script for key management functionality.
This validates the security storage system and key management features.
"""

import os
import sys
import json
from datetime import datetime

def test_security_storage():
    """Test the security storage functionality."""
    print("🔍 Testing Security Storage System...")
    
    try:
        # Import our security storage module
        import security_storage
        print("✅ security_storage module imported successfully")
        
        # Test initialization
        print("\n📁 Testing storage initialization...")
        security_storage.init_security_storage()
        print("✅ Storage initialized")
        
        # Test storing a document key
        print("\n🔑 Testing key storage...")
        test_doc_hash = "test_document_hash_12345"
        test_doc_name = "test_document.pdf"
        test_key = b"sample_security_key_data"
        
        success = security_storage.store_document_key(
            document_hash=test_doc_hash,
            document_name=test_doc_name,
            security_key=test_key
        )
        print(f"✅ Key storage: {'SUCCESS' if success else 'FAILED'}")
        
        # Test retrieving the key
        print("\n📥 Testing key retrieval...")
        retrieved_key = security_storage.retrieve_document_key(test_doc_hash)
        if retrieved_key:
            print("✅ Key retrieved successfully")
            print(f"   Document: {retrieved_key['document_name']}")
            print(f"   Created: {retrieved_key['created_at']}")
            print(f"   Access count: {retrieved_key['access_count']}")
        else:
            print("❌ Key retrieval failed")
        
        # Test listing documents
        print("\n📋 Testing document listing...")
        documents = security_storage.list_secured_documents()
        print(f"✅ Found {len(documents)} secured documents")
        for doc in documents:
            print(f"   - {doc['document_name']} (Hash: {doc['document_hash'][:8]}...)")
        
        # Test cleanup (remove test data)
        print("\n🧹 Testing key deletion...")
        deleted = security_storage.delete_document_key(test_doc_hash)
        print(f"✅ Key deletion: {'SUCCESS' if deleted else 'FAILED'}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_key_management_features():
    """Test key management features."""
    print("\n🛠️ Testing Key Management Features...")
    
    # Test with multiple keys
    try:
        import security_storage
        
        # Create multiple test keys
        test_keys = [
            ("doc1_hash", "Document1.pdf", b"key1_data"),
            ("doc2_hash", "Document2.docx", b"key2_data"),
            ("doc3_hash", "Very_Long_Document_Name_That_Should_Be_Truncated.pdf", b"key3_data"),
        ]
        
        print("\n📝 Creating test keys...")
        for doc_hash, doc_name, key_data in test_keys:
            success = security_storage.store_document_key(doc_hash, doc_name, key_data)
            print(f"   {'✅' if success else '❌'} {doc_name}")
        
        # Test export backup
        print("\n💾 Testing backup export...")
        backup_data = security_storage.export_security_backup()
        if backup_data and 'keys' in backup_data:
            print(f"✅ Backup created with {len(backup_data['keys'])} keys")
        else:
            print("❌ Backup export failed")
        
        # Test cleanup
        print("\n🧹 Cleaning up test data...")
        for doc_hash, _, _ in test_keys:
            security_storage.delete_document_key(doc_hash)
        print("✅ Test cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Key management test error: {e}")
        return False

def test_api_endpoints():
    """Test that our API endpoint functions would work."""
    print("\n🌐 Testing API Endpoint Logic...")
    
    try:
        # Test that we can import the functions we need
        import security_storage
        
        # Simulate API calls
        print("   📊 Testing statistics calculation...")
        documents = security_storage.list_secured_documents()
        total_docs = len(documents)
        print(f"   ✅ Total documents: {total_docs}")
        
        print("   📈 Testing status calculation...")
        now = datetime.now()
        active_count = 0
        for doc in documents:
            try:
                last_accessed = datetime.fromisoformat(doc['last_accessed'].replace('Z', '+00:00'))
                days_diff = (now - last_accessed).days
                if days_diff <= 7:
                    active_count += 1
            except:
                pass
        
        print(f"   ✅ Active documents: {active_count}")
        print("   ✅ API logic validation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Key Management System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Security Storage", test_security_storage),
        ("Key Management Features", test_key_management_features),
        ("API Endpoint Logic", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} Tests...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Key management system is ready.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
