import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PYQService } from '../../services/pyq.service';
import { PYQAnalysis } from '../../shared/models';
import { SkeletonComponent } from '../../shared/components/skeleton/skeleton.component';

@Component({
  selector: 'app-pyq-analyzer',
  standalone: true,
  imports: [CommonModule, FormsModule, SkeletonComponent],
  template: `
    <div class="space-y-6 animate-fade-in">

      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-white">PYQ Analyzer</h1>
        <p class="text-gray-400 mt-1">Analyze previous year questions, identify trends, and get AI insights</p>
      </div>

      <!-- Search Panel -->
      <div class="glass-card p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm text-gray-400 mb-1.5">Topic / Keyword</label>
            <input
              type="text"
              [(ngModel)]="searchTopic"
              placeholder="e.g., Monsoon, Federalism, Landforms, El Niño..."
              class="input-field"
              (keydown.enter)="analyze()"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1.5">Subject (optional)</label>
            <input
              type="text"
              [(ngModel)]="searchSubject"
              placeholder="e.g., Geography, Polity..."
              class="input-field"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1.5">Years to analyze</label>
            <select [(ngModel)]="yearsToAnalyze" class="input-field">
              <option value="5">Last 5 years</option>
              <option value="10" selected>Last 10 years</option>
              <option value="15">Last 15 years</option>
              <option value="20">Last 20 years</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1.5">Exam Type</label>
            <select [(ngModel)]="examType" class="input-field">
              <option value="">Both Prelims & Mains</option>
              <option value="prelims">Prelims Only</option>
              <option value="mains">Mains Only</option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              (click)="analyze()"
              [disabled]="!searchTopic.trim() || loading()"
              class="btn-primary w-full flex items-center justify-center gap-2"
            >
              @if (loading()) {
                <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Analyzing...
              } @else {
                🔍 Analyze PYQs
              }
            </button>
          </div>
        </div>
      </div>

      <!-- Results -->
      @if (loading()) {
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          @for (i of [1,2,3,4,5,6]; track i) {
            <app-skeleton height="120px" />
          }
        </div>
      }

      @if (analysis() && !loading()) {
        <!-- Stats row -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="glass-card p-4 text-center">
            <p class="text-3xl font-bold text-white">{{ analysis()!.total_questions }}</p>
            <p class="text-gray-400 text-sm mt-1">Total Questions</p>
          </div>
          <div class="glass-card p-4 text-center">
            <p class="text-3xl font-bold"
               [class]="getProbabilityColor(analysis()!.probability_score)">
              {{ (analysis()!.probability_score * 100) | number:'1.0-0' }}%
            </p>
            <p class="text-gray-400 text-sm mt-1">Probability Score</p>
          </div>
          <div class="glass-card p-4 text-center">
            <p class="text-3xl font-bold text-blue-400">
              {{ analysis()!.exam_type_distribution['prelims'] || 0 }}
            </p>
            <p class="text-gray-400 text-sm mt-1">Prelims Questions</p>
          </div>
          <div class="glass-card p-4 text-center">
            <p class="text-3xl font-bold text-purple-400">
              {{ analysis()!.exam_type_distribution['mains'] || 0 }}
            </p>
            <p class="text-gray-400 text-sm mt-1">Mains Questions</p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <!-- Year-wise chart -->
          <div class="glass-card p-6">
            <h3 class="text-lg font-semibold text-white mb-4">Year-wise Frequency</h3>
            <div class="flex items-end gap-2 h-32">
              @for (entry of yearWiseEntries(); track entry.year) {
                <div class="flex-1 flex flex-col items-center gap-1">
                  <div
                    class="w-full rounded-t-sm transition-all duration-500"
                    [style.height.%]="(entry.count / maxYearCount()) * 100"
                    [style.background]="entry.count > 0 ? 'linear-gradient(180deg, #6366f1, #4f46e5)' : 'rgba(255,255,255,0.05)'"
                    style="min-height: 4px;"
                    [attr.data-tooltip]="entry.year + ': ' + entry.count + ' questions'"
                  ></div>
                  <span class="text-gray-600 text-xs">{{ entry.year }}</span>
                </div>
              }
            </div>
          </div>

          <!-- Keywords -->
          <div class="glass-card p-6">
            <h3 class="text-lg font-semibold text-white mb-4">Recurring Keywords</h3>
            <div class="flex flex-wrap gap-2">
              @for (kw of analysis()!.recurring_keywords.slice(0, 15); track kw.keyword) {
                <span
                  class="px-3 py-1 rounded-full text-sm font-medium"
                  [style.background]="'rgba(99,102,241,' + (kw.count / maxKeywordCount() * 0.4 + 0.1) + ')'"
                  [style.border]="'1px solid rgba(99,102,241,0.3)'"
                  [style.color]="'rgba(165,180,252,' + (kw.count / maxKeywordCount() * 0.5 + 0.5) + ')'"
                >
                  {{ kw.keyword }} ({{ kw.count }})
                </span>
              }
            </div>
          </div>
        </div>

        <!-- AI Insights -->
        <div class="glass-card p-6">
          <div class="flex items-center gap-2 mb-4">
            <span class="text-xl">🤖</span>
            <h3 class="text-lg font-semibold text-white">AI Insights</h3>
            <span class="badge badge-primary">AI Generated</span>
          </div>
          <div class="text-gray-300 text-sm leading-relaxed whitespace-pre-line">
            {{ analysis()!.ai_insights }}
          </div>
        </div>

        <!-- Mains Angles -->
        @if (analysis()!.mains_angles.length > 0) {
          <div class="glass-card p-6">
            <h3 class="text-lg font-semibold text-white mb-4">✍️ Mains Answer Angles</h3>
            <div class="space-y-2">
              @for (angle of analysis()!.mains_angles; track angle) {
                <div class="flex items-start gap-2 p-3 rounded-xl"
                     style="background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.15);">
                  <span class="text-primary-400 mt-0.5">→</span>
                  <span class="text-gray-300 text-sm">{{ angle }}</span>
                </div>
              }
            </div>
          </div>
        }

        <!-- Questions list -->
        <div class="glass-card p-6">
          <h3 class="text-lg font-semibold text-white mb-4">
            Questions ({{ analysis()!.questions.length }})
          </h3>
          <div class="space-y-3">
            @for (q of analysis()!.questions.slice(0, 10); track q.id) {
              <div class="p-4 rounded-xl transition-all duration-200"
                   style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);">
                <div class="flex items-center gap-2 mb-2">
                  <span class="badge" [class]="q.exam === 'prelims' ? 'badge-info' : 'badge-primary'">
                    {{ q.exam | titlecase }}
                  </span>
                  <span class="badge badge-warning">{{ q.year }}</span>
                  @if (q.paper) {
                    <span class="badge badge-success">{{ q.paper }}</span>
                  }
                  <span class="text-gray-500 text-xs ml-auto">{{ q.difficulty }}</span>
                </div>
                <p class="text-gray-300 text-sm">{{ q.question }}</p>
              </div>
            }
          </div>
        </div>
      }

      <!-- Empty state -->
      @if (!analysis() && !loading()) {
        <div class="glass-card p-12 text-center">
          <span class="text-6xl">🔍</span>
          <h3 class="text-xl font-semibold text-white mt-4">Enter a topic to analyze</h3>
          <p class="text-gray-400 mt-2">
            Search for any UPSC topic to see PYQ trends, frequency analysis, and AI insights
          </p>
          <div class="flex flex-wrap gap-2 justify-center mt-4">
            @for (topic of popularTopics; track topic) {
              <button
                (click)="searchTopic = topic; analyze()"
                class="badge badge-primary cursor-pointer hover:bg-primary-500/30 transition-colors"
              >
                {{ topic }}
              </button>
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class PYQAnalyzerComponent {
  private pyqService = inject(PYQService);

  searchTopic = '';
  searchSubject = '';
  yearsToAnalyze = 10;
  examType = '';
  loading = signal(false);
  analysis = signal<PYQAnalysis | null>(null);

  popularTopics = ['Monsoon', 'Federalism', 'Landforms', 'El Niño', 'Fundamental Rights', 'Green Revolution'];

  yearWiseEntries = () => {
    const data = this.analysis()?.year_wise_count || {};
    return Object.entries(data)
      .map(([year, count]) => ({ year, count: count as number }))
      .sort((a, b) => a.year.localeCompare(b.year));
  };

  maxYearCount = () => Math.max(...this.yearWiseEntries().map(e => e.count), 1);

  maxKeywordCount = () => {
    const kws = this.analysis()?.recurring_keywords || [];
    return Math.max(...kws.map(k => k.count), 1);
  };

  getProbabilityColor(score: number): string {
    if (score >= 0.7) return 'text-green-400';
    if (score >= 0.4) return 'text-yellow-400';
    return 'text-red-400';
  }

  analyze(): void {
    if (!this.searchTopic.trim()) return;
    this.loading.set(true);
    this.analysis.set(null);

    this.pyqService.analyzeTopic({
      topic: this.searchTopic,
      subject: this.searchSubject || undefined,
      years: this.yearsToAnalyze,
      exam_type: this.examType || undefined,
    }).subscribe({
      next: (data) => {
        this.analysis.set(data);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }
}
