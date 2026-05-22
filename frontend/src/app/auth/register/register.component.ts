import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, CommonModule],
  template: `
    <div class="glass-card p-8 animate-slide-up">
      <h2 class="text-xl font-bold text-white mb-2">Start your journey</h2>
      <p class="text-gray-400 text-sm mb-6">Create your AI-powered study account</p>

      <form [formGroup]="form" (ngSubmit)="onSubmit()" class="space-y-4">
        <!-- Full Name -->
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Full Name</label>
          <input type="text" formControlName="full_name" placeholder="Arjun Sharma"
                 class="input-field" />
        </div>

        <!-- Email -->
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Email</label>
          <input type="email" formControlName="email" placeholder="you@example.com"
                 class="input-field" />
        </div>

        <!-- Username -->
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Username</label>
          <input type="text" formControlName="username" placeholder="arjun_upsc"
                 class="input-field" />
        </div>

        <!-- Exam Target -->
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Exam Target</label>
          <select formControlName="exam_target" class="input-field">
            <option value="upsc">UPSC Civil Services</option>
            <option value="mpsc">MPSC</option>
            <option value="both">Both UPSC & MPSC</option>
          </select>
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm text-gray-400 mb-1.5">Password</label>
          <div class="relative">
            <input
              [type]="showPassword() ? 'text' : 'password'"
              formControlName="password"
              placeholder="Min 8 chars, 1 uppercase, 1 number"
              class="input-field pr-12"
            />
            <button type="button" (click)="toggleShowPassword()"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white">
              {{ showPassword() ? '🙈' : '👁️' }}
            </button>
          </div>
          @if (form.get('password')?.invalid && form.get('password')?.touched) {
            <p class="text-red-400 text-xs mt-1">
              Password must be 8+ chars with uppercase and number
            </p>
          }
        </div>

        <!-- Submit -->
        <button type="submit" class="btn-primary w-full"
                [disabled]="form.invalid || authService.isLoading()">
          @if (authService.isLoading()) {
            <span class="flex items-center justify-center gap-2">
              <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Creating account...
            </span>
          } @else {
            Create Account
          }
        </button>
      </form>

      <p class="text-center text-gray-500 text-sm mt-6">
        Already have an account?
        <a routerLink="/auth/login" class="text-primary-400 hover:text-primary-300 ml-1">Sign in</a>
      </p>
    </div>
  `,
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private notifications = inject(NotificationService);
  authService = inject(AuthService);

  showPassword = signal(false);

  form: FormGroup = this.fb.group({
    full_name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    username: ['', [Validators.required, Validators.minLength(3), Validators.pattern(/^[a-zA-Z0-9_]+$/)]],
    exam_target: ['upsc', Validators.required],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  toggleShowPassword(): void {
    this.showPassword.update(v => !v);
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    this.authService.register(this.form.value).subscribe({
      next: () => {
        this.notifications.success('Account created! Welcome to AI UPSC Study OS 🎉');
        this.router.navigate(['/dashboard']);
      },
      error: () => {},
    });
  }
}
