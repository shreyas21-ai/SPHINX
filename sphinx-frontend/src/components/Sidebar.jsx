import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText,
  Box, Typography, Divider, Chip, Avatar
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import LockSearchIcon from '@mui/icons-material/ManageSearch';
import PeopleIcon from '@mui/icons-material/People';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import EventIcon from '@mui/icons-material/Event';
import SecurityIcon from '@mui/icons-material/Security';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import PersonIcon from '@mui/icons-material/Person';
import ShieldMoonIcon from '@mui/icons-material/ShieldMoon';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import { useAuth } from '../contexts/AuthContext';

const DRAWER_WIDTH = 260;

export const Sidebar = ({ mobileOpen, handleDrawerToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, role } = useAuth();

  let navItems = [];

  if (role === 'ADMIN') {
    navItems = [
      { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
      { label: 'Patient Directory', path: '/patients', icon: <PeopleIcon /> },
      { label: 'Appointments', path: '/appointments', icon: <EventIcon /> },
      { label: 'Audit Trail', path: '/audit-logs', icon: <SecurityIcon /> },
      { label: 'User Management', path: '/users', icon: <AdminPanelSettingsIcon /> },
      { label: 'My Account', path: '/profile', icon: <PersonIcon /> },
    ];
  } else if (role === 'RECEPTIONIST') {
    navItems = [
      { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
      { label: 'Patient Directory', path: '/patients', icon: <PeopleIcon /> },
      { label: 'Appointments', path: '/appointments', icon: <EventIcon /> },
      { label: 'My Account', path: '/profile', icon: <PersonIcon /> },
    ];
  } else if (role === 'INSURANCE_OFFICER') {
    navItems = [
      { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
      { label: 'Patient Directory', path: '/patients', icon: <PeopleIcon /> },
      { label: 'Billing & Claims', path: '/billing', icon: <ReceiptLongIcon /> },
      { label: 'My Account', path: '/profile', icon: <PersonIcon /> },
    ];
  } else if (role === 'DOCTOR') {
    navItems = [
      { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
      { label: 'Cryptographic Search', path: '/search', icon: <LockSearchIcon /> },
      { label: 'My Patients', path: '/patients', icon: <PeopleIcon /> },
      { label: 'My Appointments', path: '/appointments', icon: <EventIcon /> },
      { label: 'My Account', path: '/profile', icon: <PersonIcon /> },
    ];
  } else {
    // NURSE
    navItems = [
      { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
      { label: 'Cryptographic Search', path: '/search', icon: <LockSearchIcon /> },
      { label: 'Patient Directory', path: '/patients', icon: <PeopleIcon /> },
      { label: 'Appointments', path: '/appointments', icon: <EventIcon /> },
      { label: 'My Account', path: '/profile', icon: <PersonIcon /> },
    ];
  }

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Brand Header */}
      <Box sx={{ p: 2.5, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Avatar sx={{ bgcolor: 'primary.main', width: 40, height: 40 }}>
          <ShieldMoonIcon />
        </Avatar>
        <Box>
          <Typography variant="h6" fontWeight="700" letterSpacing="-0.5px" color="primary">
            SPHINX
          </Typography>
          <Typography variant="caption" color="text.secondary" fontWeight="600">
            Searchable Encryption
          </Typography>
        </Box>
      </Box>

      <Divider />

      {/* Navigation List */}
      <List sx={{ px: 1.5, py: 2, flexGrow: 1 }}>
        {navItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={active}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  py: 1.2,
                  px: 2,
                  '&.Mui-selected': {
                    bgcolor: 'primary.main',
                    color: 'primary.contrastText',
                    '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
                    '&:hover': { bgcolor: 'primary.dark' },
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: active ? 'inherit' : 'action.active' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: active ? 600 : 500 }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider />

      {/* User Info Footer */}
      <Box sx={{ p: 2, bgcolor: 'action.hover' }}>
        <Typography variant="subtitle2" fontWeight="700" noWrap>
          {user?.first_name} {user?.last_name}
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" noWrap>
          {user?.email}
        </Typography>
        <Chip
          label={`Role: ${role}`}
          size="small"
          color="primary"
          variant="outlined"
          sx={{ mt: 1, fontWeight: 700, fontSize: '0.7rem' }}
        />
      </Box>
    </Box>
  );

  return (
    <Box component="nav" sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}>
      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Desktop Permanent Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH, borderRight: '1px solid', borderColor: 'divider' },
        }}
        open
      >
        {drawerContent}
      </Drawer>
    </Box>
  );
};

export { DRAWER_WIDTH };
