#!/usr/bin/env python3
"""
Kill process using port 8000
"""

import socket
import subprocess
import os
import signal

def kill_port(port):
    """Kill process using specified port"""
    try:
        # Try using netstat
        result = subprocess.run(
            ['netstat', '-tlnp'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTEN' in line:
                parts = line.split()
                if len(parts) > 6:
                    pid_program = parts[6]
                    if '/' in pid_program:
                        pid = pid_program.split('/')[0]
                        if pid.isdigit():
                            print(f"Found process on port {port}: PID {pid}")
                            try:
                                os.kill(int(pid), signal.SIGTERM)
                                print(f"✅ Killed process {pid}")
                                return True
                            except ProcessLookupError:
                                print(f"Process {pid} already dead")
                            except PermissionError:
                                print(f"Permission denied to kill {pid}")
        
        # Try pgrep for uvicorn
        result = subprocess.run(
            ['pgrep', '-f', 'uvicorn'],
            capture_output=True,
            text=True
        )
        
        pids = [p for p in result.stdout.strip().split('\n') if p]
        if pids:
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ Killed uvicorn process {pid}")
                except:
                    pass
            return True
        
        print(f"✅ No process found on port {port}")
        return True
        
    except FileNotFoundError:
        # netstat/pgrep not available, try socket approach
        print("System tools not available, trying socket approach...")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', port))
            s.close()
            print(f"✅ Port {port} is free")
            return True
        except OSError:
            print(f"⚠️  Port {port} is in use, but cannot kill process")
            print(f"   Try using a different port: uvicorn main:app --port 8001")
            return False

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    kill_port(port)

