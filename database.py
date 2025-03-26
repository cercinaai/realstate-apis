# database.py
import motor.motor_asyncio
from loguru import logger
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer les identifiants et les encoder
username = quote_plus("admin")
password = quote_plus("SuperSecureP@ssw0rd!")
host = os.getenv("MONGO_HOST", "mongodb")  # Par défaut "mongodb" pour Docker
database_name = os.getenv("DATABASE_NAME", "xtracto-io-prod")

# Construire l'URI MongoDB
MONGO_URI = f"mongodb://{username}:{password}@{host}:27017/{database_name}?authSource=admin"

# Variables globales pour la connexion
client = None
db = None

async def init_db():
    global client, db
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        db = client[database_name]
        await db.command("ping")  # Vérifie la connexion
        logger.success("✅ Connexion à MongoDB établie")
    except Exception as e:
        logger.error(f"⚠️ Échec de la connexion à MongoDB : {e}")
        raise

async def close_db():
    global client
    if client:
        client.close()
        logger.info("🔌 Connexion MongoDB fermée")

def get_db():
    if db is None:
        raise Exception("La base de données n'est pas initialisée. Appelez init_db() d'abord.")
    return db