import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { User } from '../types';
import { ArrowLeft, Save, X } from 'lucide-react';

export default function FeedbackForm() {
  const { employeeId, feedbackId } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    strengths: '',
    improvements: '',
    sentiment: 'neutral' as 'positive' | 'neutral' | 'negative',
    tags: [] as string[],
  });
  const [tagInput, setTagInput] = useState('');

  const isEditing = !!feedbackId;

  useEffect(() => {
    if (employeeId) {
      fetchEmployee();
    }
    if (feedbackId) {
      fetchFeedback();
    }
  }, [employeeId, feedbackId]);

  const fetchEmployee = async () => {
    try {
      const response = await api.get(`/employees/${employeeId}`);
      setEmployee(response.data);
    } catch (error) {
      console.error('Failed to fetch employee:', error);
    }
  };

  const fetchFeedback = async () => {
    try {
      const response = await api.get(`/feedback/${feedbackId}`);
      const feedback = response.data;
      setFormData({
        strengths: feedback.strengths,
        improvements: feedback.improvements,
        sentiment: feedback.sentiment,
        tags: feedback.tags || [],
      });
      setEmployee({ id: feedback.employee_id, name: feedback.employee_name } as User);
    } catch (error) {
      console.error('Failed to fetch feedback:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        employee_id: parseInt(employeeId || '0'),
      };

      if (isEditing) {
        await api.put(`/feedback/${feedbackId}`, payload);
      } else {
        await api.post('/feedback', payload);
      }

      navigate('/');
    } catch (error) {
      console.error('Failed to save feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()],
      });
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToRemove),
    });
  };

  const handleTagInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center mb-6">
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-gray-600 hover:text-gray-900 transition-colors mr-4"
        >
          <ArrowLeft className="h-5 w-5 mr-1" />
          Back to Dashboard
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          {isEditing ? 'Edit Feedback' : 'Give Feedback'}
          {employee && <span className="text-gray-600"> for {employee.name}</span>}
        </h1>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="strengths" className="block text-sm font-medium text-gray-700 mb-2">
              Strengths <span className="text-red-500">*</span>
            </label>
            <textarea
              id="strengths"
              required
              rows={4}
              className="input resize-y"
              placeholder="What are this employee's key strengths? (Markdown supported)"
              value={formData.strengths}
              onChange={(e) => setFormData({ ...formData, strengths: e.target.value })}
            />
            <p className="mt-1 text-sm text-gray-500">
              Highlight what the employee does well and their positive contributions.
            </p>
          </div>

          <div>
            <label htmlFor="improvements" className="block text-sm font-medium text-gray-700 mb-2">
              Areas for Improvement <span className="text-red-500">*</span>
            </label>
            <textarea
              id="improvements"
              required
              rows={4}
              className="input resize-y"
              placeholder="What areas could benefit from development? (Markdown supported)"
              value={formData.improvements}
              onChange={(e) => setFormData({ ...formData, improvements: e.target.value })}
            />
            <p className="mt-1 text-sm text-gray-500">
              Provide constructive feedback on areas where the employee can grow.
            </p>
          </div>

          <div>
            <label htmlFor="sentiment" className="block text-sm font-medium text-gray-700 mb-2">
              Overall Sentiment <span className="text-red-500">*</span>
            </label>
            <select
              id="sentiment"
              required
              className="input"
              value={formData.sentiment}
              onChange={(e) => setFormData({ ...formData, sentiment: e.target.value as any })}
            >
              <option value="positive">Positive - Exceeding expectations</option>
              <option value="neutral">Neutral - Meeting expectations</option>
              <option value="negative">Needs Improvement - Below expectations</option>
            </select>
          </div>

          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-2">
              Tags (Optional)
            </label>
            <div className="flex space-x-2 mb-3">
              <input
                type="text"
                placeholder="Add a tag (e.g., communication, leadership)"
                className="input flex-1"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={handleTagInputKeyPress}
              />
              <button
                type="button"
                onClick={addTag}
                className="btn btn-secondary"
              >
                Add Tag
              </button>
            </div>
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-2 text-primary-600 hover:text-primary-800"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </span>
                ))}
              </div>
            )}
            <p className="mt-1 text-sm text-gray-500">
              Add relevant tags to categorize this feedback (e.g., communication, technical skills, leadership).
            </p>
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="h-4 w-4 mr-1" />
              {loading ? 'Saving...' : (isEditing ? 'Update Feedback' : 'Submit Feedback')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}