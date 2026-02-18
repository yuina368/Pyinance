import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { X, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { apiService } from '../services/api';
import type { SentimentHistory } from '../types';

interface StockDetailProps {
  ticker: string;
  onClose: () => void;
}

export const StockDetail: React.FC<StockDetailProps> = ({ ticker, onClose }) => {
  const [history, setHistory] = useState<SentimentHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiService.getTickerSentimentHistory(ticker, 30);
        setHistory(data.reverse());
      } catch (err) {
        setError('Failed to fetch sentiment history');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [ticker]);

  const getLatestScore = (): number => {
    if (history.length === 0) return 0;
    return history[history.length - 1].avg_score;
  };

  const getScoreIcon = () => {
    const score = getLatestScore();
    if (score > 0.05) return <TrendingUp className="w-6 h-6 text-green-600" />;
    if (score < -0.05) return <TrendingDown className="w-6 h-6 text-red-600" />;
    return <Minus className="w-6 h-6 text-gray-600" />;
  };

  const getScoreColor = (): string => {
    const score = getLatestScore();
    if (score > 0.05) return 'text-green-600';
    if (score < -0.05) return 'text-red-600';
    return 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
          <p className="text-center mt-4 text-gray-600">Loading sentiment history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <p className="text-red-600 text-center">{error}</p>
          <button
            onClick={onClose}
            className="mt-4 w-full bg-gray-200 text-gray-800 py-2 px-4 rounded hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">{ticker}</h2>
            <p className="text-gray-600 mt-1">Sentiment History (Last 30 Days)</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex items-center gap-4 mb-6">
          {getScoreIcon()}
          <div>
            <p className={`text-4xl font-bold ${getScoreColor()}`}>
              {getLatestScore().toFixed(3)}
            </p>
            <p className="text-sm text-gray-600">Latest Sentiment Score</p>
          </div>
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Sentiment Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString('ja-JP')}
              />
              <YAxis 
                domain={[-1, 1]}
                tickFormatter={(value) => value.toFixed(2)}
              />
              <Tooltip 
                labelFormatter={(value) => new Date(value).toLocaleDateString('ja-JP')}
                formatter={(value: number) => [value.toFixed(3), 'Score']}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="avg_score" 
                stroke="#0ea5e9" 
                strokeWidth={2}
                dot={{ fill: '#0ea5e9' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Positive</p>
            <p className="text-2xl font-bold text-green-600">
              {history.length > 0 ? `${history[history.length - 1].positive_pct.toFixed(1)}%` : '0%'}
            </p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Negative</p>
            <p className="text-2xl font-bold text-red-600">
              {history.length > 0 ? `${history[history.length - 1].negative_pct.toFixed(1)}%` : '0%'}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Neutral</p>
            <p className="text-2xl font-bold text-gray-600">
              {history.length > 0 ? `${history[history.length - 1].neutral_pct.toFixed(1)}%` : '0%'}
            </p>
          </div>
        </div>

        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-4">Recent Articles</h3>
          <div className="space-y-2">
            {history.slice(-5).reverse().map((item, index) => (
              <div key={index} className="bg-gray-50 p-3 rounded">
                <div className="flex justify-between items-center">
                  <p className="text-sm font-medium">{new Date(item.date).toLocaleDateString('ja-JP')}</p>
                  <p className={`text-sm font-bold ${item.avg_score > 0 ? 'text-green-600' : item.avg_score < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                    {item.avg_score.toFixed(3)}
                  </p>
                </div>
                <p className="text-xs text-gray-600 mt-1">{item.article_count} articles</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
