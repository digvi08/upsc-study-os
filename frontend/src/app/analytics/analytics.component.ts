import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardService } from '../services/dashboard.service';
import { StatCardComponent } from '../shared/components/stat-card/stat-card.component';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule, StatCardComponent],
  template: `
    <div class="space-y-6 animate-fade-in">
      <div>
        <h1 class="text-2xl font-bold text-white">Analytics Dashboard</h1>
        <p class="text-gray-400 mt-1">Track your preparation progress and performance</p>
      </div>

      @if (overview()) {
        <!-- Overview stats -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <app-stat-card icon="⏱️" label="Study Hours" [value]="studyHoursDisplay()" color="#6366f1" />
          <app-stat-card icon="✅" label="Topics Done" [value]="overview()!.overview.total_topics_completed" color="#10b981" />
          <app-stat-card icon="🔄" label="Revisions" [value]="overview()!.overview.total_revisions" color="#f59e0b" />
          <app-stat-card icon="🤖" label="AI Queries" [value]="overview()!.overview.total_ai_queries" color="#8b5cf6" />
        </div>

        <!-- Subject progress -->
        <div class="glass-card p-6">
          <h2 class="text-lg font-semibold text-white mb-4">Subject-wise Progress</h2>
          <div class="space-y-4">
            @for (subject of overview()!.subjects; track subject.name) {
              <div>
                <div class="flex justify-between text-sm mb-1.5">
                  <span class="text-white font-medium">{{ subject.name }}</span>
                  <span class="text-gray-400">{{ subject.completed_topics }}/{{ subject.total_topics }}</span>
                </div>
                <div class="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500"
                       [style.width.%]="subject.completion_percentage"
                       [style.background]="subject.color"></div>
                </div>
              </div>
            }
          </div>
        </div>

        <!-- Heatmap -->
        <div class="glass-card p-6">
          <h2 class="text-lg font-semibold text-white mb-4">Study Heatmap</h2>
          <div class="flex flex-wrap gap-1">
            @for (entry of heatmapEntries(); track entry.date) {
              <div
                class="w-3 h-3 rounded-sm"
                [style.background]="getHeatmapColor(entry.hours)"
                [attr.data-tooltip]="entry.date + ': ' + entry.hours + 'h'"
              ></div>
            }
          </div>
          <div class="flex items-center gap-2 mt-3">
            <span class="text-gray-500 text-xs">Less</span>
            @for (level of [0, 2, 4, 6, 8]; track level) {
              <div class="w-3 h-3 rounded-sm" [style.background]="getHeatmapColor(level)"></div>
            }
            <span class="text-gray-500 text-xs">More</span>
          </div>
        </div>
      }
    </div>
  `,
})
export class AnalyticsComponent implements OnInit {
  private dashboardService = inject(DashboardService);
  overview = signal<any>(null);
  heatmapData = signal<Record<string, number>>({});

  heatmapEntries = () => {
    return Object.entries(this.heatmapData()).map(([date, hours]) => ({ date, hours }));
  };

  studyHoursDisplay(): string {
    const hours = this.overview()?.overview?.total_study_hours ?? 0;
    return Math.round(hours).toString();
  }

  getHeatmapColor(hours: number): string {
    if (hours === 0) return 'rgba(255,255,255,0.05)';
    if (hours < 2) return 'rgba(99,102,241,0.2)';
    if (hours < 4) return 'rgba(99,102,241,0.4)';
    if (hours < 6) return 'rgba(99,102,241,0.6)';
    if (hours < 8) return 'rgba(99,102,241,0.8)';
    return '#6366f1';
  }

  ngOnInit(): void {
    this.dashboardService.getAnalyticsOverview().subscribe(data => this.overview.set(data));
    this.dashboardService.getStudyHeatmap().subscribe(data => this.heatmapData.set(data.heatmap || {}));
  }
}
