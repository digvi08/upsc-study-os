import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { NotificationService } from '../services/notification.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notifications = inject(NotificationService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let message = 'An unexpected error occurred';

      if (error.error?.detail) {
        message = error.error.detail;
      } else if (error.status === 0) {
        message = 'Cannot connect to server. Please check your connection.';
      } else if (error.status === 403) {
        message = 'You do not have permission to perform this action.';
      } else if (error.status === 404) {
        message = 'Resource not found.';
      } else if (error.status === 429) {
        message = 'Too many requests. Please slow down.';
      } else if (error.status >= 500) {
        message = 'Server error. Please try again later.';
      }

      // Don't show notification for 401 (handled by auth interceptor)
      if (error.status !== 401) {
        notifications.error(message);
      }

      return throwError(() => error);
    }),
  );
};
