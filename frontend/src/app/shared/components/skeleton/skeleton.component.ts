import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-skeleton',
  standalone: true,
  template: `
    <div
      class="skeleton rounded-xl"
      [style.height]="height"
      [style.width]="width"
    ></div>
  `,
})
export class SkeletonComponent {
  @Input() height = '100px';
  @Input() width = '100%';
}
