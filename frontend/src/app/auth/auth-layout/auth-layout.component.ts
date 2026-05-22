import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-auth-layout',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <div class="min-h-screen flex items-center justify-center relative overflow-hidden"
         style="background: #0f0f23;">

      <!-- Animated background orbs -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute -top-40 -right-40 w-96 h-96 rounded-full opacity-20 blur-3xl"
             style="background: radial-gradient(circle, #6366f1, transparent);
                    animation: pulse 4s ease-in-out infinite;"></div>
        <div class="absolute -bottom-40 -left-40 w-96 h-96 rounded-full opacity-20 blur-3xl"
             style="background: radial-gradient(circle, #8b5cf6, transparent);
                    animation: pulse 4s ease-in-out infinite 2s;"></div>
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full opacity-10 blur-3xl"
             style="background: radial-gradient(circle, #ec4899, transparent);
                    animation: pulse 6s ease-in-out infinite 1s;"></div>
      </div>

      <!-- Grid pattern overlay -->
      <div class="absolute inset-0 opacity-5"
           style="background-image: linear-gradient(rgba(99,102,241,0.3) 1px, transparent 1px),
                                    linear-gradient(90deg, rgba(99,102,241,0.3) 1px, transparent 1px);
                  background-size: 50px 50px;"></div>

      <div class="relative z-10 w-full max-w-md px-4">
        <!-- Logo -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4"
               style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">
            <span class="text-white font-bold text-2xl">AI</span>
          </div>
          <h1 class="text-2xl font-bold text-white">UPSC Study OS</h1>
          <p class="text-gray-400 text-sm mt-1">Your AI-powered preparation companion</p>
        </div>

        <router-outlet />
      </div>
    </div>
  `,
})
export class AuthLayoutComponent {}
