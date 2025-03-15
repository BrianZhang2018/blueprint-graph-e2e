import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from '../api/api';
import { 
  Rule, 
  Alert, 
  CreateRuleRequest, 
  UpdateRuleRequest, 
  CreateEventRequest,
  RuleFilters,
  AlertFilters
} from '../types/api';

// Rules hooks
export const useRules = (filters?: RuleFilters) => {
  return useQuery({
    queryKey: ['rules', filters],
    queryFn: () => api.getRules(filters),
  });
};

export const useRule = (id: string) => {
  return useQuery({
    queryKey: ['rule', id],
    queryFn: () => api.getRule(id),
    enabled: !!id,
  });
};

export const useCreateRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (rule: CreateRuleRequest) => api.createRule(rule),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
    },
  });
};

export const useUpdateRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (rule: UpdateRuleRequest) => api.updateRule(rule),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
      queryClient.invalidateQueries({ queryKey: ['rule', data.id] });
    },
  });
};

export const useDeleteRule = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => api.deleteRule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
    },
  });
};

// Events hooks
export const useCreateEvent = () => {
  return useMutation({
    mutationFn: (event: CreateEventRequest) => api.createEvent(event),
  });
};

export const useEvent = (id: string) => {
  return useQuery({
    queryKey: ['event', id],
    queryFn: () => api.getEvent(id),
    enabled: !!id,
  });
};

// Detection hooks
export const useRunDetection = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (ruleId?: string) => 
      ruleId ? api.runDetectionRule(ruleId) : api.runDetection(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
};

// Alerts hooks
export const useAlerts = (filters?: AlertFilters) => {
  return useQuery({
    queryKey: ['alerts', filters],
    queryFn: () => api.getAlerts(filters),
  });
};

// Health check hook
export const useHealth = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: api.getHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}; 