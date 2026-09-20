import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Container, Paper, Typography, Avatar } from '@mui/material';
import ShieldMoonIcon from '@mui/icons-material/ShieldMoon';

export const AuthLayout = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0f172a 0%, #0284c7 100%)',
        p: 2,
      }}
    >
      <Container maxWidth="xs">
        <Paper
          elevation={12}
          sx={{
            p: 4,
            borderRadius: 3,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            bgcolor: 'background.paper'
          }}
        >
          <Avatar sx={{ m: 1, bgcolor: 'primary.main', width: 56, height: 56 }}>
            <ShieldMoonIcon fontSize="large" />
          </Avatar>
          <Typography variant="h4" fontWeight="700" color="primary" gutterBottom>
            SPHINX
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Secure Patient Healthcare Information Platform
          </Typography>
          <Outlet />
        </Paper>
      </Container>
    </Box>
  );
};
