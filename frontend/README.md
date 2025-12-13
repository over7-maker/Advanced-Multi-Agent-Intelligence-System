# AMAS Frontend Dashboard

Advanced Multi-Agent Intelligence System - Professional Dashboard

## 🚀 Quick Start

### Prerequisites

- **Node.js**: >=18.17.0 <20.0.0
- **npm**: >=9.0.0

### Installation

```bash
# Install dependencies
npm install

# Verify setup
./verify_setup.sh

# Start development server
npm run dev
```

The frontend will be available at: **http://localhost:3000**

## 📋 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run type-check` - TypeScript type checking
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors
- `npm run format` - Format code with Prettier
- `npm test` - Run tests

## 🔗 Backend Integration

The frontend is configured to proxy API requests to the backend:

- **Development**: Frontend (`:3000`) → proxies `/api/*` → Backend (`:8000`)
- **WebSocket**: `/ws` → `ws://localhost:8000/ws`

To change the backend URL, edit `vite.config.ts`:

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

## 🎨 Features

- ✅ React 18 + TypeScript
- ✅ Material-UI (MUI) components with dark theme
- ✅ React Router for navigation
- ✅ React Query for data fetching
- ✅ Framer Motion for animations
- ✅ Vite for fast builds
- ✅ ESLint + Prettier for code quality

## 🐛 Troubleshooting

### "npm: command not found"
- Install Node.js from https://nodejs.org/
- Or use nvm: `nvm install 18 && nvm use 18`

### "Cannot connect to backend"
- Make sure backend is running on port 8000
- Check `vite.config.ts` proxy configuration
- Check backend health: `curl http://localhost:8000/health`

### TypeScript errors
- Run `npm run type-check` to see all errors
- Run `npm run lint:fix` to auto-fix some issues

## 📚 Documentation

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [Material-UI Documentation](https://mui.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

---

**Ready to develop! 🎉**

