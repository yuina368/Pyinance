export interface Company {
  id: number;
  ticker: string;
  name: string;
  created_at: string;
}

export interface Article {
  id: number;
  company_id: number;
  title: string;
  content: string;
  source: string;
  source_url: string;
  published_at: string;
  sentiment_score: number | null;
  sentiment_confidence: number | null;
  fetched_at: string;
}

export interface Score {
  id: number;
  company_id: number;
  date: string;
  score: number;
  article_count: number;
  avg_sentiment: number | null;
  rank: number;
  created_at: string;
  company: Company;
}

export interface NewsSentiment {
  id: number;
  ticker: string;
  published_at: string;
  sentiment_score: number;
  label: string;
  created_at: string;
  url_hash: string;
}

export interface SentimentHistory {
  date: string;
  avg_score: number;
  article_count: number;
  positive_pct: number;
  negative_pct: number;
  neutral_pct: number;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
}

export interface ModelStatusResponse {
  loaded: boolean;
  model: string;
  status: string;
}
