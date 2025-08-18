import React from 'react';
import { Feedback } from '../types';
import { MessageSquare, Calendar, CheckCircle, Clock, MessageCircle } from 'lucide-react';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import { api } from '../services/api';

interface EmployeeDashboardProps {
  feedback: Feedback[];
  onRefresh: () => void;
}

export default function EmployeeDashboard({ feedback, onRefresh }: EmployeeDashboardProps) {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'neutral': return 'text-yellow-600 bg-yellow-100';
      case 'negative': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const handleAcknowledge = async (feedbackId: number) => {
    try {
      await api.post(`/feedback/${feedbackId}/acknowledge`);
      onRefresh();
    } catch (error) {
      console.error('Failed to acknowledge feedback:', error);
    }
  };

  const handleAddComment = async (feedbackId: number, comment: string) => {
    try {
      await api.post(`/feedback/${feedbackId}/comment`, { comment });
      onRefresh();
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  const unacknowledgedCount = feedback.filter(f => !f.acknowledged).length;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">My Feedback</h1>
        {unacknowledgedCount > 0 && (
          <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
            {unacknowledgedCount} new feedback
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <MessageSquare className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Feedback</p>
              <p className="text-2xl font-bold text-gray-900">{feedback.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Acknowledged</p>
              <p className="text-2xl font-bold text-gray-900">
                {feedback.filter(f => f.acknowledged).length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-gray-900">{unacknowledgedCount}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Feedback Timeline */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Feedback Timeline</h2>
        
        {feedback.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No feedback yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Your manager hasn't provided any feedback yet.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {feedback.map((item) => (
              <FeedbackCard
                key={item.id}
                feedback={item}
                onAcknowledge={handleAcknowledge}
                onAddComment={handleAddComment}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface FeedbackCardProps {
  feedback: Feedback;
  onAcknowledge: (id: number) => void;
  onAddComment: (id: number, comment: string) => void;
}

function FeedbackCard({ feedback, onAcknowledge, onAddComment }: FeedbackCardProps) {
  const [showCommentForm, setShowCommentForm] = React.useState(false);
  const [comment, setComment] = React.useState('');

  const handleSubmitComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (comment.trim()) {
      onAddComment(feedback.id, comment);
      setComment('');
      setShowCommentForm(false);
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

  return (
    <div className={`border rounded-lg p-6 ${!feedback.acknowledged ? 'border-yellow-200 bg-yellow-50' : 'border-gray-200 bg-white'}`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="h-4 w-4 mr-1" />
            {format(new Date(feedback.created_at), 'MMM d, yyyy')}
          </div>
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSentimentColor(feedback.sentiment)}`}>
            {feedback.sentiment}
          </span>
          {!feedback.acknowledged && (
            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
              New
            </span>
          )}
        </div>
        <div className="text-sm text-gray-500">
          From: {feedback.manager_name}
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="font-medium text-green-800 mb-2">Strengths</h4>
          <div className="text-gray-700 prose prose-sm max-w-none">
            <ReactMarkdown>{feedback.strengths}</ReactMarkdown>
          </div>
        </div>

        <div>
          <h4 className="font-medium text-blue-800 mb-2">Areas for Improvement</h4>
          <div className="text-gray-700 prose prose-sm max-w-none">
            <ReactMarkdown>{feedback.improvements}</ReactMarkdown>
          </div>
        </div>

        {feedback.tags && feedback.tags.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Tags</h4>
            <div className="flex flex-wrap gap-2">
              {feedback.tags.map((tag, index) => (
                <span key={index} className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {feedback.employee_comment && (
          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-800 mb-2">Your Comment</h4>
            <div className="text-gray-700 prose prose-sm max-w-none bg-gray-50 p-3 rounded">
              <ReactMarkdown>{feedback.employee_comment}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-between items-center mt-6 pt-4 border-t">
        <div className="flex space-x-3">
          {!feedback.acknowledged && (
            <button
              onClick={() => onAcknowledge(feedback.id)}
              className="btn btn-primary"
            >
              <CheckCircle className="h-4 w-4 mr-1" />
              Acknowledge
            </button>
          )}
          {!feedback.employee_comment && (
            <button
              onClick={() => setShowCommentForm(!showCommentForm)}
              className="btn btn-secondary"
            >
              <MessageCircle className="h-4 w-4 mr-1" />
              Add Comment
            </button>
          )}
        </div>
        {feedback.acknowledged && (
          <div className="flex items-center text-sm text-green-600">
            <CheckCircle className="h-4 w-4 mr-1" />
            Acknowledged
          </div>
        )}
      </div>

      {showCommentForm && (
        <form onSubmit={handleSubmitComment} className="mt-4 pt-4 border-t">
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add your comment (Markdown supported)..."
            className="input min-h-[100px] resize-y"
            required
          />
          <div className="flex justify-end space-x-2 mt-3">
            <button
              type="button"
              onClick={() => setShowCommentForm(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Add Comment
            </button>
          </div>
        </form>
      )}
    </div>
  );
}