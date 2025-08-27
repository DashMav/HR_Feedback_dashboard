export interface User {
  id: number;
  email: string;
  name: string;
  role: 'owner' | 'admin' | 'manager' | 'employee';
  organization_id: number;
  manager_id?: number;
  is_active: boolean;
  last_login?: string;
}

export interface Organization {
  id: number;
  name: string;
  domain?: string;
  created_at: string;
  is_active: boolean;
}

export interface Employee {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  feedback_count: number;
  last_feedback_date?: string;
  avg_sentiment: number;
}

export interface Feedback {
  id: number;
  employee_id: number;
  manager_id: number;
  organization_id: number;
  strengths: string;
  improvements: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  tags: string[];
  created_at: string;
  updated_at: string;
  acknowledged: boolean;
  employee_comment?: string;
  employee_name: string;
  manager_name: string;
}

export interface Invitation {
  id: number;
  email: string;
  role: string;
  expires_at: string;
  accepted_at?: string;
  created_at: string;
  invited_by_name: string;
}

export interface DashboardStats {
  total_employees: number;
  total_feedback: number;
  pending_invitations: number;
  sentiment_distribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
}