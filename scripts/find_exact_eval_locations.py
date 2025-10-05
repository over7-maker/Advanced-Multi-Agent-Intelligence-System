
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
        return expr[1:-1]
    if expr.startswith("'") and expr.endswith("'"):
        return expr[1:-1]
    
    # Boolean evaluation
    if expr.lower() in ['true', 'false']:
        return expr.lower() == 'true'
    
    # Default return
    return str(expression)

#!/usr/bin/env python3
"""
Find exact safe_eval_replacement() locations for targeted fixing
"""
import re
from pathlib import Path

def find_exact_eval_calls():
    """Find exact eval() function calls with context"""
    print("🔍 Locating all safe_eval_replacement() function calls...")
    
    eval_locations = []
    for file_path in Path('.').rglob('*.py'):
        if '.git' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                
                # Find actual eval( calls
                if re.search(r'\beval\s*\(', line):
                    # Exclude safe_eval
                    if 'safe_eval(' not in line and 'def safe_eval(' not in line:
                        # Exclude string literals
                        if not ('"eval(' in line or "'eval(" in line or '"""' in line):
                            eval_locations.append({
                                'file': str(file_path),
                                'line': i,
                                'code': line.strip()
                            })
                            
        except Exception:
            continue
    
    print(f"📍 Found {len(eval_locations)} safe_eval_replacement() calls:")
    for loc in eval_locations:
        print(f"   {loc['file']}:{loc['line']} -> {loc['code']}")
    
    return eval_locations

if __name__ == "__main__":
    find_exact_eval_calls()
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

