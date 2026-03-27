import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebsocketService } from '../../services/websocket.service';
import { ApiService } from '../../services/api.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit, OnDestroy {
  public latestEvents: any[] = [];
  public stats = { accesses: 0, alerts: 0, users: 0 };
  private wsSubscription!: Subscription;

  constructor(private wsService: WebsocketService, private apiService: ApiService) {}

  ngOnInit() {
    this.loadInitialData();
    this.wsSubscription = this.wsService.getMessages().subscribe(msg => {
      this.handleWsMessage(msg);
    });
  }

  loadInitialData() {
    this.apiService.getLogs().subscribe((logs: any) => {
      this.stats.accesses = logs.length;
    });
    this.apiService.getAlerts().subscribe((alerts: any) => {
      this.stats.alerts = alerts.length;
    });
    this.apiService.getUsers().subscribe((users: any) => {
      this.stats.users = users.length;
    });
  }

  handleWsMessage(msg: any) {
    // Agregar evento a la lista con formato PRO
    const event = {
      ...msg,
      timestamp: new Date().toLocaleTimeString(),
      confidence_pct: msg.confidence ? Math.round(msg.confidence * 100) : null
    };

    this.latestEvents.unshift(event);
    if (this.latestEvents.length > 8) {
      this.latestEvents.pop();
    }

    // Actualizar contadores dinámicamente
    if (msg.type === 'access' && msg.status === 'success') {
      this.stats.accesses++;
    } else if (msg.type === 'alert' || msg.type === 'access_denied') {
      this.stats.alerts++;
    }
  }

  ngOnDestroy() {
    if (this.wsSubscription) {
      this.wsSubscription.unsubscribe();
    }
  }
}
