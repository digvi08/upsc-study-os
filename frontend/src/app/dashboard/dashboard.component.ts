import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { DashboardService } from '../services/dashboard.service';
import { AuthService } from '../services/auth.service';
import { ProgressRingComponent } from '../shared/components/progress-ring/progress-ring.component';
import { StatCardComponent } from '../shared/components/stat-card/stat-card.component';
import { SkeletonComponent } from '../shared/components/skeleton/skeleton.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, ProgressRingComponent, StatCardComponent, SkeletonComponent],
  template: `
    <div class="space-y-6 animate-fade-in">

      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white">
            Good {{ greeting }}, {{ userFirstName() }} 👋
          </h1>
          <p class="text-gray-400 mt-1">Here's your preparation overview for today</p>
        </div>
        <div class="flex items-center gap-3">
          <div class="glass-card px-4 py-2 flex items-center gap-2">
            <span>🔥</span>
            <span class="text-yellow-400 font-bold">{{ stats()?.streak?.current || 0 }} day streak</span>
          </div>
          <button class="btn-primary text-sm px-4 py-2">
            + Log Study Session
          </button>
        </div>
      </div>

      <!-- Stats Grid -->
      @if (loading()) {
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          @for (i of [1,2,3,4]; track i) {
            <app-skeleton height="120px" />
          }
        </div>
      } @else {
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <app-stat-card
            icon="📚"
            label="Subjects"
            [value]="stats()?.subjects?.total || 0"
            subtitle="Active subjects"
            color="#6366f1"
          />
          <app-stat-card
            icon="✅"
            label="Topics Done"
            [value]="stats()?.subjects?.topics_completed || 0"
            [subtitle]="'of ' + (stats()?.subjects?.topics_total || 0) + ' total'"
            color="#10b981"
          />
          <app-stat-card
            icon="📝"
            label="Notes"
            [value]="stats()?.notes?.total || 0"
            subtitle="Created notes"
            color="#8b5cf6"
          />
          <app-stat-card
            icon="🔄"
            label="Revisions Due"
            [value]="stats()?.revisions?.pending || 0"
            subtitle="Pending today"
            color="#f59e0b"
          />
        </div>
      }

      <!-- Main content grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Today's Tasks -->
        <div class="lg:col-span-2 glass-card p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-white">Today's Tasks</h2>
            <a routerLink="/planner" class="text-primary-400 text-sm hover:text-primary-300">View all →</a>
          </div>

          @if (loading()) {
            <div class="space-y-3">
              @for (i of [1,2,3]; track i) {
                <app-skeleton height="60px" />
              }
            </div>
          } @else if (!stats()?.today?.tasks_total) {
            <div class="text-center py-8">
              <span class="text-4xl">📅</span>
              <p class="text-gray-400 mt-2">No tasks planned for today</p>
              <a routerLink="/planner" class="btn-primary text-sm px-4 py-2 mt-3 inline-block">
                Generate AI Plan
              </a>
            </div>
          } @else {
            <!-- Progress bar -->
            <div class="mb-4">
              <div class="flex justify-between text-sm mb-2">
                <span class="text-gray-400">Daily Progress</span>
                <span class="text-white font-medium">
                  {{ stats()?.today?.tasks_completed }}/{{ stats()?.today?.tasks_total }} tasks
                </span>
              </div>
              <div class="h-2 bg-white/10 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  style="background: linear-gradient(90deg, #6366f1, #8b5cf6);"
                  [style.width.%]="stats()?.today?.completion_percentage || 0"
                ></div>
              </div>
            </div>
          }
        </div>

        <!-- Progress Ring -->
        <div class="glass-card p-6 flex flex-col items-center justify-center">
          <h2 class="text-lg font-semibold text-white mb-4 self-start">Overall Progress</h2>
          <app-progress-ring
            [percentage]="stats()?.subjects?.completion_percentage || 0"
            [size]="140"
            color="#6366f1"
          />
          <p class="text-gray-400 text-sm mt-3 text-center">
            {{ stats()?.subjects?.topics_completed || 0 }} of
            {{ stats()?.subjects?.topics_total || 0 }} topics completed
          </p>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="glass-card p-6">
        <h2 class="text-lg font-semibold text-white mb-4">Quick Actions</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          @for (action of quickActions; track action.label) {
            <a
              [routerLink]="action.route"
              class="flex flex-col items-center gap-2 p-4 rounded-xl transition-all duration-200 cursor-pointer group"
              style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);"
              [style.--hover-color]="action.color"
            >
              <span class="text-2xl group-hover:scale-110 transition-transform">{{ action.icon }}</span>
              <span class="text-xs text-gray-400 group-hover:text-white text-center transition-colors">
                {{ action.label }}
              </span>
            </a>
          }
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="glass-card p-6">
        <h2 class="text-lg font-semibold text-white mb-4">Study Activity (Last 7 Days)</h2>
        <div class="flex items-end gap-2 h-24">
          @for (day of recentActivity(); track day.date) {
            <div class="flex-1 flex flex-col items-center gap-1">
              <div
                class="w-full rounded-t-sm transition-all duration-300"
                [style.height.%]="(day.study_hours / maxHours()) * 100"
                [style.background]="day.study_hours > 0 ? 'linear-gradient(180deg, #6366f1, #4f46e5)' : 'rgba(255,255,255,0.05)'"
                [style.min-height]="'4px'"
                [attr.data-tooltip]="day.study_hours + 'h'"
              ></div>
              <span class="text-gray-600 text-xs">{{ day.day }}</span>
            </div>
          }
        </div>
      </div>

    </div>
  `,
})
export class DashboardComponent implements OnInit {
  authService = inject(AuthService);
  private dashboardService = inject(DashboardService);

  stats = signal<any>(null);
  loading = signal(true);
  recentActivity = signal<any[]>([]);
  maxHours = signal(8);

  quickActions = [
    { icon: '🔍', label: 'Analyze PYQ', route: '/pyq', color: '#6366f1' },
    { icon: '🤖', label: 'Ask AI Mentor', route: '/ai-mentor', color: '#8b5cf6' },
    { icon: '📝', label: 'New Note', route: '/notes', color: '#10b981' },
    { icon: '🔄', label: 'Revise Now', route: '/revision', color: '#f59e0b' },
    { icon: '📰', label: 'Current Affairs', route: '/current-affairs', color: '#3b82f6' },
    { icon: '✍️', label: 'Evaluate Answer', route: '/answer-evaluation', color: '#ec4899' },
  ];

  userFirstName(): string {
    const name = this.authService.user()?.full_name;
    return name ? name.split(' ')[0] : 'Aspirant';
  }

  get greeting(): string {
    const hour = new Date().getHours();
    if (hour < 12) return 'morning';
    if (hour < 17) return 'afternoon';
    return 'evening';
  }

  ngOnInit(): void {
    this.dashboardService.getDashboardStats().subscribe({
      next: (data) => {
        this.stats.set(data);
        const activity = data.recent_activity || [];
        this.recentActivity.set(activity.map((a: any) => ({
          ...a,
          day: new Date(a.date).toLocaleDateString('en', { weekday: 'short' }),
        })));
        const max = Math.max(...activity.map((a: any) => a.study_hours), 1);
        this.maxHours.set(max);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }
}
