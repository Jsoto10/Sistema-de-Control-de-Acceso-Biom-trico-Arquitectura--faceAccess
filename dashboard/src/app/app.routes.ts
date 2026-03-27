import { Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { UsersComponent } from './components/users/users.component';
import { LogsComponent } from './components/logs/logs.component';
import { AlertsComponent } from './components/alerts/alerts.component';
import { UserRegistration } from './components/user-registration/user-registration';
import { LoginComponent } from './components/login/login';
import { AuthGuard } from './auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [AuthGuard] 
  },
  { 
    path: 'users', 
    component: UsersComponent,
    canActivate: [AuthGuard] 
  },
  { 
    path: 'register', 
    component: UserRegistration,
    canActivate: [AuthGuard] 
  },
  { 
    path: 'logs', 
    component: LogsComponent,
    canActivate: [AuthGuard] 
  },
  { 
    path: 'alerts', 
    component: AlertsComponent,
    canActivate: [AuthGuard] 
  }
];
