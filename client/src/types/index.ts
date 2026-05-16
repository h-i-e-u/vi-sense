export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export interface SentimentResult {
  label: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  confidence: number;
  text: string;
}

export interface AnalysisJob {
  id: string;
  user_id: string;
  type: 'text' | 'link' | 'file';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  results?: SentimentResult[];
  metadata?: {
    total_comments?: number;
    positive_ratio?: number;
    neutral_ratio?: number;
    negative_ratio?: number;
    keywords?: string[];
  };
}

export interface Comment {
  id: string;
  job_id: string;
  text: string;
  sentiment: SentimentResult;
  source_url?: string;
  created_at: string;
}

export interface AnalyticsSummary {
  total_analyses: number;
  text_analyses: number;
  file_analyses: number;
  link_analyses: number;
  sentiment_distribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
  trend_data: Array<{
    date: string;
    positive: number;
    neutral: number;
    negative: number;
  }>;
  top_keywords: Array<{
    word: string;
    count: number;
  }>;
  top_positive_comments: Comment[];
  top_negative_comments: Comment[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface AnalyzeTextRequest {
  text: string;
}

export interface AnalyzeLinkRequest {
  url: string;
  type: 'youtube' | 'shopee' | 'tiki';
}

export interface AnalyzeFileRequest {
  file: File;
}