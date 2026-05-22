import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-stat-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="glass-card-hover p-5 cursor-default">
      <div class="flex items-start justify-between mb-3">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
             [style.background]="color + '20'"
             [style.border]="'1px solid ' + color + '30'">
          {{ icon }}
        </div>
        @if (trend !== undefined) {
          <span class="text-xs font-medium px-2 py-0.5 rounded-full"
                [class]="trend >= 0 ? 'text-green-400 bg-green-500/10' : 'text-red-400 bg-red-500/10'">
            {{ trend >= 0 ? '↑' : '↓' }} {{ trend | number:'1.0-0' }}%
          </span>
        }
      </div>
      <p class="text-2xl font-bold text-white">{{ value }}</p>
      <p class="text-gray-400 text-sm mt-0.5">{{ label }}</p>
      @if (subtitle) {
        <p class="text-gray-600 text-xs mt-0.5">{{ subtitle }}</p>
      }
    </div>
  `,
})
export class StatCardComponent {
  @Input() icon = '📊';
  @Input() label = '';
  @Input() value: number | string = 0;
  @Input() subtitle = '';
  @Input() color = '#6366f1';
  @Input() trend?: number;
}
