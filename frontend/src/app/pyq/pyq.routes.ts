import { Routes } from '@angular/router';

export const pyqRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pyq-analyzer/pyq-analyzer.component').then(m => m.PYQAnalyzerComponent),
  },
];
