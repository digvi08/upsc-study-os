import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <h1 class="text-2xl font-bold text-white">Profile Settings</h1>

      <div class="glass-card p-6">
        <!-- Avatar -->
        <div class="flex items-center gap-4 mb-6">
          <div class="w-20 h-20 rounded-2xl flex items-center justify-center text-3xl font-bold text-white"
               style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">
            {{ authService.user()?.full_name?.charAt(0) }}
          </div>
          <div>
            <h2 class="text-xl font-bold text-white">{{ authService.user()?.full_name }}</h2>
            <p class="text-gray-400">{{ authService.user()?.email }}</p>
            <span class="badge badge-primary mt-1">{{ authService.user()?.role }}</span>
          </div>
        </div>

        <!-- Form -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1.5">Full Name</label>
            <input type="text" [(ngModel)]="profile.full_name" class="input-field" />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1.5">Bio</label>
            <textarea [(ngModel)]="profile.bio" rows="3" class="input-field resize-none"
                      placeholder="Tell us about your preparation journey..."></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Exam Target</label>
              <select [(ngModel)]="profile.exam_target" class="input-field">
                <option value="upsc">UPSC</option>
                <option value="mpsc">MPSC</option>
                <option value="both">Both</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1.5">Daily Study Hours</label>
              <input type="number" [(ngModel)]="profile.daily_study_hours" min="1" max="16" class="input-field" />
            </div>
          </div>
          <button (click)="saveProfile()" class="btn-primary">Save Changes</button>
        </div>
      </div>

      <!-- Stats -->
      <div class="glass-card p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Your Stats</h3>
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <p class="text-2xl font-bold text-yellow-400">🔥 {{ authService.user()?.current_streak }}</p>
            <p class="text-gray-400 text-sm">Day Streak</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-primary-400">{{ authService.user()?.longest_streak }}</p>
            <p class="text-gray-400 text-sm">Best Streak</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-green-400">{{ authService.user()?.total_study_hours }}h</p>
            <p class="text-gray-400 text-sm">Total Hours</p>
          </div>
        </div>
      </div>
    </div>
  `,
})
export class ProfileComponent {
  authService = inject(AuthService);
  private http = inject(HttpClient);
  private notifications = inject(NotificationService);

  profile = {
    full_name: this.authService.user()?.full_name || '',
    bio: this.authService.user()?.bio || '',
    exam_target: this.authService.user()?.exam_target || 'upsc',
    daily_study_hours: this.authService.user()?.daily_study_hours || 8,
  };

  saveProfile(): void {
    this.http.put<any>(`${environment.apiUrl}/users/profile`, this.profile).subscribe({
      next: (user) => {
        this.authService.updateUser(user);
        this.notifications.success('Profile updated');
      },
    });
  }
}
