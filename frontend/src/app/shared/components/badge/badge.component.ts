import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type BadgeVariant = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';

@Component({
  selector: 'app-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span
      class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border"
      [ngClass]="variantClasses[variant]"
    >
      @if (icon) { <span>{{ icon }}</span> }
      <ng-content />
    </span>
  `,
})
export class BadgeComponent {
  @Input() variant: BadgeVariant = 'primary';
  @Input() icon = '';

  variantClasses: Record<BadgeVariant, string> = {
    primary: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
    success: 'bg-green-500/20 text-green-300 border-green-500/30',
    warning: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    danger:  'bg-red-500/20 text-red-300 border-red-500/30',
    info:    'bg-blue-500/20 text-blue-300 border-blue-500/30',
    neutral: 'bg-white/10 text-gray-300 border-white/10',
  };
}
