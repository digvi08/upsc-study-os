import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  constructor(private snackBar: MatSnackBar) {}

  show(message: string, type: NotificationType = 'info', duration = 4000): void {
    const panelClass = {
      success: 'snack-success',
      error: 'snack-error',
      warning: 'snack-warning',
      info: 'snack-info',
    }[type];

    this.snackBar.open(message, '✕', {
      duration,
      panelClass: [panelClass],
      horizontalPosition: 'right',
      verticalPosition: 'top',
    });
  }

  success(message: string): void { this.show(message, 'success'); }
  error(message: string): void { this.show(message, 'error', 6000); }
  warning(message: string): void { this.show(message, 'warning'); }
  info(message: string): void { this.show(message, 'info'); }
}
