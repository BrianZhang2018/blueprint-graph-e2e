import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { useCreateEvent } from '../hooks/useApi';
import { formatJson } from '../utils/formatters';

interface EventFormProps {
  open: boolean;
  onClose: () => void;
}

const EventForm: React.FC<EventFormProps> = ({ open, onClose }) => {
  const [rawData, setRawData] = useState('');
  const [sourceFormat, setSourceFormat] = useState('json');
  const [validationError, setValidationError] = useState<string | null>(null);
  
  const createEventMutation = useCreateEvent();
  
  const handleRawDataChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setRawData(e.target.value);
    setValidationError(null);
  };
  
  const handleSourceFormatChange = (e: React.ChangeEvent<{ value: unknown }>) => {
    setSourceFormat(e.target.value as string);
  };
  
  const validateData = (): boolean => {
    if (!rawData.trim()) {
      setValidationError('Event data cannot be empty');
      return false;
    }
    
    if (sourceFormat === 'json') {
      try {
        JSON.parse(rawData);
      } catch (error) {
        setValidationError('Invalid JSON format');
        return false;
      }
    }
    
    return true;
  };
  
  const handleSubmit = () => {
    if (!validateData()) return;
    
    createEventMutation.mutate(
      {
        raw_data: rawData,
        source_format: sourceFormat
      },
      {
        onSuccess: () => {
          onClose();
          setRawData('');
          setSourceFormat('json');
          setValidationError(null);
        },
        onError: (error: any) => {
          setValidationError(error.message || 'Failed to create event');
        }
      }
    );
  };
  
  const handleFormatJson = () => {
    if (sourceFormat === 'json') {
      try {
        const formatted = formatJson(JSON.parse(rawData));
        setRawData(formatted);
        setValidationError(null);
      } catch (error) {
        setValidationError('Invalid JSON format');
      }
    }
  };
  
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Submit New Event</DialogTitle>
      <DialogContent>
        <Box mb={2}>
          <Typography variant="body2" color="text.secondary">
            Submit a new event to be processed by the system. The event will be parsed, mapped to OCSF format, and stored in the graph database.
          </Typography>
        </Box>
        
        <FormControl fullWidth margin="normal">
          <InputLabel>Source Format</InputLabel>
          <Select
            value={sourceFormat}
            onChange={handleSourceFormatChange}
            label="Source Format"
          >
            <MenuItem value="json">JSON</MenuItem>
            <MenuItem value="syslog">Syslog</MenuItem>
            <MenuItem value="cef">CEF</MenuItem>
            <MenuItem value="leef">LEEF</MenuItem>
            <MenuItem value="raw">Raw Text</MenuItem>
          </Select>
        </FormControl>
        
        <TextField
          label="Event Data"
          value={rawData}
          onChange={handleRawDataChange}
          fullWidth
          margin="normal"
          multiline
          rows={10}
          required
          placeholder={sourceFormat === 'json' ? '{\n  "key": "value"\n}' : 'Enter event data...'}
          InputProps={{
            style: { fontFamily: 'monospace' }
          }}
        />
        
        {sourceFormat === 'json' && (
          <Box mt={1}>
            <Button 
              variant="outlined" 
              size="small" 
              onClick={handleFormatJson}
            >
              Format JSON
            </Button>
          </Box>
        )}
        
        {validationError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {validationError}
          </Alert>
        )}
        
        {createEventMutation.isSuccess && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Event created successfully!
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          color="primary"
          disabled={createEventMutation.isPending || !rawData.trim()}
          startIcon={createEventMutation.isPending ? <CircularProgress size={20} /> : undefined}
        >
          Submit
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EventForm; 