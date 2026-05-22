import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly API = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getDashboardStats(): Observable<any> {
    return this.http.get(`${this.API}/users/dashboard-stats`);
  }

  getAnalyticsOverview(): Observable<any> {
    return this.http.get(`${this.API}/analytics/overview`);
  }

  getStudyHeatmap(days = 365): Observable<any> {
    return this.http.get(`${this.API}/analytics/heatmap`, { params: { days: String(days) } });
  }

  getWeeklyReport(): Observable<any> {
    return this.http.get(`${this.API}/analytics/weekly-report`);
  }

  logStudySession(data: {
    study_hours: number;
    topics_studied?: number;
    revisions_done?: number;
    notes_created?: number;
    mood?: string;
  }): Observable<any> {
    return this.http.post(`${this.API}/analytics/log-study`, null, { params: data as any });
  }
}
