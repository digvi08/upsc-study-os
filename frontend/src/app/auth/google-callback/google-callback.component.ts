import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-google-callback',
  standalone: true,
  template: `
    <div class="min-h-screen flex items-center justify-center" style="background: #0f0f23;">
      <div class="glass-card p-8 text-center">
        <div class="text-4xl mb-4 animate-pulse">🔐</div>
        <p class="text-white font-medium">Completing Google sign-in...</p>
        <p class="text-gray-400 text-sm mt-2">Please wait</p>
      </div>
    </div>
  `,
})
export class GoogleCallbackComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authService = inject(AuthService);
  private notifications = inject(NotificationService);

  ngOnInit(): void {
    const code = this.route.snapshot.queryParamMap.get('code');
    if (!code) {
      this.notifications.error('Google sign-in failed');
      this.router.navigate(['/auth/login']);
      return;
    }
    const redirectUri = window.location.origin + '/auth/google/callback';
    this.authService.googleLogin(code, redirectUri).subscribe({
      next: () => {
        this.notifications.success('Signed in with Google');
        this.router.navigate(['/dashboard']);
      },
      error: () => this.router.navigate(['/auth/login']),
    });
  }
}
