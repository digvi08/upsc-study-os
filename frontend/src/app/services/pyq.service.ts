import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { PYQ, PYQAnalysis, PYQAnalysisRequest } from '../shared/models';

@Injectable({ providedIn: 'root' })
export class PYQService {
  private readonly API = `${environment.apiUrl}/pyq`;

  constructor(private http: HttpClient) {}

  getPYQs(filters: {
    topic?: string;
    subject?: string;
    year?: number;
    exam?: string;
    search?: string;
    page?: number;
    page_size?: number;
  } = {}): Observable<any> {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) params = params.set(key, String(value));
    });
    return this.http.get<any>(this.API, { params });
  }

  analyzeTopic(request: PYQAnalysisRequest): Observable<PYQAnalysis> {
    return this.http.post<PYQAnalysis>(`${this.API}/analyze`, request);
  }

  getAvailableYears(): Observable<number[]> {
    return this.http.get<number[]>(`${this.API}/years`);
  }

  getSubjects(): Observable<string[]> {
    return this.http.get<string[]>(`${this.API}/subjects`);
  }
}
