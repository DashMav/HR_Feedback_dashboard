import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import { Employee, DashboardStats, Feedback } from '../types';
import ManagerDashboard from './ManagerDashboard';
import EmployeeDashboard from './EmployeeDashboard';

export default function Dashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [feedback, setFeedback] = useState<Feedback[]>([]);

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      if (user?.role === 'manager') {
        const [employeesRes, statsRes] = await Promise.all([
          api.get('/employees'),
          api.get('/dashboard/stats')
        ]);
        setEmployees(employeesRes.data);
        setStats(statsRes.data);
      } else {
        const feedbackRes = await api.get('/feedback/received');
        setFeedback(feedbackRes.data);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      {user?.role === 'manager' ? (
        <ManagerDashboard 
          employees={employees} 
          stats={stats} 
          onRefresh={fetchDashboardData}
        />
      ) : (
        <EmployeeDashboard 
          feedback={feedback} 
          onRefresh={fetchDashboardData}
        />
      )}
    </div>
  );
}