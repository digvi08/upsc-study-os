import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { NoteService } from '../../services/note.service';
import { NotificationService } from '../../services/notification.service';
import { Note } from '../../shared/models';
import { SkeletonComponent } from '../../shared/components/skeleton/skeleton.component';

@Component({
  selector: 'app-note-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, SkeletonComponent],
  template: `
    <div class="space-y-6 animate-fade-in max-w-4xl mx-auto">
      <a routerLink="/notes" class="text-primary-400 text-sm hover:text-primary-300">← Back to Notes</a>

      @if (loading()) {
        <app-skeleton height="400px" />
      } @else if (note()) {
        <div class="glass-card p-6 space-y-4" [style.border-left]="'4px solid ' + note()!.color">
          <div class="flex items-start justify-between gap-4">
            <input
              type="text"
              [(ngModel)]="editTitle"
              class="input-field text-xl font-bold flex-1"
            />
            <div class="flex gap-2">
              <button (click)="togglePin()" class="btn-secondary text-sm">
                {{ note()!.is_pinned ? '📌 Pinned' : '📌 Pin' }}
              </button>
              <button (click)="saveNote()" class="btn-primary text-sm" [disabled]="saving()">
                {{ saving() ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>

          <textarea
            [(ngModel)]="editContent"
            rows="16"
            class="input-field resize-none font-mono text-sm leading-relaxed"
            placeholder="Write your note (Markdown supported)..."
          ></textarea>

          @if (note()!.ai_summary) {
            <div class="rounded-xl p-4" style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.2);">
              <h3 class="text-sm font-semibold text-primary-300 mb-2">🤖 AI Summary</h3>
              <p class="text-gray-300 text-sm whitespace-pre-wrap">{{ note()!.ai_summary }}</p>
            </div>
          }

          @if (note()!.flashcards.length) {
            <div>
              <h3 class="text-sm font-semibold text-white mb-3">Flashcards ({{ note()!.flashcards.length }})</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                @for (card of note()!.flashcards; track $index) {
                  <div class="glass-card p-4 text-sm">
                    <p class="text-gray-400 text-xs mb-1">Q</p>
                    <p class="text-white mb-2">{{ card.front }}</p>
                    <p class="text-gray-400 text-xs mb-1">A</p>
                    <p class="text-gray-300">{{ card.back }}</p>
                  </div>
                }
              </div>
            </div>
          }

          <div class="flex flex-wrap gap-2 pt-2 border-t border-white/5">
            <button (click)="generateSummary()" class="btn-secondary text-sm">🤖 AI Summary</button>
            <button (click)="generateFlashcards()" class="btn-secondary text-sm">🃏 Generate Flashcards</button>
            <button (click)="deleteNote()" class="text-red-400 hover:text-red-300 text-sm ml-auto">🗑️ Delete</button>
          </div>
        </div>
      }
    </div>
  `,
})
export class NoteDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private noteService = inject(NoteService);
  private notifications = inject(NotificationService);

  note = signal<Note | null>(null);
  loading = signal(true);
  saving = signal(false);
  editTitle = '';
  editContent = '';

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.router.navigate(['/notes']);
      return;
    }
    this.noteService.getNote(id).subscribe({
      next: (n) => {
        this.note.set(n);
        this.editTitle = n.title;
        this.editContent = n.content;
        this.loading.set(false);
      },
      error: () => {
        this.notifications.error('Note not found');
        this.router.navigate(['/notes']);
      },
    });
  }

  saveNote(): void {
    const n = this.note();
    if (!n) return;
    this.saving.set(true);
    this.noteService.updateNote(n.id, {
      title: this.editTitle,
      content: this.editContent,
    }).subscribe({
      next: (updated) => {
        this.note.set(updated);
        this.saving.set(false);
        this.notifications.success('Note saved');
      },
      error: () => this.saving.set(false),
    });
  }

  togglePin(): void {
    const n = this.note();
    if (!n) return;
    this.noteService.togglePin(n.id).subscribe({
      next: (updated) => this.note.set(updated),
    });
  }

  generateSummary(): void {
    const n = this.note();
    if (!n) return;
    this.notifications.info('Generating AI summary...');
    this.noteService.generateAISummary(n.id).subscribe({
      next: () => {
        this.noteService.getNote(n.id).subscribe({
          next: (updated) => this.note.set(updated),
        });
        this.notifications.success('Summary generated');
      },
    });
  }

  generateFlashcards(): void {
    const n = this.note();
    if (!n) return;
    this.notifications.info('Generating flashcards...');
    this.noteService.generateFlashcards(n.id).subscribe({
      next: () => {
        this.noteService.getNote(n.id).subscribe({
          next: (updated) => this.note.set(updated),
        });
        this.notifications.success('Flashcards generated');
      },
    });
  }

  deleteNote(): void {
    const n = this.note();
    if (!n || !confirm('Delete this note?')) return;
    this.noteService.deleteNote(n.id).subscribe({
      next: () => {
        this.notifications.success('Note deleted');
        this.router.navigate(['/notes']);
      },
    });
  }
}
