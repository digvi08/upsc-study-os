import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-answer-evaluation',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-6 animate-fade-in">
      <div>
        <h1 class="text-2xl font-bold text-white">Answer Evaluation</h1>
        <p class="text-gray-400 mt-1">Get AI feedback on your UPSC answers — typed or handwritten</p>
      </div>

      <!-- Input form -->
      <div class="glass-card p-6">
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1.5">Question</label>
            <textarea [(ngModel)]="question" placeholder="Enter the UPSC question..."
                      rows="3" class="input-field resize-none"></textarea>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1.5">Your Answer</label>
            <textarea [(ngModel)]="answer" placeholder="Write your answer here..."
                      rows="10" class="input-field resize-none font-mono text-sm"></textarea>
          </div>
          <div class="flex items-center gap-4">
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Total Marks</label>
              <input type="number" [(ngModel)]="marks" min="5" max="25" class="input-field w-24" />
            </div>
            <button (click)="evaluate()" [disabled]="!question.trim() || !answer.trim() || evaluating()"
                    class="btn-primary flex items-center gap-2 mt-5">
              @if (evaluating()) {
                <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Evaluating...
              } @else {
                ✍️ Evaluate Answer
              }
            </button>
          </div>
        </div>
      </div>

      <!-- Results -->
      @if (result()) {
        <div class="space-y-4 animate-slide-up">
          <!-- Score overview -->
          <div class="glass-card p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-white">Evaluation Result</h2>
              <div class="text-center">
                <p class="text-3xl font-bold"
                   [class]="getScoreColor(result()!.result.percentage || 0)">
                  {{ result()!.result.obtained_marks }}/{{ result()!.result.total_marks }}
                </p>
                <p class="text-gray-400 text-sm">{{ result()!.result.percentage | number:'1.0-0' }}%</p>
              </div>
            </div>

            <!-- Score breakdown -->
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
              @for (score of scoreBreakdown(); track score.label) {
                <div class="p-3 rounded-xl" style="background: rgba(255,255,255,0.03);">
                  <p class="text-gray-400 text-xs">{{ score.label }}</p>
                  <div class="flex items-center gap-2 mt-1">
                    <div class="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div class="h-full rounded-full" [style.width.%]="score.value * 10"
                           [style.background]="getScoreBarColor(score.value)"></div>
                    </div>
                    <span class="text-white text-sm font-medium">{{ score.value | number:'1.0-1' }}</span>
                  </div>
                </div>
              }
            </div>
          </div>

          <!-- Feedback -->
          <div class="glass-card p-6">
            <h3 class="text-lg font-semibold text-white mb-3">Overall Feedback</h3>
            <p class="text-gray-300 text-sm leading-relaxed">{{ result()!.result.overall_feedback }}</p>
          </div>

          <!-- Strengths & Improvements -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="glass-card p-5">
              <h3 class="text-green-400 font-semibold mb-3">✅ Strengths</h3>
              <ul class="space-y-2">
                @for (s of result()!.result.strengths; track s) {
                  <li class="text-gray-300 text-sm flex items-start gap-2">
                    <span class="text-green-400 mt-0.5">•</span> {{ s }}
                  </li>
                }
              </ul>
            </div>
            <div class="glass-card p-5">
              <h3 class="text-yellow-400 font-semibold mb-3">💡 Improvements</h3>
              <ul class="space-y-2">
                @for (i of result()!.result.improvements; track i) {
                  <li class="text-gray-300 text-sm flex items-start gap-2">
                    <span class="text-yellow-400 mt-0.5">•</span> {{ i }}
                  </li>
                }
              </ul>
            </div>
          </div>
        </div>
      }
    </div>
  `,
})
export class AnswerEvaluationComponent {
  private http = inject(HttpClient);
  question = '';
  answer = '';
  marks = 10;
  evaluating = signal(false);
  result = signal<any>(null);

  getScoreColor(pct: number): string {
    if (pct >= 70) return 'text-green-400';
    if (pct >= 50) return 'text-yellow-400';
    return 'text-red-400';
  }

  getScoreBarColor(val: number): string {
    if (val >= 7) return '#10b981';
    if (val >= 5) return '#f59e0b';
    return '#ef4444';
  }

  scoreBreakdown = () => {
    const r = this.result()?.result;
    if (!r) return [];
    return [
      { label: 'Structure', value: r.structure_score || 0 },
      { label: 'Content', value: r.content_score || 0 },
      { label: 'Keywords', value: r.keyword_score || 0 },
      { label: 'Analysis', value: r.analytical_score || 0 },
      { label: 'Grammar', value: r.grammar_score || 0 },
      { label: 'Examples', value: r.examples_score || 0 },
    ];
  };

  evaluate(): void {
    this.evaluating.set(true);
    this.http.post(`${environment.apiUrl}/answer-evaluation/evaluate-text`, null, {
      params: { question: this.question, answer: this.answer, marks: this.marks },
    }).subscribe({
      next: (data) => { this.result.set(data); this.evaluating.set(false); },
      error: () => this.evaluating.set(false),
    });
  }
}
