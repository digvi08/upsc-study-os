import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { NoteService } from '../../services/note.service';
import { NotificationService } from '../../services/notification.service';
import { Note, NoteCreate } from '../../shared/models';
import { SkeletonComponent } from '../../shared/components/skeleton/skeleton.component';
import { debounceTime, Subject } from 'rxjs';

@Component({
  selector: 'app-notes-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, SkeletonComponent],
  template: `
    <div class="space-y-6 animate-fade-in">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-white">Smart Notes</h1>
          <p class="text-gray-400 mt-1">{{ totalNotes() }} notes · AI-powered summaries & flashcards</p>
        </div>
        <div class="flex gap-3">
          <button (click)="generateAINote()" class="btn-secondary flex items-center gap-2">
            🤖 AI Generate
          </button>
          <button (click)="showCreateForm.set(true)" class="btn-primary flex items-center gap-2">
            + New Note
          </button>
        </div>
      </div>

      <!-- Search & Filters -->
      <div class="glass-card p-4 flex gap-4 flex-wrap">
        <div class="flex-1 min-w-48 relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">🔍</span>
          <input type="text" [(ngModel)]="searchQuery" (ngModelChange)="onSearch($event)"
                 placeholder="Search notes..." class="input-field pl-10 py-2 text-sm" />
        </div>
        <select [(ngModel)]="filterType" (ngModelChange)="loadNotes()" class="input-field py-2 text-sm w-40">
          <option value="">All Types</option>
          <option value="manual">Manual</option>
          <option value="ai_generated">AI Generated</option>
          <option value="summary">Summary</option>
          <option value="flashcard">Flashcard</option>
        </select>
        <button (click)="togglePinnedFilter()"
                class="px-4 py-2 rounded-xl text-sm transition-all"
                [class]="pinnedOnly() ? 'bg-primary-500/20 text-primary-300 border border-primary-500/40' : 'btn-secondary'">
          📌 Pinned
        </button>
      </div>

      <!-- Create Note Form -->
      @if (showCreateForm()) {
        <div class="glass-card p-6 animate-slide-up">
          <h3 class="text-lg font-semibold text-white mb-4">New Note</h3>
          <div class="space-y-4">
            <input type="text" [(ngModel)]="newNote.title" placeholder="Note title..."
                   class="input-field text-lg font-medium" />
            <textarea [(ngModel)]="newNote.content" placeholder="Write your note here... (Markdown supported)"
                      rows="8" class="input-field resize-none font-mono text-sm"></textarea>
            <div class="flex gap-3">
              <button (click)="createNote()" class="btn-primary">Save Note</button>
              <button (click)="showCreateForm.set(false)" class="btn-secondary">Cancel</button>
            </div>
          </div>
        </div>
      }

      <!-- Notes Grid -->
      @if (loading()) {
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          @for (i of [1,2,3,4,5,6]; track i) { <app-skeleton height="200px" /> }
        </div>
      } @else if (notes().length === 0) {
        <div class="glass-card p-12 text-center">
          <span class="text-6xl">📝</span>
          <h3 class="text-xl font-semibold text-white mt-4">No notes yet</h3>
          <p class="text-gray-400 mt-2">Create your first note or let AI generate one for you</p>
        </div>
      } @else {
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          @for (note of notes(); track note.id) {
            <a [routerLink]="['/notes', note.id]"
               class="glass-card-hover p-5 flex flex-col gap-3 cursor-pointer no-underline"
               [style.border-left]="'3px solid ' + note.color">
              <!-- Note header -->
              <div class="flex items-start justify-between gap-2">
                <h3 class="text-white font-semibold text-sm leading-tight flex-1">{{ note.title }}</h3>
                <div class="flex gap-1 flex-shrink-0">
                  @if (note.is_pinned) { <span class="text-yellow-400 text-xs">📌</span> }
                  @if (note.is_favorite) { <span class="text-red-400 text-xs">❤️</span> }
                </div>
              </div>

              <!-- Content preview -->
              <p class="text-gray-400 text-xs leading-relaxed line-clamp-3">
                {{ note.content | slice:0:150 }}{{ note.content.length > 150 ? '...' : '' }}
              </p>

              <!-- Tags -->
              @if (note.tags.length > 0) {
                <div class="flex flex-wrap gap-1">
                  @for (tag of note.tags.slice(0, 3); track tag) {
                    <span class="badge badge-primary text-xs">{{ tag }}</span>
                  }
                </div>
              }

              <!-- Footer -->
              <div class="flex items-center justify-between mt-auto pt-2 border-t border-white/5">
                <span class="text-gray-600 text-xs">{{ note.created_at | date:'MMM d' }}</span>
                <div class="flex gap-2">
                  <button (click)="togglePin(note); $event.stopPropagation()"
                          class="text-gray-500 hover:text-yellow-400 transition-colors text-sm">📌</button>
                  <button (click)="generateSummary(note); $event.stopPropagation()"
                          class="text-gray-500 hover:text-primary-400 transition-colors text-sm">🤖</button>
                  <button (click)="deleteNote(note.id); $event.stopPropagation()"
                          class="text-gray-500 hover:text-red-400 transition-colors text-sm">🗑️</button>
                </div>
              </div>
            </a>
          }
        </div>
      }
    </div>
  `,
})
export class NotesListComponent implements OnInit {
  private noteService = inject(NoteService);
  private notifications = inject(NotificationService);
  private searchSubject = new Subject<string>();

  notes = signal<Note[]>([]);
  loading = signal(true);
  totalNotes = signal(0);
  showCreateForm = signal(false);
  searchQuery = '';
  filterType = '';
  pinnedOnly = signal(false);

  newNote: NoteCreate = {
    title: '', content: '', note_type: 'manual', tags: [], color: '#6366f1', is_pinned: false,
  };

  ngOnInit(): void {
    this.loadNotes();
    this.searchSubject.pipe(debounceTime(400)).subscribe(() => this.loadNotes());
  }

  onSearch(query: string): void {
    this.searchSubject.next(query);
  }

  togglePinnedFilter(): void {
    this.pinnedOnly.update(v => !v);
    this.loadNotes();
  }

  loadNotes(): void {
    this.loading.set(true);
    this.noteService.getNotes({
      search: this.searchQuery || undefined,
      note_type: this.filterType || undefined,
      pinned_only: this.pinnedOnly(),
    }).subscribe({
      next: (data) => {
        this.notes.set(data.items);
        this.totalNotes.set(data.total);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  createNote(): void {
    if (!this.newNote.title.trim()) return;
    this.noteService.createNote(this.newNote).subscribe({
      next: (note) => {
        this.notes.update(n => [note, ...n]);
        this.showCreateForm.set(false);
        this.newNote = { title: '', content: '', note_type: 'manual', tags: [], color: '#6366f1', is_pinned: false };
        this.notifications.success('Note created');
      },
    });
  }

  togglePin(note: Note): void {
    this.noteService.togglePin(note.id).subscribe({
      next: (updated) => this.notes.update(ns => ns.map(n => n.id === updated.id ? updated : n)),
    });
  }

  generateSummary(note: Note): void {
    this.notifications.info('Generating AI summary...');
    this.noteService.generateAISummary(note.id).subscribe({
      next: () => this.notifications.success('AI summary generated'),
    });
  }

  generateAINote(): void {
    const topic = prompt('Enter topic for AI note generation:');
    if (!topic) return;
    this.notifications.info('Generating AI note...');
    this.noteService.generateAINote(topic).subscribe({
      next: (note) => {
        this.notes.update(n => [note, ...n]);
        this.notifications.success('AI note generated');
      },
    });
  }

  deleteNote(id: string): void {
    this.noteService.deleteNote(id).subscribe({
      next: () => {
        this.notes.update(ns => ns.filter(n => n.id !== id));
        this.notifications.success('Note deleted');
      },
    });
  }
}
