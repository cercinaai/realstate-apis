import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-agency-update-dialog',
  template: `
    <h2 mat-dialog-title>{{ data.name }}</h2>
    <mat-dialog-content>
      <p>ID: {{ data.id }}</p>
      <p>Email: {{ data.email }}</p>
      <p>Numéro: {{ data.number }}</p>
      <p>Lien: {{ data.lien }}</p>
    </mat-dialog-content>
    <mat-dialog-actions>
      <button mat-button mat-dialog-close>Fermer</button>
    </mat-dialog-actions>
  `
})
export class AgencyUpdateDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: any) {}
}