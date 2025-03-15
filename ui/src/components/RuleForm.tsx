import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControlLabel,
  Switch,
  Slider,
  Typography,
  Box,
  Chip,
  InputAdornment,
  IconButton,
  Autocomplete
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { Rule, CreateRuleRequest, UpdateRuleRequest } from '../types/api';
import { useCreateRule, useUpdateRule } from '../hooks/useApi';

interface RuleFormProps {
  open: boolean;
  onClose: () => void;
  initialRule?: Rule;
}

const defaultRule: CreateRuleRequest = {
  name: '',
  description: '',
  severity: 5,
  query: '',
  tags: [],
  mitre_techniques: [],
  enabled: true
};

const RuleForm: React.FC<RuleFormProps> = ({ open, onClose, initialRule }) => {
  const [rule, setRule] = useState<CreateRuleRequest>(defaultRule);
  const [tagInput, setTagInput] = useState('');
  const [techniqueInput, setTechniqueInput] = useState('');
  
  const createRuleMutation = useCreateRule();
  const updateRuleMutation = useUpdateRule();
  
  // Reset form when dialog opens/closes or initialRule changes
  useEffect(() => {
    if (initialRule) {
      setRule({
        name: initialRule.name,
        description: initialRule.description,
        severity: initialRule.severity,
        query: initialRule.query,
        tags: [...initialRule.tags],
        mitre_techniques: [...initialRule.mitre_techniques],
        enabled: initialRule.enabled
      });
    } else {
      setRule(defaultRule);
    }
    setTagInput('');
    setTechniqueInput('');
  }, [open, initialRule]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setRule(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSeverityChange = (_: Event, value: number | number[]) => {
    setRule(prev => ({ ...prev, severity: value as number }));
  };
  
  const handleEnabledChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRule(prev => ({ ...prev, enabled: e.target.checked }));
  };
  
  const handleAddTag = () => {
    if (tagInput.trim() && !rule.tags.includes(tagInput.trim())) {
      setRule(prev => ({ ...prev, tags: [...prev.tags, tagInput.trim()] }));
      setTagInput('');
    }
  };
  
  const handleDeleteTag = (tagToDelete: string) => {
    setRule(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToDelete)
    }));
  };
  
  const handleAddTechnique = () => {
    if (techniqueInput.trim() && !rule.mitre_techniques.includes(techniqueInput.trim())) {
      setRule(prev => ({ ...prev, mitre_techniques: [...prev.mitre_techniques, techniqueInput.trim()] }));
      setTechniqueInput('');
    }
  };
  
  const handleDeleteTechnique = (techniqueToDelete: string) => {
    setRule(prev => ({
      ...prev,
      mitre_techniques: prev.mitre_techniques.filter(technique => technique !== techniqueToDelete)
    }));
  };
  
  const handleSubmit = () => {
    if (initialRule) {
      const updatePayload: UpdateRuleRequest = {
        id: initialRule.id,
        ...rule
      };
      updateRuleMutation.mutate(updatePayload, {
        onSuccess: () => {
          onClose();
        }
      });
    } else {
      createRuleMutation.mutate(rule, {
        onSuccess: () => {
          onClose();
        }
      });
    }
  };
  
  const isSubmitDisabled = !rule.name || !rule.query || rule.severity < 1 || rule.severity > 10;
  
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>{initialRule ? 'Edit Rule' : 'Create New Rule'}</DialogTitle>
      <DialogContent>
        <TextField
          name="name"
          label="Rule Name"
          value={rule.name}
          onChange={handleChange}
          fullWidth
          margin="normal"
          required
        />
        
        <TextField
          name="description"
          label="Description"
          value={rule.description}
          onChange={handleChange}
          fullWidth
          margin="normal"
          multiline
          rows={2}
        />
        
        <Box mt={2}>
          <Typography gutterBottom>Severity (1-10)</Typography>
          <Slider
            value={rule.severity}
            onChange={handleSeverityChange}
            min={1}
            max={10}
            step={1}
            marks
            valueLabelDisplay="auto"
          />
        </Box>
        
        <TextField
          name="query"
          label="Cypher Query"
          value={rule.query}
          onChange={handleChange}
          fullWidth
          margin="normal"
          multiline
          rows={4}
          required
          placeholder="MATCH (n) WHERE ... RETURN n"
          InputProps={{
            style: { fontFamily: 'monospace' }
          }}
        />
        
        <Box mt={2}>
          <Typography gutterBottom>Tags</Typography>
          <Box display="flex" alignItems="center" mb={1}>
            <TextField
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              placeholder="Add tag"
              size="small"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddTag();
                }
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleAddTag} edge="end" size="small">
                      <AddIcon />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
          </Box>
          <Box display="flex" flexWrap="wrap" gap={0.5}>
            {rule.tags.map((tag) => (
              <Chip
                key={tag}
                label={tag}
                onDelete={() => handleDeleteTag(tag)}
                size="small"
              />
            ))}
          </Box>
        </Box>
        
        <Box mt={2}>
          <Typography gutterBottom>MITRE ATT&CK Techniques</Typography>
          <Box display="flex" alignItems="center" mb={1}>
            <Autocomplete
              freeSolo
              options={[
                'T1078', 'T1059', 'T1027', 'T1486', 'T1048', 
                'T1567', 'T1110', 'T1566', 'T1190', 'T1133'
              ]}
              inputValue={techniqueInput}
              onInputChange={(_, value) => setTechniqueInput(value)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder="Add technique (e.g., T1078)"
                  size="small"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddTechnique();
                    }
                  }}
                />
              )}
              size="small"
              style={{ width: 300 }}
            />
            <IconButton onClick={handleAddTechnique} size="small" sx={{ ml: 1 }}>
              <AddIcon />
            </IconButton>
          </Box>
          <Box display="flex" flexWrap="wrap" gap={0.5}>
            {rule.mitre_techniques.map((technique) => (
              <Chip
                key={technique}
                label={technique}
                onDelete={() => handleDeleteTechnique(technique)}
                size="small"
              />
            ))}
          </Box>
        </Box>
        
        <Box mt={2}>
          <FormControlLabel
            control={
              <Switch
                checked={rule.enabled}
                onChange={handleEnabledChange}
                color="primary"
              />
            }
            label="Enabled"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          color="primary"
          disabled={isSubmitDisabled || createRuleMutation.isPending || updateRuleMutation.isPending}
        >
          {initialRule ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RuleForm; 