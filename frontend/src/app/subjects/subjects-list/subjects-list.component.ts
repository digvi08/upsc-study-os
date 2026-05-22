import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { SubjectService } from '../../services/subject.service';
import { NotificationService } from '../../services/notification.service';
import { Subject, SubjectCategory } from '../../shared/models';
import { ProgressRingComponent } from '../../shared/components/progress-ring/progress-ring.component';
import { SkeletonComponent } from '../../shared/components/skeleton/skeleton.component';

@Component({
  selector: 'app-subjects-list',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, ProgressRingComponent, SkeletonComponent],
  template: `
    <div class="space-y-6 animate-fade-in">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white">Subjects</h1>
          <p class="text-gray-400 mt-1">Manage your UPSC syllabus subjects and topics</p>
        </div>
        <button (click)="showAddForm.set(true)" class="btn-primary flex items-center gap-2">
          <span>+</span> Add Subject
        </button>
      </div>

      <!-- Add Subject Form -->
      @if (showAddForm()) {
        <div class="glass-card p-6 animate-slide-up">
          <h3 class="text-lg font-semibold text-white mb-4">Add New Subject</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Subject Name</label>
              <input type="text" [(ngModel)]="newSubject.name" placeholder="e.g., Indian Geography"
                     class="input-field" />
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Category</label>
              <select [(ngModel)]="newSubject.category" class="input-field">
                @for (cat of categories; track cat.value) {
                  <option [value]="cat.value">{{ cat.label }}</option>
                }
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Color</label>
              <div class="flex gap-2">
                @for (color of colorOptions; track color) {
                  <button
                    (click)="newSubject.color = color"
                    class="w-8 h-8 rounded-lg border-2 transition-all"
                    [style.background]="color"
                    [class.border-white]="newSubject.color === color"
                    [class.border-transparent]="newSubject.color !== color"
                  ></button>
                }
              </div>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Description (optional)</label>
              <input type="text" [(ngModel)]="newSubject.description" placeholder="Brief description"
                     class="input-field" />
            </div>
          </div>
          <div class="flex gap-3 mt-4">
            <button (click)="addSubject()" class="btn-primary">Add Subject</button>
            <button (click)="showAddForm.set(false)" class="btn-secondary">Cancel</button>
          </div>
        </div>
      }

      <!-- Subjects Grid -->
      @if (loading()) {
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          @for (i of [1,2,3,4,5,6]; track i) {
            <app-skeleton height="180px" />
          }
        </div>
      } @else if (subjects().length === 0) {
        <div class="glass-card p-12 text-center">
          <span class="text-6xl">📚</span>
          <h3 class="text-xl font-semibold text-white mt-4">No subjects yet</h3>
          <p class="text-gray-400 mt-2">Add your first subject to start organizing your preparation</p>
          <button (click)="showAddForm.set(true)" class="btn-primary mt-4">Add First Subject</button>
        </div>
      } @else {
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          @for (subject of subjects(); track subject.id) {
            <a [routerLink]="['/subjects', subject.id]"
               class="glass-card-hover p-5 block cursor-pointer">
              <div class="flex items-start justify-between mb-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
                       [style.background]="subject.color + '20'"
                       [style.border]="'1px solid ' + subject.color + '40'">
                    📚
                  </div>
                  <div>
                    <h3 class="text-white font-semibold">{{ subject.name }}</h3>
                    <span class="badge badge-primary text-xs">{{ getCategoryLabel(subject.category) }}</span>
                  </div>
                </div>
                <app-progress-ring
                  [percentage]="subject.completion_percentage"
                  [size]="50"
                  [strokeWidth]="4"
                  [color]="subject.color"
                />
              </div>

              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-400">
                  {{ subject.completed_topics }}/{{ subject.total_topics }} topics
                </span>
                <div class="h-1.5 flex-1 mx-3 bg-white/10 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500"
                       [style.width.%]="subject.completion_percentage"
                       [style.background]="subject.color"></div>
                </div>
                <span class="font-medium" [style.color]="subject.color">
                  {{ subject.completion_percentage | number:'1.0-0' }}%
                </span>
              </div>
            </a>
          }
        </div>
      }
    </div>
  `,
})
export class SubjectsListComponent implements OnInit {
  private subjectService = inject(SubjectService);
  private notifications = inject(NotificationService);

  subjects = signal<Subject[]>([]);
  loading = signal(true);
  showAddForm = signal(false);

  newSubject = { name: '', category: 'gs1' as SubjectCategory, color: '#6366f1', description: '' };

  categories = [
    { value: 'gs1', label: 'GS Paper 1' },
    { value: 'gs2', label: 'GS Paper 2' },
    { value: 'gs3', label: 'GS Paper 3' },
    { value: 'gs4', label: 'GS Paper 4' },
    { value: 'csat', label: 'CSAT' },
    { value: 'optional', label: 'Optional' },
    { value: 'current_affairs', label: 'Current Affairs' },
  ];

  colorOptions = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#14b8a6'];

  getCategoryLabel(cat: string): string {
    return this.categories.find(c => c.value === cat)?.label || cat;
  }

  ngOnInit(): void {
    this.loadSubjects();
  }

  loadSubjects(): void {
    this.subjectService.getSubjects().subscribe({
      next: (data) => { this.subjects.set(data); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  addSubject(): void {
    if (!this.newSubject.name.trim()) return;
    this.subjectService.createSubject(this.newSubject).subscribe({
      next: (subject) => {
        this.subjects.update(s => [...s, subject]);
        this.showAddForm.set(false);
        this.newSubject = { name: '', category: 'gs1', color: '#6366f1', description: '' };
        this.notifications.success('Subject added successfully');
      },
    });
  }
}
