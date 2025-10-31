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