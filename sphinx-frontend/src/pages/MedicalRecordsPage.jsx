import React, { useState } from 'react';
import {
  Box, Typography, Card, CardContent, TextField, Button, Grid,
  Alert, Divider, Chip
} from '@mui/material';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import LockSearchIcon from '@mui/icons-material/ManageSearch';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const MedicalRecordsPage = () => {
  const navigate = useNavigate();
  const { role } = useAuth();

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <HealthAndSafetyIcon color="primary" sx={{ fontSize: 36 }} />
          <Box>
            <Typography variant="h4" fontWeight="700">
              Clinical Medical Records Engine
            </Typography>
            <Typography variant="body2" color="text.secondary">
              AES-256 field-level encrypted clinical repository with role masking ({role})
            </Typography>
          </Box>
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<LockSearchIcon />}
          onClick={() => navigate('/search')}
        >
          Search Records Index
        </Button>
      </Box>

      <Card variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" fontWeight="700" gutterBottom>
          Secure Search & Directory Access
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto', mb: 3 }}>
          To view or query medical records, use the Cryptographic Search Console or select a patient from the Patient Directory. Every access request requires a declared Purpose of Access.
        </Typography>

        <Box display="flex" justifyContent="center" gap={2}>
          <Button variant="contained" onClick={() => navigate('/search')}>
            Launch Search Console
          </Button>
          <Button variant="outlined" onClick={() => navigate('/patients')}>
            Go to Patient Directory
          </Button>
        </Box>
      </Card>
    </Box>
  );
};
