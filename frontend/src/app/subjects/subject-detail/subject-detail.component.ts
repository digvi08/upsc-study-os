import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { SubjectService } from '../../services/subject.service';
import { NotificationService } from '../../services/notification.service';
import { Subject, Topic, TopicStatus } from '../../shared/models';

@Component({
  selector: 'app-subject-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="space-y-6 animate-fade-in">
      <!-- Back + Header -->
      <div class="flex items-center gap-4">
        <a routerLink="/subjects" class="text-gray-400 hover:text-white transition-colors">← Back</a>
        @if (subject()) {
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                 [style.background]="subject()!.color + '20'">📚</div>
            <div>
              <h1 class="text-2xl font-bold text-white">{{ subject()!.name }}</h1>
              <p class="text-gray-400 text-sm">{{ subject()!.completed_topics }}/{{ subject()!.total_topics }} topics completed</p>
            </div>
          </div>
        }
        <button (click)="showAddTopic.set(true)" class="btn-primary ml-auto flex items-center gap-2">
          + Add Topic
        </button>
      </div>

      <!-- Add Topic Form -->
      @if (showAddTopic()) {
        <div class="glass-card p-6 animate-slide-up">
          <h3 class="text-lg font-semibold text-white mb-4">Add New Topic</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Topic Name</label>
              <input type="text" [(ngModel)]="newTopic.name" placeholder="e.g., Indian Ocean Dipole"
                     class="input-field" />
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Priority</label>
              <select [(ngModel)]="newTopic.priority" class="input-field">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Importance (1-10)</label>
              <input type="range" [(ngModel)]="newTopic.importance_score" min="1" max="10"
                     class="w-full" />
              <span class="text-primary-400 text-sm">{{ newTopic.importance_score }}/10</span>
            </div>
          </div>
          <div class="flex gap-3 mt-4">
            <button (click)="addTopic()" class="btn-primary">Add Topic</button>
            <button (click)="showAddTopic.set(false)" class="btn-secondary">Cancel</button>
          </div>
        </div>
      }

      <!-- Filter tabs -->
      <div class="flex gap-2">
        @for (filter of statusFilters; track filter.value) {
          <button
            (click)="activeFilter.set(filter.value)"
            class="px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200"
            [class]="activeFilter() === filter.value
              ? 'text-white bg-primary-500/20 border border-primary-500/40'
              : 'text-gray-400 hover:text-white border border-white/10'"
          >
            {{ filter.label }}
            <span class="ml-1 text-xs opacity-70">({{ getTopicCount(filter.value) }})</span>
          </button>
        }
      </div>

      <!-- Topics list -->
      <div class="space-y-2">
        @for (topic of filteredTopics(); track topic.id) {
          <div class="glass-card p-4 flex items-center gap-4 group">
            <!-- Status indicator -->
            <button
              (click)="cycleStatus(topic)"
              class="w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all"
              [class]="getStatusClass(topic.status)"
            >
              @if (topic.status === 'completed') { ✓ }
            </button>

            <!-- Topic info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-white font-medium" [class.line-through]="topic.status === 'completed'"
                      [class.text-gray-500]="topic.status === 'completed'">
                  {{ topic.name }}
                </span>
                <span class="badge" [class]="getPriorityBadge(topic.priority)">
                  {{ topic.priority }}
                </span>
                @if (topic.pyq_frequency > 0) {
                  <span class="badge badge-warning text-xs">PYQ ×{{ topic.pyq_frequency }}</span>
                }
              </div>
              <div class="flex items-center gap-3 mt-1">
                <span class="text-gray-500 text-xs">Importance: {{ topic.importance_score }}/10</span>
                @if (topic.revision_count > 0) {
                  <span class="text-gray-500 text-xs">Revised {{ topic.revision_count }}×</span>
                }
                @if (topic.study_time_minutes > 0) {
                  <span class="text-gray-500 text-xs">{{ topic.study_time_minutes }}min studied</span>
                }
              </div>
            </div>

            <!-- Confidence bar -->
            <div class="w-24 hidden md:block">
              <div class="flex justify-between text-xs text-gray-500 mb-1">
                <span>Confidence</span>
                <span>{{ topic.confidence_level }}%</span>
              </div>
              <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all"
                     [style.width.%]="topic.confidence_level"
                     [style.background]="getConfidenceColor(topic.confidence_level)"></div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button class="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all text-sm"
                      title="Schedule revision">🔄</button>
              <button class="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all text-sm"
                      title="Add note">📝</button>
              <button (click)="deleteTopic(topic.id)"
                      class="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-all text-sm">
                🗑️
              </button>
            </div>
          </div>
        }

        @if (filteredTopics().length === 0) {
          <div class="glass-card p-8 text-center">
            <span class="text-4xl">📋</span>
            <p class="text-gray-400 mt-2">No topics in this category</p>
          </div>
        }
      </div>
    </div>
  `,
})
export class SubjectDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private subjectService = inject(SubjectService);
  private notifications = inject(NotificationService);

  subject = signal<Subject | null>(null);
  topics = signal<Topic[]>([]);
  showAddTopic = signal(false);
  activeFilter = signal('all');

  newTopic = { name: '', priority: 'medium' as any, importance_score: 5, tags: [] as string[] };

  statusFilters = [
    { value: 'all', label: 'All' },
    { value: 'not_started', label: 'Not Started' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'needs_revision', label: 'Needs Revision' },
  ];

  filteredTopics = () => {
    const filter = this.activeFilter();
    if (filter === 'all') return this.topics();
    return this.topics().filter(t => t.status === filter);
  };

  getTopicCount(filter: string): number {
    if (filter === 'all') return this.topics().length;
    return this.topics().filter(t => t.status === filter).length;
  }

  getStatusClass(status: TopicStatus): string {
    const classes: Record<string, string> = {
      not_started: 'border-gray-600 text-transparent',
      in_progress: 'border-yellow-500 text-yellow-500',
      completed: 'border-green-500 bg-green-500 text-white',
      needs_revision: 'border-orange-500 text-orange-500',
    };
    return classes[status] || '';
  }

  getPriorityBadge(priority: string): string {
    const classes: Record<string, string> = {
      low: 'badge-info',
      medium: 'badge-warning',
      high: 'badge-danger',
      critical: 'bg-red-600/30 text-red-300 border border-red-500/40 badge',
    };
    return classes[priority] || 'badge-info';
  }

  getConfidenceColor(level: number): string {
    if (level >= 70) return '#10b981';
    if (level >= 40) return '#f59e0b';
    return '#ef4444';
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id')!;
    this.subjectService.getSubject(id).subscribe(s => this.subject.set(s));
    this.subjectService.getTopics(id).subscribe(t => this.topics.set(t));
  }

  addTopic(): void {
    const subjectId = this.subject()?.id;
    if (!subjectId || !this.newTopic.name.trim()) return;
    this.subjectService.createTopic(subjectId, { ...this.newTopic, subject_id: subjectId }).subscribe({
      next: (topic) => {
        this.topics.update(t => [...t, topic]);
        this.showAddTopic.set(false);
        this.newTopic = { name: '', priority: 'medium', importance_score: 5, tags: [] };
        this.notifications.success('Topic added');
      },
    });
  }

  cycleStatus(topic: Topic): void {
    const cycle: Record<TopicStatus, TopicStatus> = {
      not_started: 'in_progress',
      in_progress: 'completed',
      completed: 'needs_revision',
      needs_revision: 'not_started',
    };
    const newStatus = cycle[topic.status];
    this.subjectService.updateTopic(topic.id, { status: newStatus }).subscribe({
      next: (updated) => {
        this.topics.update(ts => ts.map(t => t.id === updated.id ? updated : t));
      },
    });
  }

  deleteTopic(id: string): void {
    this.subjectService.deleteTopic(id).subscribe({
      next: () => {
        this.topics.update(ts => ts.filter(t => t.id !== id));
        this.notifications.success('Topic deleted');
      },
    });
  }
}
