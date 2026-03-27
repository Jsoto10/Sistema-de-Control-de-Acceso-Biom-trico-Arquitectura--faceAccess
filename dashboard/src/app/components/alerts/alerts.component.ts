import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-alerts',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alerts.component.html',
  styleUrl: './alerts.component.css',
})
export class AlertsComponent implements OnInit {
  public alerts: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadAlerts();
  }

  loadAlerts() {
    this.apiService.getAlerts().subscribe((data: any) => {
      this.alerts = data;
    });
  }

  getFullImagePath(path: string) {
    if (!path) return '';
    const filename = path.replace(/\\/g, '/').split('/').pop();
    return `http://127.0.0.1:8000/static/alertas/${filename}`;
  }

  searchOnInternet(imageUrl: string) {
    if (!imageUrl || !imageUrl.startsWith('http')) {
      alert('La imagen debe ser pública');
      return;
    }

    const searchUrl = `https://lens.google.com/uploadbyurl?url=${encodeURIComponent(imageUrl)}`;
    window.open(searchUrl, '_blank');
  }
}
