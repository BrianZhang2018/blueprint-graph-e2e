import React, { useState } from 'react';
import { 
  Typography, 
  Box, 
  TextField, 
  MenuItem, 
  Grid, 
  Paper, 
  InputAdornment,
  CircularProgress,
  Button,
  FormControl,
  InputLabel,
  Select,
  Pagination
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useAlerts, useRules } from '../hooks/useApi';
import AlertCard from '../components/AlertCard';
import { Alert, AlertFilters } from '../types/api';

const Alerts: React.FC = () => {
  const [filters, setFilters] = useState<AlertFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { data: alerts, isLoading: isLoadingAlerts } = useAlerts(filters);
  const { data: rules } = useRules();

  // Filter alerts by search term (rule name or description)
  const filteredAlerts = alerts?.filter(alert => 
    alert.rule_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    alert.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  // Paginate alerts
  const paginatedAlerts = filteredAlerts.slice((page - 1) * pageSize, page * pageSize);
  const totalPages = Math.ceil(filteredAlerts.length / pageSize);

  const handleFilterChange = (e: React.ChangeEvent<{ name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    if (name) {
      setFilters(prev => ({
        ...prev,
        [name]: value === 'all' ? undefined : value
      }));
      setPage(1);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setPage(1);
  };

  const handlePageChange = (_: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleClearFilters = () => {
    setFilters({});
    setSearchTerm('');
    setPage(1);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Alerts
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search alerts..."
              value={searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Severity</InputLabel>
              <Select
                name="severity"
                value={filters.severity || 'all'}
                onChange={handleFilterChange}
                label="Severity"
              >
                <MenuItem value="all">All Severities</MenuItem>
                <MenuItem value={9}>Critical (9-10)</MenuItem>
                <MenuItem value={7}>High (7-8)</MenuItem>
                <MenuItem value={5}>Medium (5-6)</MenuItem>
                <MenuItem value={3}>Low (3-4)</MenuItem>
                <MenuItem value={1}>Info (1-2)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Rule</InputLabel>
              <Select
                name="rule_id"
                value={filters.rule_id || 'all'}
                onChange={handleFilterChange}
                label="Rule"
              >
                <MenuItem value="all">All Rules</MenuItem>
                {rules?.map(rule => (
                  <MenuItem key={rule.id} value={rule.id}>
                    {rule.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button 
              variant="outlined" 
              fullWidth
              onClick={handleClearFilters}
            >
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {isLoadingAlerts ? (
        <Box display="flex" justifyContent="center" p={5}>
          <CircularProgress />
        </Box>
      ) : paginatedAlerts.length > 0 ? (
        <>
          {paginatedAlerts.map(alert => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
          
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={3}>
              <Pagination 
                count={totalPages} 
                page={page} 
                onChange={handlePageChange} 
                color="primary" 
              />
            </Box>
          )}
        </>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No alerts found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {Object.keys(filters).length > 0 || searchTerm
              ? 'Try adjusting your filters or search term'
              : 'Run detection to generate alerts'}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default Alerts; 