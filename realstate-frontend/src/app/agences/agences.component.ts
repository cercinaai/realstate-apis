import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { AgenceService } from '../agence.service';

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
  isLoading = false;

  constructor(
    private agenceService: AgenceService,
    public dialog: MatDialog,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadAgences();
  }

  loadAgences() {
    this.isLoading = true;
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
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des agences:', err);
        this.agences = [];
        this.totalAgences = 0;
        this.totalPages = 0;
        this.isLoading = false;
      }
    });
  }

  addEmail(agence: any) {
    agence.emails.push('');
  }

  saveAgence(agence: any) {
    this.isLoading = true;
    const update = { email: agence.emails.join(','), number: agence.number };
    this.agenceService.updateAgence(agence.id, update).subscribe({
      next: () => {
        alert('Agence mise à jour');
        this.loadAgences();
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  get paginationPages(): number[] {
    const pages: number[] = [];
    const blockSize = 10;
    const currentBlock = Math.floor((this.page - 1) / blockSize);
    const startPage = currentBlock * blockSize + 1; // Correction appliquée
    const endPage = Math.min(startPage + blockSize - 1, this.totalPages);

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return pages;
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
    return index;
  }
}