import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, CommonModule],
  template: `
    <div class="glass-card p-8 animate-slide-up">
      <h2 class="text-xl font-bold text-white mb-2">Welcome back</h2>
      <p class="text-gray-400 text-sm mb-6">Sign in to continue your preparation</p>

      <form [formGroup]="form" (ngSubmit)="onSubmit()" class="space-y-4">
        <!-- Email -->
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Email</label>
          <input
            type="email"
            formControlName="email"
            placeholder="you@example.com"
            class="input-field"
            [class.border-red-500]="form.get('email')?.invalid && form.get('email')?.touched"
          />
          @if (form.get('email')?.invalid && form.get('email')?.touched) {
            <p class="text-red-400 text-xs mt-1">Please enter a valid email</p>
          }
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Password</label>
          <div class="relative">
            <input
              [type]="showPassword() ? 'text' : 'password'"
              formControlName="password"
              placeholder="••••••••"
              class="input-field pr-12"
              [class.border-red-500]="form.get('password')?.invalid && form.get('password')?.touched"
            />
            <button
              type="button"
              (click)="toggleShowPassword()"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
            >
              {{ showPassword() ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <!-- Forgot password -->
        <div class="flex justify-end">
          <a href="#" class="text-primary-400 text-sm hover:text-primary-300">Forgot password?</a>
        </div>

        <!-- Submit -->
        <button
          type="submit"
          class="btn-primary w-full"
          [disabled]="form.invalid || authService.isLoading()"
        >
          @if (authService.isLoading()) {
            <span class="flex items-center justify-center gap-2">
              <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Signing in...
            </span>
          } @else {
            Sign In
          }
        </button>

        <!-- Divider -->
        <div class="flex items-center gap-3">
          <div class="flex-1 h-px bg-white/10"></div>
          <span class="text-gray-500 text-xs">or</span>
          <div class="flex-1 h-px bg-white/10"></div>
        </div>

        <!-- Google OAuth -->
        <button
          type="button"
          (click)="googleLogin()"
          class="btn-secondary w-full flex items-center justify-center gap-3"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </button>
      </form>

      <p class="text-center text-gray-500 text-sm mt-6">
        Don't have an account?
        <a routerLink="/auth/register" class="text-primary-400 hover:text-primary-300 ml-1">Sign up</a>
      </p>
    </div>
  `,
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private notifications = inject(NotificationService);
  authService = inject(AuthService);

  showPassword = signal(false);

  form: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  toggleShowPassword(): void {
    this.showPassword.update(v => !v);
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.authService.login(this.form.value).subscribe({
      next: () => {
        this.notifications.success('Welcome back!');
        this.router.navigate(['/dashboard']);
      },
      error: () => {},
    });
  }

  googleLogin(): void {
    if (!environment.googleClientId || environment.googleClientId.startsWith('YOUR_')) {
      this.notifications.error('Configure googleClientId in environment.ts');
      return;
    }
    const clientId = environment.googleClientId;
    const redirectUri = encodeURIComponent(window.location.origin + '/auth/google/callback');
    const scope = encodeURIComponent('openid email profile');
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}`;
  }
}
