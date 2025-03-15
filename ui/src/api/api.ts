import axios from 'axios';
import { 
  Rule, 
  Event, 
  Alert, 
  CreateRuleRequest, 
  UpdateRuleRequest, 
  CreateEventRequest,
  RunDetectionRequest,
  RuleFilters,
  AlertFilters
} from '../types/api';

// Create axios instance with base URL
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Rules API
export const getRules = async (filters?: RuleFilters): Promise<Rule[]> => {
  const { data } = await api.get('/rules', { params: filters });
  return data;
};

export const getRule = async (id: string): Promise<Rule> => {
  const { data } = await api.get(`/rules/${id}`);
  return data;
};

export const createRule = async (rule: CreateRuleRequest): Promise<Rule> => {
  const { data } = await api.post('/rules', rule);
  return data;
};

export const updateRule = async (rule: UpdateRuleRequest): Promise<Rule> => {
  const { data } = await api.put(`/rules/${rule.id}`, rule);
  return data;
};

export const deleteRule = async (id: string): Promise<void> => {
  await api.delete(`/rules/${id}`);
};

// Events API
export const createEvent = async (event: CreateEventRequest): Promise<Event> => {
  const { data } = await api.post('/events', event);
  return data;
};

export const getEvent = async (id: string): Promise<Event> => {
  const { data } = await api.get(`/events/${id}`);
  return data;
};

// Detection API
export const runDetection = async (params?: RunDetectionRequest): Promise<Alert[]> => {
  const { data } = await api.post('/run-detection', params || {});
  return data;
};

export const runDetectionRule = async (ruleId: string): Promise<Alert[]> => {
  const { data } = await api.post(`/rules/${ruleId}/run`);
  return data;
};

// Alerts API
export const getAlerts = async (filters?: AlertFilters): Promise<Alert[]> => {
  const { data } = await api.get('/alerts', { params: filters });
  return data;
};

// Health check
export const getHealth = async (): Promise<{ status: string }> => {
  const { data } = await api.get('/health');
  return data;
};

export interface GraphQueryResponse {
  nodes: Array<{
    id: string;
    labels: string[];
    properties: Record<string, any>;
  }>;
  relationships: Array<{
    id: string;
    type: string;
    start: string;
    end: string;
    properties: Record<string, any>;
  }>;
}

export const executeGraphQuery = async (query: string): Promise<GraphQueryResponse> => {
  const response = await api.post<GraphQueryResponse>('/graph/query', { query });
  return response.data;
};

export default api; 