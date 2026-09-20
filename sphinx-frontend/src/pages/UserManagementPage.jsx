import React, { useState, useEffect } from 'react';
import {
  Box, Card, Typography, Button, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Switch, Chip, Alert, CircularProgress,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Grid
} from '@mui/material';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import api from '../services/api';

export const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Register Modal State
  const [openRegister, setOpenRegister] = useState(false);
  const [newUser, setNewUser] = useState({
    email: '', password: '', first_name: '', last_name: '', role_name: 'DOCTOR'
  });
  const [registering, setRegistering] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/users');
      if (response.data?.status === 'success') {
        setUsers(response.data.data);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load user list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleToggleStatus = async (public_id, currentStatus) => {
    try {
      const newStatus = !currentStatus;
      await api.patch(`/users/${public_id}/status`, { is_active: newStatus });
      setUsers((prev) =>
        prev.map((u) => (u.public_id === public_id ? { ...u, is_active: newStatus } : u))
      );
      setSuccessMsg(`User status updated to ${newStatus ? 'Active' : 'Inactive'}.`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update user status.');
    }
  };

  const handleRegisterUser = async (e) => {
    e.preventDefault();
    setRegistering(true);
    setError('');
    try {
      const response = await api.post('/auth/register', newUser);
      if (response.data?.status === 'success') {
        setOpenRegister(false);
        setNewUser({ email: '', password: '', first_name: '', last_name: '', role_name: 'DOCTOR' });
        setSuccessMsg('New user created successfully.');
        fetchUsers();
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to register user.');
    } finally {
      setRegistering(false);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <AdminPanelSettingsIcon color="primary" sx={{ fontSize: 36 }} />
          <Box>
            <Typography variant="h4" fontWeight="700">
              User & Role Management
            </Typography>
            <Typography variant="body2" color="text.secondary">
              System user account activation, role assignment, and access control
            </Typography>
          </Box>
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<PersonAddIcon />}
          onClick={() => setOpenRegister(true)}
        >
          Register Staff Account
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {successMsg && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMsg('')}>{successMsg}</Alert>}

      <TableContainer component={Card} variant="outlined">
        <Table>
          <TableHead sx={{ bgcolor: 'action.hover' }}>
            <TableRow>
              <TableCell fontWeight="700">Public User ID</TableCell>
              <TableCell fontWeight="700">Full Name</TableCell>
              <TableCell fontWeight="700">Work Email</TableCell>
              <TableCell fontWeight="700">Assigned Role</TableCell>
              <TableCell fontWeight="700">Account Status</TableCell>
              <TableCell align="right" fontWeight="700">Toggle Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <CircularProgress size={32} />
                </TableCell>
              </TableRow>
            ) : users.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No users found.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              users.map((u) => (
                <TableRow key={u.public_id} hover>
                  <TableCell fontFamily="monospace" fontWeight="700">#{u.public_id.substring(0, 8)}</TableCell>
                  <TableCell fontWeight="600">{u.first_name} {u.last_name}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>
                    <Chip label={u.role || 'N/A'} size="small" color="primary" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={u.is_active ? 'ACTIVE' : 'INACTIVE'}
                      size="small"
                      color={u.is_active ? 'success' : 'error'}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Switch
                      checked={u.is_active}
                      onChange={() => handleToggleStatus(u.public_id, u.is_active)}
                      color="primary"
                    />
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Register User Dialog */}
      <Dialog open={openRegister} onClose={() => setOpenRegister(false)} maxWidth="xs" fullWidth>
        <DialogTitle fontWeight="700">Register Staff Account</DialogTitle>
        <Box component="form" onSubmit={handleRegisterUser}>
          <DialogContent dividers>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField label="First Name" fullWidth required value={newUser.first_name} onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Last Name" fullWidth required value={newUser.last_name} onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <TextField label="Email" type="email" fullWidth required value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <TextField label="Password" type="password" fullWidth required value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <TextField select label="Role" fullWidth value={newUser.role_name} onChange={(e) => setNewUser({ ...newUser, role_name: e.target.value })}>
                  <MenuItem value="ADMIN">ADMIN</MenuItem>
                  <MenuItem value="DOCTOR">DOCTOR</MenuItem>
                  <MenuItem value="NURSE">NURSE</MenuItem>
                  <MenuItem value="RECEPTIONIST">RECEPTIONIST</MenuItem>
                  <MenuItem value="INSURANCE_OFFICER">INSURANCE_OFFICER</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ px: 3, py: 2 }}>
            <Button onClick={() => setOpenRegister(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={registering}>
              {registering ? 'Registering...' : 'Create Account'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  );
};
