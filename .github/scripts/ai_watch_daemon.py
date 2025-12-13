#!/usr/bin/env python3
"""
AI Analysis Watch Daemon - Background service for continuous analysis
Automatically analyzes Python files on save and outputs VS Code diagnostics
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Set

# Load environment variables from .env file
PROJECT_ROOT = Path(__file__).parent.parent.parent
try:
    from dotenv import load_dotenv
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    # dotenv not installed, try to load .env manually
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create dummy classes for graceful degradation
    class FileSystemEventHandler:
        pass
    class Observer:
        def __init__(self, *args, **kwargs):
            pass
        def schedule(self, *args, **kwargs):
            pass
        def start(self):
            pass
        def stop(self):
            pass
        def join(self):
            pass

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / ".github" / "scripts"))

from cursor_ai_diagnostics import BulletproofAIDiagnostics


class AIAnalysisHandler(FileSystemEventHandler):
    """Auto-analyze files on save"""
    
    def __init__(self, project_root: Path):
        self.analyzer = BulletproofAIDiagnostics()
        self.processing: Set[str] = set()
        self.cooldown: dict[str, float] = {}
        self.project_root = project_root
        self.cooldown_seconds = 3  # Don't analyze same file twice within 3 seconds
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.py'):
            return
        
        # Skip hidden files and __pycache__
        if any(part.startswith('.') or part == '__pycache__' for part in Path(event.src_path).parts):
            return
        
        # Debounce: don't analyze same file twice within cooldown period
        now = time.time()
        if event.src_path in self.cooldown:
            if now - self.cooldown[event.src_path] < self.cooldown_seconds:
                return
        
        self.cooldown[event.src_path] = now
        
        if event.src_path not in self.processing:
            self.processing.add(event.src_path)
            asyncio.create_task(self._analyze_file(event.src_path))
    
    async def _analyze_file(self, file_path: str):
        """Analyze file and output diagnostics"""
        try:
            # Read file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}", file=sys.stderr, flush=True)
                return
            
            # Analyze
            diagnostics = await self.analyzer.analyze_code(file_path, code)
            
            # Output to stdout for VS Code problem matcher
            severity_names = {1: "error", 2: "warning", 3: "info", 4: "hint"}
            
            for diag in diagnostics:
                severity = severity_names.get(diag["severity"], "warning")
                line = diag["line"] + 1  # Convert to 1-indexed
                col = diag["column"] + 1
                msg = diag["message"].replace('\n', ' ').replace('\r', '')
                
                # VS Code problem matcher format
                print(f"{file_path}:{line}:{col}: {severity}: {msg}", flush=True)
            
            # Summary
            if diagnostics:
                error_count = sum(1 for d in diagnostics if d["severity"] == 1)
                warning_count = sum(1 for d in diagnostics if d["severity"] == 2)
                file_name = Path(file_path).name
                
                if error_count > 0:
                    print(f"🔴 {file_name}: {error_count} error(s), {warning_count} warning(s)", flush=True)
                elif warning_count > 0:
                    print(f"🟡 {file_name}: {warning_count} warning(s)", flush=True)
            else:
                file_name = Path(file_path).name
                print(f"✅ {file_name}: No issues found", flush=True)
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}", file=sys.stderr, flush=True)
        finally:
            self.processing.discard(file_path)


async def main():
    """Start watch daemon"""
    if not WATCHDOG_AVAILABLE:
        print("❌ Error: watchdog not installed. Install with: pip install watchdog", file=sys.stderr, flush=True)
        print("   Watch mode requires watchdog for file system monitoring.", file=sys.stderr, flush=True)
        sys.exit(1)
    
    print("🔄 Bulletproof AI Watch Daemon Starting...", flush=True)
    print(f"📁 Watching: {PROJECT_ROOT / 'src'}", flush=True)
    print("💡 AI analysis will run automatically on file save", flush=True)
    print("⏹️  Press Ctrl+C to stop\n", flush=True)
    
    handler = AIAnalysisHandler(PROJECT_ROOT)
    observer = Observer()
    
    # Watch src directory recursively
    src_path = PROJECT_ROOT / 'src'
    if src_path.exists():
        observer.schedule(handler, str(src_path), recursive=True)
    else:
        print(f"Warning: {src_path} does not exist, watching project root", file=sys.stderr, flush=True)
        observer.schedule(handler, str(PROJECT_ROOT), recursive=True)
    
    observer.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Stopping AI Watch Daemon...", flush=True)
        observer.stop()
    
    observer.join()
    print("✅ AI Watch Daemon stopped", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Exiting...", flush=True)
        sys.exit(0)

