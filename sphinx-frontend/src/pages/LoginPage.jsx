import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TextField, Button, Alert, Box, Checkbox, FormControlLabel,
  Typography, CircularProgress, Divider, Chip
} from '@mui/material';
import LoginIcon from '@mui/icons-material/Login';
import { useAuth } from '../contexts/AuthContext';

export const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState('dr.smith@sphinxhealth.com');
  const [password, setPassword] = useState('DoctorPass123!');
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const setQuickCredentials = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <TextField
        label="Work Email Address"
        type="email"
        fullWidth
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        margin="normal"
        autoComplete="email"
      />

      <TextField
        label="Password"
        type="password"
        fullWidth
        required
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        margin="normal"
        autoComplete="current-password"
      />

      <Box display="flex" justifyContent="space-between" alignItems="center" mt={1} mb={2}>
        <FormControlLabel
          control={<Checkbox checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} color="primary" />}
          label={<Typography variant="body2">Remember Me</Typography>}
        />
      </Box>

      <Button
        type="submit"
        fullWidth
        variant="contained"
        size="large"
        disabled={loading}
        startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <LoginIcon />}
        sx={{ py: 1.5, mt: 1, mb: 2 }}
      >
        {loading ? 'Authenticating...' : 'Sign In'}
      </Button>

      <Divider sx={{ my: 2 }}>
        <Typography variant="caption" color="text.secondary">Demo Quick Logins</Typography>
      </Divider>

      <Box display="flex" flexWrap="wrap" gap={1} justifyContent="center">
        <Chip label="Admin" size="small" onClick={() => setQuickCredentials('admin@sphinxhealth.com', 'AdminSecurePass123!')} clickable color="primary" variant="outlined" />
        <Chip label="Doctor" size="small" onClick={() => setQuickCredentials('dr.smith@sphinxhealth.com', 'DoctorPass123!')} clickable color="success" variant="outlined" />
        <Chip label="Nurse" size="small" onClick={() => setQuickCredentials('nurse.john@sphinxhealth.com', 'NursePass123!')} clickable color="info" variant="outlined" />
        <Chip label="Receptionist" size="small" onClick={() => setQuickCredentials('rec.sarah@sphinxhealth.com', 'RecPass123!')} clickable color="warning" variant="outlined" />
        <Chip label="Insurance" size="small" onClick={() => setQuickCredentials('ins.mark@sphinxhealth.com', 'InsPass123!')} clickable color="secondary" variant="outlined" />
      </Box>
    </Box>
  );
};
