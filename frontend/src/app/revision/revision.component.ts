import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-revision',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="space-y-6 animate-fade-in">
      <div>
        <h1 class="text-2xl font-bold text-white">Revision System</h1>
        <p class="text-gray-400 mt-1">Spaced repetition — never forget what you've studied</p>
      </div>

      <!-- Pending revisions -->
      <div class="glass-card p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-white">Due Today</h2>
          <span class="badge badge-danger">{{ pendingRevisions().length }} pending</span>
        </div>

        @if (pendingRevisions().length === 0) {
          <div class="text-center py-8">
            <span class="text-4xl">🎉</span>
            <p class="text-white font-semibold mt-2">All caught up!</p>
            <p class="text-gray-400 text-sm mt-1">No revisions due today</p>
          </div>
        } @else {
          <div class="space-y-3">
            @for (rev of pendingRevisions(); track rev.id) {
              <div class="flex items-center gap-4 p-4 rounded-xl"
                   style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);">
                <div class="flex-1">
                  <p class="text-white font-medium">{{ rev.topic_name }}</p>
                  <p class="text-gray-500 text-xs mt-0.5">
                    Revision #{{ rev.revision_number }} ·
                    <span [class]="rev.is_overdue ? 'text-red-400' : 'text-gray-500'">
                      {{ rev.is_overdue ? 'Overdue' : 'Due today' }}
                    </span>
                  </p>
                </div>
                <button
                  (click)="completeRevision(rev.id)"
                  class="btn-primary text-sm px-4 py-2"
                >
                  Mark Done ✓
                </button>
              </div>
            }
          </div>
        }
      </div>

      <!-- Revision intervals info -->
      <div class="glass-card p-6">
        <h2 class="text-lg font-semibold text-white mb-4">Spaced Repetition Schedule</h2>
        <div class="flex gap-4 flex-wrap">
          @for (interval of intervals; track interval.label) {
            <div class="flex flex-col items-center p-4 rounded-xl flex-1 min-w-24"
                 style="background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.15);">
              <span class="text-2xl font-bold text-primary-400">{{ interval.days }}</span>
              <span class="text-gray-400 text-xs mt-1">days</span>
              <span class="text-gray-500 text-xs mt-0.5">{{ interval.label }}</span>
            </div>
          }
        </div>
      </div>
    </div>
  `,
})
export class RevisionComponent implements OnInit {
  private http = inject(HttpClient);
  pendingRevisions = signal<any[]>([]);

  intervals = [
    { days: 1, label: '1st Revision' },
    { days: 3, label: '2nd Revision' },
    { days: 7, label: '3rd Revision' },
    { days: 15, label: '4th Revision' },
    { days: 30, label: '5th Revision' },
  ];

  ngOnInit(): void {
    this.http.get<any[]>(`${environment.apiUrl}/revision/pending`).subscribe({
      next: (data) => this.pendingRevisions.set(data),
    });
  }

  completeRevision(id: string): void {
    this.http.post(`${environment.apiUrl}/revision/${id}/complete`, null, {
      params: { confidence_after: '70', time_spent_minutes: '30' },
    }).subscribe({
      next: () => this.pendingRevisions.update(rs => rs.filter(r => r.id !== id)),
    });
  }
}
