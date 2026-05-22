import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-current-affairs',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-6 animate-fade-in">
      <div>
        <h1 class="text-2xl font-bold text-white">Current Affairs Linker</h1>
        <p class="text-gray-400 mt-1">Connect current events with static UPSC subjects</p>
      </div>

      <!-- Filters -->
      <div class="glass-card p-4 flex gap-4 flex-wrap">
        <input type="text" [(ngModel)]="search" (ngModelChange)="loadAffairs()"
               placeholder="Search current affairs..." class="input-field flex-1 min-w-48 py-2 text-sm" />
        <select [(ngModel)]="daysFilter" (ngModelChange)="loadAffairs()" class="input-field py-2 text-sm w-36">
          <option value="7">Last 7 days</option>
          <option value="30" selected>Last 30 days</option>
          <option value="90">Last 3 months</option>
          <option value="365">Last year</option>
        </select>
      </div>

      <!-- Affairs list -->
      <div class="space-y-4">
        @for (affair of affairs(); track affair.id) {
          <div class="glass-card-hover p-5 cursor-pointer" (click)="selectedAffair.set(affair)">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span class="badge" [class]="getRelevanceBadge(affair.upsc_relevance_score)">
                    {{ affair.upsc_relevance_score || 'Medium' }} Relevance
                  </span>
                  @if (affair.prelims_relevant) { <span class="badge badge-info">Prelims</span> }
                  @if (affair.mains_relevant) { <span class="badge badge-primary">Mains</span> }
                  <span class="text-gray-500 text-xs ml-auto">{{ affair.published_date }}</span>
                </div>
                <h3 class="text-white font-semibold">{{ affair.title }}</h3>
                <p class="text-gray-400 text-sm mt-1 line-clamp-2">{{ affair.summary }}</p>
                @if (affair.related_subjects.length > 0) {
                  <div class="flex flex-wrap gap-1 mt-2">
                    @for (subject of affair.related_subjects; track subject) {
                      <span class="badge badge-success text-xs">{{ subject }}</span>
                    }
                  </div>
                }
              </div>
            </div>
          </div>
        }

        @if (affairs().length === 0 && !loading()) {
          <div class="glass-card p-12 text-center">
            <span class="text-6xl">📰</span>
            <p class="text-gray-400 mt-2">No current affairs found</p>
          </div>
        }
      </div>

      <!-- Detail modal -->
      @if (selectedAffair()) {
        <div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
             (click)="selectedAffair.set(null)">
          <div class="glass-card p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
               (click)="$event.stopPropagation()">
            <div class="flex items-start justify-between mb-4">
              <h2 class="text-xl font-bold text-white">{{ selectedAffair()!.title }}</h2>
              <button (click)="selectedAffair.set(null)" class="text-gray-400 hover:text-white text-xl">✕</button>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">{{ selectedAffair()!.summary }}</p>
            @if (selectedAffair()!.ai_relevance_explanation) {
              <div class="mt-4 p-4 rounded-xl" style="background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.2);">
                <p class="text-primary-300 text-sm font-medium mb-1">🤖 AI Relevance Analysis</p>
                <p class="text-gray-300 text-sm">{{ selectedAffair()!.ai_relevance_explanation }}</p>
              </div>
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class CurrentAffairsComponent implements OnInit {
  private http = inject(HttpClient);
  affairs = signal<any[]>([]);
  loading = signal(true);
  selectedAffair = signal<any>(null);
  search = '';
  daysFilter = 30;

  getRelevanceBadge(score: string): string {
    return { High: 'badge-danger', Medium: 'badge-warning', Low: 'badge-info' }[score] || 'badge-info';
  }

  ngOnInit(): void { this.loadAffairs(); }

  loadAffairs(): void {
    let params = new HttpParams().set('days', this.daysFilter);
    if (this.search) params = params.set('search', this.search);
    this.http.get<any>(`${environment.apiUrl}/current-affairs`, { params }).subscribe({
      next: (data) => { this.affairs.set(data.items || []); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }
}
