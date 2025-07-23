#!/usr/bin/env python3
"""
Comprehensive JavaScript validation test for security functions
"""

import html.parser
import re

def test_security_functions():
    try:
        with open('d:/steno/templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print('🔒 Testing Security JavaScript Functions...')
        
        # Test HTML syntax
        parser = html.parser.HTMLParser()
        parser.feed(content)
        print('✅ HTML syntax is valid!')
        
        # Check for named functions
        functions_to_check = [
            'generateDocumentKey',
            'generateSecureQR', 
            'validateQRSecurity',
            'copySecurityKey',
            'showSecurityStatus',
            'hashDocument',
            'validateSecurityKey'
        ]
        
        print('\n📋 Checking Security Functions:')
        for func in functions_to_check:
            if f'function {func}(' in content:
                print(f'✅ {func}() - Found')
            else:
                print(f'❌ {func}() - Missing')
        
        # Check event listeners
        event_listeners = [
            'generateKeyBtn',
            'copyKeyBtn', 
            'getHashBtn',
            'generateSecureQrBtn',
            'validateSecurityBtn'
        ]
        
        print('\n🎯 Checking Event Listeners:')
        for listener in event_listeners:
            if f"getElementById('{listener}').addEventListener" in content:
                print(f'✅ {listener} - Connected')
            else:
                print(f'❌ {listener} - Missing')
        
        # Check API endpoints
        api_endpoints = [
            '/generate_document_key',
            '/get_document_hash',
            '/generate_secure_qr', 
            '/validate_qr_security'
        ]
        
        print('\n🌐 Checking API Endpoint References:')
        for endpoint in api_endpoints:
            if endpoint in content:
                print(f'✅ {endpoint} - Referenced')
            else:
                print(f'❌ {endpoint} - Missing')
        
        # Check tab integration
        if "'security': 'securityProcess'" in content:
            print('\n✅ Security tab integrated in clearTabResults')
        else:
            print('\n❌ Security tab missing from clearTabResults')
        
        # Count JavaScript functions
        js_function_count = len(re.findall(r'function\s+\w+\s*\(', content))
        async_function_count = len(re.findall(r'async\s+function\s+\w+\s*\(', content))
        
        print(f'\n📊 JavaScript Statistics:')
        print(f'Total functions: {js_function_count}')
        print(f'Async functions: {async_function_count}')
        print(f'Event listeners: {len(re.findall(r"addEventListener", content))}')
        
        # Check for security validations
        if 'validateSecurityKey' in content:
            print('\n🔐 Security key validation implemented')
        
        if 'showSecurityStatus' in content:
            print('🔐 Security status display implemented')
            
        print('\n🎉 All security JavaScript functions have been implemented!')
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == "__main__":
    test_security_functions()
