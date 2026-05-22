export type SubjectCategory = 'gs1' | 'gs2' | 'gs3' | 'gs4' | 'csat' | 'optional' | 'current_affairs';
export type TopicStatus = 'not_started' | 'in_progress' | 'completed' | 'needs_revision';
export type TopicPriority = 'low' | 'medium' | 'high' | 'critical';

export interface Subject {
  id: string;
  name: string;
  description?: string;
  category: SubjectCategory;
  color: string;
  icon?: string;
  order_index: number;
  is_active: boolean;
  total_topics: number;
  completed_topics: number;
  completion_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface Topic {
  id: string;
  subject_id: string;
  parent_id?: string;
  name: string;
  description?: string;
  status: TopicStatus;
  importance_score: number;
  priority: TopicPriority;
  tags: string[];
  study_time_minutes: number;
  revision_count: number;
  confidence_level: number;
  pyq_frequency: number;
  last_asked_year?: number;
  ai_summary?: string;
  key_concepts: any[];
  subtopics?: Topic[];
  created_at: string;
  updated_at: string;
}

export interface SubjectCreate {
  name: string;
  description?: string;
  category: SubjectCategory;
  color: string;
  icon?: string;
}

export interface TopicCreate {
  subject_id: string;
  parent_id?: string;
  name: string;
  description?: string;
  importance_score: number;
  priority: TopicPriority;
  tags: string[];
}
