import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface RevisionItem {
  id: string;
  topic_id: string;
  topic_name: string;
  subject_id?: string;
  revision_number: number;
  scheduled_date: string;
  is_overdue: boolean;
  status: string;
  confidence_before: number;
}

export interface RevisionCalendarDay {
  date: string;
  revisions: { id: string; topic_id: string; topic_name: string; revision_number: number }[];
}

@Injectable({ providedIn: 'root' })
export class RevisionService {
  private readonly API = `${environment.apiUrl}/revision`;

  constructor(private http: HttpClient) {}

  scheduleTopic(topicId: string): Observable<any> {
    return this.http.post(`${this.API}/schedule/${topicId}`, {});
  }

  getPending(): Observable<RevisionItem[]> {
    return this.http.get<RevisionItem[]>(`${this.API}/pending`);
  }

  getCalendar(days = 30): Observable<RevisionCalendarDay[]> {
    return this.http.get<RevisionCalendarDay[]>(`${this.API}/calendar`, {
      params: new HttpParams().set('days', days),
    });
  }

  getStats(): Observable<any> {
    return this.http.get(`${this.API}/stats`);
  }

  completeRevision(id: string, confidenceAfter: number, timeSpent: number, notes?: string): Observable<any> {
    let params = new HttpParams()
      .set('confidence_after', confidenceAfter)
      .set('time_spent_minutes', timeSpent);
    if (notes) params = params.set('notes', notes);
    return this.http.post(`${this.API}/${id}/complete`, {}, { params });
  }

  skipRevision(id: string): Observable<any> {
    return this.http.post(`${this.API}/${id}/skip`, {});
  }
}
