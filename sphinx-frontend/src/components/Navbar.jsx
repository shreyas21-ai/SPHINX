import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AppBar, Toolbar, IconButton, Typography, Box, Chip,
  Menu, MenuItem, Tooltip, Avatar
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import LockIcon from '@mui/icons-material/Lock';
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '../contexts/AuthContext';
import { usePurpose } from '../contexts/PurposeContext';
import { useThemeContext } from '../contexts/ThemeContext';
import { DRAWER_WIDTH } from './Sidebar';

export const Navbar = ({ handleDrawerToggle }) => {
  const navigate = useNavigate();
  const { user, role, logout } = useAuth();
  const { purpose, requirePurposeConfirmation } = usePurpose();
  const { mode, toggleTheme } = useThemeContext();

  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);

  const handleLogout = () => {
    handleMenuClose();
    logout();
    navigate('/login');
  };

  const handlePurposeClick = () => {
    requirePurposeConfirmation(() => {});
  };

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
        ml: { sm: `${DRAWER_WIDTH}px` },
        bgcolor: 'background.paper',
        color: 'text.primary',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box display="flex" alignItems="center" gap={1}>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 1, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="subtitle1" fontWeight="700" color="primary">
            Enterprise Healthcare Record Retrieval Platform
          </Typography>
        </Box>

        <Box display="flex" alignItems="center" gap={1.5}>
          {/* Active Purpose Chip */}
          <Tooltip title="Current HIPAA Purpose Header attached to outgoing requests. Click to change.">
            <Chip
              icon={<LockIcon fontSize="small" />}
              label={`Purpose: ${purpose}`}
              color="primary"
              variant="outlined"
              onClick={handlePurposeClick}
              sx={{ fontWeight: 700, cursor: 'pointer' }}
            />
          </Tooltip>

          {/* Theme Toggle */}
          <Tooltip title="Toggle Light/Dark Theme">
            <IconButton onClick={toggleTheme} color="inherit">
              {mode === 'dark' ? <Brightness7Icon color="warning" /> : <Brightness4Icon />}
            </IconButton>
          </Tooltip>

          {/* User Profile Avatar */}
          <IconButton onClick={handleMenuOpen} sx={{ p: 0.5 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 36, height: 36, fontWeight: 700 }}>
              {user?.first_name ? user.first_name[0] : 'U'}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={() => { handleMenuClose(); navigate('/profile'); }}>
              <PersonIcon fontSize="small" sx={{ mr: 1 }} /> My Profile
            </MenuItem>
            <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
              <LogoutIcon fontSize="small" sx={{ mr: 1 }} /> Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};
