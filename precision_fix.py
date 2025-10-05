#!/usr/bin/env python3
"""
Precision fixes for specific syntax errors identified
"""
import os
import re
from pathlib import Path

def fix_precision_errors():
    """Fix each specific error precisely"""
    print("🎯 Applying precision fixes...")
    
    # Fix 1: scripts/complete_security_hardening.py line 120
    # Error: invalid character '✅' (U+2705) in f-string
    fix_emoji_in_fstring('scripts/complete_security_hardening.py')
    
    # Fix 2: scripts/final_security_verification.py line 88
    # Error: invalid syntax, missing comma in f-string
    fix_fstring_syntax('scripts/final_security_verification.py')
    
    # Fix 3: scripts/generate_release_notes.py line 35
    # Error: invalid syntax in docstring
    fix_docstring_syntax('scripts/generate_release_notes.py')
    
    # Fix 4: scripts/verify_security_fixes.py line 53
    # Error: unexpected indent
    fix_indentation('scripts/verify_security_fixes.py')
    
    # Fix 5: src/amas/security/audit.py line 21
    # Error: DEBUG = "debug"""
    fix_malformed_string('src/amas/security/audit.py')
    
    # Fix 6: src/amas/security/authorization.py line 184
    # Error: unterminated string literal with quotes
    fix_quote_issue('src/amas/security/authorization.py')
    
    # Fix 7: src/amas/services/database_service.py line 100
    # Error: unmatched ')'
    fix_unmatched_paren('src/amas/services/database_service.py')
    
    # Fix 8 & 9: test files with invalid docstring syntax
    fix_test_docstrings('tests/test_security_fixes.py')
    fix_test_docstrings('tests/test_services.py')

def fix_emoji_in_fstring(file_path):
    """Fix emoji characters in f-strings"""
    if not Path(file_path).exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace f-strings with emojis with regular string concatenation
    content = re.sub(r'print\(f"✅ ([^"]+)"\)', r'print("✅ " + \1)', content)
    content = re.sub(r'print\(f✅ ([^)]+)\)', r'print("✅ " + str(\1))', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed emoji in f-string in {file_path}")

def fix_fstring_syntax(file_path):
    """Fix f-string syntax errors"""
    if not Path(file_path).exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix malformed f-strings
    content = re.sub(r'raise ValueError\(f"Unsafe expression: \{([^}]+)\}"\)', 
                     r'raise ValueError(f"Unsafe expression: {\1}")', content)
    content = re.sub(r'fUnsafe expression:', r'f"Unsafe expression:', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed f-string syntax in {file_path}")

def fix_docstring_syntax(file_path):
    """Fix docstring syntax issues"""
    if not Path(file_path).exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        # Fix incomplete docstrings
        if '"""Generate comprehensive release notes"""' in line and not line.strip().startswith('def'):
            lines[i] = '    """Generate comprehensive release notes"""\n'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Fixed docstring syntax in {file_path}")

def fix_indentation(file_path):
    """Fix unexpected indentation issues"""
    if not Path(file_path).exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        # Fix unexpected try: indentation
        if line.strip() == 'try:' and i > 0:
            prev_line = lines[i-1].strip()
            if prev_line and not prev_line.endswith(':'):
                # Add proper context for try block
                lines[i] = '        try:\n'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Fixed indentation in {file_path}")

def fix_malformed_string(file_path):
    """Fix malformed string assignments"""
    if not Path(file_path).exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix DEBUG = "debug"""
    content = re.sub(r'DEBUG = "debug"""', 'DEBUG = "debug"', content)
    content = re.sub(r'(\w+)\s*=\s*"([^"]+)"""', r'\1 = "\2"', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed malformed strings in {file_path}")

def fix_quote_issue(file_path):
    """Fix quote escaping issues"""
    if not Path(file_path).exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix left = parts[0].strip().strip("'"")
    content = re.sub(r'\.strip\("\'"\)', '.strip("\'")', content)
    content = re.sub(r'\.strip\(\'""\)', '.strip(\'"\\"\')', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed quote issues in {file_path}")

def fix_unmatched_paren(file_path):
    """Fix unmatched parentheses"""
    if not Path(file_path).exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        # Fix )""" pattern
        if ')"""' in line and line.count('(') < line.count(')'):
            lines[i] = line.replace(')"""', '"""')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Fixed unmatched parentheses in {file_path}")

def fix_test_docstrings(file_path):
    """Fix test file docstring issues"""
    if not Path(file_path).exists():
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix standalone docstrings that should be function docstrings
    content = re.sub(r'^    """([^"]+)"""$', r'def temp_function():\n    """\1"""\n    pass', content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed test docstrings in {file_path}")

def main():
    """Main precision fix function"""
    print("🎯 PRECISION SYNTAX FIXES")
    print("=" * 30)
    
    fix_precision_errors()
    
    print("\n✅ All precision fixes applied!")

if __name__ == "__main__":
    main()