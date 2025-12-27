# AMAS Frontend - Landing Page

Modern, responsive React frontend for the Advanced Multi-Agent Intelligence System.

## 🎄 Features

- 🌉 **Dark Mode Support** - Seamless light/dark theme switching
- 🌿 **Responsive Design** - Beautiful on all devices
- ⚡ **Fast Development** - Vite with HMR
- 🚀 **Optimized Build** - Production-ready with code splitting
- 💫 **Mock API** - Develop without backend
- 🎨 **Tailwind CSS** - Utility-first styling
- 📄 **TypeScript** - Full type safety
- 🛰 **Lucide Icons** - Beautiful icon library

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Production Build

```bash
npm run build
```

Output files will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 📂 Project Structure

```
src/
├── components/
│   └── landing/
│       ├── Header.tsx
│       ├── HeroSection.tsx
│       ├── ArchitectureSection.tsx
│       ├── FeaturesSection.tsx
│       ├── MonitoringDashboard.tsx
│       ├── InteractiveDemo.tsx
│       ├── DocumentationSection.tsx
│       └── Footer.tsx
├── hooks/
│   └── useDarkMode.ts
├── lib/
│   └── api.ts
├── App.tsx
├── main.tsx
└── index.css
```

## 🎎 Customization

### Colors

Edit `tailwind.config.ts` to change the color palette:

```typescript
// Primary colors (Teal)
// Secondary colors (Brown)
// Accent colors (Orange)
```

### Fonts

Customize fonts in `index.css`. Currently using Inter from Google Fonts.

### Dark Mode

Dark mode toggle is in the header. Preferences persist in localStorage.

## 🔇 API Integration

### Mock Data (Development)

By default, the app uses mock data. To enable real backend:

```typescript
// frontend/src/lib/api.ts
const USE_MOCK_DATA = false; // Set to false
```

### Backend Endpoints

Required endpoints:

```
GET  /api/metrics    - System metrics
GET  /api/agents     - Agent list
POST /api/demo/execute - Execute command
POST /api/feedback   - Submit feedback
GET  /api/health     - Health check
```

## 📆 Scripts

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## 📄 Documentation

See the main project documentation for:
- [Full Integration Guide](../FRONTEND_INTEGRATION_COMPLETE.md)
- [Architecture Overview](../ARCHITECTURE.md)
- [API Reference](../API.md)

## 🚦 Deployment

### Docker

```bash
# Build image
docker build -t amas-frontend .

# Run container
docker run -p 3000:3000 amas-frontend
```

### Environment Variables

```bash
VITE_API_URL=http://localhost:8000/api
```

## 🔓 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📝 License

MIT License - See LICENSE file in root directory

## 🚽c Contributing

Contributions are welcome! Please:

1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a PR

## 🌐 Live Demo

Available at: `https://ui.example.com` (after deployment)

---

**Built with ❤️ by the AMAS team**
