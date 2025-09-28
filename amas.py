#!/usr/bin/env python3
"""
AMAS CLI Entry Point

This script provides a convenient entry point for AMAS CLI operations
without requiring package installation.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from amas.cli import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error: Could not import AMAS modules: {e}")
    print("Please ensure you have installed the requirements:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)