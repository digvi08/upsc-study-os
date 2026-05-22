import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface StudyLogPayload {
  study_hours: number;
  topics_studied?: number;
  revisions_done?: number;
  notes_created?: number;
  pyqs_attempted?: number;
  tasks_completed?: number;
  tasks_total?: number;
  mood?: 'great' | 'good' | 'okay' | 'bad';
}

@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private readonly API = `${environment.apiUrl}/analytics`;

  constructor(private http: HttpClient) {}

  getOverview(): Observable<any> {
    return this.http.get(`${this.API}/overview`);
  }

  getHeatmap(days = 365): Observable<any> {
    return this.http.get(`${this.API}/heatmap`, {
      params: new HttpParams().set('days', days),
    });
  }

  getWeeklyReport(): Observable<any> {
    return this.http.get(`${this.API}/weekly-report`);
  }

  getSubjectPerformance(): Observable<any[]> {
    return this.http.get<any[]>(`${this.API}/subject-performance`);
  }

  logStudySession(payload: StudyLogPayload): Observable<any> {
    return this.http.post(`${this.API}/log-study`, payload);
  }
}
