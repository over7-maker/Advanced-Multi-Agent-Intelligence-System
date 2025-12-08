# API Path Fix - /auth/me → /me

## ✅ Issue Fixed

**Problem**: Frontend was calling `/api/v1/auth/me` but backend route is `/api/v1/me`

**Root Cause**: 
- Backend auth router is registered with prefix `/api/v1` in `main.py`
- Routes in `auth.py` are: `/login`, `/logout`, `/me` (no `/auth` prefix)
- Frontend was using `/auth/login`, `/auth/logout`, `/auth/me` (incorrect)

**Solution**: Changed all auth paths in frontend to remove `/auth` prefix

## Changes Made

### `frontend/src/services/api.ts`

**Before:**
```typescript
async login(...) {
  await this.client.post('/auth/login', ...);
}

async logout() {
  await this.client.post('/auth/logout');
}

async getCurrentUser() {
  await this.client.get('/auth/me');
}
```

**After:**
```typescript
async login(...) {
  await this.client.post('/login', ...);
}

async logout() {
  await this.client.post('/logout');
}

async getCurrentUser() {
  await this.client.get('/me');
}
```

## Backend Routes (Reference)

**File**: `src/api/routes/auth.py`
- `@router.post("/login")` → `/api/v1/login`
- `@router.post("/logout")` → `/api/v1/logout`
- `@router.get("/me")` → `/api/v1/me`

**Registration**: `main.py`
```python
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
```

## Result

✅ Frontend now calls correct paths:
- `/api/v1/login` ✅
- `/api/v1/logout` ✅
- `/api/v1/me` ✅

**No more 404 errors for `/api/v1/auth/me`!**

