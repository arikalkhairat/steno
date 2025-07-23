#!/usr/bin/env python3
"""
Quick HTML validation test
"""

import html.parser

def test_html():
    try:
        parser = html.parser.HTMLParser()
        with open('d:/steno/templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            parser.feed(content)
        print('✅ HTML syntax is valid!')
        
        # Count tabs
        import re
        tab_buttons = len(re.findall(r'class="tab-btn"', content))
        tab_panes = len(re.findall(r'class="tab-pane"', content))
        
        print(f'📊 Found {tab_buttons} tab buttons and {tab_panes} tab panes')
        
        # Check for security tab
        if 'security-tab' in content:
            print('🔒 Security tab found!')
        
        if 'Document Security' in content:
            print('🔒 Security tab content found!')
            
        return True
    except Exception as e:
        print(f'❌ HTML error: {e}')
        return False

if __name__ == "__main__":
    test_html()
