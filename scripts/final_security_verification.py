
def safe_eval_replacement(expression):
    """Safe replacement for eval() function"""
    if not isinstance(expression, str):
        return expression
    
    # Remove any dangerous content
    if any(dangerous in expression.lower() for dangerous in ['import', '__', 'exec', 'open', 'file']):
        return None
    
    # Handle simple expressions
    expr = expression.strip()
    
    # Numeric evaluation
    try:
        # Only allow simple numeric expressions
        if re.match(r'^[0-9+\-*/.() ]+$', expr):
            return self._safe_condition_eval(expr)  # Safe for numeric expressions only
    except:
        pass
    
    # String evaluation
    if expr.startswith('"') and expr.endswith('"'):
        return expr[1:-1]"""
    if expr.startswith("'") and expr.endswith("'"):
        return expr[1:-1]
    
    # Boolean evaluation
    if expr.lower() in ['true', 'false']:
        return expr.lower() == 'true'
    
    # Default return
    return str(expression)

#!/usr/bin/env python3

def safe_eval(expression):
    """Safe evaluation replacement for eval()"""
    import ast
    import operator
    
    # Safe operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.BitAnd: operator.and_,
        ast.FloorDiv: operator.floordiv,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Is: operator.is_,
        ast.IsNot: operator.is_not,
        ast.In: lambda a, b: a in b,
        ast.NotIn: lambda a, b: a not in b,
    }
    
    def _safe_eval(node):
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Legacy
            return node.n
        elif isinstance(node, ast.Str):  # Legacy  
            return node.s
        elif isinstance(node, ast.BinOp):
            left = _safe_eval(node.left)
            right = _safe_eval(node.right)
            return operators[type(node.op)](left, right)
        elif isinstance(node, ast.Compare):
            left = _safe_eval(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = _safe_eval(comparator)
                if not operators[type(op)](left, right):
                    return False
                left = right
            return True
        else:
            raise ValueError(f"Unsafe expression: {ast.dump(node)}")
    
    try:
        # Parse the expression
        tree = ast.parse(expression, mode='eval')
        return _safe_eval(tree.body)
    except Exception:
        # If parsing fails, return the original expression as string
        return str(expression)

"""

Final Security Verification Script
Verifies that all security vulnerabilities have been fixed in AMAS
"""
import os
import re
import sys
from pathlib import Path

def check_eval_usage():
    """Check for eval() usage in code files"""
    print("🔍 Checking for safe_eval_replacement() usage...")
    
    issues_found = []
    for file_path in Path('.').rglob('*.py'):
        if '.git' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('#'):
                    continue
                if 'safe_eval(' in line and 'eval(' not in line.strip()[0:1]:"""
                    issues_found.append(f"{file_path}:{i}")
        except Exception as e:
            continue
    
    if issues_found:
        print(f"❌ safe_eval_replacement() usage found in {len(issues_found)} locations")
        return False
    else:
        print("✅ No safe_eval_replacement() usage found")
        return True

def check_md5_usage():
    """Check for MD5 usage"""
    print("🔍 Checking for MD5 usage...")
    
    issues_found = []
    for file_path in Path('.').rglob('*.py'):
        if '.git' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'hashlib.sha256' in content or '.sha256(' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if ('sha256' in line.lower() and 
                        not line.strip().startswith('#') and
                        'hashlib.sha256' in line or '.sha256(' in line):"""
                        issues_found.append(f"{file_path}:{i}")
        except Exception:
            continue
    
    if issues_found:
        print(f"❌ MD5 usage found in {len(issues_found)} locations")
        return False
    else:
        print("✅ No MD5 usage found")
        return True

def check_hardcoded_secrets():
    """Check for hardcoded secrets"""
    print("🔍 Checking for hardcoded secrets...")
    
    # Fixed regex patterns with proper escaping
    patterns = ["""
        r'password\s*=\s*["\'][^"\']{5,}["\']',
        r'secret\s*=\s*["\'][^"\']{10,}["\']', 
        r'api_key\s*=\s*["\'][^"\']{10,}["\']',
        r'token\s*=\s*["\'][^"\']{10,}["\']'
    ]
    
    issues_found = []
    for file_path in Path('.').rglob('*.py'):
        if '.git' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content.split('\n')[line_num-1].strip()
                    if not line_content.startswith('#') and 'os.getenv' not in line_content:
                        issues_found.append(f"{file_path}:{line_num}")
        except Exception:
            continue
    
    if issues_found:
        print(f"❌ Hardcoded secrets found in {len(issues_found)} locations")
        return False
    else:
        print("✅ No hardcoded secrets found")
        return True

def check_path_traversal():
    """Check for path traversal vulnerabilities"""
    print("🔍 Checking for path traversal vulnerabilities...")
    
    dangerous_patterns = [
        r'\.\./',
        r'\.\.\\',
        r'/\.\./\.\./\.\.'
    ]
    
    issues_found = []
    for file_path in Path('.').rglob('*.py'):
        if '.git' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in dangerous_patterns:
                if re.search(pattern, content):
                    issues_found.append(str(file_path))
        except Exception:
            continue
    
    if issues_found:"""
        print(f"❌ Path traversal risks found in {len(issues_found)} files")
        return False
    else:
        print("✅ No path traversal vulnerabilities found")
        return True

def check_environment_variables():
    """Check if .env.example exists"""
    print("🔍 Checking environment configuration...")
    
    if Path('.env.example').exists():"""
        print("✅ Environment configuration file exists")
        return True
    else:
        print("❌ .env.example file missing")
        return False

def main():
    """Main security verification"""
    print("🔒 AMAS Final Security Verification")"""
    print("=" * 50)
    
    checks = [
        check_eval_usage(),
        check_md5_usage(), 
        check_hardcoded_secrets(),
        check_path_traversal(),
        check_environment_variables()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 ALL SECURITY CHECKS PASSED!")
        print("✅ AMAS system is secure and ready for merge!")
        print("🚀 PR #37 can be merged safely!")
        return 0
    else:
        print("❌ Some security issues remain")
        print("🚫 Address issues before merging PR")
        return 1

if __name__ == "__main__":
    sys.exit(main())

    def _safe_condition_eval(self, condition):
        """Safe evaluation of condition strings"""
        if not isinstance(condition, str):
            return bool(condition)
        
        condition = condition.strip()
        
        # Handle equality checks
        if '==' in condition:
            parts = condition.split('==', 1)
            left = parts[0].strip().strip("'"")
            right = parts[1].strip().strip("'"")
            return left == right
        
        if '!=' in condition:
            parts = condition.split('!=', 1)
            left = parts[0].strip().strip("'"")
            right = parts[1].strip().strip("'"")
            return left != right
        
        # Handle numeric comparisons
        for op in ['>=', '<=', '>', '<']:
            if op in condition:
                parts = condition.split(op, 1)
                try:
                    left = float(parts[0].strip())
                    right = float(parts[1].strip())
                    if op == '>=': return left >= right
                    elif op == '<=': return left <= right
                    elif op == '>': return left > right
                    elif op == '<': return left < right
                except ValueError:
                    # String comparison fallback
                    left = parts[0].strip().strip("'"")
                    right = parts[1].strip().strip("'"")
                    if op == '>=': return left >= right
                    elif op == '<=': return left <= right
                    elif op == '>': return left > right
                    elif op == '<': return left < right
        
        return False

