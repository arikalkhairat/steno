#!/usr/bin/env python3
"""
Test script to check API endpoints
"""
import requests
import json

# Base URL for testing
BASE_URL = "http://127.0.0.1:5001"

def test_endpoints():
    """Test various endpoints to identify issues"""
    
    print("Testing API endpoints...")
    
    # Test 1: List keys endpoint
    print("\n1. Testing /api/security/list-keys")
    try:
        response = requests.get(f"{BASE_URL}/api/security/list-keys", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✓ list-keys working")
        else:
            print(f"✗ list-keys failed: {response.text}")
    except Exception as e:
        print(f"✗ list-keys error: {e}")
    
    # Test 2: Statistics endpoint
    print("\n2. Testing /api/security/statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/security/statistics", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✓ statistics working")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"✗ statistics failed: {response.text}")
    except Exception as e:
        print(f"✗ statistics error: {e}")
    
    # Test 3: Document hash endpoint
    print("\n3. Testing /get_document_hash")
    try:
        # This requires a file upload, so we'll just check if the endpoint exists
        response = requests.post(f"{BASE_URL}/get_document_hash", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 400:  # Expected since we didn't send a file
            print("✓ get_document_hash endpoint exists")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ get_document_hash error: {e}")

if __name__ == "__main__":
    test_endpoints()
