// API Response Types
export interface Rule {
  id: string;
  name: string;
  description: string;
  severity: number;
  query: string;
  tags: string[];
  mitre_techniques: string[];
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface Event {
  id: string;
  class_uid: string;
  category_uid: string;
  time: string;
  severity: number;
  raw_data: string;
  source_format: string;
  metadata: Record<string, any>;
}

export interface Entity {
  id: string;
  type: string;
  properties: Record<string, any>;
}

export interface Alert {
  id: string;
  rule_id: string;
  rule_name: string;
  severity: number;
  created_at: string;
  entities: Entity[];
  description: string;
  mitre_techniques: string[];
}

// API Request Types
export interface CreateRuleRequest {
  name: string;
  description: string;
  severity: number;
  query: string;
  tags: string[];
  mitre_techniques: string[];
  enabled: boolean;
}

export interface UpdateRuleRequest extends Partial<CreateRuleRequest> {
  id: string;
}

export interface CreateEventRequest {
  raw_data: string;
  source_format?: string;
  metadata?: Record<string, any>;
}

export interface RunDetectionRequest {
  rule_id?: string;
}

// API Filter Types
export interface RuleFilters {
  enabled?: boolean;
  tag?: string;
}

export interface AlertFilters {
  severity?: number;
  rule_id?: string;
  start_date?: string;
  end_date?: string;
} 