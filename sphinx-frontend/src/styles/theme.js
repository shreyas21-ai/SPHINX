import { createTheme } from '@mui/material/styles';

export const getTheme = (mode = 'light') => createTheme({
  palette: {
    mode,
    primary: {
      main: '#0284c7', // Healthcare Teal / Ocean Blue
      light: '#38bdf8',
      dark: '#0369a1',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#0d9488', // Emerald Mint
      light: '#2dd4bf',
      dark: '#0f766e',
      contrastText: '#ffffff',
    },
    background: {
      default: mode === 'light' ? '#f8fafc' : '#0b0f19',
      paper: mode === 'light' ? '#ffffff' : '#111827',
    },
    text: {
      primary: mode === 'light' ? '#0f172a' : '#f1f5f9',
      secondary: mode === 'light' ? '#475569' : '#94a3b8',
    },
    error: {
      main: '#e11d48',
    },
    warning: {
      main: '#d97706',
    },
    success: {
      main: '#10b981',
    },
    info: {
      main: '#3b82f6',
    },
  },
  typography: {
    fontFamily: ['Inter', 'Roboto', 'sans-serif'].join(','),
    h1: { fontFamily: 'Outfit, sans-serif', fontWeight: 700 },
    h2: { fontFamily: 'Outfit, sans-serif', fontWeight: 700 },
    h3: { fontFamily: 'Outfit, sans-serif', fontWeight: 600 },
    h4: { fontFamily: 'Outfit, sans-serif', fontWeight: 600 },
    h5: { fontFamily: 'Outfit, sans-serif', fontWeight: 600 },
    h6: { fontFamily: 'Outfit, sans-serif', fontWeight: 600 },
  },
  shape: {
    borderRadius: 10,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(2, 132, 199, 0.25)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: mode === 'light'
            ? '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)'
            : '0 4px 20px 0 rgba(0, 0, 0, 0.5)',
          border: mode === 'light' ? '1px solid #e2e8f0' : '1px solid #1e293b',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});
