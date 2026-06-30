import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { User, AuthResponse, LoginRequest, RegisterRequest, AuthTokens } from '../shared/models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API = environment.apiUrl;
  private readonly TOKEN_KEY = 'upsc_access_token';
  private readonly REFRESH_KEY = 'upsc_refresh_token';
  private readonly USER_KEY = 'upsc_user';

  // Reactive state using Angular signals
  private _user = signal<User | null>(this.loadUser());
  private _isLoading = signal(false);

  readonly user = this._user.asReadonly();
  readonly isLoading = this._isLoading.asReadonly();
  readonly isAuthenticated = computed(() => !!this._user());
  readonly isAdmin = computed(() => this._user()?.role === 'admin');

  constructor(private http: HttpClient, private router: Router) {}

  register(data: RegisterRequest): Observable<AuthResponse> {
    this._isLoading.set(true);
    return this.http.post<AuthResponse>(`${this.API}/auth/register`, data).pipe(
      tap(res => this.handleAuthSuccess(res)),
      catchError(err => { this._isLoading.set(false); return throwError(() => err); }),
    );
  }

  login(data: LoginRequest): Observable<AuthResponse> {
    this._isLoading.set(true);
    return this.http.post<AuthResponse>(`${this.API}/auth/login`, data).pipe(
      tap(res => this.handleAuthSuccess(res)),
      catchError(err => { this._isLoading.set(false); return throwError(() => err); }),
    );
  }

  googleLogin(code: string, redirectUri?: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.API}/auth/google`, { code, redirect_uri: redirectUri })
      .pipe(tap(res => this.handleAuthSuccess(res)));
  }

  refreshToken(): Observable<AuthTokens> {
    const refresh_token = this.getRefreshToken();
    return this.http.post<AuthTokens>(`${this.API}/auth/refresh`, { refresh_token }).pipe(
      tap(tokens => {
        localStorage.setItem(this.TOKEN_KEY, tokens.access_token);
        localStorage.setItem(this.REFRESH_KEY, tokens.refresh_token);
      }),
    );
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.USER_KEY);
    this._user.set(null);
    this.router.navigate(['/auth/login']);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_KEY);
  }

  updateUser(user: User): void {
    this._user.set(user);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  private handleAuthSuccess(res: AuthResponse): void {
    localStorage.setItem(this.TOKEN_KEY, res.tokens.access_token);
    localStorage.setItem(this.REFRESH_KEY, res.tokens.refresh_token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(res.user));
    this._user.set(res.user);
    this._isLoading.set(false);
  }

  private loadUser(): User | null {
    try {
      const stored = localStorage.getItem(this.USER_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }
}
