export interface User {
  id: number;
  email: string;
  name: string;
  role: 'manager' | 'employee';
  manager_id?: number;
}

export interface Employee {
  id: number;
  name: string;
  email: string;
  feedback_count: number;
  last_feedback_date?: string;
  avg_sentiment: number;
}

export interface Feedback {
  id: number;
  employee_id: number;
  manager_id: number;
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

export interface FeedbackRequest {
  employee_id: number;
  message: string;
  created_at: string;
  status: 'pending' | 'completed';
}

export interface DashboardStats {
  total_employees: number;
  total_feedback: number;
  pending_requests: number;
  sentiment_distribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
}