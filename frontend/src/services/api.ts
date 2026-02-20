import axios from 'axios';
import type {
  Company,
  Article,
  Score,
  NewsSentiment,
  SentimentHistory,
  HealthResponse,
  ModelStatusResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const apiService = {
  // Health check
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/health/');
    return response.data;
  },

  // Model status
  async getModelStatus(): Promise<ModelStatusResponse> {
    const response = await api.get<ModelStatusResponse>('/model/status');
    return response.data;
  },

  // Companies
  async getCompanies(): Promise<Company[]> {
    const response = await api.get<Company[]>('/companies/');
    return response.data;
  },

  // Articles
  async getArticles(params?: {
    company_id?: number;
    sentiment_filter?: string;
    limit?: number;
  }): Promise<Article[]> {
    const response = await api.get<Article[]>('/articles/', { params });
    return response.data;
  },

  // Scores
  async getScores(date: string, params?: {
    limit?: number;
    sentiment_filter?: string;
  }): Promise<Score[]> {
    console.log(`[DEBUG] getScores called with date: ${date}, params:`, params);
    console.log(`[DEBUG] API URL: ${API_BASE_URL}/scores/ranking/${date}`);
    try {
      const response = await api.get<Score[]>(`/scores/ranking/${date}`, { params });
      console.log(`[DEBUG] getScores response:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`[DEBUG] getScores error:`, error);
      throw error;
    }
  },

  async calculateScores(date: string): Promise<{ companies_scored: number }> {
    console.log(`[DEBUG] calculateScores called with date: ${date}`);
    console.log(`[DEBUG] API URL: ${API_BASE_URL}/scores/calculate/${date}`);
    try {
      const response = await api.post<{ companies_scored: number }>(`/scores/calculate/${date}`);
      console.log(`[DEBUG] calculateScores response:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`[DEBUG] calculateScores error:`, error);
      throw error;
    }
  },

  // Sentiments
  async getDailySentiments(date: string): Promise<NewsSentiment[]> {
    const response = await api.get<NewsSentiment[]>(`/sentiments/daily?target_date=${date}`);
    return response.data;
  },

  async getTickerSentimentHistory(ticker: string, days: number = 30): Promise<SentimentHistory[]> {
    const response = await api.get<SentimentHistory[]>(`/sentiments/${ticker}?days=${days}`);
    return response.data;
  },

  async getSentimentSummary(): Promise<any> {
    const response = await api.get('/sentiments/summary');
    return response.data;
  },
};

export default api;
