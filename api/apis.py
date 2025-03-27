# api/apis.py
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import Optional, List, Dict
from loguru import logger
from models.annonce import AnnonceOutput
from models.agenc import AgenceOutput
from database import get_db  # Importer get_db
import math
from pydantic import BaseModel

api_router = APIRouter()

# Modèle pour la mise à jour des agences
class AgencyUpdate(BaseModel):
    email: Optional[str] = None
    number: Optional[str] = None

# Helper pour formater une annonce
def format_annonce(annonce: Dict) -> Dict:
    return {
        "id": str(annonce["_id"]),
        "Titre": annonce.get("title", ""),
        "Description": annonce.get("description", ""),
        "Prix": annonce.get("price", 0),
        "Images": annonce.get("images", []),
        "L'essentiel": {
            "Type de bien": annonce.get("typeBien", ""),
            "Meublé": annonce.get("meuble", ""),
            "Surface": annonce.get("surface", ""),
            "Nombre de pièces": annonce.get("nombreDepiece", ""),
            "Nombre de chambres": annonce.get("nombreChambres", ""),
            "Nombre de salles de bain": annonce.get("nb_salles_de_bain", ""),
            "Étage": annonce.get("etage", ""),
            "Ascenseur": annonce.get("ascenseur", ""),
            "Charges incluses": annonce.get("charges_incluses", ""),
            "Dépôt de garantie": annonce.get("depot_garantie", ""),
            "Charges mensuelles": annonce.get("loyer_mensuel_charges", "")
        },
        "Bilan énergétique": {
            "DPE": annonce.get("classeEnergie", ""),
            "GES": annonce.get("ges", "")
        },
        "Agence": {
            "Nom": annonce.get("agenceName", "")
        },
        "location": {
            "region": annonce.get("region", ""),
            "city": annonce.get("city", ""),
            "codepostal": annonce.get("zipcode", ""),
            "departement": annonce.get("departement", ""),
            "latitude": annonce.get("latitude", 0.0),
            "longitude": annonce.get("longitude", 0.0)
        }
    }

# Helper pour formater une agence
def format_agence(agence: Dict) -> Dict:
    return {
        "id": str(agence["_id"]),
        "store_id": agence.get("storeId", ""),
        "name": agence.get("name", ""),
        "logo": agence.get("logo", None),
        "intervention_zone": agence.get("zone_intervention", None),
        "website": agence.get("siteWeb", None),
        "opening_hours": agence.get("horaires", None),
        "phone_number": agence.get("number", None),
        "description": agence.get("description", None),
        "email": agence.get("email", None)
    }

# API pour toutes les annonces avec pagination
@api_router.get("/realstate/all", response_model=Dict)
async def get_all_annonces(page: int = 1):
    try:
        per_page = 8
        skip = (page - 1) * per_page
        db = get_db()
        collection = db["realStateFinale"]
        total_annonces = await collection.count_documents({})
        total_pages = math.ceil(total_annonces / per_page)

        annonces = await collection.find({}) \
            .sort("processed_at", -1) \
            .skip(skip) \
            .limit(per_page) \
            .to_list(length=per_page)

        formatted_annonces = [format_annonce(annonce) for annonce in annonces]

        response = {
            "total_annonces": total_annonces,
            "total_pages": total_pages,
            "current_page": page,
            "annonces": formatted_annonces
        }
        logger.info(f"✅ Récupération de {len(formatted_annonces)} annonces pour la page {page}")
        return response
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la récupération des annonces : {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# API pour annonces filtrées avec pagination
@api_router.get("/realstate/filtered", response_model=Dict)
async def get_filtered_annonces(
    location_valeur: Optional[str] = None,
    location_type: Optional[str] = None,
    property_type: Optional[str] = None,
    furnished: Optional[bool] = None,
    min_surface: Optional[float] = None,
    max_price: Optional[float] = None,
    page: int = 1
):
    try:
        per_page = 8
        skip = (page - 1) * per_page
        query = {}
        db = get_db()
        collection = db["realStateFinale"]

        if location_type and location_type not in ["region", "departement", "city"]:
            raise HTTPException(status_code=400, detail="location_type doit être 'region', 'departement' ou 'city'")
        if location_valeur and location_type:
            regex = {"$regex": f"^{location_valeur}$", "$options": "i"}
            query[location_type] = regex
        if property_type:
            query["typeBien"] = property_type.capitalize()
        if furnished is not None:
            query["meuble"] = "Meublé" if furnished else {"$ne": "Meublé"}
        if min_surface:
            query["$expr"] = {
                "$gte": [
                    {"$toDouble": {"$arrayElemAt": [{"$split": ["$surface", " "]}, 0]}},
                    min_surface
                ]
            }
        if max_price:
            query["price"] = {"$lte": max_price}

        total_annonces = await collection.count_documents(query)
        total_pages = math.ceil(total_annonces / per_page)

        annonces = await collection.find(query) \
            .sort("processed_at", -1) \
            .skip(skip) \
            .limit(per_page) \
            .to_list(length=per_page)

        formatted_annonces = [format_annonce(annonce) for annonce in annonces]

        response = {
            "total_annonces": total_annonces,
            "total_pages": total_pages,
            "current_page": page,
            "annonces": formatted_annonces
        }
        logger.info(f"✅ Récupération de {len(formatted_annonces)} annonces filtrées pour la page {page}")
        return response
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la récupération des annonces filtrées : {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# API pour détail d'une annonce avec annonces similaires
@api_router.get("/realstate/detail/{annonce_id}", response_model=Dict)
async def get_annonce_detail(annonce_id: str):
    try:
        db = get_db()
        collection = db["realStateFinale"]
        annonce = await collection.find_one({"_id": ObjectId(annonce_id)})
        if not annonce:
            raise HTTPException(status_code=404, detail="Annonce non trouvée")

        formatted_annonce = format_annonce(annonce)

        # Recherche d'annonces similaires (4 km, ±200€)
        lat, lon = annonce.get("latitude", 0.0), annonce.get("longitude", 0.0)
        price = annonce.get("price", 0)
        earth_radius_km = 6371
        distance_km = 4 / earth_radius_km

        similar_query = {
            "latitude": {"$gte": lat - distance_km, "$lte": lat + distance_km},
            "longitude": {"$gte": lon - distance_km, "$lte": lon + distance_km},
            "price": {"$gte": price - 200, "$lte": price + 200},
            "_id": {"$ne": ObjectId(annonce_id)}
        }
        similar_annonces = await collection.find(similar_query).limit(5).to_list(length=5)
        formatted_similar = [format_annonce(a) for a in similar_annonces]

        response = {
            "annonce": formatted_annonce,
            "similar_annonces": formatted_similar
        }
        logger.info(f"✅ Détails récupérés pour l'annonce {annonce_id} avec {len(formatted_similar)} similaires")
        return response
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la récupération de l'annonce {annonce_id} : {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# API pour toutes les agences avec pagination
@api_router.get("/agence/all", response_model=Dict)
async def get_all_agences(page: int = 1):
    try:
        per_page = 8
        skip = (page - 1) * per_page
        db = get_db()
        collection = db["agencesFinale"]
        total_agences = await collection.count_documents({})
        total_pages = math.ceil(total_agences / per_page)

        agences = await collection.find({}) \
            .sort("_id", -1) \
            .skip(skip) \
            .limit(per_page) \
            .to_list(length=per_page)

        formatted_agences = [format_agence(agence) for agence in agences]

        response = {
            "total_agences": total_agences,
            "total_pages": total_pages,
            "current_page": page,
            "agences": formatted_agences
        }
        logger.info(f"✅ Récupération de {len(formatted_agences)} agences pour la page {page}")
        return response
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la récupération des agences : {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# API pour détail d'une agence avec ses annonces
@api_router.get("/agence/detail/{agence_id}", response_model=Dict)
async def get_agence_detail(agence_id: str):
    try:
        db = get_db()
        collection = db["agencesFinale"]
        agence = await collection.find_one({"_id": ObjectId(agence_id)})
        if not agence:
            raise HTTPException(status_code=404, detail="Agence non trouvée")

        formatted_agence = format_agence(agence)

        # Récupérer les annonces associées à cette agence
        annonce_collection = db["realStateFinale"]
        agence_annonces = await annonce_collection.find({"idAgence": str(agence["_id"])}).to_list(length=None)
        formatted_annonces = [format_annonce(a) for a in agence_annonces]

        response = {
            "agence": formatted_agence,
            "annonces": formatted_annonces
        }
        logger.info(f"✅ Détails récupérés pour l'agence {agence_id} avec {len(formatted_annonces)} annonces")
        return response
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la récupération de l'agence {agence_id} : {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# Nouvelle API pour récupérer toutes les agences avec pagination (version /api/v1/agencies/all)
@api_router.get("/api/v1/agencies/all", response_model=Dict)
async def get_agencies(page: int = 1, limit: int = 10):
    try:
        skip = (page - 1) * limit
        db = get_db()
        collection = db["agencesFinale"]
        total_agencies = await collection.count_documents({})
        total_pages = math.ceil(total_agencies / limit)

        agencies = await collection.find().skip(skip).limit(limit).to_list(length=limit)
        response_agencies = [
            {
                "id": str(agency["_id"]),
                "name": agency.get("name", ""),
                "email": agency.get("email", ""),
                "number": agency.get("number", ""),
                "lien": agency.get("siteWeb", "")
            }
            for agency in agencies
        ]
        response = {
            "agencies": response_agencies,
            "total_agencies": total_agencies,
            "total_pages": total_pages,
            "current_page": page
        }
        logger.info(f"✅ Récupération de {len(response_agencies)} agences pour la page {page}")
        return response
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la récupération des agences : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

# Nouvelle API pour mettre à jour une agence dans agencesFinale
@api_router.put("/api/v1/agencies/{agency_id}", response_model=Dict)
async def update_agency(agency_id: str, update: AgencyUpdate):
    try:
        agency_object_id = ObjectId(agency_id)
        update_data = {k: v for k, v in update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

        db = get_db()
        collection = db["agencesFinale"]
        result = await collection.update_one(
            {"_id": agency_object_id},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Agence non trouvée")
        
        logger.info(f"✅ Agence {agency_id} mise à jour avec succès")
        return {"message": "Mise à jour réussie"}
    except ValueError as e:
        logger.error(f"⚠️ ID invalide pour l'agence {agency_id} : {e}")
        raise HTTPException(status_code=400, detail=f"ID invalide : {str(e)}")
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la mise à jour de l'agence {agency_id} : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")