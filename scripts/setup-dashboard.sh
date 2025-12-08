#!/bin/bash
# AMAS Dashboard Setup Script

set -e

echo "🎨 Setting up AMAS React Dashboard..."
echo "===================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

echo "✅ Node.js $(node --version) detected"
echo "✅ npm $(npm --version) detected"

# Create frontend directory if it doesn't exist
mkdir -p frontend/src/components
mkdir -p frontend/public
mkdir -p frontend/src/hooks
mkdir -p frontend/src/utils

cd frontend

# Install dependencies
echo "📦 Installing React dependencies..."
npm install

# Initialize Tailwind CSS
echo "🎨 Setting up Tailwind CSS..."
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Create index.html
echo "📄 Creating index.html..."
cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0F172A" />
    <meta name="description" content="Advanced Multi-Agent Intelligence System Control Dashboard" />
    
    <!-- Neural network favicon (base64 encoded) -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTQiIGZpbGw9IiMzYjgyZjYiLz4KPGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iOCIgZmlsbD0iIzFlNDBhZiIvPgo8Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSI0IiBmaWxsPSIjMzczOWJlIi8+Cjwvc3ZnPgo=" />
    
    <title>AMAS Control Center</title>
  </head>
  <body class="bg-slate-900">
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# Create main App component
echo "⚛️ Creating main App component..."
cat > src/App.tsx << 'EOF'
import React from 'react';
import AMASControlCenter from './components/AMASControlCenter';
import './App.css';

function App() {
  return (
    <div className="App">
      <AMASControlCenter />
    </div>
  );
}

export default App;
EOF

# Create CSS file
echo "🎨 Creating App.css..."
cat > src/App.css << 'EOF'
@tailwind base;
@tailwind components; 
@tailwind utilities;

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
}

::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.8);
}

/* Neural glow effect */
.neural-glow {
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

/* Typing animation */
.typing-cursor::after {
  content: '_';
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Smooth transitions */
* {
  transition: all 0.2s ease-in-out;
}

/* Custom gradient backgrounds */
.gradient-neural {
  background: linear-gradient(135deg, #1e40af 0%, #3730a3 50%, #1e1b4b 100%);
}

.gradient-quantum {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
}
EOF

# Create index.tsx
echo "🚀 Creating index.tsx..."
cat > src/index.tsx << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Create custom hooks
echo "🎣 Creating custom hooks..."
mkdir -p src/hooks

cat > src/hooks/useWebSocket.ts << 'EOF'
import { useEffect, useRef, useState } from 'react';

interface UseWebSocketProps {
  url: string;
  onMessage?: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export const useWebSocket = ({ url, onMessage, onConnect, onDisconnect }: UseWebSocketProps) => {
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    ws.current = new WebSocket(url);
    
    ws.current.onopen = () => {
      setIsConnected(true);
      onConnect?.();
    };
    
    ws.current.onclose = () => {
      setIsConnected(false);
      onDisconnect?.();
    };
    
    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };
    
    return () => {
      ws.current?.close();
    };
  }, [url, onMessage, onConnect, onDisconnect]);
  
  const sendMessage = (data: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    }
  };
  
  return { isConnected, sendMessage };
};
EOF

# Create dashboard launcher script
cd ..

cat > start-dashboard.sh << 'EOF'
#!/bin/bash
# Start AMAS Dashboard

echo "🎨 Starting AMAS Control Center Dashboard..."

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found. Run setup-dashboard.sh first."
    exit 1
fi

cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start development server
echo "🚀 Starting React development server..."
echo ""
echo "🌐 Dashboard will be available at: http://localhost:3000"
echo "📊 API should be running at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the dashboard"

npm start
EOF

chmod +x start-dashboard.sh

# Create production build script
cat > build-dashboard.sh << 'EOF'
#!/bin/bash
# Build AMAS Dashboard for production

echo "🏗️ Building AMAS Dashboard for production..."

cd web

# Install dependencies
npm install

# Build for production
npm run build

echo "✅ Production build complete!"
echo "📁 Build files are in web/build/"
echo ""
echo "To serve the production build:"
echo "  npx serve -s build"
echo ""
echo "Or copy the build/ directory to your web server"
EOF

chmod +x build-dashboard.sh

echo ""
echo -e "${BLUE}===================================="
echo "✅ AMAS Dashboard Setup Complete!"
echo -e "====================================${NC}"
echo ""
echo -e "${GREEN}Available Commands:${NC}"
echo "  ./start-dashboard.sh     - Start development server"
echo "  ./build-dashboard.sh     - Build for production"
echo ""
echo -e "${YELLOW}Features Included:${NC}"
echo "  ✅ Modern React 18 with TypeScript"
echo "  ✅ Tailwind CSS with custom design system"
echo "  ✅ Real-time agent status monitoring"
echo "  ✅ Interactive command interface"
echo "  ✅ Beautiful charts and visualizations"
echo "  ✅ Neural network animated backgrounds"
echo "  ✅ Responsive design for all devices"
echo "  ✅ WebSocket support for real-time data"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Start the dashboard: ./start-dashboard.sh"
echo "2. Open http://localhost:3000 in your browser"
echo "3. Ensure your AMAS API is running on port 8000"
echo ""
echo "🎉 Your AMAS now has a world-class control interface! 🚀"