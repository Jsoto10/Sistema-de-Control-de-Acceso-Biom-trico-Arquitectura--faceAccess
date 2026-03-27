import { Component, signal } from '@angular/core';
import { Router, NavigationEnd, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from './services/auth.service';
import { filter } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('FaceAccess Pro');
  public isLoginRoute: boolean = false;

  constructor(public auth: AuthService, private router: Router) {
    // Escuchar cambios de ruta para ocultar sidebar en /login
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.isLoginRoute = event.urlAfterRedirects === '/login' || event.urlAfterRedirects === '/';
    });
  }

  logout() {
    this.auth.logout();
  }
}
