import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-alerts',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alerts.html',
  styleUrl: './alerts.css',
})
export class Alerts implements OnInit {
  alerts: any[] = [];
  selectedAlert: any = null;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadAlerts();
  }

  loadAlerts() {
    this.api.getAlerts().subscribe({
      next: (data) => {
        this.alerts = data;
      },
      error: (err) => console.error('Error cargando alertas:', err)
    });
  }

  openInvestigation(alert: any) {
    this.selectedAlert = alert;
  }

  playEvidence(alert: any) {
    this.selectedAlert = alert;
    // El video se reproducirá automáticamente en el modal
  }

  closeModal() {
    this.selectedAlert = null;
  }

  markAsReviewed(alert: any) {
    // Implementar endpoint en backend si es necesario
    alert.estado = 'revisado';
    this.closeModal();
  }
}
