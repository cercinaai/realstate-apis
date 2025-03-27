import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class AgenceService {
  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getAgences(page: number, limit: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/agencies/all?page=${page}&limit=${limit}`, { headers: this.getHeaders() });
  }

  updateAgence(id: string, update: any): Observable<any> {
    return this.http.put(`${environment.apiUrl}/agencies/${id}`, update, { headers: this.getHeaders() });
  }
}