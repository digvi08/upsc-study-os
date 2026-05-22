import { Routes } from '@angular/router';

export const notesRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./notes-list/notes-list.component').then(m => m.NotesListComponent),
  },
  {
    path: ':id',
    loadComponent: () => import('./note-detail/note-detail.component').then(m => m.NoteDetailComponent),
  },
];
