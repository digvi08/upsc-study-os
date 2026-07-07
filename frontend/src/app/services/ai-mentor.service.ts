import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface AIQueryRequest {
  query: string;
  context?: string;
  mode: 'beginner' | 'prelims' | 'mains' | 'quick_revision';
  subject?: string;
  topic?: string;
}

@Injectable({ providedIn: 'root' })
export class AIMentorService {
  private readonly API = `${environment.apiUrl}/ai-mentor`;

  constructor(private http: HttpClient) {}

  chat(request: AIQueryRequest, history?: ChatMessage[]): Observable<{ response: string }> {
    return this.http.post<{ response: string }>(`${this.API}/chat`, request);
  }

  explainTopic(topic: string, subject?: string, mode = 'mains'): Observable<any> {
    return this.http.post(`${this.API}/explain`, null, {
      params: { topic, ...(subject ? { subject } : {}), mode },
    });
  }

  compareConcepts(concept1: string, concept2: string): Observable<any> {
    return this.http.post(`${this.API}/compare`, null, {
      params: { concept1, concept2 },
    });
  }

  getAnswerStructure(question: string, marks = 10): Observable<any> {
    return this.http.post(`${this.API}/answer-structure`, null, {
      params: { question, marks: String(marks) },
    });
  }

  linkCurrentAffairs(topic: string): Observable<any> {
    return this.http.post(`${this.API}/current-affairs-link`, null, {
      params: { topic },
    });
  }

  // Server-Sent Events streaming
  streamChat(request: AIQueryRequest): EventSource {
    const token = localStorage.getItem('upsc_access_token');
    const params = new URLSearchParams({
      query: request.query,
      mode: request.mode,
      ...(request.subject ? { subject: request.subject } : {}),
      ...(request.topic ? { topic: request.topic } : {}),
    });
    return new EventSource(
      `${this.API}/chat/stream?${params.toString()}&token=${token}`
    );
  }
}
