import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Feedback, User } from '../types';
import { ArrowLeft, Edit, Calendar, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';

export default function FeedbackHistory() {
  const { employeeId } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState<User | null>(null);
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [employeeId]);

  const fetchData = async () => {
    try {
      const [employeeRes, feedbackRes] = await Promise.all([
        api.get(`/employees/${employeeId}`),
        api.get(`/feedback/employee/${employeeId}`)
      ]);
      setEmployee(employeeRes.data);
      setFeedback(feedbackRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (feedbackId: number) => {
    if (window.confirm('Are you sure you want to delete this feedback?')) {
      try {
        await api.delete(`/feedback/${feedbackId}`);
        setFeedback(feedback.filter(f => f.id !== feedbackId));
      } catch (error) {
        console.error('Failed to delete feedback:', error);
      }
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'neutral': return 'text-yellow-600 bg-yellow-100';
      case 'negative': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
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
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors mr-4"
          >
            <ArrowLeft className="h-5 w-5 mr-1" />
            Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            Feedback History
            {employee && <span className="text-gray-600"> for {employee.name}</span>}
          </h1>
        </div>
        {employee && (
          <Link
            to={`/feedback/new/${employee.id}`}
            className="btn btn-primary"
          >
            Give New Feedback
          </Link>
        )}
      </div>

      {feedback.length === 0 ? (
        <div className="card text-center py-12">
          <Calendar className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No feedback history</h3>
          <p className="mt-1 text-sm text-gray-500">
            No feedback has been given to this employee yet.
          </p>
          {employee && (
            <Link
              to={`/feedback/new/${employee.id}`}
              className="mt-4 btn btn-primary"
            >
              Give First Feedback
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {feedback.map((item) => (
            <div key={item.id} className="card">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="h-4 w-4 mr-1" />
                    {format(new Date(item.created_at), 'MMM d, yyyy')}
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSentimentColor(item.sentiment)}`}>
                    {item.sentiment}
                  </span>
                  {item.acknowledged && (
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      Acknowledged
                    </span>
                  )}
                </div>
                <div className="flex space-x-2">
                  <Link
                    to={`/feedback/edit/${item.id}`}
                    className="text-primary-600 hover:text-primary-800 transition-colors"
                  >
                    <Edit className="h-4 w-4" />
                  </Link>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="text-red-600 hover:text-red-800 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-green-800 mb-2">Strengths</h4>
                  <div className="text-gray-700 prose prose-sm max-w-none">
                    <ReactMarkdown>{item.strengths}</ReactMarkdown>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-blue-800 mb-2">Areas for Improvement</h4>
                  <div className="text-gray-700 prose prose-sm max-w-none">
                    <ReactMarkdown>{item.improvements}</ReactMarkdown>
                  </div>
                </div>
              </div>

              {item.tags && item.tags.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium text-gray-800 mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {item.tags.map((tag, index) => (
                      <span key={index} className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {item.employee_comment && (
                <div className="mt-4 pt-4 border-t">
                  <h4 className="font-medium text-gray-800 mb-2">Employee Comment</h4>
                  <div className="text-gray-700 prose prose-sm max-w-none bg-gray-50 p-3 rounded">
                    <ReactMarkdown>{item.employee_comment}</ReactMarkdown>
                  </div>
                </div>
              )}

              {item.updated_at !== item.created_at && (
                <div className="mt-4 pt-4 border-t text-sm text-gray-500">
                  Last updated: {format(new Date(item.updated_at), 'MMM d, yyyy')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}