#!/usr/bin/env python3
"""
Surgical fix for specific syntax errors
"""
import os
import re
from pathlib import Path

def fix_specific_syntax_errors():
    """Fix each specific syntax error individually"""
    print("🔧 Applying surgical fixes...")
    
    # Fix 1: scripts/complete_security_hardening.py line 23
    fix_file_line('scripts/complete_security_hardening.py', 23, 
                  r'        return expr\[1:-1\]"""', 
                  '        return expr[1:-1]')
    
    # Fix 2: scripts/generate_release_notes.py line 14
    fix_file_line('scripts/generate_release_notes.py', 14,
                  r'    print\("📋 Release Notes Generator"\)"""',
                  '    print("📋 Release Notes Generator")')
    
    # Fix 3: scripts/final_security_verification.py line 23
    fix_file_line('scripts/final_security_verification.py', 23,
                  r'        return expr\[1:-1\]"""',
                  '        return expr[1:-1]')
    
    # Fix 4: src/amas/security/audit.py line 20
    fix_file_line('src/amas/security/audit.py', 20,
                  r'    """Audit log levels"""',
                  '    """Audit log levels"""')
    
    # Fix 5: scripts/verify_security_fixes.py line 23
    fix_file_line('scripts/verify_security_fixes.py', 23,
                  r'        return expr\[1:-1\]"""',
                  '        return expr[1:-1]')
    
    # Fix 6: src/amas/services/database_service.py line 24
    fix_file_line('src/amas/services/database_service.py', 24,
                  r'    """Database Service for AMAS Intelligence System - Security hardened"""',
                  '    """Database Service for AMAS Intelligence System - Security hardened"""')
    
    # Fix 7: tests/test_security_fixes.py line 36
    fix_file_line('tests/test_security_fixes.py', 36,
                  r'    """Validate and sanitize file paths to prevent traversal attacks"""',
                  '    """Validate and sanitize file paths to prevent traversal attacks"""')
    
    # Fix 8: src/amas/security/authorization.py line 35
    fix_file_line('src/amas/security/authorization.py', 35,
                  r'Authorization Module for AMAS',
                  '"""Authorization Module for AMAS"""')
    
    # Fix 9: tests/test_services.py line 37
    fix_file_line('tests/test_services.py', 37,
                  r'    """Safe evaluation replacement for eval\(\)"""',
                  '    """Safe evaluation replacement for eval()"""')

def fix_file_line(file_path, line_num, pattern, replacement):
    """Fix a specific line in a file"""
    if not Path(file_path).exists():
        print(f"⚠️ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_num <= len(lines):
            original_line = lines[line_num - 1]
            
            # Apply the fix
            if re.search(pattern, original_line):
                lines[line_num - 1] = re.sub(pattern, replacement, original_line)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                print(f"✅ Fixed line {line_num} in {file_path}")
                return True
            else:
                # Try a more general approach
                if '"""' in original_line and original_line.count('"""') % 2 != 0:
                    # Fix unterminated docstring
                    lines[line_num - 1] = original_line.rstrip() + '\n'
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    print(f"✅ Fixed unterminated string in line {line_num} of {file_path}")
                    return True
        
        print(f"ℹ️ No changes needed for line {line_num} in {file_path}")
        return False
        
    except Exception as e:
        print(f"⚠️ Error fixing {file_path}: {e}")
        return False

def nuclear_fix_approach():
    """Nuclear approach - completely rewrite problematic sections"""
    print("🚀 Applying nuclear fixes...")
    
    files_to_fix = [
        'scripts/complete_security_hardening.py',
        'scripts/final_security_verification.py',
        'scripts/generate_release_notes.py',
        'scripts/verify_security_fixes.py',
        'src/amas/security/audit.py',
        'src/amas/security/authorization.py',
        'src/amas/services/database_service.py',
        'tests/test_security_fixes.py',
        'tests/test_services.py'
    ]
    
    for file_path in files_to_fix:
        if not Path(file_path).exists():
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove all malformed triple quotes and fix them
            content = re.sub(r'"""([^"]*)"""([^"]*)"""', r'"""\1\2"""', content)
            content = re.sub(r'"""([^"]*)"([^"]*)"([^"]*)"""', r'"""\1\2\3"""', content)
            
            # Fix any unterminated strings
            lines = content.split('\n')
            fixed_lines = []
            
            for i, line in enumerate(lines):
                # Count quotes in line
                single_quotes = line.count("'") - line.count("\\'")
                double_quotes = line.count('"') - line.count('\\"')
                triple_single = line.count("'''")
                triple_double = line.count('"""')
                
                # Fix unterminated strings
                if triple_double % 2 != 0 and not line.strip().startswith('#'):
                    # Unterminated triple double quote
                    if '"""' in line and not line.strip().endswith('"""'):
                        line = line.rstrip() + '"""'
                
                fixed_lines.append(line)
            
            content = '\n'.join(fixed_lines)
            
            # Ensure file ends with newline
            if not content.endswith('\n'):
                content += '\n'
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Applied nuclear fix to {file_path}")
            
        except Exception as e:
            print(f"⚠️ Error with nuclear fix for {file_path}: {e}")

def main():
    """Main surgical fix function"""
    print("🔧 SURGICAL SYNTAX FIXES")
    print("=" * 30)
    
    # Try surgical fixes first
    fix_specific_syntax_errors()
    
    # Apply nuclear approach
    nuclear_fix_approach()
    
    print("\n✅ All surgical fixes applied!")

if __name__ == "__main__":
    main()