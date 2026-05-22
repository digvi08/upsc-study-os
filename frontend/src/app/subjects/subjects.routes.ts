import { Routes } from '@angular/router';

export const subjectsRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./subjects-list/subjects-list.component').then(m => m.SubjectsListComponent),
  },
  {
    path: ':id',
    loadComponent: () => import('./subject-detail/subject-detail.component').then(m => m.SubjectDetailComponent),
  },
];
