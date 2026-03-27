import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './users.component.html',
  styleUrl: './users.component.css'
})
export class UsersComponent implements OnInit {
  public users: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.apiService.getUsers().subscribe((data: any) => {
      this.users = data;
    });
  }

  deleteUser(userId: number) {
    if (confirm('¿Estás seguro de eliminar este usuario? Esta acción no se puede deshacer.')) {
      this.apiService.deleteUser(userId).subscribe(() => {
        this.loadUsers();
      });
    }
  }

  toggleStatus(user: any) {
    const nuevoEstado = !user.activo;
    const msg = nuevoEstado ? '¿Habilitar ingreso?' : '¿Deshabilitar ingreso?';
    if (confirm(msg)) {
      this.apiService.toggleUserStatus(user.id, nuevoEstado).subscribe(() => {
        this.loadUsers();
      });
    }
  }
}
