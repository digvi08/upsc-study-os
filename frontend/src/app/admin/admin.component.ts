import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="space-y-6 animate-fade-in">
      <div>
        <h1 class="text-2xl font-bold text-white">Admin Panel</h1>
        <p class="text-gray-400 mt-1">Platform management and oversight</p>
      </div>

      @if (stats()) {
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="glass-card p-5 text-center">
            <p class="text-3xl font-bold text-white">{{ stats()!.users.total }}</p>
            <p class="text-gray-400 text-sm mt-1">Total Users</p>
          </div>
          <div class="glass-card p-5 text-center">
            <p class="text-3xl font-bold text-green-400">{{ stats()!.users.active }}</p>
            <p class="text-gray-400 text-sm mt-1">Active Users</p>
          </div>
          <div class="glass-card p-5 text-center">
            <p class="text-3xl font-bold text-primary-400">{{ stats()!.content.total_pyqs }}</p>
            <p class="text-gray-400 text-sm mt-1">Total PYQs</p>
          </div>
          <div class="glass-card p-5 text-center">
            <p class="text-3xl font-bold text-yellow-400">{{ stats()!.users.recent_signups }}</p>
            <p class="text-gray-400 text-sm mt-1">New This Week</p>
          </div>
        </div>
      }

      <!-- Users table -->
      <div class="glass-card p-6">
        <h2 class="text-lg font-semibold text-white mb-4">Recent Users</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-gray-400 border-b border-white/10">
                <th class="text-left py-2 pr-4">Name</th>
                <th class="text-left py-2 pr-4">Email</th>
                <th class="text-left py-2 pr-4">Target</th>
                <th class="text-left py-2 pr-4">Role</th>
                <th class="text-left py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              @for (user of users(); track user.id) {
                <tr class="border-b border-white/5 hover:bg-white/2 transition-colors">
                  <td class="py-3 pr-4 text-white">{{ user.full_name }}</td>
                  <td class="py-3 pr-4 text-gray-400">{{ user.email }}</td>
                  <td class="py-3 pr-4">
                    <span class="badge badge-primary">{{ user.exam_target?.toUpperCase() }}</span>
                  </td>
                  <td class="py-3 pr-4 text-gray-400">{{ user.role }}</td>
                  <td class="py-3">
                    <span class="badge" [class]="user.is_active ? 'badge-success' : 'badge-danger'">
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
})
export class AdminComponent implements OnInit {
  private http = inject(HttpClient);
  stats = signal<any>(null);
  users = signal<any[]>([]);

  ngOnInit(): void {
    this.http.get(`${environment.apiUrl}/admin/stats`).subscribe(data => this.stats.set(data));
    this.http.get<any>(`${environment.apiUrl}/admin/users`).subscribe(data => this.users.set(data.users || []));
  }
}
