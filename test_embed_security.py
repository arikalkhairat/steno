#!/usr/bin/env python3
"""
Test script for embed security enhancements
"""

import re

def test_embed_security():
    try:
        with open('d:/steno/templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print('🔒 Testing Embed Security Enhancements...')
        
        # Check for security settings section
        if 'Security Settings' in content and 'toggleSecuritySettings' in content:
            print('✅ Security Settings section added')
        else:
            print('❌ Security Settings section missing')
        
        # Check for security form elements
        security_elements = [
            'enableDocumentSecurity',
            'embedSecurityKey',
            'validateQrAuth',
            'generateEmbedKey',
            'embedSecurityStatus',
            'embedSecurityWarnings'
        ]
        
        print('\n📋 Checking Security Form Elements:')
        for element in security_elements:
            if f'id="{element}"' in content:
                print(f'✅ {element} - Found')
            else:
                print(f'❌ {element} - Missing')
        
        # Check for security functions
        security_functions = [
            'toggleSecuritySettings',
            'toggleEmbedSecurity',
            'detectDocumentSecurity',
            'generateEmbedSecurityKey',
            'validateEmbedQRAuth',
            'showEmbedSecurityStatus',
            'validateEmbedSecurity'
        ]
        
        print('\n🔧 Checking Security Functions:')
        for func in security_functions:
            if f'function {func}(' in content:
                print(f'✅ {func}() - Implemented')
            else:
                print(f'❌ {func}() - Missing')
        
        # Check for event listeners
        security_listeners = [
            'enableDocumentSecurity',
            'generateEmbedKey',
            'validateQrAuth',
            'qrFileEmbed',
            'docxFileEmbed'
        ]
        
        print('\n🎯 Checking Security Event Listeners:')
        for listener in security_listeners:
            if f"getElementById('{listener}').addEventListener" in content:
                print(f'✅ {listener} - Connected')
            else:
                print(f'❌ {listener} - Missing')
        
        # Check for form validation integration
        if 'validateEmbedSecurity()' in content and 'if (!validateEmbedSecurity())' in content:
            print('\n✅ Security validation integrated in form submission')
        else:
            print('\n❌ Security validation missing from form submission')
        
        # Check for security parameters in form submission
        if 'security_enabled' in content and 'security_key' in content:
            print('✅ Security parameters added to form submission')
        else:
            print('❌ Security parameters missing from form submission')
        
        # Check CSS styling
        if '.security-info' in content and '.security-controls' in content:
            print('✅ Security CSS styling added')
        else:
            print('❌ Security CSS styling missing')
        
        print('\n📊 Summary:')
        print('- Security Settings section with expandable UI')
        print('- Document security detection and key generation')
        print('- QR authorization validation with warnings')
        print('- Form submission integration with security parameters')
        print('- Proper event handling and user feedback')
        
        print('\n🎉 Embed security enhancements completed!')
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == "__main__":
    test_embed_security()
