#!/usr/bin/env python3
"""
Backend API v4 - Production Launcher

This script properly initializes the Windows SelectorEventLoop BEFORE uvicorn starts.

Usage:
    python run_backend_api.py

Environment Variables (optional):
    API_HOST=0.0.0.0
    API_PORT=5814
    LOG_LEVEL=INFO
"""

import sys
import os
import asyncio
import selectors


def get_event_loop_factory():
    """
    Returns the correct event loop factory for the platform.
    On Windows: SelectorEventLoop (compatible with psycopg3)
    On Unix: Default event loop
    """
    if sys.platform == "win32":
        print("[INIT] Windows detected - Using SelectorEventLoop factory...")
        return lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
    else:
        print("[INIT] Unix detected - Using default event loop...")
        return None


async def main():
    """
    Main entry point - runs uvicorn server.
    """
    import uvicorn
    
    # Configuration from environment or defaults
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "5814"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print("\n" + "="*70)
    print("Backend API v4 - Production Server")
    print("="*70)
    print(f"Host: {api_host}")
    print(f"Port: {api_port}")
    print(f"Log Level: {log_level}")
    print(f"Platform: {sys.platform}")
    if sys.platform == "win32":
        print(f"Event Loop: SelectorEventLoop (Windows compatible)")
    print("="*70 + "\n")
    
    # Create and run server
    config = uvicorn.Config(
        "redirector.backend_api_v4:app",
        host=api_host,
        port=api_port,
        workers=1,
        reload=False,
        log_level=log_level,
    )
    
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    # Get the correct event loop factory
    loop_factory = get_event_loop_factory()
    
    # Run with the correct event loop
    if loop_factory:
        # Windows: use SelectorEventLoop
        print("[INIT] SelectorEventLoop factory set successfully\n")
        asyncio.run(main(), loop_factory=loop_factory)
    else:
        # Unix: use default
        print("[INIT] Using default event loop\n")
        asyncio.run(main())
