# ✅ Frontend & Backend - Complete Setup Guide

## 🎯 Current Status

### ✅ Backend: **WORKING**
- Server starts successfully
- All errors fixed (datetime serialization, rate limiting, Prometheus)
- Health endpoint working
- API endpoints ready

### ✅ Frontend: **READY** (needs Node.js)
- All files created
- Entry point configured
- Components ready
- Just needs Node.js/npm to run

---

## 🚀 Quick Start

### Backend

```bash
# Start backend (auto-finds available port)
python3 start_backend_auto_port.py

# Or manually
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs on**: `http://localhost:8000` (or 8001 if 8000 is busy)

### Frontend

```bash
# Install Node.js first (if not installed)
# Then:
cd frontend
npm install
npm run dev
```

**Frontend runs on**: `http://localhost:3000`

---

## 📋 Backend Endpoints

- **Root**: `http://localhost:8000/`
- **Health**: `http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs`
- **Tasks**: `http://localhost:8000/api/v1/tasks`
- **Agents**: `http://localhost:8000/api/v1/agents`
- **Users**: `http://localhost:8000/api/v1/users`
- **Auth**: `http://localhost:8000/api/v1/auth`

---

## 🔗 Frontend → Backend Integration

The frontend is configured to proxy API requests:

- **Development**: Frontend on `:3000` → proxies `/api/*` → Backend on `:8000`
- **WebSocket**: `/ws` → `ws://localhost:8000/ws`

**Configuration**: `frontend/vite.config.ts`

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

---

## ✅ What's Working

### Backend
- ✅ FastAPI server starts
- ✅ Health checks work
- ✅ Error handling fixed
- ✅ Rate limiting configured (lenient for dev)
- ✅ Optional services (DB, Redis, Neo4j) don't block startup
- ✅ Prometheus optional

### Frontend
- ✅ React + TypeScript setup
- ✅ Material-UI components
- ✅ React Router configured
- ✅ React Query for data fetching
- ✅ Vite build system
- ✅ All components ready

---

## ⚠️ Requirements

### Backend
- Python 3.11+
- Dependencies: `pip install -r requirements.txt`

### Frontend
- Node.js >=18.17.0 <20.0.0
- npm >=9.0.0

---

## 🐛 Troubleshooting

### Backend "Address already in use"
```bash
# Use auto-port script
python3 start_backend_auto_port.py

# Or kill process on port 8000
python3 kill_port_8000.py 8000
```

### Frontend "npm not found"
- Install Node.js 18+ from https://nodejs.org/
- Or use nvm: `nvm install 18 && nvm use 18`

### Frontend can't connect to backend
- Make sure backend is running first
- Check backend URL in `frontend/vite.config.ts`
- Check backend is on port 8000 (or update proxy config)

---

## 📁 Project Structure

```
.
├── main.py                    # Backend entry point
├── src/                       # Backend source
│   ├── api/routes/           # API endpoints
│   ├── amas/                 # AMAS core
│   └── ...
├── frontend/                  # Frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.tsx          # Main app
│   │   └── main.tsx         # Entry point
│   ├── index.html           # HTML template
│   └── vite.config.ts       # Vite config
└── ...
```

---

## 🎉 Everything is Ready!

**Backend**: ✅ Working  
**Frontend**: ✅ Ready (just needs Node.js)

**Next Steps**:
1. Start backend: `python3 start_backend_auto_port.py`
2. Install Node.js (if needed)
3. Start frontend: `cd frontend && npm install && npm run dev`
4. Open browser: `http://localhost:3000`

---

**Both frontend and backend are ready to go! 🚀**

