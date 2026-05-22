import { Component, Input, Output, EventEmitter, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [RouterLink, CommonModule, FormsModule],
  template: `
    <header class="flex items-center gap-4 px-6 py-4 border-b border-white/5 flex-shrink-0"
            style="background: rgba(15,15,35,0.8); backdrop-filter: blur(12px);">

      <!-- Sidebar toggle -->
      <button
        (click)="toggleSidebar.emit()"
        class="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-all"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>

      <!-- Search bar -->
      <div class="flex-1 max-w-xl relative">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">🔍</span>
        <input
          type="text"
          placeholder="Search topics, notes, PYQs..."
          [(ngModel)]="searchQuery"
          class="input-field pl-10 py-2 text-sm"
        />
        @if (searchQuery) {
          <button
            (click)="searchQuery = ''"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
          >✕</button>
        }
      </div>

      <div class="flex items-center gap-3 ml-auto">
        <!-- Streak badge -->
        <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl"
             style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2);">
          <span>🔥</span>
          <span class="text-yellow-400 font-semibold text-sm">
            {{ authService.user()?.current_streak || 0 }}
          </span>
        </div>

        <!-- Notifications -->
        <button class="relative p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-all">
          <span class="text-xl">🔔</span>
          <span class="notification-dot"></span>
        </button>

        <!-- Profile -->
        <a routerLink="/profile"
           class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold text-white cursor-pointer"
           style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">
          {{ userInitial }}
        </a>
      </div>
    </header>
  `,
})
export class TopbarComponent {
  @Input() sidebarCollapsed = false;
  @Output() toggleSidebar = new EventEmitter<void>();

  authService = inject(AuthService);
  searchQuery = '';

  get userInitial(): string {
    return this.authService.user()?.full_name?.charAt(0)?.toUpperCase() || 'U';
  }
}
