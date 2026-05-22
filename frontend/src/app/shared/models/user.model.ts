export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  profile_picture?: string;
  bio?: string;
  exam_target: 'upsc' | 'mpsc' | 'both';
  daily_study_hours: number;
  exam_year?: number;
  is_active: boolean;
  is_verified: boolean;
  role: 'student' | 'admin' | 'moderator';
  current_streak: number;
  longest_streak: number;
  total_study_hours: number;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
  message: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  full_name: string;
  password: string;
  exam_target: string;
}
