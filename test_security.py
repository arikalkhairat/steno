#!/usr/bin/env python3
"""
Simple test to debug security endpoint issues without external dependencies
"""
import urllib.request
import urllib.error
import json

def test_statistics_endpoint():
    """Test the statistics endpoint"""
    
    url = "http://127.0.0.1:5001/api/security/statistics"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            status = response.getcode()
            data = response.read().decode('utf-8')
            
            print(f"Status Code: {status}")
            print(f"Response: {data}")
            
            if status == 200:
                try:
                    json_data = json.loads(data)
                    print("✓ Statistics endpoint working")
                    print(f"Statistics: {json.dumps(json_data, indent=2)}")
                except json.JSONDecodeError:
                    print("✗ Invalid JSON response")
            else:
                print(f"✗ Non-200 status code: {status}")
                
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error: {e.code} - {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"✗ URL Error: {e.reason}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

def test_list_keys_endpoint():
    """Test the list-keys endpoint"""
    
    url = "http://127.0.0.1:5001/api/security/list-keys"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            status = response.getcode()
            data = response.read().decode('utf-8')
            
            print(f"Status Code: {status}")
            print(f"Response: {data}")
            
            if status == 200:
                try:
                    json_data = json.loads(data)
                    print("✓ List keys endpoint working")
                    print(f"Keys count: {len(json_data.get('keys', []))}")
                except json.JSONDecodeError:
                    print("✗ Invalid JSON response")
            else:
                print(f"✗ Non-200 status code: {status}")
                
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error: {e.code} - {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"✗ URL Error: {e.reason}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    print("Testing Security Endpoints...")
    
    print("\n=== Testing List Keys ===")
    test_list_keys_endpoint()
    
    print("\n=== Testing Statistics ===")
    test_statistics_endpoint()
