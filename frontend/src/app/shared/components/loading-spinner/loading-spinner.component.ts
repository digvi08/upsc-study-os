import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  template: `
    <div class="flex items-center justify-center" [class]="containerClass">
      <svg
        class="animate-spin text-indigo-400"
        [class]="sizeClass"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12" cy="12" r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
      @if (label) {
        <span class="ml-3 text-gray-400 text-sm">{{ label }}</span>
      }
    </div>
  `,
})
export class LoadingSpinnerComponent {
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() label = '';
  @Input() fullPage = false;

  get sizeClass(): string {
    return { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' }[this.size];
  }

  get containerClass(): string {
    return this.fullPage ? 'fixed inset-0 bg-black/40 z-50' : '';
  }
}
