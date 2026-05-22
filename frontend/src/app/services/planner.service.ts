import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface StudyTask {
  id: string;
  title: string;
  description?: string;
  task_type: string;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped' | 'rescheduled';
  scheduled_date: string;
  duration_minutes: number;
  actual_duration_minutes?: number;
  priority: string;
  subject_id?: string;
  topic_id?: string;
}

export interface WeeklyDay {
  date: string;
  tasks: StudyTask[];
}

@Injectable({ providedIn: 'root' })
export class PlannerService {
  private readonly API = `${environment.apiUrl}/planner`;

  constructor(private http: HttpClient) {}

  generateAIPlan(config: {
    subjects: string[];
    weak_areas: string[];
    available_hours: number;
    exam_date: string;
    completed_topics?: string[];
  }): Observable<any> {
    return this.http.post(`${this.API}/generate`, config);
  }

  getTodayTasks(): Observable<StudyTask[]> {
    return this.http.get<StudyTask[]>(`${this.API}/today`);
  }

  getWeeklyPlan(weekStart?: string): Observable<WeeklyDay[]> {
    let params = new HttpParams();
    if (weekStart) params = params.set('week_start', weekStart);
    return this.http.get<WeeklyDay[]>(`${this.API}/weekly`, { params });
  }

  getPlans(): Observable<any[]> {
    return this.http.get<any[]>(`${this.API}/plans`);
  }

  completeTask(taskId: string, actualDuration?: number): Observable<any> {
    let params = new HttpParams();
    if (actualDuration) params = params.set('actual_duration', actualDuration);
    return this.http.post(`${this.API}/tasks/${taskId}/complete`, {}, { params });
  }

  skipTask(taskId: string): Observable<any> {
    return this.http.post(`${this.API}/tasks/${taskId}/skip`, {});
  }
}
