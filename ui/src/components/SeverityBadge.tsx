import React from 'react';
import { Chip, ChipProps } from '@mui/material';
import { formatSeverity } from '../utils/formatters';

interface SeverityBadgeProps {
  severity: number;
  size?: ChipProps['size'];
}

const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, size = 'small' }) => {
  const { text, color } = formatSeverity(severity);
  
  return (
    <Chip
      label={text}
      size={size}
      sx={{
        backgroundColor: `${color}20`, // 20% opacity
        color: color,
        fontWeight: 'bold',
        borderColor: color,
        border: '1px solid'
      }}
    />
  );
};

export default SeverityBadge; 