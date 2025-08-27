'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';
import { Building, User, Lock, Mail, ArrowLeft } from 'lucide-react';

export default function Setup() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  // Organization data
  const [orgData, setOrgData] = useState({
    name: '',
    domain: '',
  });

  // User data
  const [userData, setUserData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [createdOrgId, setCreatedOrgId] = useState<number | null>(null);

  const handleOrgSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/organizations', {
        name: orgData.name,
        domain: orgData.domain || null,
      });
      setCreatedOrgId(response.data.id);
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create organization');
    } finally {
      setLoading(false);
    }
  };

  const handleUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (userData.password !== userData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!createdOrgId) {
      setError('Organization not found');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.post(`/auth/register?organization_id=${createdOrgId}`, {
        name: userData.name,
        email: userData.email,
        password: userData.password,
        role: 'owner',
      });
      
      // Redirect to login with success message
      router.push('/login?setup=success');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create user account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-primary-600 rounded-full flex items-center justify-center">
            <Building className="h-6 w-6 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            {step === 1 ? 'Create Organization' : 'Create Admin Account'}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {step === 1 
              ? 'Set up your organization to get started'
              : 'Create your admin account to manage the organization'
            }
          </p>
        </div>

        <div className="card">
          {step === 1 ? (
            <form className="space-y-6" onSubmit={handleOrgSubmit}>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <div className="form-group">
                <label htmlFor="orgName" className="form-label">
                  Organization Name <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    id="orgName"
                    type="text"
                    required
                    className="input pl-10"
                    placeholder="Enter organization name"
                    value={orgData.name}
                    onChange={(e) => setOrgData({ ...orgData, name: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="orgDomain" className="form-label">
                  Email Domain (Optional)
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    id="orgDomain"
                    type="text"
                    className="input pl-10"
                    placeholder="company.com"
                    value={orgData.domain}
                    onChange={(e) => setOrgData({ ...orgData, domain: e.target.value })}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Users with this email domain can be auto-assigned to your organization
                </p>
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => router.push('/login')}
                  className="flex-1 btn btn-secondary"
                >
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  Back to Login
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 btn btn-primary"
                >
                  {loading ? 'Creating...' : 'Continue'}
                </button>
              </div>
            </form>
          ) : (
            <form className="space-y-6" onSubmit={handleUserSubmit}>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                Organization "{orgData.name}" created successfully!
              </div>

              <div className="form-group">
                <label htmlFor="userName" className="form-label">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    id="userName"
                    type="text"
                    required
                    className="input pl-10"
                    placeholder="Enter your full name"
                    value={userData.name}
                    onChange={(e) => setUserData({ ...userData, name: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="userEmail" className="form-label">
                  Email Address <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    id="userEmail"
                    type="email"
                    required
                    className="input pl-10"
                    placeholder="Enter your email"
                    value={userData.email}
                    onChange={(e) => setUserData({ ...userData, email: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="userPassword" className="form-label">
                  Password <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    id="userPassword"
                    type="password"
                    required
                    className="input pl-10"
                    placeholder="Enter password"
                    value={userData.password}
                    onChange={(e) => setUserData({ ...userData, password: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword" className="form-label">
                  Confirm Password <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    id="confirmPassword"
                    type="password"
                    required
                    className="input pl-10"
                    placeholder="Confirm password"
                    value={userData.confirmPassword}
                    onChange={(e) => setUserData({ ...userData, confirmPassword: e.target.value })}
                  />
                </div>
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 btn btn-secondary"
                >
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  Back
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 btn btn-primary"
                >
                  {loading ? 'Creating Account...' : 'Complete Setup'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}