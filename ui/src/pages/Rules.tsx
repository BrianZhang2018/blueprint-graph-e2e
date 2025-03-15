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
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Pagination,
  Fab
} from '@mui/material';
import { 
  Search as SearchIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { useRules, useDeleteRule } from '../hooks/useApi';
import RuleCard from '../components/RuleCard';
import RuleForm from '../components/RuleForm';
import { Rule, RuleFilters } from '../types/api';

const Rules: React.FC = () => {
  const [filters, setFilters] = useState<RuleFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 5;
  
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [editRule, setEditRule] = useState<Rule | null>(null);
  const [deleteRule, setDeleteRule] = useState<Rule | null>(null);
  
  const { data: rules, isLoading: isLoadingRules } = useRules(filters);
  const deleteRuleMutation = useDeleteRule();

  // Filter rules by search term (name or description)
  const filteredRules = rules?.filter(rule => 
    rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    rule.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  // Paginate rules
  const paginatedRules = filteredRules.slice((page - 1) * pageSize, page * pageSize);
  const totalPages = Math.ceil(filteredRules.length / pageSize);

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
  
  const handleOpenCreateDialog = () => {
    setOpenCreateDialog(true);
  };
  
  const handleCloseCreateDialog = () => {
    setOpenCreateDialog(false);
  };
  
  const handleEditRule = (rule: Rule) => {
    setEditRule(rule);
  };
  
  const handleCloseEditDialog = () => {
    setEditRule(null);
  };
  
  const handleDeleteRule = (rule: Rule) => {
    setDeleteRule(rule);
  };
  
  const handleConfirmDelete = () => {
    if (deleteRule) {
      deleteRuleMutation.mutate(deleteRule.id, {
        onSuccess: () => {
          setDeleteRule(null);
        }
      });
    }
  };
  
  const handleCancelDelete = () => {
    setDeleteRule(null);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Detection Rules
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenCreateDialog}
        >
          Create Rule
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search rules..."
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
              <InputLabel>Status</InputLabel>
              <Select
                name="enabled"
                value={filters.enabled === undefined ? 'all' : filters.enabled}
                onChange={handleFilterChange}
                label="Status"
              >
                <MenuItem value="all">All Rules</MenuItem>
                <MenuItem value={true}>Enabled</MenuItem>
                <MenuItem value={false}>Disabled</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Tag</InputLabel>
              <Select
                name="tag"
                value={filters.tag || 'all'}
                onChange={handleFilterChange}
                label="Tag"
              >
                <MenuItem value="all">All Tags</MenuItem>
                {/* Get unique tags from all rules */}
                {Array.from(new Set(rules?.flatMap(rule => rule.tags) || [])).map(tag => (
                  <MenuItem key={tag} value={tag}>
                    {tag}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {isLoadingRules ? (
        <Box display="flex" justifyContent="center" p={5}>
          <CircularProgress />
        </Box>
      ) : paginatedRules.length > 0 ? (
        <>
          {paginatedRules.map(rule => (
            <RuleCard 
              key={rule.id} 
              rule={rule} 
              onEdit={handleEditRule}
              onDelete={handleDeleteRule}
            />
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
            No rules found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {Object.keys(filters).length > 0 || searchTerm
              ? 'Try adjusting your filters or search term'
              : 'Create a new rule to get started'}
          </Typography>
          {!(Object.keys(filters).length > 0 || searchTerm) && (
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<AddIcon />}
              onClick={handleOpenCreateDialog}
              sx={{ mt: 2 }}
            >
              Create Rule
            </Button>
          )}
        </Paper>
      )}
      
      {/* Create Rule Dialog */}
      <RuleForm 
        open={openCreateDialog} 
        onClose={handleCloseCreateDialog} 
      />
      
      {/* Edit Rule Dialog */}
      {editRule && (
        <RuleForm 
          open={!!editRule} 
          onClose={handleCloseEditDialog}
          initialRule={editRule}
        />
      )}
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={!!deleteRule}
        onClose={handleCancelDelete}
      >
        <DialogTitle>Delete Rule</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the rule "{deleteRule?.name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete}>Cancel</Button>
          <Button 
            onClick={handleConfirmDelete} 
            color="error"
            disabled={deleteRuleMutation.isPending}
          >
            {deleteRuleMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Mobile FAB for creating rules */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          display: { xs: 'flex', md: 'none' }
        }}
        onClick={handleOpenCreateDialog}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

export default Rules; 