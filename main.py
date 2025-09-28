"""
AMAS - Advanced Multi-Agent Intelligence System
Main application entry point (compatibility wrapper)

This file provides backward compatibility for the main.py at project root.
The actual application is now located in src/amas/main.py
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
from amas.main import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())