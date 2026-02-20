import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Heatmap } from './components/Heatmap';
import { StockDetail } from './components/StockDetail';
import { Search } from './components/Search';
import { apiService } from './services/api';
import type { Company, Score, Article } from './types';

const COLORS = {
  positive: '#10b981',
  negative: '#ef4444',
  neutral: '#6b7280',
};

function App() {
  const [, setCompanies] = useState<Company[]>([]);
  const [scores, setScores] = useState<Score[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [sentimentFilter, setSentimentFilter] = useState<'all' | 'positive' | 'negative'>('all');
  const [loading, setLoading] = useState(false);
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'unhealthy' | 'loading'>('loading');

  useEffect(() => {
    const initializeApp = async () => {
      try {
        setLoading(true);
        
        // Check health
        const health = await apiService.getHealth();
        setHealthStatus(health.status === 'healthy' ? 'healthy' : 'unhealthy');

        // Load companies
        const companiesData = await apiService.getCompanies();
        setCompanies(companiesData);

        // Load scores for selected date
        await loadScores(selectedDate);
      } catch (error) {
        console.error('Failed to initialize app:', error);
        setHealthStatus('unhealthy');
      } finally {
        setLoading(false);
      }
    };

    initializeApp();
  }, []);

  const loadScores = async (date: string) => {
    console.log(`[DEBUG] loadScores called with date: ${date}, sentimentFilter: ${sentimentFilter}`);
    try {
      setLoading(true);
      const sentimentParam = sentimentFilter === 'all' ? undefined : sentimentFilter;
      const scoresData = await apiService.getScores(date, { limit: 100, sentiment_filter: sentimentParam });
      console.log(`[DEBUG] loadScores received scoresData:`, scoresData);
      setScores(scoresData);
      
      // Load articles
      const articlesData = await apiService.getArticles({ limit: 20, sentiment_filter: sentimentParam });
      setArticles(articlesData);
    } catch (error) {
      console.error('Failed to load scores:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    await loadScores(selectedDate);
  };

  const handleCalculateScores = async () => {
    console.log(`[DEBUG] handleCalculateScores called with selectedDate: ${selectedDate}`);
    try {
      setLoading(true);
      const result = await apiService.calculateScores(selectedDate);
      console.log(`[DEBUG] calculateScores result:`, result);
      console.log(`Calculated scores for ${result.companies_scored} companies`);
      await loadScores(selectedDate);
    } catch (error) {
      console.error('Failed to calculate scores:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (date: string) => {
    setSelectedDate(date);
    loadScores(date);
  };

  const handleSentimentFilterChange = (filter: 'all' | 'positive' | 'negative') => {
    setSentimentFilter(filter);
    loadScores(selectedDate);
  };

  const handleStockClick = (ticker: string) => {
    setSelectedStock(ticker);
  };

  const handleCompanySelect = (company: Company) => {
    setSelectedStock(company.ticker);
  };

  const getStats = () => {
    const positiveCount = scores.filter((s) => s.score > 0).length;
    const negativeCount = scores.filter((s) => s.score < 0).length;
    const neutralCount = scores.filter((s) => s.score === 0).length;
    const avgScore = scores.length > 0 ? scores.reduce((sum, s) => sum + s.score, 0) / scores.length : 0;

    return { positiveCount, negativeCount, neutralCount, avgScore };
  };

  const stats = getStats();

  // Debug: Log scores state changes
  useEffect(() => {
    console.log(`[DEBUG] scores state changed:`, scores);
    console.log(`[DEBUG] scores.length: ${scores.length}`);
  }, [scores]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">NewsSpY</h1>
              <span className="text-sm text-gray-600">US Stock Sentiment Analysis</span>
            </div>
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 ${healthStatus === 'healthy' ? 'text-green-600' : healthStatus === 'unhealthy' ? 'text-red-600' : 'text-gray-600'}`}>
                <div className={`w-3 h-3 rounded-full ${healthStatus === 'healthy' ? 'bg-green-600' : healthStatus === 'unhealthy' ? 'bg-red-600' : 'bg-gray-600'}`} />
                <span className="text-sm font-medium capitalize">{healthStatus}</span>
              </div>
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Controls */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => handleDateChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sentiment Filter</label>
              <select
                value={sentimentFilter}
                onChange={(e) => handleSentimentFilterChange(e.target.value as 'all' | 'positive' | 'negative')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All</option>
                <option value="positive">Positive</option>
                <option value="negative">Negative</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <Search onCompanySelect={handleCompanySelect} />
            </div>
          </div>
          <div className="mt-4">
            <button
              onClick={handleCalculateScores}
              disabled={loading}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Calculating...' : 'Calculate Scores'}
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Positive</p>
                <p className="text-3xl font-bold text-green-600">{stats.positiveCount}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Negative</p>
                <p className="text-3xl font-bold text-red-600">{stats.negativeCount}</p>
              </div>
              <TrendingDown className="w-8 h-8 text-red-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Neutral</p>
                <p className="text-3xl font-bold text-gray-600">{stats.neutralCount}</p>
              </div>
              <Minus className="w-8 h-8 text-gray-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Score</p>
                <p className={`text-3xl font-bold ${stats.avgScore > 0 ? 'text-green-600' : stats.avgScore < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                  {stats.avgScore.toFixed(2)}
                </p>
              </div>
              <Minus className="w-8 h-8 text-gray-600" />
            </div>
          </div>
        </div>

        {/* Heatmap */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Sentiment Heatmap</h2>
          {scores.length > 0 ? (
            <Heatmap scores={scores} onStockClick={handleStockClick} />
          ) : (
            <div className="text-center py-12 text-gray-600">
              No scores available for this date. Click "Calculate Scores" to generate scores.
            </div>
          )}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Top 10 Companies</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={scores.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="company.ticker" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="score" fill="#0ea5e9" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Sentiment Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Positive', value: stats.positiveCount },
                    { name: 'Negative', value: stats.negativeCount },
                    { name: 'Neutral', value: stats.neutralCount },
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  <Cell fill={COLORS.positive} />
                  <Cell fill={COLORS.negative} />
                  <Cell fill={COLORS.neutral} />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Articles */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Articles</h2>
          {articles.length > 0 ? (
            <div className="space-y-4">
              {articles.slice(0, 10).map((article) => (
                <div key={article.id} className="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">{article.title}</h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {article.source} • {new Date(article.published_at).toLocaleDateString('ja-JP')}
                      </p>
                      <p className="text-sm text-gray-700 line-clamp-2">{article.content?.substring(0, 200)}...</p>
                    </div>
                    {article.sentiment_score !== null && (
                      <div className={`ml-4 px-3 py-1 rounded ${article.sentiment_score > 0 ? 'bg-green-100 text-green-800' : article.sentiment_score < 0 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                        <span className="font-bold">{article.sentiment_score.toFixed(3)}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-600">
              No articles available.
            </div>
          )}
        </div>
      </main>

      {/* Stock Detail Modal */}
      {selectedStock && (
        <StockDetail ticker={selectedStock} onClose={() => setSelectedStock(null)} />
      )}
    </div>
  );
}

export default App;
