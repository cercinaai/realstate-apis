import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { AgenceService } from '../agence.service';
import { AgencyUpdateDialogComponent } from './agency-update-dialog/agency-update-dialog.component';

@Component({
  selector: 'app-agences',
  templateUrl: './agences.component.html',
  styleUrls: ['./agences.component.css']
})
export class AgencesComponent implements OnInit {
  displayedColumns: string[] = ['name', 'email', 'number', 'lien', 'actions'];
  agences: any[] = [];
  page = 1;
  limit = 10;

  constructor(private agenceService: AgenceService, public dialog: MatDialog) {}

  ngOnInit() {
    this.loadAgences();
  }

  loadAgences() {
    this.agenceService.getAgences(this.page, this.limit).subscribe((data) => {
      this.agences = data.agencies.map(agence => ({
        ...agence,
        emails: agence.email ? agence.email.split(',') : []
      }));
    });
  }

  addEmail(agence: any) {
    agence.emails.push('');
  }

  saveAgence(agence: any) {
    const update = { email: agence.emails.join(','), number: agence.number };
    this.agenceService.updateAgence(agence.id, update).subscribe(() => alert('Agence mise à jour'));
  }

  openDetails(agence: any) {
    this.dialog.open(AgencyUpdateDialogComponent, { data: agence });
  }
}