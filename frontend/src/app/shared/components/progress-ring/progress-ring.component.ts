import { Component, Input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-progress-ring',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="relative inline-flex items-center justify-center">
      <svg
        [attr.width]="size"
        [attr.height]="size"
        class="progress-ring"
      >
        <!-- Background circle -->
        <circle
          [attr.cx]="size / 2"
          [attr.cy]="size / 2"
          [attr.r]="radius"
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          [attr.stroke-width]="strokeWidth"
        />
        <!-- Progress circle -->
        <circle
          class="progress-ring-circle"
          [attr.cx]="size / 2"
          [attr.cy]="size / 2"
          [attr.r]="radius"
          fill="none"
          [attr.stroke]="color"
          [attr.stroke-width]="strokeWidth"
          [attr.stroke-dasharray]="circumference"
          [attr.stroke-dashoffset]="dashOffset()"
          stroke-linecap="round"
        />
      </svg>
      <!-- Center text -->
      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span class="font-bold text-white" [style.font-size.px]="size * 0.18">
          {{ percentage | number:'1.0-0' }}%
        </span>
        @if (label) {
          <span class="text-gray-500 text-xs mt-0.5">{{ label }}</span>
        }
      </div>
    </div>
  `,
})
export class ProgressRingComponent {
  @Input() percentage = 0;
  @Input() size = 120;
  @Input() strokeWidth = 8;
  @Input() color = '#6366f1';
  @Input() label = '';

  get radius(): number {
    return (this.size - this.strokeWidth * 2) / 2;
  }

  get circumference(): number {
    return 2 * Math.PI * this.radius;
  }

  dashOffset = computed(() => {
    const offset = this.circumference - (this.percentage / 100) * this.circumference;
    return Math.max(0, offset);
  });
}
