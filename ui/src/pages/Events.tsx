import React, { useState } from 'react';
import { 
  Typography, 
  Box, 
  Paper, 
  Button,
  Fab
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import EventForm from '../components/EventForm';

const Events: React.FC = () => {
  const [openEventForm, setOpenEventForm] = useState(false);
  
  const handleOpenEventForm = () => {
    setOpenEventForm(true);
  };
  
  const handleCloseEventForm = () => {
    setOpenEventForm(false);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Events
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenEventForm}
        >
          Submit Event
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Event Processing
        </Typography>
        <Typography variant="body1" paragraph>
          Events are the foundation of the Blueprint Graph system. When you submit an event, the following process occurs:
        </Typography>
        
        <Box component="ol" sx={{ pl: 2 }}>
          <Box component="li" sx={{ mb: 1 }}>
            <Typography variant="body1">
              <strong>Parsing:</strong> The event is parsed based on its source format (JSON, Syslog, CEF, etc.).
            </Typography>
          </Box>
          <Box component="li" sx={{ mb: 1 }}>
            <Typography variant="body1">
              <strong>OCSF Mapping:</strong> The parsed event is mapped to the Open Cybersecurity Schema Framework (OCSF) format for standardization.
            </Typography>
          </Box>
          <Box component="li" sx={{ mb: 1 }}>
            <Typography variant="body1">
              <strong>Graph Storage:</strong> The event and its related entities (IPs, users, hosts, etc.) are stored in the Neo4j graph database, creating relationships between them.
            </Typography>
          </Box>
          <Box component="li">
            <Typography variant="body1">
              <strong>Detection:</strong> Detection rules can be run against the stored events to generate alerts for potential security issues.
            </Typography>
          </Box>
        </Box>
        
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Supported Formats
          </Typography>
          <Box component="ul" sx={{ pl: 2 }}>
            <Box component="li">
              <Typography variant="body1">
                <strong>JSON:</strong> Structured JSON data from various sources
              </Typography>
            </Box>
            <Box component="li">
              <Typography variant="body1">
                <strong>Syslog:</strong> Standard syslog format
              </Typography>
            </Box>
            <Box component="li">
              <Typography variant="body1">
                <strong>CEF:</strong> Common Event Format
              </Typography>
            </Box>
            <Box component="li">
              <Typography variant="body1">
                <strong>LEEF:</strong> Log Event Extended Format
              </Typography>
            </Box>
            <Box component="li">
              <Typography variant="body1">
                <strong>Raw Text:</strong> Unstructured text logs
              </Typography>
            </Box>
          </Box>
        </Box>
        
        <Box mt={3} display="flex" justifyContent="center">
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenEventForm}
            size="large"
          >
            Submit New Event
          </Button>
        </Box>
      </Paper>
      
      <EventForm open={openEventForm} onClose={handleCloseEventForm} />
      
      {/* Mobile FAB */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          display: { xs: 'flex', md: 'none' }
        }}
        onClick={handleOpenEventForm}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default Events; 