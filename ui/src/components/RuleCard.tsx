import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip, 
  Switch, 
  IconButton, 
  Collapse,
  Divider,
  Button
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  PlayArrow as RunIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Label as TagIcon
} from '@mui/icons-material';
import { Rule } from '../types/api';
import SeverityBadge from './SeverityBadge';
import { formatDate } from '../utils/formatters';
import { useUpdateRule, useRunDetection } from '../hooks/useApi';

interface RuleCardProps {
  rule: Rule;
  onEdit?: (rule: Rule) => void;
  onDelete?: (rule: Rule) => void;
}

const RuleCard: React.FC<RuleCardProps> = ({ rule, onEdit, onDelete }) => {
  const [expanded, setExpanded] = useState(false);
  const updateRuleMutation = useUpdateRule();
  const runDetectionMutation = useRunDetection();

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleToggleEnabled = () => {
    updateRuleMutation.mutate({
      id: rule.id,
      enabled: !rule.enabled
    });
  };

  const handleRunRule = () => {
    runDetectionMutation.mutate(rule.id);
  };

  return (
    <Card 
      sx={{ 
        mb: 2, 
        borderLeft: '4px solid', 
        borderColor: rule.enabled ? '#4caf50' : '#9e9e9e' 
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="h6" component="div">
              {rule.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Last updated: {formatDate(rule.updated_at)}
            </Typography>
          </Box>
          <Box display="flex" alignItems="center">
            <SeverityBadge severity={rule.severity} />
            <Switch
              checked={rule.enabled}
              onChange={handleToggleEnabled}
              color="primary"
              size="small"
              sx={{ ml: 1 }}
              disabled={updateRuleMutation.isPending}
            />
          </Box>
        </Box>
        
        <Typography variant="body2" sx={{ mt: 1 }}>
          {rule.description}
        </Typography>
        
        <Box display="flex" mt={1} flexWrap="wrap" gap={0.5}>
          {rule.tags.map((tag) => (
            <Chip 
              key={tag} 
              label={tag} 
              size="small" 
              icon={<TagIcon />} 
              variant="outlined" 
            />
          ))}
        </Box>
        
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
          <Box>
            <Button
              startIcon={<RunIcon />}
              size="small"
              variant="outlined"
              onClick={handleRunRule}
              disabled={!rule.enabled || runDetectionMutation.isPending}
              sx={{ mr: 1 }}
            >
              Run Rule
            </Button>
            {onEdit && (
              <IconButton 
                size="small" 
                onClick={() => onEdit(rule)}
                sx={{ mr: 0.5 }}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            )}
            {onDelete && (
              <IconButton 
                size="small" 
                onClick={() => onDelete(rule)}
                color="error"
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            )}
          </Box>
          <IconButton
            onClick={handleExpandClick}
            aria-expanded={expanded}
            aria-label="show more"
            size="small"
          >
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle2" gutterBottom>
            Query
          </Typography>
          <Box 
            sx={{ 
              p: 1, 
              backgroundColor: '#f5f5f5', 
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              overflowX: 'auto'
            }}
          >
            <pre style={{ margin: 0 }}>{rule.query}</pre>
          </Box>
          
          {rule.mitre_techniques.length > 0 && (
            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                MITRE ATT&CK Techniques
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={0.5}>
                {rule.mitre_techniques.map((technique) => (
                  <Chip 
                    key={technique} 
                    label={technique} 
                    size="small" 
                    variant="outlined" 
                  />
                ))}
              </Box>
            </Box>
          )}
          
          <Box mt={2}>
            <Typography variant="body2" color="text.secondary">
              Rule ID: {rule.id}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Created: {formatDate(rule.created_at)}
            </Typography>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default RuleCard; 