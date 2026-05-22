import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Subject, Topic, SubjectCreate, TopicCreate } from '../shared/models';

@Injectable({ providedIn: 'root' })
export class SubjectService {
  private readonly API = `${environment.apiUrl}/subjects`;

  constructor(private http: HttpClient) {}

  // ── Subjects ──────────────────────────────────────────────────────────────

  getSubjects(includeInactive = false): Observable<Subject[]> {
    const params = new HttpParams().set('include_inactive', includeInactive);
    return this.http.get<Subject[]>(this.API, { params });
  }

  getSubject(id: string): Observable<Subject> {
    return this.http.get<Subject>(`${this.API}/${id}`);
  }

  createSubject(data: SubjectCreate): Observable<Subject> {
    return this.http.post<Subject>(this.API, data);
  }

  updateSubject(id: string, data: Partial<SubjectCreate>): Observable<Subject> {
    return this.http.put<Subject>(`${this.API}/${id}`, data);
  }

  deleteSubject(id: string): Observable<any> {
    return this.http.delete(`${this.API}/${id}`);
  }

  // ── Topics ────────────────────────────────────────────────────────────────

  getTopics(subjectId: string, status?: string, search?: string): Observable<Topic[]> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    if (search) params = params.set('search', search);
    return this.http.get<Topic[]>(`${this.API}/${subjectId}/topics`, { params });
  }

  getTopicTree(subjectId: string): Observable<Topic[]> {
    return this.http.get<Topic[]>(`${this.API}/${subjectId}/topics/tree`);
  }

  createTopic(subjectId: string, data: TopicCreate): Observable<Topic> {
    return this.http.post<Topic>(`${this.API}/${subjectId}/topics`, data);
  }

  updateTopic(topicId: string, data: Partial<Topic>): Observable<Topic> {
    return this.http.put<Topic>(`${this.API}/topics/${topicId}`, data);
  }

  deleteTopic(topicId: string): Observable<any> {
    return this.http.delete(`${this.API}/topics/${topicId}`);
  }

  markTopicComplete(topicId: string): Observable<Topic> {
    return this.updateTopic(topicId, { status: 'completed' });
  }
}
