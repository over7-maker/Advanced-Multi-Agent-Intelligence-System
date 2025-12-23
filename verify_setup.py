#!/usr/bin/env python3
"""Verify that all setup is correct for frontend and backend"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

print("=" * 60)
print("AMAS Setup Verification")
print("=" * 60)
print()

errors = []
warnings = []

# Check 1: Frontend dist exists
print("1. Checking frontend build...")
frontend_dist = Path("frontend/dist/index.html")
if frontend_dist.exists():
    print(f"   [OK] Frontend dist exists: {frontend_dist.resolve()}")
else:
    errors.append(f"Frontend dist not found: {frontend_dist}")
    print(f"   [ERROR] Frontend dist NOT found: {frontend_dist}")

# Check 2: Frontend assets exist
print("\n2. Checking frontend assets...")
frontend_assets = Path("frontend/dist/assets")
if frontend_assets.exists():
    asset_files = list(frontend_assets.glob("*.js"))
    print(f"   [OK] Frontend assets exist: {len(asset_files)} JS files")
else:
    warnings.append("Frontend assets directory not found")
    print(f"   [WARN] Frontend assets directory not found")

# Check 3: API routes can be imported
print("\n3. Checking API routes...")
try:
    from src.api.routes import agents, tasks, health, auth
    print("   [OK] API routes can be imported")
    print(f"   - Agents router: {len(agents.router.routes)} routes")
    print(f"   - Tasks router: {len(tasks.router.routes)} routes")
    print(f"   - Health router: {len(health.router.routes)} routes")
    print(f"   - Auth router: {len(auth.router.routes)} routes")
except Exception as e:
    errors.append(f"Cannot import API routes: {e}")
    print(f"   [ERROR] Cannot import API routes: {e}")

# Check 4: Main app can be created
print("\n4. Checking main app...")
try:
    import os
    os.environ["ENVIRONMENT"] = "development"
    from main import app
    print("   [OK] Main app can be created")
    
    # Count routes
    all_routes = [r for r in app.routes if hasattr(r, "path")]
    api_routes = [r for r in all_routes if hasattr(r, "path") and "/api/v1" in r.path]
    print(f"   - Total routes: {len(all_routes)}")
    print(f"   - API v1 routes: {len(api_routes)}")
except Exception as e:
    errors.append(f"Cannot create main app: {e}")
    print(f"   [ERROR] Cannot create main app: {e}")

# Check 5: Environment variable
print("\n5. Checking environment...")
import os
env = os.getenv("ENVIRONMENT", "not set")
if env.lower() in ["development", "dev", "test"]:
    print(f"   [OK] ENVIRONMENT is set to: {env}")
else:
    warnings.append(f"ENVIRONMENT is '{env}', should be 'development' for dev mode")
    print(f"   [WARN] ENVIRONMENT is '{env}' (should be 'development' for dev mode)")

# Summary
print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

if errors:
    print(f"\n[ERROR] ERRORS ({len(errors)}):")
    for error in errors:
        print(f"  - {error}")
    print("\n[FAIL] Setup has ERRORS. Please fix them before starting the server.")
    sys.exit(1)
elif warnings:
    print(f"\n[WARN] WARNINGS ({len(warnings)}):")
    for warning in warnings:
        print(f"  - {warning}")
    print("\n[OK] Setup is mostly OK, but has warnings.")
    sys.exit(0)
else:
    print("\n[SUCCESS] All checks passed! Setup is correct.")
    print("\nYou can now start the server with:")
    print("  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    print("\nOr use the restart script:")
    print("  restart_server.bat")
    sys.exit(0)

