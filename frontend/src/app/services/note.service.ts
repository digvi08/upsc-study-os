import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Note, NoteCreate, PaginatedNotes } from '../shared/models';

@Injectable({ providedIn: 'root' })
export class NoteService {
  private readonly API = `${environment.apiUrl}/notes`;

  constructor(private http: HttpClient) {}

  getNotes(filters: {
    topic_id?: string;
    subject_id?: string;
    note_type?: string;
    search?: string;
    pinned_only?: boolean;
    page?: number;
    page_size?: number;
  } = {}): Observable<PaginatedNotes> {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params = params.set(key, String(value));
      }
    });
    return this.http.get<PaginatedNotes>(this.API, { params });
  }

  getNote(id: string): Observable<Note> {
    return this.http.get<Note>(`${this.API}/${id}`);
  }

  createNote(data: NoteCreate): Observable<Note> {
    return this.http.post<Note>(this.API, data);
  }

  updateNote(id: string, data: Partial<NoteCreate>): Observable<Note> {
    return this.http.put<Note>(`${this.API}/${id}`, data);
  }

  deleteNote(id: string): Observable<any> {
    return this.http.delete(`${this.API}/${id}`);
  }

  togglePin(id: string): Observable<Note> {
    return this.http.post<Note>(`${this.API}/${id}/pin`, {});
  }

  toggleFavorite(id: string): Observable<Note> {
    return this.http.post<Note>(`${this.API}/${id}/favorite`, {});
  }

  generateAISummary(id: string): Observable<{ summary: string }> {
    return this.http.post<{ summary: string }>(`${this.API}/${id}/ai-summary`, {});
  }

  generateFlashcards(id: string, count = 10): Observable<{ flashcards: any[] }> {
    const params = new HttpParams().set('count', count);
    return this.http.post<{ flashcards: any[] }>(`${this.API}/${id}/flashcards`, {}, { params });
  }

  generateAINote(topic: string, subject?: string, noteType = 'summary'): Observable<Note> {
    return this.http.post<Note>(`${this.API}/ai-generate`, {
      topic, subject, note_type: noteType, detail_level: 'medium',
    });
  }
}
