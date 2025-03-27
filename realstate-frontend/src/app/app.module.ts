import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import { AgencesComponent } from './agences/agences.component';
import { AgencyUpdateDialogComponent } from './agences/agency-update-dialog/agency-update-dialog.component';

@NgModule({
  declarations: [AppComponent, LoginComponent, AgencesComponent, AgencyUpdateDialogComponent],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    MatTableModule,
    MatButtonModule,
    MatDialogModule,
    AppRoutingModule
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}