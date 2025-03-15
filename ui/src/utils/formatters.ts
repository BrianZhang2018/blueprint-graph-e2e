import { format, parseISO } from 'date-fns';

// Format date string to a readable format
export const formatDate = (dateString: string): string => {
  try {
    return format(parseISO(dateString), 'MMM d, yyyy h:mm a');
  } catch (error) {
    return dateString;
  }
};

// Format severity level to text and color
export const formatSeverity = (severity: number): { text: string; color: string } => {
  if (severity >= 9) {
    return { text: 'Critical', color: '#d32f2f' };
  } else if (severity >= 7) {
    return { text: 'High', color: '#f44336' };
  } else if (severity >= 5) {
    return { text: 'Medium', color: '#ff9800' };
  } else if (severity >= 3) {
    return { text: 'Low', color: '#2196f3' };
  } else {
    return { text: 'Info', color: '#4caf50' };
  }
};

// Truncate long text with ellipsis
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

// Format JSON for display
export const formatJson = (json: any): string => {
  try {
    return JSON.stringify(json, null, 2);
  } catch (error) {
    return String(json);
  }
};

// Convert camelCase or snake_case to Title Case
export const toTitleCase = (str: string): string => {
  return str
    .replace(/([A-Z])/g, ' $1') // Insert a space before all capital letters
    .replace(/_/g, ' ') // Replace underscores with spaces
    .replace(/^\w/, (c) => c.toUpperCase()) // Capitalize the first letter
    .replace(/\s+(\w)/g, (_, c) => ' ' + c.toUpperCase()); // Capitalize all words
};

// Format bytes to human-readable format
export const formatBytes = (bytes: number, decimals = 2): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}; 