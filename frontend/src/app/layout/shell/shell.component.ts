import { Component, signal, HostListener } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { TopbarComponent } from '../topbar/topbar.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent, TopbarComponent, CommonModule],
  template: `
    <div class="flex h-screen overflow-hidden bg-[#0f0f23]">
      <!-- Sidebar -->
      <app-sidebar
        [collapsed]="sidebarCollapsed()"
        (toggleCollapse)="toggleSidebar()"
        class="flex-shrink-0 z-30"
      />

      <!-- Mobile overlay -->
      @if (!sidebarCollapsed() && isMobile()) {
        <div
          class="fixed inset-0 bg-black/60 z-20 lg:hidden"
          (click)="toggleSidebar()"
        ></div>
      }

      <!-- Main content -->
      <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
        <app-topbar
          [sidebarCollapsed]="sidebarCollapsed()"
          (toggleSidebar)="toggleSidebar()"
        />
        <main class="flex-1 overflow-y-auto p-6 animate-fade-in">
          <router-outlet />
        </main>
      </div>
    </div>
  `,
})
export class ShellComponent {
  sidebarCollapsed = signal(false);
  isMobile = signal(window.innerWidth < 1024);

  @HostListener('window:resize')
  onResize(): void {
    this.isMobile.set(window.innerWidth < 1024);
    if (window.innerWidth < 1024) {
      this.sidebarCollapsed.set(true);
    }
  }

  toggleSidebar(): void {
    this.sidebarCollapsed.update(v => !v);
  }
}
