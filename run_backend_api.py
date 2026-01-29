#!/usr/bin/env python3
"""
Backend API v4 - Production Launcher

This script properly initializes the Windows SelectorEventLoop BEFORE uvicorn starts.

Usage:
    python run_backend_api.py

Environment Variables (optional):
    API_HOST=0.0.0.0
    API_PORT=5814
    API_WORKERS=1
    LOG_LEVEL=INFO
"""

import sys
import os
import asyncio


# ═══════════════════════════════════════════════════════════════════════════
# CRITICAL: Set Windows Event Loop BEFORE any async imports or uvicorn start
# ═══════════════════════════════════════════════════════════════════════════

if sys.platform == "win32":
    print("[INIT] Windows detected - Setting SelectorEventLoop...")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("[INIT] SelectorEventLoop policy set successfully")


# ═══════════════════════════════════════════════════════════════════════════
# NOW SAFE to import uvicorn
# ═══════════════════════════════════════════════════════════════════════════

import uvicorn


if __name__ == "__main__":
    # Configuration from environment or defaults
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "5814"))
    api_workers = int(os.getenv("API_WORKERS", "1"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print("\n" + "="*70)
    print("Backend API v4 - Production Server")
    print("="*70)
    print(f"Host: {api_host}")
    print(f"Port: {api_port}")
    print(f"Workers: {api_workers}")
    print(f"Log Level: {log_level}")
    print(f"Platform: {sys.platform}")
    if sys.platform == "win32":
        print(f"Event Loop: SelectorEventLoop (Windows compatible)")
    print("="*70 + "\n")
    
    # Run uvicorn
    uvicorn.run(
        "redirector.backend_api_v4:app",
        host=api_host,
        port=api_port,
        workers=api_workers,
        reload=False,
        log_level=log_level,
    )
