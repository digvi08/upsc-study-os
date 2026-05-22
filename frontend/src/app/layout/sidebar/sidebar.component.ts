import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

interface NavItem {
  label: string;
  icon: string;
  route: string;
  badge?: number;
  adminOnly?: boolean;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  template: `
    <aside
      class="h-full flex flex-col transition-all duration-300 ease-in-out"
      [class]="collapsed
        ? 'w-16 fixed lg:relative'
        : 'w-64 fixed lg:relative'"
      style="background: rgba(15,15,35,0.95); border-right: 1px solid rgba(255,255,255,0.06);"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-4 py-5 border-b border-white/5">
        <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
             style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">
          <span class="text-white font-bold text-sm">AI</span>
        </div>
        @if (!collapsed) {
          <div class="animate-fade-in">
            <p class="text-white font-bold text-sm leading-tight">UPSC Study OS</p>
            <p class="text-gray-500 text-xs">AI-Powered Prep</p>
          </div>
        }
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        @for (item of navItems; track item.route) {
          @if (!item.adminOnly || authService.isAdmin()) {
            <a
              [routerLink]="item.route"
              routerLinkActive="active"
              class="sidebar-item group relative"
              [class.justify-center]="collapsed"
              [attr.data-tooltip]="collapsed ? item.label : null"
            >
              <span class="text-xl flex-shrink-0">{{ item.icon }}</span>
              @if (!collapsed) {
                <span class="text-sm font-medium animate-fade-in">{{ item.label }}</span>
                @if (item.badge) {
                  <span class="ml-auto badge badge-danger text-xs">{{ item.badge }}</span>
                }
              }
              @if (collapsed && item.badge) {
                <span class="notification-dot"></span>
              }
            </a>
          }
        }
      </nav>

      <!-- User section -->
      <div class="border-t border-white/5 p-3">
        @if (!collapsed) {
          <div class="flex items-center gap-3 px-2 py-2 rounded-xl hover:bg-white/5 cursor-pointer transition-colors">
            <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold text-white"
                 style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">
              {{ userInitial }}
            </div>
            <div class="flex-1 min-w-0 animate-fade-in">
              <p class="text-white text-sm font-medium truncate">{{ authService.user()?.full_name }}</p>
              <p class="text-gray-500 text-xs truncate">{{ authService.user()?.exam_target?.toUpperCase() }}</p>
            </div>
          </div>
        }
        <button
          (click)="authService.logout()"
          class="w-full mt-2 flex items-center gap-3 px-3 py-2 rounded-xl text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200"
          [class.justify-center]="collapsed"
        >
          <span class="text-lg">🚪</span>
          @if (!collapsed) {
            <span class="text-sm animate-fade-in">Logout</span>
          }
        </button>
      </div>
    </aside>
  `,
})
export class SidebarComponent {
  @Input() collapsed = false;
  @Output() toggleCollapse = new EventEmitter<void>();

  authService = inject(AuthService);

  navItems: NavItem[] = [
    { label: 'Dashboard', icon: '🏠', route: '/dashboard' },
    { label: 'Subjects', icon: '📚', route: '/subjects' },
    { label: 'PYQ Analyzer', icon: '🔍', route: '/pyq' },
    { label: 'AI Mentor', icon: '🤖', route: '/ai-mentor' },
    { label: 'Smart Notes', icon: '📝', route: '/notes' },
    { label: 'Revision', icon: '🔄', route: '/revision' },
    { label: 'Daily Planner', icon: '📅', route: '/planner' },
    { label: 'Current Affairs', icon: '📰', route: '/current-affairs' },
    { label: 'Answer Eval', icon: '✍️', route: '/answer-evaluation' },
    { label: 'Analytics', icon: '📊', route: '/analytics' },
    { label: 'Admin', icon: '⚙️', route: '/admin', adminOnly: true },
  ];

  get userInitial(): string {
    return this.authService.user()?.full_name?.charAt(0)?.toUpperCase() || 'U';
  }
}
