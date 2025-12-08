# 🎨 Frontend Setup Guide

## ✅ Frontend Status

The frontend is **ready** but needs Node.js/npm to run.

## 📋 Prerequisites

- **Node.js**: >=18.17.0 <20.0.0
- **npm**: >=9.0.0

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will start on **http://localhost:3000**

### 3. Build for Production

```bash
npm run build
npm run preview
```

---

## 🔧 Configuration

### Backend API Proxy

The frontend is configured to proxy API requests to the backend:

- **Development**: `http://localhost:3000` → proxies `/api/*` to `http://localhost:8000`
- **WebSocket**: `/ws` → proxies to `ws://localhost:8000`

**To change backend URL**, edit `frontend/vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000', // Change this
      changeOrigin: true,
    },
  },
}
```

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── Dashboard/     # Dashboard components
│   │   ├── WorkflowBuilder/
│   │   └── ProgressTracker/
│   ├── types/            # TypeScript types
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
├── index.html            # HTML template
├── vite.config.ts        # Vite configuration
└── package.json          # Dependencies
```

---

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - TypeScript type checking
- `npm test` - Run tests

---

## 🎯 Features

- ✅ React 18 + TypeScript
- ✅ Material-UI (MUI) components
- ✅ React Router for navigation
- ✅ React Query for data fetching
- ✅ Vite for fast builds
- ✅ ESLint + Prettier for code quality

---

## ⚠️ Current Status

**Missing**: Node.js/npm in the container

**To run frontend**:
1. Install Node.js 18+ in your environment
2. Run `npm install` in the `frontend/` directory
3. Run `npm run dev` to start the dev server

---

## 🔗 Backend Integration

The frontend expects the backend to be running on:
- **Default**: `http://localhost:8000`
- **API Endpoints**: `/api/v1/*`
- **WebSocket**: `ws://localhost:8000/ws`

Make sure the backend is running before starting the frontend!

---

**Frontend is ready! Just need Node.js to run it! 🚀**

