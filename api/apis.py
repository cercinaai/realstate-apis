# api/apis.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from typing import Optional, List, Dict
from loguru import logger
from models.annonce import AnnonceOutput
from models.agenc import AgenceOutput
from database import get_db  # Importer get_db
import math
from pydantic import BaseModel
import bcrypt
import jwt
from datetime import datetime, timedelta

api_router = APIRouter()

# Modèle pour la requête de login
class LoginRequest(BaseModel):
    username: str
    password: str

# Modèle pour la mise à jour des agences
class AgencyUpdate(BaseModel):
    email: Optional[str] = None
    number: Optional[str] = None

# Clé secrète pour JWT
SECRET_KEY = "cercina-F7zR1aXq3N9vL8Pw"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 240000

# Utilisateur par défaut
DEFAULT_USER = {
    "username": "realEstateAdmin",
    "password": bcrypt.hashpw("realEstateData15963".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
}

# OAuth2 pour valider le token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Vérification du mot de passe
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Création d’un token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=150000)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Vérification du token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != DEFAULT_USER["username"]:
            raise credentials_exception
        return username
    except jwt.PyJWTError:
        raise credentials_exception

# API de login
@api_router.post("/auth/login", response_model=Dict)
async def login(request: LoginRequest):
    try:
        if request.username != DEFAULT_USER["username"]:
            raise HTTPException(status_code=401, detail="Nom d'utilisateur incorrect")
        if not verify_password(request.password, DEFAULT_USER["password"]):
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": request.username}, expires_delta=access_token_expires
        )
        logger.info(f"✅ Connexion réussie pour {request.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la connexion : {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# Helper pour formater une annonce
def format_annonce(annonce: Dict) -> Dict:
    return {
        "id": annonce.get("idSec", ""),  # id = idSec
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
            "id": annonce.get("storeId", ""),  # id = storeId au lieu de idAgence
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
        "id": agence.get("storeId", ""),  # id = storeId
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

        # Filtrer uniquement les annonces avec un storeId existant dans agencesFinale
        pipeline = [
            {"$lookup": {
                "from": "agencesFinale",
                "localField": "storeId",
                "foreignField": "storeId",
                "as": "agence_info"
            }},
            {"$match": {"agence_info": {"$ne": []}}},  # Ne garder que les annonces avec agence
            {"$sort": {"scraped_at": -1}},  # Tri par scraped_at
            {"$skip": skip},
            {"$limit": per_page}
        ]

        annonces = await collection.aggregate(pipeline).to_list(length=per_page)
        total_annonces = await collection.aggregate([
            {"$lookup": {
                "from": "agencesFinale",
                "localField": "storeId",
                "foreignField": "storeId",
                "as": "agence_info"
            }},
            {"$match": {"agence_info": {"$ne": []}}},
            {"$count": "total"}
        ]).to_list(length=1)
        total_annonces = total_annonces[0]["total"] if total_annonces else 0
        total_pages = math.ceil(total_annonces / per_page)

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
        db = get_db()
        collection = db["realStateFinale"]
        query = {}

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

        # Pipeline pour filtrer les annonces avec agence et appliquer les filtres
        pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "agencesFinale",
                "localField": "storeId",
                "foreignField": "storeId",
                "as": "agence_info"
            }},
            {"$match": {"agence_info": {"$ne": []}}},  # Ne garder que les annonces avec agence
            {"$sort": {"scraped_at": -1}},  # Tri par scraped_at
            {"$skip": skip},
            {"$limit": per_page}
        ]

        annonces = await collection.aggregate(pipeline).to_list(length=per_page)
        total_annonces = await collection.aggregate([
            {"$match": query},
            {"$lookup": {
                "from": "agencesFinale",
                "localField": "storeId",
                "foreignField": "storeId",
                "as": "agence_info"
            }},
            {"$match": {"agence_info": {"$ne": []}}},
            {"$count": "total"}
        ]).to_list(length=1)
        total_annonces = total_annonces[0]["total"] if total_annonces else 0
        total_pages = math.ceil(total_annonces / per_page)

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
        annonce = await collection.find_one({"idSec": annonce_id})
        if not annonce:
            raise HTTPException(status_code=404, detail="Annonce non trouvée")

        # Vérifier si l'annonce a une agence associée
        agence_collection = db["agencesFinale"]
        agence = await agence_collection.find_one({"storeId": annonce.get("storeId")})
        if not agence:
            raise HTTPException(status_code=404, detail="Annonce sans agence associée")

        formatted_annonce = format_annonce(annonce)

        lat, lon = annonce.get("latitude", 0.0), annonce.get("longitude", 0.0)
        price = annonce.get("price", 0)
        earth_radius_km = 6371
        distance_km = 4 / earth_radius_km

        similar_query = {
            "latitude": {"$gte": lat - distance_km, "$lte": lat + distance_km},
            "longitude": {"$gte": lon - distance_km, "$lte": lon + distance_km},
            "price": {"$gte": price - 200, "$lte": price + 200},
            "idSec": {"$ne": annonce_id}
        }
        # Filtrer les similaires pour qu'elles aient une agence
        similar_pipeline = [
            {"$match": similar_query},
            {"$lookup": {
                "from": "agencesFinale",
                "localField": "storeId",
                "foreignField": "storeId",
                "as": "agence_info"
            }},
            {"$match": {"agence_info": {"$ne": []}}}
        ]
        similar_annonces = await collection.aggregate(similar_pipeline).to_list(length=5)
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

        # Optimisation : ne charger que les champs nécessaires dans $lookup
        pipeline = [
            {"$lookup": {
                "from": "realStateFinale",
                "localField": "storeId",
                "foreignField": "storeId",
                "pipeline": [{"$project": {"_id": 1}}],  # Limiter les données
                "as": "annonces_info"
            }},
            {"$match": {"annonces_info": {"$ne": []}}},
            {"$sort": {"_id": -1}},
            {"$skip": skip},
            {"$limit": per_page}
        ]

        agences = await collection.aggregate(pipeline).to_list(length=per_page)
        total_pipeline = [
            {"$lookup": {
                "from": "realStateFinale",
                "localField": "storeId",
                "foreignField": "storeId",
                "pipeline": [{"$project": {"_id": 1}}],
                "as": "annonces_info"
            }},
            {"$match": {"annonces_info": {"$ne": []}}},
            {"$count": "total"}
        ]
        total_result = await collection.aggregate(total_pipeline).to_list(length=1)
        total_agences = total_result[0]["total"] if total_result else 0
        total_pages = math.ceil(total_agences / per_page)

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
        agence = await collection.find_one({"storeId": agence_id})
        if not agence:
            raise HTTPException(status_code=404, detail="Agence non trouvée")

        # Vérifier si l'agence a des annonces
        annonce_collection = db["realStateFinale"]
        agence_annonces = await annonce_collection.find({"storeId": agence_id}).to_list(length=None)
        if not agence_annonces:
            raise HTTPException(status_code=404, detail="Agence sans annonces associées")

        formatted_agence = format_agence(agence)
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

# API pour toutes les agences avec pagination et authentification
@api_router.get("/agencies/all", response_model=Dict)
async def get_agencies(page: int = 1, limit: int = 10, current_user: str = Depends(get_current_user)):
    try:
        skip = (page - 1) * limit
        db = get_db()
        agencies_collection = db["agencesFinale"]

        # Optimisation : limiter les champs dans $lookup
        pipeline = [
            {"$lookup": {
                "from": "realStateFinale",
                "localField": "storeId",
                "foreignField": "storeId",
                "pipeline": [{"$project": {"_id": 1}}],  # Réduire la taille des données
                "as": "annonces_info"
            }},
            {"$match": {"annonces_info": {"$ne": []}}},
            {"$project": {
                "id": "$storeId",
                "name": {"$ifNull": ["$name", ""]},
                "email": {"$ifNull": ["$email", ""]},
                "number": {"$ifNull": ["$number", ""]},
                "lien": {"$ifNull": ["$lien", ""]},
                "annonces_count": {"$size": "$annonces_info"}
            }},
            {"$sort": {"annonces_count": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]

        agencies = await agencies_collection.aggregate(pipeline).to_list(length=limit)
        total_pipeline = [
            {"$lookup": {
                "from": "realStateFinale",
                "localField": "storeId",
                "foreignField": "storeId",
                "pipeline": [{"$project": {"_id": 1}}],
                "as": "annonces_info"
            }},
            {"$match": {"annonces_info": {"$ne": []}}},
            {"$count": "total"}
        ]
        total_result = await agencies_collection.aggregate(total_pipeline).to_list(length=1)
        total_agencies = total_result[0]["total"] if total_result else 0
        total_pages = math.ceil(total_agencies / limit)

        response_agencies = [
            {
                "id": agency.get("id", ""),
                "name": agency.get("name", ""),
                "email": agency.get("email", ""),
                "number": agency.get("number", ""),
                "lien": agency.get("lien", ""),
                "annonces_count": agency.get("annonces_count", 0)
            }
            for agency in agencies
        ]

        response = {
            "agencies": response_agencies,
            "total_agencies": total_agencies,
            "total_pages": total_pages,
            "current_page": page
        }
        logger.info(f"✅ Récupération de {len(response_agencies)} agences pour la page {page}, triées par nombre d'annonces")
        return response
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la récupération des agences : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

# API pour mettre à jour une agence
@api_router.put("/agencies/{agency_id}", response_model=Dict)
async def update_agency(agency_id: str, update: AgencyUpdate, current_user: str = Depends(get_current_user)):
    try:
        update_data = {k: v for k, v in update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

        db = get_db()
        collection = db["agencesFinale"]
        result = await collection.update_one(
            {"storeId": agency_id},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Agence non trouvée")
        
        logger.info(f"✅ Agence {agency_id} mise à jour avec succès")
        return {"message": "Mise à jour réussie"}
    except Exception as e:
        logger.error(f"⚠️ Erreur lors de la mise à jour de l'agence {agency_id} : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")