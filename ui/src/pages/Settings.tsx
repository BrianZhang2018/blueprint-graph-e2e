import React, { useState } from 'react';
import { 
  Typography, 
  Box, 
  Paper, 
  TextField, 
  Button, 
  Grid,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Snackbar
} from '@mui/material';

const Settings: React.FC = () => {
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_URL || 'http://localhost:8000');
  const [darkMode, setDarkMode] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30);
  const [showSnackbar, setShowSnackbar] = useState(false);
  
  const handleSaveSettings = () => {
    // In a real app, you would save these settings to localStorage or a backend
    localStorage.setItem('apiUrl', apiUrl);
    localStorage.setItem('darkMode', String(darkMode));
    localStorage.setItem('autoRefresh', String(autoRefresh));
    localStorage.setItem('refreshInterval', String(refreshInterval));
    
    setShowSnackbar(true);
  };
  
  const handleCloseSnackbar = () => {
    setShowSnackbar(false);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          API Configuration
        </Typography>
        <Box mb={3}>
          <TextField
            label="API URL"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            fullWidth
            margin="normal"
            helperText="The URL of the Blueprint Graph API"
          />
        </Box>
        
        <Divider sx={{ my: 3 }} />
        
        <Typography variant="h6" gutterBottom>
          UI Preferences
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={darkMode}
                  onChange={(e) => setDarkMode(e.target.checked)}
                  color="primary"
                />
              }
              label="Dark Mode"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  color="primary"
                />
              }
              label="Auto-refresh Data"
            />
          </Grid>
          {autoRefresh && (
            <Grid item xs={12} md={6}>
              <TextField
                label="Refresh Interval (seconds)"
                type="number"
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                fullWidth
                margin="normal"
                inputProps={{ min: 5, max: 300 }}
              />
            </Grid>
          )}
        </Grid>
        
        <Divider sx={{ my: 3 }} />
        
        <Typography variant="h6" gutterBottom>
          About
        </Typography>
        <Box mb={3}>
          <Typography variant="body1">
            Blueprint Graph is a security event processing and detection system that uses graph database technology to identify security threats.
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Version: 1.0.0
          </Typography>
        </Box>
        
        <Box mt={3} display="flex" justifyContent="flex-end">
          <Button
            variant="contained"
            color="primary"
            onClick={handleSaveSettings}
          >
            Save Settings
          </Button>
        </Box>
      </Paper>
      
      <Snackbar
        open={showSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          Settings saved successfully!
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings; 