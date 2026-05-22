import { Routes } from '@angular/router';

export const authRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./auth-layout/auth-layout.component').then(m => m.AuthLayoutComponent),
    children: [
      { path: '', redirectTo: 'login', pathMatch: 'full' },
      {
        path: 'login',
        loadComponent: () => import('./login/login.component').then(m => m.LoginComponent),
        title: 'Login — AI UPSC Study OS',
      },
      {
        path: 'register',
        loadComponent: () => import('./register/register.component').then(m => m.RegisterComponent),
        title: 'Register — AI UPSC Study OS',
      },
    ],
  },
  {
    path: 'google/callback',
    loadComponent: () => import('./google-callback/google-callback.component').then(m => m.GoogleCallbackComponent),
    title: 'Google Sign In — AI UPSC Study OS',
  },
];
