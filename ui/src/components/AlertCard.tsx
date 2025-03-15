import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip, 
  Collapse, 
  IconButton, 
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Rule as RuleIcon,
  AccessTime as TimeIcon,
  Label as LabelIcon
} from '@mui/icons-material';
import { Alert, Entity } from '../types/api';
import SeverityBadge from './SeverityBadge';
import { formatDate, truncateText } from '../utils/formatters';

interface AlertCardProps {
  alert: Alert;
}

const AlertCard: React.FC<AlertCardProps> = ({ alert }) => {
  const [expanded, setExpanded] = useState(false);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <Card 
      sx={{ 
        mb: 2, 
        borderLeft: '4px solid', 
        borderColor: formatSeverity(alert.severity).color 
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="h6" component="div">
              {alert.rule_name}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              <TimeIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
              {formatDate(alert.created_at)}
            </Typography>
          </Box>
          <Box>
            <SeverityBadge severity={alert.severity} />
          </Box>
        </Box>
        
        <Typography variant="body2" sx={{ mt: 1 }}>
          {truncateText(alert.description, expanded ? 1000 : 100)}
        </Typography>
        
        <Box display="flex" mt={1} flexWrap="wrap" gap={0.5}>
          {alert.mitre_techniques.map((technique) => (
            <Chip 
              key={technique} 
              label={technique} 
              size="small" 
              icon={<LabelIcon />} 
              variant="outlined" 
            />
          ))}
        </Box>
        
        <Box display="flex" justifyContent="flex-end" mt={1}>
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
            Entities
          </Typography>
          <Grid container spacing={2}>
            {alert.entities.map((entity, index) => (
              <Grid item xs={12} md={6} key={`${entity.id}-${index}`}>
                <EntityCard entity={entity} />
              </Grid>
            ))}
          </Grid>
          
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              <RuleIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
              Rule ID: {alert.rule_id}
            </Typography>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

interface EntityCardProps {
  entity: Entity;
}

const EntityCard: React.FC<EntityCardProps> = ({ entity }) => {
  return (
    <Card variant="outlined" sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="subtitle2" gutterBottom>
          {entity.type}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          ID: {entity.id}
        </Typography>
        <List dense>
          {Object.entries(entity.properties).map(([key, value]) => (
            <ListItem key={key} disablePadding>
              <ListItemText 
                primary={`${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`}
                primaryTypographyProps={{ 
                  variant: 'body2',
                  sx: { 
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }
                }}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default AlertCard; 