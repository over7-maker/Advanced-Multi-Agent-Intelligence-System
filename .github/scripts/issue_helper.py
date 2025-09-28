#!/usr/bin/env python3
"""
Issue-specific helper for providing targeted solutions
"""
import re
import json
from typing import Dict, List

class IssueHelper:
    def __init__(self):
        self.patterns = {
            'import_error': [
                r'ImportError|ModuleNotFoundError|No module named',
                r'cannot import name',
                r'import.*failed'
            ],
            'type_error': [
                r'TypeError|type.*error',
                r'expected.*got',
                r'unsupported operand'
            ],
            'syntax_error': [
                r'SyntaxError|syntax',
                r'invalid syntax',
                r'unexpected.*token'
            ],
            'performance': [
                r'slow|performance|optimize',
                r'memory|RAM|heap',
                r'timeout|taking too long'
            ],
            'async': [
                r'async|await|asyncio',
                r'coroutine|concurrent',
                r'threading|multiprocessing'
            ],
            'database': [
                r'database|DB|SQL',
                r'query|queries',
                r'connection|cursor'
            ],
            'api': [
                r'API|REST|endpoint',
                r'request|response',
                r'authentication|auth'
            ]
        }
        
    def analyze_issue_text(self, text: str) -> Dict[str, List[str]]:
        """Analyze issue text and return specific solutions"""
        text_lower = text.lower()
        solutions = {}
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    solutions[category] = self.get_solutions(category)
                    break
                    
        return solutions
    
    def get_solutions(self, category: str) -> List[str]:
        """Get specific solutions for each category"""
        solutions_map = {
            'import_error': [
                "Check virtual environment: `which python` and `pip list`",
                "Install missing package: `pip install package-name`",
                "Add to PYTHONPATH: `export PYTHONPATH=$PYTHONPATH:/path/to/module`",
                "Check for circular imports",
                "Verify __init__.py files exist in package directories"
            ],
            'type_error': [
                "Add type hints: `def func(param: str) -> int:`",
                "Use isinstance() for type checking",
                "Convert types explicitly: `int(value)`, `str(value)`",
                "Check None values: `if value is not None:`",
                "Use mypy for static type checking: `mypy script.py`"
            ],
            'syntax_error': [
                "Check for missing colons after if/for/def/class",
                "Verify matching parentheses, brackets, and quotes",
                "Look for incorrect indentation (use 4 spaces)",
                "Remove trailing commas in single-element tuples",
                "Check for Python 2 vs 3 syntax differences"
            ],
            'performance': [
                "Profile code: `python -m cProfile -s cumulative script.py`",
                "Use generators instead of lists for large datasets",
                "Cache expensive operations with @lru_cache",
                "Use numpy for numerical operations",
                "Consider using multiprocessing for CPU-bound tasks"
            ],
            'async': [
                "Use asyncio.run() for main entry point",
                "Don't mix sync and async code without proper handling",
                "Use aiohttp for async HTTP requests",
                "Gather concurrent tasks: `await asyncio.gather(*tasks)`",
                "Debug with PYTHONASYNCIODEBUG=1 environment variable"
            ],
            'database': [
                "Use connection pooling for better performance",
                "Always use parameterized queries to prevent SQL injection",
                "Add indexes on frequently queried columns",
                "Use transactions for data consistency",
                "Enable query logging for debugging"
            ],
            'api': [
                "Add proper error handling for network requests",
                "Use requests.Session() for connection pooling",
                "Implement exponential backoff for retries",
                "Add timeout to all requests: `requests.get(url, timeout=30)`",
                "Log all API calls for debugging"
            ]
        }
        
        return solutions_map.get(category, ["Please provide more specific error details"])
    
    def generate_code_snippet(self, category: str) -> str:
        """Generate helpful code snippets for common issues"""
        snippets = {
            'import_error': '''# Debug import issues
import sys
print("Python path:", sys.path)
print("Python version:", sys.version)

# Try different import methods
try:
    import module_name
except ImportError as e:
    print(f"Import failed: {e}")
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
''',
            'type_error': '''# Type checking example
from typing import Optional, Union, List

def process_data(value: Union[str, int]) -> Optional[str]:
    """Process data with proper type handling"""
    if isinstance(value, str):
        return value.upper()
    elif isinstance(value, int):
        return str(value)
    return None

# Using TypedDict for complex structures
from typing import TypedDict

class UserData(TypedDict):
    name: str
    age: int
    email: Optional[str]
''',
            'performance': '''# Performance optimization patterns
from functools import lru_cache
import time

# Cache expensive operations
@lru_cache(maxsize=128)
def expensive_function(n: int) -> int:
    # Simulated expensive operation
    return n ** 2

# Use generators for memory efficiency
def read_large_file(filename: str):
    """Read file line by line without loading all into memory"""
    with open(filename) as f:
        for line in f:
            yield line.strip()

# Profile code execution
def profile_function(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.4f} seconds")
        return result
    return wrapper
''',
            'async': '''# Async/await patterns
import asyncio
import aiohttp

async def fetch_data(session: aiohttp.ClientSession, url: str) -> dict:
    """Fetch data asynchronously"""
    try:
        async with session.get(url, timeout=10) as response:
            return await response.json()
    except asyncio.TimeoutError:
        print(f"Timeout fetching {url}")
        return {}

async def main():
    urls = ["http://api1.com", "http://api2.com"]
    
    async with aiohttp.ClientSession() as session:
        # Fetch all URLs concurrently
        results = await asyncio.gather(
            *[fetch_data(session, url) for url in urls],
            return_exceptions=True
        )
    
    return results

# Run async code
if __name__ == "__main__":
    asyncio.run(main())
'''
        }
        
        return snippets.get(category, "# No specific code snippet available")

def main():
    """Main function for testing"""
    import sys
    
    if len(sys.argv) > 1:
        issue_text = ' '.join(sys.argv[1:])
        helper = IssueHelper()
        solutions = helper.analyze_issue_text(issue_text)
        
        print("## Detected Issue Categories and Solutions\n")
        
        for category, solution_list in solutions.items():
            print(f"### {category.replace('_', ' ').title()}\n")
            for i, solution in enumerate(solution_list, 1):
                print(f"{i}. {solution}")
            print()
            
            # Add code snippet
            snippet = helper.generate_code_snippet(category)
            if snippet:
                print("**Example Code:**")
                print("```python")
                print(snippet)
                print("```\n")
    else:
        print("Usage: python issue_helper.py <issue description>")

if __name__ == "__main__":
    main()