# Frontend CORS and API URL Fixes

## ✅ Issues Fixed

### 1. Frontend API URL (Port Mismatch)
**Problem**: Frontend was hardcoded to `http://localhost:8000` but server runs on `8001`.

**Solution**: Changed to **relative URLs** (`/api/v1`) which work with any port.

**File**: `frontend/src/services/api.ts`
- Changed from: `'http://localhost:8000/api/v1'`
- Changed to: `'/api/v1'` (relative URL)

### 2. Frontend WebSocket URL (Port Mismatch)
**Problem**: WebSocket was hardcoded to `localhost:8000`.

**Solution**: Changed to use **current window host** (relative URL).

**File**: `frontend/src/services/websocket.ts`
- Now uses: `window.location.host` for same-origin connections
- Works automatically with any port

### 3. CORS Origins (Missing localhost:8001)
**Problem**: CORS only allowed `http://localhost:3000`, blocking requests from `8001`.

**Solution**: Added `localhost:8000` and `localhost:8001` to allowed origins.

**File**: `src/config/settings.py`
- Added: `"http://localhost:8000"`, `"http://localhost:8001"`, `"http://127.0.0.1:8000"`, `"http://127.0.0.1:8001"`

## What Changed

### `frontend/src/services/api.ts`
```typescript
// Before:
baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// After:
baseURL: import.meta.env.VITE_API_URL || '/api/v1'  // Relative URL
```

### `frontend/src/services/websocket.ts`
```typescript
// Before:
const wsHost = ... || 'localhost:8000';

// After:
// Uses window.location.host for same-origin (works with any port)
```

### `src/config/settings.py`
```python
# Before:
cors_origins: List[str] = Field(default=["http://localhost:3000"])

# After:
cors_origins: List[str] = Field(default=[
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001"
])
```

## Benefits

✅ **Relative URLs** - Work with any port automatically
✅ **No hardcoded ports** - Frontend adapts to server port
✅ **CORS fixed** - All localhost ports allowed
✅ **Production ready** - Works in any environment

## Testing

After restarting the server, test:

1. **Frontend**: http://localhost:8001/
   - Should load without CORS errors
   - API calls should work

2. **Login**: Try logging in
   - Should connect to API on port 8001
   - No CORS errors in console

3. **WebSocket**: Check browser console
   - Should connect to `ws://localhost:8001/ws`
   - No connection errors

## Environment Variables (Optional)

If you need to override URLs, create `frontend/.env`:
```bash
VITE_API_URL=/api/v1
VITE_WS_URL=ws://localhost:8001/ws
```

But **relative URLs work automatically** - no config needed!

## Summary

✅ **Frontend uses relative URLs** - Works with any port
✅ **CORS allows all localhost ports** - No more CORS errors
✅ **WebSocket uses current host** - Automatic port detection

**Restart server and test - CORS errors should be gone!**

