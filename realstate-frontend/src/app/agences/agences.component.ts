import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
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
  totalAgences = 0;
  totalPages = 0;
  limitOptions = [10, 20, 50];

  constructor(
    private agenceService: AgenceService,
    public dialog: MatDialog,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadAgences();
  }

  loadAgences() {
    this.agenceService.getAgences(this.page, this.limit).subscribe({
      next: (data) => {
        if (data && data.agencies) {
          this.agences = data.agencies.map(agence => ({
            ...agence,
            emails: agence.email ? agence.email.split(',') : []
          }));
          this.totalAgences = data.total_agencies;
          this.totalPages = data.total_pages;
        } else {
          console.error('Aucune donnée ou agences trouvées:', data);
          this.agences = [];
          this.totalAgences = 0;
          this.totalPages = 0;
        }
      },
      error: (err) => {
        console.error('Erreur lors du chargement des agences:', err);
        this.agences = [];
        this.totalAgences = 0;
        this.totalPages = 0;
      }
    });
  }

  addEmail(agence: any) {
    agence.emails.push('');
  }

  saveAgence(agence: any) {
    const update = { email: agence.emails.join(','), number: agence.number };
    this.agenceService.updateAgence(agence.id, update).subscribe(() => {
      alert('Agence mise à jour');
      this.loadAgences();
    });
  }

  openDetails(agence: any) {
    this.dialog.open(AgencyUpdateDialogComponent, { data: agence });
  }

  changePage(newPage: number) {
    if (newPage >= 1 && newPage <= this.totalPages) {
      this.page = newPage;
      this.loadAgences();
    }
  }

  changeLimit(newLimit: number) {
    this.limit = newLimit;
    this.page = 1;
    this.loadAgences();
  }

  logout() {
    localStorage.removeItem('token');
    this.router.navigate(['/xtracto/signin']);
  }

  trackByIndex(index: number, item: any): number {
    return index; // Retourne l'index comme identifiant unique
  }
}