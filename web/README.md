# AMAS Web Interface

A modern React-based web interface for the Advanced Multi-Agent Intelligence System (AMAS).

## Features

### 🎯 Dashboard
- Real-time system status monitoring
- Agent status overview
- Task completion metrics
- System health indicators

### 🤖 Agent Management
- View all active agents
- Monitor agent capabilities
- Agent status tracking
- Performance metrics

### 📋 Task Management
- Submit new tasks to the system
- Monitor task progress
- View task history
- Task status tracking

### 📊 Analytics
- Task completion distribution
- Agent performance metrics
- System utilization charts
- Historical data analysis

### ⚙️ Settings
- System configuration
- Agent parameters
- Security settings
- Logging configuration

## Technology Stack

- **React 18** - Modern React with hooks
- **Ant Design 5** - UI component library
- **React Router 6** - Client-side routing
- **Axios** - HTTP client for API communication
- **CSS3** - Custom styling with glassmorphism effects

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm 8+
- AMAS API server running on localhost:8000

### Installation

1. **Clone the repository** (if not already done):
```bash
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System/web
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment** (optional):
```bash
# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env
echo "REACT_APP_API_TOKEN=valid_token" >> .env
```

4. **Start the development server**:
```bash
npm start
```

The application will open at `http://localhost:3000`

### Building for Production

1. **Build the application**:
```bash
npm run build
```

2. **Or use the build script**:
```bash
./build.sh
```

The built files will be in the `build/` directory.

## API Integration

The web interface communicates with the AMAS API through the following endpoints:

### System Status
- `GET /health` - Health check
- `GET /status` - System status

### Agents
- `GET /agents` - List all agents
- `GET /agents/{agent_id}` - Get agent status

### Tasks
- `POST /tasks` - Submit new task
- `GET /tasks/{task_id}` - Get task status

### Workflows
- `POST /workflows/{workflow_id}/execute` - Execute workflow

### Audit
- `GET /audit` - Get audit log

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | AMAS API base URL | `http://localhost:8000` |
| `REACT_APP_API_TOKEN` | API authentication token | `valid_token` |

### API Authentication

The web interface uses Bearer token authentication. Set the token in your environment:

```bash
export REACT_APP_API_TOKEN="your_actual_token"
```

## Development

### Project Structure

```
web/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── App.js              # Main application component
│   ├── index.js            # Application entry point
│   └── index.css           # Global styles
├── package.json
├── build.sh                # Build script
└── README.md
```

### Key Components

- **Dashboard** - System overview and metrics
- **Agents** - Agent management and monitoring
- **Tasks** - Task submission and tracking
- **Analytics** - Performance and usage analytics
- **Settings** - System configuration

### Styling

The interface uses a modern glassmorphism design with:
- Gradient backgrounds
- Glass-like card effects
- Smooth animations
- Responsive layout
- Dark/light theme support

### State Management

The application uses React hooks for state management:
- `useState` for component state
- `useEffect` for side effects
- `useLocation` for routing

## Deployment

### Static Hosting

1. **Build the application**:
```bash
npm run build
```

2. **Deploy the `build/` directory** to your hosting service:
   - Netlify
   - Vercel
   - AWS S3
   - GitHub Pages

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://amas-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

1. **API Connection Errors**:
   - Check if AMAS API is running
   - Verify API URL configuration
   - Check network connectivity

2. **Authentication Issues**:
   - Verify API token is correct
   - Check token expiration
   - Ensure proper headers

3. **Build Errors**:
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify all dependencies

### Debug Mode

Enable debug logging:

```bash
# Set debug environment
export REACT_APP_DEBUG=true
npm start
```

### Performance Optimization

1. **Code Splitting**: Implement lazy loading for routes
2. **Bundle Analysis**: Use `npm run build -- --analyze`
3. **Image Optimization**: Compress and lazy load images
4. **Caching**: Implement proper caching strategies

## Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Development Guidelines

- Follow React best practices
- Use functional components with hooks
- Implement proper error handling
- Write meaningful commit messages
- Test on multiple browsers

## License

This project is part of the AMAS system and follows the same license terms.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub
- Contact the development team

## Roadmap

### Planned Features

- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Custom agent configuration
- [ ] Workflow designer
- [ ] Mobile responsive design
- [ ] Dark/light theme toggle
- [ ] Multi-language support
- [ ] Advanced security features

### Future Enhancements

- [ ] WebSocket integration for real-time updates
- [ ] Progressive Web App (PWA) support
- [ ] Offline functionality
- [ ] Advanced data visualization
- [ ] Machine learning insights
- [ ] Collaborative features
- [ ] API documentation integration
- [ ] Automated testing suite