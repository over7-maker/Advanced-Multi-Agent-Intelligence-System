// frontend/src/components/Layout/MainLayout.tsx
import {
  SmartToy as AgentIcon,
  Dashboard as DashboardIcon,
  HealthAndSafety as HealthIcon,
  IntegrationInstructions as IntegrationIcon,
  Menu as MenuIcon,
  Assignment as TaskIcon,
} from '@mui/icons-material';
import {
  AppBar,
  Avatar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { apiService, User } from '../../services/api';
import { websocketService } from '../../services/websocket';

interface MainLayoutProps {
  children: React.ReactNode;
}

interface MenuItem {
  text: string;
  icon: React.ReactNode;
  path: string;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [drawerOpen, setDrawerOpen] = useState(!isMobile);
  const [user, setUser] = useState<User | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const menuItems: MenuItem[] = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Tasks', icon: <TaskIcon />, path: '/tasks' },
    { text: 'Agents', icon: <AgentIcon />, path: '/agents' },
    { text: 'Integrations', icon: <IntegrationIcon />, path: '/integrations' },
    { text: 'System Health', icon: <HealthIcon />, path: '/health' },
  ];

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await apiService.getCurrentUser();
        setUser(userData);
      } catch (error: any) {
        // Silently handle 403/401 - user is not authenticated (expected)
        // Only log unexpected errors
        if (error?.response?.status !== 403 && error?.response?.status !== 401) {
          console.error('Failed to fetch user:', error);
        }
      }
    };

    fetchUser();

    // Connect WebSocket (with delay to avoid multiple connections)
    const connectTimeout = setTimeout(() => {
      if (!websocketService.isConnected()) {
        websocketService.connect();
      }
    }, 500);

    return () => {
      clearTimeout(connectTimeout);
      // Only disconnect if WebSocket is actually connected or connecting
      // Use a small delay to avoid "WebSocket is closed before the connection is established" error
      setTimeout(() => {
        if (websocketService.isConnected() || websocketService.getReadyState() === WebSocket.CONNECTING) {
          websocketService.disconnect();
        }
      }, 100);
    };
  }, []);

  useEffect(() => {
    // Close drawer on mobile when route changes
    if (isMobile) {
      setDrawerOpen(false);
    }
  }, [location, isMobile]);

  const handleLogout = async () => {
    try {
      await apiService.logout();
      websocketService.disconnect();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AMAS - AI Multi-Agent System
          </Typography>
          <IconButton onClick={handleMenuOpen} sx={{ p: 0 }}>
            <Avatar sx={{ bgcolor: 'secondary.main' }}>
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem onClick={handleMenuClose}>
              <Typography variant="body2" sx={{ px: 1 }}>
                {user?.username || 'User'}
              </Typography>
            </MenuItem>
            <MenuItem onClick={handleLogout}>Logout</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Drawer
        variant={isMobile ? 'temporary' : 'persistent'}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{
          width: 240,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 240,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path || 
                (item.path !== '/' && location.pathname.startsWith(item.path));
              return (
                <ListItem key={item.text} disablePadding>
                  <ListItemButton
                    selected={isActive}
                    onClick={() => {
                      navigate(item.path);
                      if (isMobile) {
                        setDrawerOpen(false);
                      }
                    }}
                  >
                    <ListItemIcon sx={{ color: isActive ? 'primary.main' : 'inherit' }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText primary={item.text} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </Box>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerOpen ? 240 : 0}px)` },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

