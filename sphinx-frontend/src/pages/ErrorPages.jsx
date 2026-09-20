import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Paper } from '@mui/material';
import BlockIcon from '@mui/icons-material/Block';
import SearchOffIcon from '@mui/icons-material/SearchOff';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

export const ForbiddenPage = () => {
  const navigate = useNavigate();
  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="70vh">
      <Paper variant="outlined" sx={{ p: 5, textAlign: 'center', maxWidth: 480 }}>
        <BlockIcon color="error" sx={{ fontSize: 64, mb: 2 }} />
        <Typography variant="h4" fontWeight="700" color="error.main" gutterBottom>
          403 Access Forbidden
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Your current assigned user role does not possess authorization permissions to view or access this resource.
        </Typography>
        <Button variant="contained" onClick={() => navigate('/dashboard')}>
          Return to Dashboard
        </Button>
      </Paper>
    </Box>
  );
};

export const NotFoundPage = () => {
  const navigate = useNavigate();
  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="70vh">
      <Paper variant="outlined" sx={{ p: 5, textAlign: 'center', maxWidth: 480 }}>
        <SearchOffIcon color="warning" sx={{ fontSize: 64, mb: 2 }} />
        <Typography variant="h4" fontWeight="700" gutterBottom>
          404 Page Not Found
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          The page or medical record identifier you requested does not exist or has been relocated.
        </Typography>
        <Button variant="contained" onClick={() => navigate('/dashboard')}>
          Return to Dashboard
        </Button>
      </Paper>
    </Box>
  );
};

export const ServerErrorPage = () => {
  const navigate = useNavigate();
  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="70vh">
      <Paper variant="outlined" sx={{ p: 5, textAlign: 'center', maxWidth: 480 }}>
        <ErrorOutlineIcon color="error" sx={{ fontSize: 64, mb: 2 }} />
        <Typography variant="h4" fontWeight="700" color="error.main" gutterBottom>
          500 Internal Error
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          An unanticipated platform server error occurred. Please try again or contact system administration.
        </Typography>
        <Button variant="contained" onClick={() => navigate('/dashboard')}>
          Return to Dashboard
        </Button>
      </Paper>
    </Box>
  );
};
