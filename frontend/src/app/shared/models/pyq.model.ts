export type ExamType = 'prelims' | 'mains' | 'interview';
export type QuestionType = 'mcq' | 'descriptive' | 'essay' | 'case_study';

export interface PYQ {
  id: string;
  year: number;
  exam: ExamType;
  exam_name: string;
  paper?: string;
  subject: string;
  topic: string;
  subtopic?: string;
  question: string;
  question_type: QuestionType;
  options?: Record<string, string>;
  correct_answer?: string;
  explanation?: string;
  word_limit?: number;
  marks?: number;
  model_answer?: string;
  keywords: string[];
  tags: string[];
  difficulty: string;
  ai_analysis?: any;
  is_verified: boolean;
  created_at: string;
}

export interface PYQAnalysisRequest {
  topic: string;
  subject?: string;
  years: number;
  exam_type?: string;
}

export interface PYQAnalysis {
  topic: string;
  total_questions: number;
  year_wise_count: Record<string, number>;
  exam_type_distribution: Record<string, number>;
  recurring_keywords: { keyword: string; count: number }[];
  trend_analysis: string;
  probability_score: number;
  mains_angles: string[];
  prelims_insights: string[];
  questions: PYQ[];
  ai_insights: string;
}
