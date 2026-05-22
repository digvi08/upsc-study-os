export type NoteType = 'manual' | 'ai_generated' | 'summary' | 'flashcard' | 'mind_map' | 'revision';

export interface Note {
  id: string;
  user_id: string;
  title: string;
  content: string;
  topic_id?: string;
  subject_id?: string;
  note_type: NoteType;
  tags: string[];
  color: string;
  is_pinned: boolean;
  is_favorite: boolean;
  ai_summary?: string;
  flashcards: Flashcard[];
  key_points: string[];
  revision_count: number;
  last_revised_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Flashcard {
  front: string;
  back: string;
}

export interface NoteCreate {
  title: string;
  content: string;
  topic_id?: string;
  subject_id?: string;
  note_type: NoteType;
  tags: string[];
  color: string;
  is_pinned: boolean;
}

export interface PaginatedNotes {
  items: Note[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}
