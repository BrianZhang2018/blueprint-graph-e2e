import React from 'react';
import { 
  Typography, 
  Grid, 
  Paper, 
  Box, 
  Button, 
  Card, 
  CardContent,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  Notifications as AlertsIcon,
  Code as RulesIcon,
  Event as EventsIcon,
  PlayArrow as RunIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useRules, useAlerts, useRunDetection } from '../hooks/useApi';
import SeverityBadge from '../components/SeverityBadge';
import { formatDate } from '../utils/formatters';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: rules, isLoading: isLoadingRules } = useRules();
  const { data: alerts, isLoading: isLoadingAlerts } = useAlerts();
  const runDetectionMutation = useRunDetection();

  const handleRunDetection = () => {
    runDetectionMutation.mutate();
  };

  const enabledRulesCount = rules?.filter(rule => rule.enabled).length || 0;
  const disabledRulesCount = rules?.length ? rules.length - enabledRulesCount : 0;

  const criticalAlertsCount = alerts?.filter(alert => alert.severity >= 9).length || 0;
  const highAlertsCount = alerts?.filter(alert => alert.severity >= 7 && alert.severity < 9).length || 0;
  const mediumAlertsCount = alerts?.filter(alert => alert.severity >= 5 && alert.severity < 7).length || 0;
  const lowAlertsCount = alerts?.filter(alert => alert.severity < 5).length || 0;

  const latestAlerts = alerts?.slice(0, 5) || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<RunIcon />}
          onClick={handleRunDetection}
          disabled={runDetectionMutation.isPending}
        >
          {runDetectionMutation.isPending ? 'Running...' : 'Run Detection'}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Box display="flex" alignItems="center" mb={2}>
              <RulesIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Detection Rules</Typography>
            </Box>
            {isLoadingRules ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Enabled Rules</Typography>
                  <Typography variant="body1" fontWeight="bold" color="primary">
                    {enabledRulesCount}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Disabled Rules</Typography>
                  <Typography variant="body1" fontWeight="bold" color="text.secondary">
                    {disabledRulesCount}
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Button 
                  variant="outlined" 
                  fullWidth
                  onClick={() => navigate('/rules')}
                >
                  View Rules
                </Button>
              </>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Box display="flex" alignItems="center" mb={2}>
              <AlertsIcon color="error" sx={{ mr: 1 }} />
              <Typography variant="h6">Alerts</Typography>
            </Box>
            {isLoadingAlerts ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Critical</Typography>
                  <Typography variant="body1" fontWeight="bold" color="error">
                    {criticalAlertsCount}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">High</Typography>
                  <Typography variant="body1" fontWeight="bold" color="#f44336">
                    {highAlertsCount}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Medium</Typography>
                  <Typography variant="body1" fontWeight="bold" color="#ff9800">
                    {mediumAlertsCount}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Low</Typography>
                  <Typography variant="body1" fontWeight="bold" color="#2196f3">
                    {lowAlertsCount}
                  </Typography>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Button 
                  variant="outlined" 
                  fullWidth
                  onClick={() => navigate('/alerts')}
                >
                  View Alerts
                </Button>
              </>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Box display="flex" alignItems="center" mb={2}>
              <EventsIcon color="info" sx={{ mr: 1 }} />
              <Typography variant="h6">Events</Typography>
            </Box>
            <Typography variant="body2" paragraph>
              Submit new events to be processed by the system. Events will be parsed, mapped to OCSF format, and stored in the graph database.
            </Typography>
            <Button 
              variant="outlined" 
              fullWidth
              onClick={() => navigate('/events')}
              sx={{ mt: 'auto' }}
            >
              Submit Events
            </Button>
          </Paper>
        </Grid>

        {/* Latest Alerts */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Latest Alerts
            </Typography>
            {isLoadingAlerts ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : latestAlerts.length > 0 ? (
              <Grid container spacing={2}>
                {latestAlerts.map((alert) => (
                  <Grid item xs={12} key={alert.id}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                          <Box>
                            <Typography variant="h6">{alert.rule_name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(alert.created_at)}
                            </Typography>
                          </Box>
                          <SeverityBadge severity={alert.severity} />
                        </Box>
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          {alert.description.length > 100
                            ? `${alert.description.substring(0, 100)}...`
                            : alert.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                No alerts found. Run detection to generate alerts.
              </Typography>
            )}
            {alerts && alerts.length > 5 && (
              <Box display="flex" justifyContent="center" mt={2}>
                <Button 
                  variant="text" 
                  onClick={() => navigate('/alerts')}
                >
                  View All Alerts
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 