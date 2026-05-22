import { Routes } from '@angular/router';
import { authGuard, guestGuard, adminGuard } from './guards/auth.guard';

export const routes: Routes = [
  // Auth routes (guest only)
  {
    path: 'auth',
    canActivate: [guestGuard],
    loadChildren: () => import('./auth/auth.routes').then(m => m.authRoutes),
  },

  // Main app routes (authenticated)
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./layout/shell/shell.component').then(m => m.ShellComponent),
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent),
        title: 'Dashboard — AI UPSC Study OS',
      },
      {
        path: 'subjects',
        loadChildren: () => import('./subjects/subjects.routes').then(m => m.subjectsRoutes),
        title: 'Subjects — AI UPSC Study OS',
      },
      {
        path: 'notes',
        loadChildren: () => import('./notes/notes.routes').then(m => m.notesRoutes),
        title: 'Notes — AI UPSC Study OS',
      },
      {
        path: 'pyq',
        loadChildren: () => import('./pyq/pyq.routes').then(m => m.pyqRoutes),
        title: 'PYQ Analyzer — AI UPSC Study OS',
      },
      {
        path: 'ai-mentor',
        loadComponent: () => import('./ai-mentor/ai-mentor.component').then(m => m.AIMentorComponent),
        title: 'AI Mentor — AI UPSC Study OS',
      },
      {
        path: 'revision',
        loadComponent: () => import('./revision/revision.component').then(m => m.RevisionComponent),
        title: 'Revision — AI UPSC Study OS',
      },
      {
        path: 'planner',
        loadComponent: () => import('./planner/planner.component').then(m => m.PlannerComponent),
        title: 'Daily Planner — AI UPSC Study OS',
      },
      {
        path: 'current-affairs',
        loadComponent: () => import('./current-affairs/current-affairs.component').then(m => m.CurrentAffairsComponent),
        title: 'Current Affairs — AI UPSC Study OS',
      },
      {
        path: 'answer-evaluation',
        loadComponent: () => import('./answer-evaluation/answer-evaluation.component').then(m => m.AnswerEvaluationComponent),
        title: 'Answer Evaluation — AI UPSC Study OS',
      },
      {
        path: 'analytics',
        loadComponent: () => import('./analytics/analytics.component').then(m => m.AnalyticsComponent),
        title: 'Analytics — AI UPSC Study OS',
      },
      {
        path: 'admin',
        canActivate: [adminGuard],
        loadComponent: () => import('./admin/admin.component').then(m => m.AdminComponent),
        title: 'Admin — AI UPSC Study OS',
      },
      {
        path: 'profile',
        loadComponent: () => import('./profile/profile.component').then(m => m.ProfileComponent),
        title: 'Profile — AI UPSC Study OS',
      },
    ],
  },

  // Fallback
  { path: '**', redirectTo: 'dashboard' },
];
