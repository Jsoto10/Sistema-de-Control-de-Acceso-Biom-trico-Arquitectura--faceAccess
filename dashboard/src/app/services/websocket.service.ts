import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  private socket!: WebSocket;
  private messagesSubject = new Subject<any>();

  constructor() {
    this.connect();
  }

  private connect() {
    this.socket = new WebSocket('ws://localhost:8000/ws/dashboard');

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.messagesSubject.next(data);
    };

    this.socket.onclose = (event) => {
      console.log('WebSocket cerrado. Reconectando en 3s...', event.reason);
      setTimeout(() => this.connect(), 3000);
    };

    this.socket.onerror = (error) => {
      console.error('Error en WebSocket:', error);
      this.socket.close();
    };
  }

  public getMessages(): Observable<any> {
    return this.messagesSubject.asObservable();
  }
}
