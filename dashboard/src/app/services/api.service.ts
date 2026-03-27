import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  getLogs(): Observable<any> {
    return this.http.get(`${this.baseUrl}/logs`);
  }

  getAlerts(): Observable<any> {
    return this.http.get(`${this.baseUrl}/alerts`);
  }

  getUsers(): Observable<any> {
    return this.http.get(`${this.baseUrl}/users`);
  }

  createUser(userData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/users`, userData);
  }

  registerUser(formData: FormData): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/register`, formData);
  }

  deleteUser(userId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/users/${userId}`);
  }

  toggleUserStatus(userId: number, activo: boolean): Observable<any> {
    return this.http.patch(`${this.baseUrl}/users/${userId}/status?activo=${activo}`, {});
  }
}
