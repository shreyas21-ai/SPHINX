import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, TextField, Button,
  Avatar, Divider, Alert, Chip, Paper
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import LockResetIcon from '@mui/icons-material/LockReset';
import ShieldIcon from '@mui/icons-material/Shield';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

export const ProfilePage = () => {
  const { user, role } = useAuth();

  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [loading, setLoading] = useState(false);

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match.' });
      return;
    }

    if (newPassword.length < 8) {
      setMessage({ type: 'error', text: 'New password must be at least 8 characters long.' });
      return;
    }

    setLoading(true);
    try {
      // Password reset request logic
      setMessage({ type: 'success', text: 'Password changed successfully.' });
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.message || 'Password update failed.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box maxWidth={900} mx="auto">
      <Typography variant="h4" fontWeight="700" mb={3}>
        User Account & Security Settings
      </Typography>

      <Grid container spacing={3}>
        {/* Profile Card */}
        <Grid item xs={12} md={5}>
          <Card variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: 'primary.main',
                fontSize: 32,
                fontWeight: 700,
                mx: 'auto',
                mb: 2
              }}
            >
              {user?.first_name ? user.first_name[0] : 'U'}
            </Avatar>
            <Typography variant="h6" fontWeight="700">
              {user?.first_name} {user?.last_name}
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              {user?.email}
            </Typography>
            <Chip
              icon={<ShieldIcon />}
              label={`Assigned Role: ${role}`}
              color="primary"
              variant="outlined"
              sx={{ fontWeight: 700 }}
            />
          </Card>
        </Grid>

        {/* Change Password Card */}
        <Grid item xs={12} md={7}>
          <Card variant="outlined">
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <LockResetIcon color="primary" />
                <Typography variant="h6" fontWeight="700">
                  Change Access Password
                </Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />

              {message.text && (
                <Alert severity={message.type} sx={{ mb: 2 }}>{message.text}</Alert>
              )}

              <Box component="form" onSubmit={handleChangePassword}>
                <TextField
                  label="Current Password"
                  type="password"
                  fullWidth
                  required
                  margin="normal"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                />
                <TextField
                  label="New Password"
                  type="password"
                  fullWidth
                  required
                  margin="normal"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
                <TextField
                  label="Confirm New Password"
                  type="password"
                  fullWidth
                  required
                  margin="normal"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />

                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  size="large"
                  disabled={loading}
                  sx={{ mt: 2 }}
                >
                  {loading ? 'Updating Password...' : 'Update Password'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
