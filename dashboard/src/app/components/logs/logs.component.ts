import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-logs',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './logs.component.html',
  styleUrl: './logs.component.css'
})
export class LogsComponent implements OnInit {
  public logs: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getLogs().subscribe((data: any) => {
      this.logs = data;
    });
  }
}
