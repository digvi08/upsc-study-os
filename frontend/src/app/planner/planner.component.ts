import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-planner',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-6 animate-fade-in">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white">Daily Planner</h1>
          <p class="text-gray-400 mt-1">AI-powered study schedule tailored to your goals</p>
        </div>
        <button (click)="showGenerateForm.set(true)" class="btn-primary flex items-center gap-2">
          🤖 Generate AI Plan
        </button>
      </div>

      <!-- Generate Plan Form -->
      @if (showGenerateForm()) {
        <div class="glass-card p-6 animate-slide-up">
          <h3 class="text-lg font-semibold text-white mb-4">Generate AI Study Plan</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Daily Study Hours</label>
              <input type="number" [(ngModel)]="planConfig.hours" min="2" max="16" class="input-field" />
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Exam Date</label>
              <input type="date" [(ngModel)]="planConfig.examDate" class="input-field" />
            </div>
          </div>
          <div class="flex gap-3 mt-4">
            <button (click)="generatePlan()" class="btn-primary" [disabled]="generating()">
              @if (generating()) { Generating... } @else { Generate Plan }
            </button>
            <button (click)="showGenerateForm.set(false)" class="btn-secondary">Cancel</button>
          </div>
        </div>
      }

      <!-- Today's Tasks -->
      <div class="glass-card p-6">
        <h2 class="text-lg font-semibold text-white mb-4">Today's Schedule</h2>
        @if (todayTasks().length === 0) {
          <div class="text-center py-8">
            <span class="text-4xl">📅</span>
            <p class="text-gray-400 mt-2">No tasks for today. Generate an AI plan to get started.</p>
          </div>
        } @else {
          <div class="space-y-3">
            @for (task of todayTasks(); track task.id) {
              <div class="flex items-center gap-4 p-4 rounded-xl transition-all"
                   [style.background]="task.status === 'completed' ? 'rgba(16,185,129,0.05)' : 'rgba(255,255,255,0.03)'"
                   [style.border]="'1px solid ' + (task.status === 'completed' ? 'rgba(16,185,129,0.2)' : 'rgba(255,255,255,0.06)')">
                <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0"
                     [class]="task.status === 'completed' ? 'border-green-500 bg-green-500' : 'border-gray-600'">
                  @if (task.status === 'completed') { <span class="text-white text-xs">✓</span> }
                </div>
                <div class="flex-1">
                  <p class="text-white font-medium" [class.line-through]="task.status === 'completed'"
                     [class.text-gray-500]="task.status === 'completed'">{{ task.title }}</p>
                  <p class="text-gray-500 text-xs">{{ task.duration_minutes }} min · {{ task.task_type }}</p>
                </div>
                <span class="badge" [class]="getPriorityBadge(task.priority)">{{ task.priority }}</span>
                @if (task.status !== 'completed') {
                  <button (click)="completeTask(task.id)" class="btn-primary text-xs px-3 py-1.5">Done</button>
                }
              </div>
            }
          </div>
        }
      </div>
    </div>
  `,
})
export class PlannerComponent implements OnInit {
  private http = inject(HttpClient);
  todayTasks = signal<any[]>([]);
  showGenerateForm = signal(false);
  generating = signal(false);
  planConfig = { hours: 8, examDate: '' };

  getPriorityBadge(p: string): string {
    return { low: 'badge-info', medium: 'badge-warning', high: 'badge-danger' }[p] || 'badge-info';
  }

  ngOnInit(): void {
    this.http.get<any[]>(`${environment.apiUrl}/planner/today`).subscribe({
      next: (data) => this.todayTasks.set(data),
    });
  }

  generatePlan(): void {
    this.generating.set(true);
    this.http.post(`${environment.apiUrl}/planner/generate`, null, {
      params: {
        subjects: ['History', 'Geography', 'Polity', 'Economy'],
        weak_areas: [],
        available_hours: this.planConfig.hours,
        exam_date: this.planConfig.examDate || '2025-06-01',
      } as any,
    }).subscribe({
      next: () => {
        this.generating.set(false);
        this.showGenerateForm.set(false);
        this.ngOnInit();
      },
      error: () => this.generating.set(false),
    });
  }

  completeTask(id: string): void {
    this.http.post(`${environment.apiUrl}/planner/tasks/${id}/complete`, null).subscribe({
      next: () => this.todayTasks.update(ts => ts.map(t => t.id === id ? { ...t, status: 'completed' } : t)),
    });
  }
}
