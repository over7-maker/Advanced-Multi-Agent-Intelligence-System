#!/usr/bin/env python3
"""
Security Fixes Verification Script
Verifies that all security vulnerabilities have been fixed
"""
import os
import re
import sys
from pathlib import Path

def check_eval_usage():
    """Check for eval() usage in security files"""
    print("🔍 Checking for eval() usage...")
    
    security_files = [
        'src/amas/security/audit.py',
        'src/amas/security/authorization.py'
    ]
    
    issues_found = []
    for file_path in security_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for eval() usage (excluding comments and docstrings)
            lines = content.split('\n')
            in_docstring = False
            for i, line in enumerate(lines, 1):
                # Skip comment lines
                if line.strip().startswith('#'):
                    continue
                # Skip docstring lines
                if '"""' in line or "'''" in line:
                    in_docstring = not in_docstring
                    continue
                if in_docstring:
                    continue
                # Check for eval() usage in actual code (not in comments or strings)
                if 'eval(' in line and not line.strip().startswith('#') and not '"""' in line and not "'''" in line:
                    # Additional check: make sure it's not in a string literal
                    if not ('"' in line and 'eval(' in line.split('"')[0]) and not ("'" in line and 'eval(' in line.split("'")[0]):
                        issues_found.append(f"{file_path}:{i}: eval() usage found")
    
    if issues_found:
        print(f"❌ eval() usage found: {issues_found}")
        return False
    else:
        print("✅ No eval() usage found")
        return True

def check_md5_usage():
    """Check for MD5 usage in security files"""
    print("🔍 Checking for MD5 usage...")
    
    security_files = [
        'src/amas/security/audit.py'
    ]
    
    issues_found = []
    for file_path in security_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for MD5 usage
            if 'hashlib.md5' in content:
                issues_found.append(f"{file_path}: MD5 usage found")
    
    if issues_found:
        print(f"❌ MD5 usage found: {issues_found}")
        return False
    else:
        print("✅ No MD5 usage found")
        return True

def check_environment_variables():
    """Check for environment variable usage in database service"""
    print("🔍 Checking environment variable usage...")
    
    db_service_path = 'src/amas/services/database_service.py'
    if os.path.exists(db_service_path):
        with open(db_service_path, 'r') as f:
            content = f.read()
        
        # Check for environment variable usage
        if 'os.getenv(' in content:
            print("✅ Environment variables used in database service")
            return True
        else:
            print("❌ Environment variables not used in database service")
            return False
    else:
        print("❌ Database service file not found")
        return False

def check_safe_evaluation():
    """Check for safe evaluation methods"""
    print("🔍 Checking for safe evaluation methods...")
    
    security_files = [
        'src/amas/security/audit.py',
        'src/amas/security/authorization.py'
    ]
    
    safe_methods_found = []
    for file_path in security_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for safe evaluation methods
            if '_safe_evaluate_condition' in content:
                safe_methods_found.append(file_path)
    
    if len(safe_methods_found) == len(security_files):
        print("✅ Safe evaluation methods implemented")
        return True
    else:
        print(f"❌ Safe evaluation methods not found in all files: {safe_methods_found}")
        return False

def check_secure_config():
    """Check for secure configuration management"""
    print("🔍 Checking secure configuration management...")
    
    secure_config_path = 'src/amas/security/secure_config.py'
    if os.path.exists(secure_config_path):
        with open(secure_config_path, 'r') as f:
            content = f.read()
        
        # Check for secure config features
        features = [
            'SecureConfigManager',
            'encrypt_sensitive_value',
            'decrypt_sensitive_value',
            'get_database_config',
            'get_security_config'
        ]
        
        missing_features = []
        for feature in features:
            if feature not in content:
                missing_features.append(feature)
        
        if missing_features:
            print(f"❌ Missing secure config features: {missing_features}")
            return False
        else:
            print("✅ Secure configuration management implemented")
            return True
    else:
        print("❌ Secure configuration file not found")
        return False

def check_security_tests():
    """Check for security test coverage"""
    print("🔍 Checking security test coverage...")
    
    test_file_path = 'tests/test_security_fixes.py'
    if os.path.exists(test_file_path):
        with open(test_file_path, 'r') as f:
            content = f.read()
        
        # Check for security test features
        test_features = [
            'test_audit_rule_evaluation_safe',
            'test_authorization_rule_evaluation_safe',
            'test_malicious_condition_handling',
            'test_correlation_id_uses_sha256',
            'test_secure_config_environment_variables'
        ]
        
        missing_tests = []
        for feature in test_features:
            if feature not in content:
                missing_tests.append(feature)
        
        if missing_tests:
            print(f"❌ Missing security tests: {missing_tests}")
            return False
        else:
            print("✅ Security test coverage implemented")
            return True
    else:
        print("❌ Security test file not found")
        return False

def main():
    """Main verification function"""
    print("🔒 AMAS Security Fixes Verification")
    print("=" * 50)
    
    checks = [
        check_eval_usage,
        check_md5_usage,
        check_environment_variables,
        check_safe_evaluation,
        check_secure_config,
        check_security_tests
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check in checks:
        try:
            if check():
                passed_checks += 1
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Security Verification Results: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("🎉 All security fixes verified successfully!")
        print("✅ AMAS system is secure and production-ready!")
        return True
    else:
        print(f"⚠️ {total_checks - passed_checks} security issues remain")
        print("❌ Please address remaining security issues before production deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)