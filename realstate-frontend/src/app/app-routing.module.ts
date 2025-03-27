import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { AgencesComponent } from './agences/agences.component';

const routes: Routes = [
  { path: 'xtracto/signin', component: LoginComponent },
  { path: 'xtracto/agences', component: AgencesComponent },
  { path: '', redirectTo: '/xtracto/signin', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}