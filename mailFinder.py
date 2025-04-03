import requests
import json
import logging
from time import sleep
from database import get_db  # Importer depuis database.py
from bson import ObjectId

# Configuration du logging
logging.basicConfig(
    filename='email_finder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Votre clé API Anymailfinder
API_KEY = "yTzIE9FoViEPQfs0mqWCbFnF"
API_URL = "https://api.anymailfinder.com/v5.0/search/company.json"

# Headers pour l'authentification
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def fetch_emails(company_name, domain=None):
    """Recherche les emails pour une entreprise via l'API Anymailfinder."""
    payload = {"company_name": company_name}
    if domain:
        payload["domain"] = domain

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=180)
        status_code = response.status_code
        data = response.json() if response.content else {}

        if status_code == 200:
            emails = data.get("results", {}).get("emails", [])
            total_count = data.get("results", {}).get("total_count", 0)
            valid = data.get("results", {}).get("validation", "") == "valid"
            
            if emails:
                log_msg = f"Entreprise: {company_name} (Domaine: {domain}) - {len(emails)} emails trouvés sur {total_count} (Valides: {valid}) - {emails}"
                logging.info(log_msg)
                return emails
            else:
                log_msg = f"Entreprise: {company_name} (Domaine: {domain}) - Aucun email trouvé ou tous risqués"
                logging.info(log_msg)
                return None

        elif status_code == 400 or status_code == 401:
            logging.error(f"Requête invalide pour {company_name} (Domaine: {domain}): {data.get('error_explained', 'Erreur non précisée')}")
            return None
        elif status_code == 402:
            logging.error(f"Crédits insuffisants pour {company_name} (Domaine: {domain}): {data.get('error_explained', 'Erreur non précisée')}")
            return None
        elif status_code == 404 or status_code == 451:
            logging.info(f"Emails non trouvés pour {company_name} (Domaine: {domain})")
            return None
        else:
            logging.error(f"Erreur inconnue pour {company_name} (Domaine: {domain}): {status_code} - {data.get('error_explained', 'Erreur non précisée')}")
            return None

    except requests.RequestException as error:
        logging.error(f"Échec de la requête pour {company_name} (Domaine: {domain}): {str(error)}")
        return None

async def update_agencies_with_emails(limit=1000):
    """Récupère 1000 agences sans email, trouve leurs emails et met à jour la base."""
    logging.info("Début de la recherche et mise à jour des emails pour 1000 agences")

    # Récupérer la connexion à la base de données
    db = get_db()
    collection = db["agencesFinale"]

    # Récupérer 1000 agences sans email
    query = {
        "$or": [
            {"email": {"$exists": False}},
            {"email": None},
            {"email": ""}
        ]
    }
    agencies = await collection.find(query).to_list(length=limit)
    total_agencies = len(agencies)
    agencies_with_emails = 0

    for agency in agencies:
        agency_id = agency.get("storeId") or str(agency.get("_id"))
        company_name = agency.get("name", "")
        domain = agency.get("siteWeb", None)  # Utiliser le champ siteWeb comme domaine si disponible
        logging.info(f"Traitement de l'agence: {company_name} (ID: {agency_id}, Domaine: {domain})")

        emails = fetch_emails(company_name, domain)
        
        if emails:
            # Mettre à jour l'agence dans la base avec les emails trouvés
            await collection.update_one(
                {"_id": ObjectId(agency["_id"]) if "_id" in agency else {"storeId": agency_id}},
                {"$set": {"email": emails}}
            )
            agencies_with_emails += 1
            print(f"{company_name} (ID: {agency_id}): {len(emails)} emails trouvés - {emails}")
        else:
            print(f"{company_name} (ID: {agency_id}): Aucun email trouvé ou erreur")

        sleep(1)  # Pause pour éviter de surcharger l'API

    logging.info(f"Fin de la recherche - {agencies_with_emails} agences sur {total_agencies} ont au moins un email")
    return {
        "total_processed": total_agencies,
        "agencies_with_emails": agencies_with_emails,
        "success_rate": (agencies_with_emails / total_agencies) * 100 if total_agencies > 0 else 0
    }

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(update_agencies_with_emails())
    print(f"Résultat: {result}")