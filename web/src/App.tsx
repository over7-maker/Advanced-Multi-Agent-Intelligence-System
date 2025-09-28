/**
 * AMAS Intelligence System - Main React Application
 * 
 * Advanced Multi-Agent Intelligence System Web Interface
 * Features:
 * - Real-time agent monitoring and task management
 * - Material-UI design system with modern UX
 * - Intelligence workflow visualization
 * - Security-first architecture with JWT authentication
 */

import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Badge,
  Alert,
  Snackbar,
  Container,
  Grid,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  SmartToy,
  Assignment,
  Analytics,
  Security,
  Settings,
  Notifications,
  AccountCircle,
  Warning,
  CheckCircle
} from '@mui/icons-material';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';

// Components
import Dashboard from './components/Dashboard';
import AgentManager from './components/AgentManager';
import TaskManager from './components/TaskManager';
import Analytics from './components/Analytics';
import SecurityMonitor from './components/SecurityMonitor';
import Settings from './components/Settings';

// Services
import { AMASApiService } from './services/api';
import { WebSocketService } from './services/websocket';

// Types
interface SystemStatus {
  status: string;
  agents: number;
  active_tasks: number;
  total_tasks: number;
  timestamp: string;
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
  timestamp: string;
}

// Theme configuration
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00bcd4',
      dark: '#0097a7',
      light: '#4dd0e1'
    },
    secondary: {
      main: '#ff5722',
      dark: '#d84315',
      light: '#ff8a65'
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e'
    },
    error: {
      main: '#f44336'
    },
    warning: {
      main: '#ff9800'
    },
    success: {
      main: '#4caf50'
    }
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600
    },
    h6: {
      fontWeight: 500
    }
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.05))',
          border: '1px solid rgba(255, 255, 255, 0.12)'
        }
      }
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, #00bcd4 0%, #0097a7 100%)'
        }
      }
    }
  }
});

const DRAWER_WIDTH = 280;

const App: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const apiService = new AMASApiService();
  const wsService = new WebSocketService();

  useEffect(() => {
    initializeApp();
    
    // Setup WebSocket for real-time updates
    wsService.connect();
    wsService.onMessage('system_status', handleSystemStatusUpdate);
    wsService.onMessage('notification', handleNotification);
    
    // Cleanup on unmount
    return () => {
      wsService.disconnect();
    };
  }, []);

  const initializeApp = async () => {
    try {
      setLoading(true);
      
      // Get initial system status
      const status = await apiService.getSystemStatus();
      setSystemStatus(status);
      
      // Initialize authentication if needed
      const token = localStorage.getItem('amas_token');
      if (!token) {
        // Mock authentication for demo
        localStorage.setItem('amas_token', 'demo_token');
        apiService.setAuthToken('demo_token');
      } else {
        apiService.setAuthToken(token);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to initialize app:', err);
      setError('Failed to initialize AMAS system');
      setLoading(false);
    }
  };

  const handleSystemStatusUpdate = (status: SystemStatus) => {
    setSystemStatus(status);
  };

  const handleNotification = (notification: Notification) => {
    setNotifications(prev => [notification, ...prev.slice(0, 9)]); // Keep last 10
  };

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleCloseError = () => {
    setError(null);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/' },
    { text: 'Agent Manager', icon: <SmartToy />, path: '/agents' },
    { text: 'Task Manager', icon: <Assignment />, path: '/tasks' },
    { text: 'Analytics', icon: <Analytics />, path: '/analytics' },
    { text: 'Security Monitor', icon: <Security />, path: '/security' },
    { text: 'Settings', icon: <Settings />, path: '/settings' }
  ];

  if (loading) {
    return (
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          flexDirection="column"
        >
          <Typography variant="h4" gutterBottom color="primary">
            AMAS Intelligence System
          </Typography>
          <Typography variant="body1" color="textSecondary" gutterBottom>
            Initializing Advanced Multi-Agent Intelligence System...
          </Typography>
          <Box sx={{ width: '300px', mt: 2 }}>
            <LinearProgress />
          </Box>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          {/* App Bar */}
          <AppBar
            position="fixed"
            sx={{
              zIndex: (theme) => theme.zIndex.drawer + 1,
              width: `calc(100% - ${drawerOpen ? DRAWER_WIDTH : 0}px)`,
              ml: drawerOpen ? `${DRAWER_WIDTH}px` : 0,
              transition: (theme) =>
                theme.transitions.create(['width', 'margin'], {
                  easing: theme.transitions.easing.sharp,
                  duration: theme.transitions.duration.leavingScreen,
                }),
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                onClick={handleDrawerToggle}
                edge="start"
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                AMAS Intelligence System
              </Typography>

              {/* System Status Indicator */}
              {systemStatus && (
                <Box display="flex" alignItems="center" mr={2}>
                  {systemStatus.status === 'operational' ? (
                    <CheckCircle color="success" />
                  ) : (
                    <Warning color="warning" />
                  )}
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    {systemStatus.agents} Agents | {systemStatus.active_tasks} Active Tasks
                  </Typography>
                </Box>
              )}

              {/* Notifications */}
              <IconButton color="inherit">
                <Badge badgeContent={notifications.length} color="error">
                  <Notifications />
                </Badge>
              </IconButton>

              {/* User Account */}
              <IconButton color="inherit">
                <AccountCircle />
              </IconButton>
            </Toolbar>
          </AppBar>

          {/* Drawer */}
          <Drawer
            variant="persistent"
            anchor="left"
            open={drawerOpen}
            sx={{
              width: DRAWER_WIDTH,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: DRAWER_WIDTH,
                boxSizing: 'border-box',
              },
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto' }}>
              <List>
                {menuItems.map((item) => (
                  <NavigationItem key={item.text} item={item} />
                ))}
              </List>
              
              <Divider sx={{ my: 2 }} />
              
              {/* System Status Card */}
              {systemStatus && (
                <Box sx={{ p: 2 }}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        System Status
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Status: {systemStatus.status}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Agents: {systemStatus.agents}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Tasks: {systemStatus.total_tasks}
                      </Typography>
                    </CardContent>
                  </Card>
                </Box>
              )}
            </Box>
          </Drawer>

          {/* Main Content */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              bgcolor: 'background.default',
              p: 3,
              width: `calc(100% - ${drawerOpen ? DRAWER_WIDTH : 0}px)`,
              transition: (theme) =>
                theme.transitions.create('width', {
                  easing: theme.transitions.easing.sharp,
                  duration: theme.transitions.duration.leavingScreen,
                }),
            }}
          >
            <Toolbar />
            
            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/agents" element={<AgentManager />} />
                <Route path="/tasks" element={<TaskManager />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/security" element={<SecurityMonitor />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Container>
          </Box>
        </Box>

        {/* Error Snackbar */}
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={handleCloseError}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        >
          <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>
      </Router>
    </ThemeProvider>
  );
};

// Navigation Item Component
const NavigationItem: React.FC<{ item: any }> = ({ item }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = location.pathname === item.path;

  return (
    <ListItem disablePadding>
      <ListItemButton
        selected={isActive}
        onClick={() => navigate(item.path)}
        sx={{
          '&.Mui-selected': {
            backgroundColor: 'rgba(0, 188, 212, 0.12)',
            '&:hover': {
              backgroundColor: 'rgba(0, 188, 212, 0.18)',
            },
          },
        }}
      >
        <ListItemIcon sx={{ color: isActive ? 'primary.main' : 'inherit' }}>
          {item.icon}
        </ListItemIcon>
        <ListItemText 
          primary={item.text} 
          sx={{ color: isActive ? 'primary.main' : 'inherit' }}
        />
      </ListItemButton>
    </ListItem>
  );
};

export default App;